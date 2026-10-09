import argparse
import json
import logging
from pathlib import Path
import time

from tqdm import tqdm

from .config import CONFIG
from .riot import RiotClient, RiotError
from .util import atomic_json, read_json

LOG = logging.getLogger(__name__)


def resolve_account(client: RiotClient, game_name: str, tag_line: str) -> dict:
    cached = read_json(CONFIG.raw / "resolved_account.json")
    if cached and cached.get("requested") == [game_name, tag_line]:
        return cached
    variants = [(game_name, tag_line), (game_name.title(), tag_line.upper()),
                (game_name.lower(), tag_line.upper()), (game_name.upper(), tag_line.upper())]
    seen = set()
    for name, tag in variants:
        if (name, tag) in seen:
            continue
        seen.add((name, tag))
        account = client.account(name, tag)
        if account and account.get("puuid"):
            result = {"requested": [game_name, tag_line], "resolved": [account.get("gameName", name), account.get("tagLine", tag)], "puuid": account["puuid"]}
            atomic_json(CONFIG.raw / "resolved_account.json", result)
            return result
    raise RiotError(404, f"Riot ID {game_name}#{tag_line} not found via account-v1 after case variants")


def fetch_ids(client: RiotClient, puuid: str, target: int) -> list[str]:
    ids, seen = [], set()
    # More IDs than target allow for remakes and missing timelines.
    maximum = target + max(20, target // 5)
    for start in range(0, maximum, 100):
        page = client.ids(puuid, start, 100)
        if not isinstance(page, list):
            raise RiotError(200, "Unexpected match-id response")
        for match_id in page:
            if isinstance(match_id, str) and match_id not in seen:
                seen.add(match_id)
                ids.append(match_id)
        LOG.info("IDs: page start=%s returned=%s unique=%s", start, len(page), len(ids))
        if len(page) < 100:
            break
    return ids


def duration_seconds(info: dict) -> float:
    duration = float(info.get("gameDuration") or 0)
    return duration / 1000 if duration > 100000 else duration


def fetch(limit: int = 1000, game_name: str | None = None, tag_line: str | None = None) -> dict:
    CONFIG.make_dirs()
    client = RiotClient()
    account = resolve_account(client, game_name or CONFIG.game_name, tag_line or CONFIG.tag_line)
    ids = fetch_ids(client, account["puuid"], limit)
    if not ids:
        raise RiotError(404, "No ranked solo games returned for this Riot ID")
    manifest_path = CONFIG.raw / "manifest.json"
    manifest = read_json(manifest_path, {"account": account, "games": {}, "order": []})
    if manifest.get("account", {}).get("puuid") != account["puuid"]:
        raise RiotError(0, "Cached manifest belongs to another PUUID; use a fresh data/raw directory")
    manifest["account"] = account
    started = time.monotonic()
    eligible = 0
    bar = tqdm(total=limit, desc="ranked games", unit="game")
    for match_id in ids:
        if eligible >= limit:
            break
        entry = manifest["games"].get(match_id)
        if entry and entry.get("status") == "ok":
            eligible += 1
            bar.update(1)
            continue
        if entry and entry.get("status") in ("remake", "not_ranked", "wrong_region", "wrong_account", "no_timeline", "missing_match"):
            continue
        try:
            if not match_id.startswith("KR_"):
                status = "wrong_region"
            else:
                match = client.match(match_id)
                if not match:
                    status = "missing_match"
                else:
                    info = match.get("info") or {}
                    participants = info.get("participants") or []
                    if info.get("queueId") != 420:
                        status = "not_ranked"
                    elif not any(p.get("puuid") == account["puuid"] for p in participants):
                        status = "wrong_account"
                    elif duration_seconds(info) < 300:
                        status = "remake"
                    else:
                        timeline = client.timeline(match_id)
                        status = "ok" if timeline and (timeline.get("info") or {}).get("frames") else "no_timeline"
            manifest["games"][match_id] = {"status": status}
            if status == "ok":
                eligible += 1
                bar.update(1)
            else:
                LOG.warning("Skipped %s: %s", match_id, status)
        except RiotError as exc:
            if exc.status in (401, 403, 429):
                atomic_json(manifest_path, manifest)
                bar.close()
                raise
            LOG.exception("Failed %s; continuing", match_id)
            manifest["games"][match_id] = {"status": "error", "reason": str(exc)}
        manifest["order"] = [mid for mid in ids if manifest["games"].get(mid, {}).get("status") == "ok"]
        atomic_json(manifest_path, manifest)
        elapsed = time.monotonic() - started
        if eligible:
            bar.set_postfix(eta_min=round((limit - eligible) * elapsed / eligible / 60, 1))
    bar.close()
    LOG.info("Fetched %d/%d usable matches (%d IDs scanned)", eligible, limit, len(ids))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--game-name")
    parser.add_argument("--tag-line")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    fetch(args.limit, args.game_name, args.tag_line)


if __name__ == "__main__":
    main()
