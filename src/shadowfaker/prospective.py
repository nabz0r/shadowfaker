"""Freeze a model and score only genuinely later, previously unseen matches."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil

import numpy as np
import torch

from .config import CONFIG
from .evaluate import evaluate
from .features import _save_npz, extract_match
from .fetch import fetch
from .train import signature
from .util import atomic_json, read_json

LOG = logging.getLogger(__name__)
PROTOCOL_VERSION = 1
MIN_NEW_MATCHES = 100


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_freeze(directory: Path) -> dict:
    protocol = read_json(directory / "protocol.json")
    if not protocol or protocol.get("version") != PROTOCOL_VERSION:
        raise ValueError("Prospective protocol is missing or has an unsupported version")
    for name, expected in (("frozen_meta.json", protocol["meta_sha256"]),
                           ("frozen_checkpoint.pt", protocol["checkpoint_sha256"])):
        if file_hash(directory / name) != expected:
            raise ValueError(f"Frozen {name} changed; refuse prospective evaluation")
    return protocol


def freeze(processed: Path = CONFIG.processed, models: Path = CONFIG.models,
           raw: Path = CONFIG.raw, directory: Path = CONFIG.root / "data" / "prospective",
           minimum_matches: int = MIN_NEW_MATCHES) -> dict:
    if minimum_matches < 1:
        raise ValueError("minimum_matches must be positive")
    if (directory / "protocol.json").exists():
        return verify_freeze(directory)
    meta = read_json(processed / "meta.json")
    manifest = read_json(raw / "manifest.json")
    if not meta or not manifest or not manifest.get("account", {}).get("puuid"):
        raise FileNotFoundError("Frozen development metadata and Riot account manifest are required")
    starts = [int(value) for value in meta.get("game_start_ms", {}).values() if int(value) > 0]
    if len(starts) != len(meta["counts"]):
        raise ValueError("Every development match needs a valid start timestamp before freezing")
    checkpoint = models / "best.pt"
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if saved.get("signature") != signature(meta) or not saved.get("calibration"):
        raise ValueError("Selected calibrated checkpoint does not match development metadata")
    region_counts = Counter()
    for mid in meta["splits"]["train"]:
        with np.load(processed / "matches" / f"{mid}.npz") as arrays:
            region_counts.update(int(value) for value in arrays["region"])
    directory.mkdir(parents=True, exist_ok=True)
    frozen_meta = directory / "frozen_meta.json"
    frozen_checkpoint = directory / "frozen_checkpoint.pt"
    shutil.copyfile(processed / "meta.json", frozen_meta.with_suffix(".tmp"))
    os.replace(frozen_meta.with_suffix(".tmp"), frozen_meta)
    shutil.copyfile(checkpoint, frozen_checkpoint.with_suffix(".tmp"))
    os.replace(frozen_checkpoint.with_suffix(".tmp"), frozen_checkpoint)
    protocol = {"version": PROTOCOL_VERSION,
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "account_puuid": manifest["account"]["puuid"],
                "schema_version": meta["schema_version"],
                "source_matches": len(meta["counts"]),
                "source_signature": signature(meta),
                "cutoff_ms": max(starts),
                "minimum_new_matches": minimum_matches,
                "primary_metric": "8x8 model top-1 gain vs strongest frozen baseline; match bootstrap 95% lower bound > 0",
                "secondary_metrics": ["16x16 top-1", "4x4 top-1", "item accuracy", "skill accuracy"],
                "train_region_counts": {str(k): int(v) for k, v in region_counts.items()},
                "meta_sha256": file_hash(frozen_meta),
                "checkpoint_sha256": file_hash(frozen_checkpoint)}
    atomic_json(directory / "protocol.json", protocol)
    return protocol


def prepare(raw: Path = CONFIG.raw, processed: Path = CONFIG.processed,
            directory: Path = CONFIG.root / "data" / "prospective") -> dict:
    protocol = verify_freeze(directory)
    meta = read_json(directory / "frozen_meta.json")
    manifest = read_json(raw / "manifest.json")
    if not manifest or manifest.get("account", {}).get("puuid") != protocol["account_puuid"]:
        raise ValueError("Riot account differs from the frozen protocol")
    development = set(meta["counts"])
    previous = read_json(directory / "manifest.json", {})
    matches = dict(previous.get("matches", {}))
    errors = dict(previous.get("errors", {}))
    for mid in manifest.get("order", []):
        if mid in development or manifest["games"].get(mid, {}).get("status") != "ok":
            continue
        try:
            match = read_json(raw / "matches" / f"{mid}.json")
            info = (match or {}).get("info") or {}
            start_ms = int(info.get("gameStartTimestamp") or info.get("gameCreation") or 0)
            if start_ms <= protocol["cutoff_ms"]:
                continue
            path = processed / "matches" / f"{mid}.npz"
            if not path.exists():
                timeline = read_json(raw / "timelines" / f"{mid}.json")
                arrays = extract_match(match, timeline, protocol["account_puuid"], meta["window"])
                _save_npz(path, arrays)
            with np.load(path) as arrays:
                count = int(len(arrays["region"]))
            player = next((p for p in info.get("participants") or []
                           if p.get("puuid") == protocol["account_puuid"]), {})
            matches[mid] = {"count": count, "patch": str(info.get("gameVersion") or "unknown").rsplit(".", 2)[0],
                            "role": str(player.get("teamPosition") or "unknown"),
                            "win": bool(player.get("win")), "start_ms": start_ms}
            errors.pop(mid, None)
        except Exception as exc:
            LOG.exception("Prospective parse failed for %s; continuing", mid)
            errors[mid] = str(exc)
    ids = sorted(matches, key=lambda mid: (matches[mid]["start_ms"], mid))
    out = {"status": "ready" if len(ids) >= protocol["minimum_new_matches"] else "pending",
           "cutoff_ms": protocol["cutoff_ms"], "new_match_ids": ids,
           "new_matches": len(ids), "minimum_new_matches": protocol["minimum_new_matches"],
           "id_snapshot": manifest.get("latest_id_snapshot"), "matches": matches, "errors": errors}
    atomic_json(directory / "manifest.json", out)
    return out


def score(processed: Path = CONFIG.processed, models: Path = CONFIG.models,
          artifacts: Path = CONFIG.artifacts,
          directory: Path = CONFIG.root / "data" / "prospective") -> dict:
    protocol = verify_freeze(directory)
    existing = read_json(directory / "score.json")
    if existing:
        return existing
    new = read_json(directory / "manifest.json")
    if not new:
        raise FileNotFoundError("Prospective manifest missing; run prepare first")
    if new["new_matches"] < protocol["minimum_new_matches"]:
        return {"status": "pending", "new_matches": new["new_matches"],
                "minimum_new_matches": protocol["minimum_new_matches"], "cutoff_ms": protocol["cutoff_ms"]}
    ids = new["new_match_ids"]
    rows = new["matches"]
    metadata = {"counts": {mid: rows[mid]["count"] for mid in ids},
                "patches": {mid: rows[mid]["patch"] for mid in ids},
                "faker_roles": {mid: rows[mid]["role"] for mid in ids},
                "faker_wins": {mid: rows[mid]["win"] for mid in ids},
                "game_start_ms": {mid: rows[mid]["start_ms"] for mid in ids}}
    metrics = evaluate(processed, models, artifacts, split="test",
                       meta_path=directory / "frozen_meta.json",
                       checkpoint_path=directory / "frozen_checkpoint.pt",
                       match_ids=ids, match_metadata=metadata,
                       train_region_counts=protocol["train_region_counts"],
                       output_tag="prospective")
    primary = metrics["macro_grids_exploratory"]["8x8"]
    outcome = {"status": "scored_once", "new_matches": len(ids),
               "primary_pass": primary["gain_bootstrap95_pp"][0] > 0,
               "primary_8x8": primary, "legacy_16x16": {
                   "top1": metrics["model_region_top1"],
                   "gain_bootstrap95_pp": metrics["region_gain_bootstrap95_pp"]},
               "checkpoint_sha256": protocol["checkpoint_sha256"],
               "source_signature": protocol["source_signature"]}
    atomic_json(directory / "score.json", outcome)
    return outcome


def run(snapshot: str | None = None, offline: bool = False,
        raw: Path = CONFIG.raw, processed: Path = CONFIG.processed,
        models: Path = CONFIG.models, artifacts: Path = CONFIG.artifacts,
        directory: Path = CONFIG.root / "data" / "prospective") -> dict:
    protocol = freeze(processed, models, raw, directory)
    existing = read_json(directory / "score.json")
    if existing:
        return existing
    if not offline:
        snapshot = snapshot or datetime.now(timezone.utc).strftime("%Y%m%d")
        fetch(1000, id_snapshot=snapshot)
    prepared = prepare(raw, processed, directory)
    LOG.info("Prospective matches: %s/%s after cutoff %s",
             prepared["new_matches"], protocol["minimum_new_matches"], protocol["cutoff_ms"])
    return score(processed, models, artifacts, directory)
