"""Patch-matched official Data Dragon item descriptors as causal IoC context.

Third-party build pages are research references, not model features: their
aggregate win rates are retrospective and may describe a different patch.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import time
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

import numpy as np
import requests
from tqdm import tqdm

from .config import CONFIG
from .features import position, _save_npz
from .ioc import _actor_order, _windows, inventory_snapshots
from .util import atomic_json, read_json

ROOT = CONFIG.root / "data" / "ioc_static"
CACHE = CONFIG.raw / "ddragon"
TAGS = ("Damage", "SpellDamage", "Health", "Armor", "SpellBlock", "Boots",
        "Vision", "Consumable", "AbilityHaste", "AttackSpeed")
FIELDS = ["catalog_value", "catalog_known_fraction", *(f"tag_{tag.lower()}" for tag in TAGS)]
NAMES = [f"p{p}_static_{field}" for p in range(10) for field in FIELDS]


def _download(url: str, path: Path) -> dict:
    if path.is_file(): return json.loads(path.read_text())
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(5):
        try:
            response = requests.get(url, timeout=(5, 25), headers={"User-Agent":"shadowfaker-research/1.0"})
            if response.status_code == 429:
                raw = response.headers.get("Retry-After", "2")
                try:
                    delay = float(raw)
                except ValueError:
                    try:
                        delay = (parsedate_to_datetime(raw) - datetime.now(timezone.utc)).total_seconds()
                    except (TypeError, ValueError, OverflowError):
                        delay = 2 ** attempt
                time.sleep(max(0, min(30, delay)))
                continue
            response.raise_for_status()
            data = response.json()
            atomic_json(path, data)
            return data
        except (requests.RequestException, ValueError):
            if attempt == 4: raise
            time.sleep(min(12, 2 ** attempt))
    raise RuntimeError(f"Could not download {url}")


def versions() -> list[str]:
    return _download("https://ddragon.leagueoflegends.com/api/versions.json",
                     CACHE / "versions.json")


def match_patch(match: dict) -> str:
    raw = str((match.get("info") or {}).get("gameVersion") or "")
    parts = raw.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else ""


def item_catalog(patch: str, releases: list[str]) -> tuple[str, dict]:
    release = next((v for v in releases if v.startswith(patch + ".")), None)
    if release is None: raise ValueError(f"No Data Dragon release for patch {patch}")
    url = f"https://ddragon.leagueoflegends.com/cdn/{release}/data/en_US/item.json"
    data = _download(url, CACHE / release / "en_US_item.json")
    return release, data["data"]


def item_vector(items: dict, catalogue: dict) -> np.ndarray:
    result = np.zeros(len(FIELDS), np.float32)
    total = sum(items.values())
    if not total: return result
    known = 0
    for item, count in items.items():
        descriptor = catalogue.get(str(item))
        if not descriptor: continue
        known += count
        result[0] += min(10000, float((descriptor.get("gold") or {}).get("total") or 0)) * count / 30000
        labels = set(descriptor.get("tags") or [])
        for i, tag in enumerate(TAGS, start=2):
            if tag in labels: result[i] += count / 6
    result[1] = known / total
    return result


def match_channels(match: dict, timeline: dict, puuid: str, catalogue: dict) -> tuple[np.ndarray, np.ndarray]:
    order, team_id = _actor_order(match, timeline, puuid)
    players = (match.get("info") or {}).get("participants") or []
    teams = {int(p.get("participantId") or i+1): int(p.get("teamId") or (100 if i<5 else 200))
             for i,p in enumerate(players)}
    if len(teams)<10: teams={i:100 if i<=5 else 200 for i in range(1,11)}
    frames = (timeline.get("info") or {}).get("frames") or []
    inventories = inventory_snapshots(timeline)[0]
    proxy = np.zeros((len(frames),len(NAMES)),np.float32)
    oracle = np.zeros_like(proxy)
    last_seen = {}
    for fi,frame in enumerate(frames):
        pf=frame.get("participantFrames") or {}
        pos={p:position(pf.get(str(p)) or pf.get(p) or {}) for p in range(1,11)}
        allies=[v for p,v in pos.items() if teams.get(p)==team_id and v is not None]
        for slot,p in enumerate(order):
            start=slot*len(FIELDS)
            vec=item_vector(inventories[fi][p], catalogue)
            oracle[fi,start:start+len(FIELDS)]=vec
            if teams.get(p)==team_id:
                proxy[fi,start:start+len(FIELDS)]=vec
            elif pos[p] is not None and any(np.linalg.norm(pos[p]-ally)<=1600/15000 for ally in allies):
                last_seen[p]=vec.copy()
                proxy[fi,start:start+len(FIELDS)]=vec
            elif p in last_seen:
                proxy[fi,start:start+len(FIELDS)]=last_seen[p]
    return proxy,oracle


def prepare(limit: int | None = None, output: Path = ROOT,
            base_root: Path = CONFIG.root / "data" / "ioc") -> dict:
    base = read_json(base_root / "meta.json")
    manifest=read_json(CONFIG.raw / "manifest.json")
    if not base or not manifest: raise FileNotFoundError("Build causal item IoC first")
    releases=versions()
    splits=base["splits"]
    ids=splits["train"]+splits["val"]+splits["test"]
    if limit is not None: ids=(splits["train"][:3]+splits["val"][:2]) if limit==5 else ids[:limit]
    output.joinpath("matches").mkdir(parents=True,exist_ok=True)
    counts,errors,patches={},{},{}
    for mid in tqdm(ids,desc="patch-matched item IoC",unit="game"):
        try:
            match=json.loads((CONFIG.raw/"matches"/f"{mid}.json").read_text())
            patch=match_patch(match)
            release,catalogue=item_catalog(patch,releases)
            target=output/"matches"/f"{mid}.npz"
            if not target.exists():
                timeline=json.loads((CONFIG.raw/"timelines"/f"{mid}.json").read_text())
                proxy,oracle=match_channels(match,timeline,manifest["account"]["puuid"],catalogue)
                with np.load(base_root/"matches"/f"{mid}.npz") as z:
                    data={key:z[key] for key in z.files}
                frames=(timeline.get("info") or {}).get("frames") or []
                for key,channels in (("x",proxy),("x_oracle",oracle)):
                    data[key]=np.concatenate((data[key],_windows(channels,frames,data["minute"],data[key].shape[1])),axis=-1)
                _save_npz(target,data)
            with np.load(target) as z:
                if z["x"].shape[2]!=base["feature_dim"]+len(NAMES):raise ValueError("Stale static IoC width")
                counts[mid]=len(z["x"])
            patches[patch]=release
        except Exception as exc: errors[mid]=str(exc)
    meta=copy.deepcopy(base)
    meta["schema_version"]=300+base["schema_version"]
    meta["feature_names"]=base["feature_names"]+NAMES
    meta["feature_dim"]=len(meta["feature_names"])
    meta["counts"],meta["errors"] = counts,errors
    meta["observations"]=sum(counts.values())
    meta["splits"]={split:[mid for mid in splits[split] if mid in counts] for split in ("train","val","test")}
    meta["static_ioc"]={"provider":"Riot Data Dragon", "releases_by_patch":patches,
                        "fields":FIELDS,"perspective":"time-t inventory with patch-matched static descriptors",
                        "source_url":"https://developer.riotgames.com/docs/lol#data-dragon"}
    atomic_json(output/"meta.json",meta)
    return meta


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("--limit",type=int);args=parser.parse_args()
    meta=prepare(args.limit)
    print({"matches":len(meta["counts"]),"observations":meta["observations"],
           "features":meta["feature_dim"],"patches":len(meta["static_ioc"]["releases_by_patch"]),
           "errors":meta["errors"]})


if __name__=="__main__": main()
