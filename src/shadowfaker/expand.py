"""Audit all queues for the same PUUID; keep non-ranked domains separate."""
import argparse
from collections import Counter
import logging
from pathlib import Path

from tqdm import tqdm

from .config import CONFIG
from .fetch import duration_seconds
from .riot import RiotClient, RiotError
from .util import atomic_json, read_json

LOG = logging.getLogger(__name__)


def discover(client: RiotClient, puuid: str, snapshot: str, max_ids: int = 5000) -> list[str]:
    ids, seen = [], set()
    for start in tqdm(range(0, max_ids, 100), desc="all-queue ID pages", unit="page"):
        page = client.ids(puuid, start, 100, snapshot=snapshot, queue=None)
        if not isinstance(page, list):
            raise RiotError(200, "Unexpected all-queue match-ID response")
        for mid in page:
            if isinstance(mid, str) and mid not in seen:
                seen.add(mid)
                ids.append(mid)
        if len(page) < 100:
            break
    else:
        LOG.warning("Reached max_ids=%d; history may have more pages", max_ids)
    return ids


def expand(snapshot: str, max_ids: int = 5000, pilot: int | None = None,
           raw: Path = CONFIG.raw, client: RiotClient | None = None) -> dict:
    ranked = read_json(raw / "manifest.json")
    if not ranked:
        raise FileNotFoundError("Ranked manifest missing; run the standard fetch first")
    puuid = ranked["account"]["puuid"]
    client = client or RiotClient(raw=raw)
    ids = discover(client, puuid, snapshot, max_ids)
    if pilot is not None:
        ids = ids[:pilot]
    previous = read_json(raw / "manifest_expanded.json", {})
    games = previous.get("games", {})
    if previous and previous.get("puuid") != puuid:
        raise ValueError("Expanded manifest belongs to another PUUID")
    for mid in tqdm(ids, desc="audit all-queue matches", unit="game"):
        if mid in games and games[mid].get("status") != "error":
            continue
        try:
            match = client.match(mid)
            if not match:
                row = {"status": "missing_match"}
            else:
                info = match.get("info") or {}
                queue = int(info.get("queueId") or -1)
                map_id = int(info.get("mapId") or -1)
                players = info.get("participants") or []
                row = {"queue": queue, "map_id": map_id,
                       "status": "eligible" if map_id == 11 and duration_seconds(info) >= 300
                       and any(p.get("puuid") == puuid for p in players) else "excluded"}
                if row["status"] == "eligible":
                    timeline = client.timeline(mid)
                    if not timeline or len((timeline.get("info") or {}).get("frames") or []) < 2:
                        row["status"] = "no_timeline"
            games[mid] = row
        except RiotError as exc:
            if exc.status in (401, 403, 429):
                atomic_json(raw / "manifest_expanded.json", {"puuid": puuid, "games": games, "snapshot": snapshot})
                raise
            LOG.exception("Could not audit %s", mid)
            games[mid] = {"status": "error", "reason": str(exc)}
        atomic_json(raw / "manifest_expanded.json", {"puuid": puuid, "games": games, "snapshot": snapshot})
    # Keep every response locally, including other maps, while preserving the
    # ranked-only evaluation domain. A queue-710 Rift game is not ranked solo.
    if pilot is None:
        for mid in tqdm((mid for mid in ids if mid not in ranked["games"]),
                        total=sum(mid not in ranked["games"] for mid in ids),
                        desc="cache other-mode timelines", unit="game"):
            if games.get(mid, {}).get("status") in ("missing_match", "no_timeline", "error"):
                continue
            try:
                timeline = client.timeline(mid)
                games[mid]["timeline_cached"] = bool(timeline and (timeline.get("info") or {}).get("frames"))
            except RiotError as exc:
                if exc.status in (401, 403, 429):
                    atomic_json(raw / "manifest_expanded.json", {"puuid": puuid, "games": games, "snapshot": snapshot})
                    raise
                games[mid]["timeline_error"] = str(exc)
            atomic_json(raw / "manifest_expanded.json", {"puuid": puuid, "games": games, "snapshot": snapshot})
    counts = Counter(str(games[mid].get("queue", "unknown")) for mid in ids if games.get(mid, {}).get("status") == "eligible")
    extra = [mid for mid in ids if games.get(mid, {}).get("status") == "eligible" and mid not in ranked["games"]
             and games[mid].get("queue") in (400, 420, 430, 440)]
    other_modes = [mid for mid in ids if mid not in ranked["games"] and mid not in extra]
    result = {"snapshot": snapshot, "all_ids": len(ids), "ranked_known": len(ranked["games"]),
              "eligible_by_queue": dict(counts), "extra_same_puuid_summoners_rift": len(extra),
              "extra_ids": extra, "other_mode_ids": len(other_modes),
              "other_mode_timeline_cached": sum(bool(games.get(mid, {}).get("timeline_cached")) for mid in other_modes),
              "all_queue_counts": dict(Counter(str(games[mid].get("queue", "unknown")) for mid in ids)),
              "pilot": pilot is not None}
    atomic_json(raw / "expanded_summary.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--max-ids", type=int, default=5000)
    parser.add_argument("--pilot", type=int)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    summary = expand(args.snapshot, args.max_ids, args.pilot)
    print({k: v for k, v in summary.items() if k != "extra_ids"})


if __name__ == "__main__":
    main()
