"""Aggregate private Riot replay-clock coverage without publishing match rows."""
import argparse
import json
from pathlib import Path

from tqdm import tqdm

from shadowfaker.config import CONFIG
from shadowfaker.util import atomic_json, read_json


def audit(limit: int | None = None) -> dict:
    meta = read_json(CONFIG.processed / "meta.json")
    ids = [mid for split in ("train", "val", "test") for mid in meta["splits"][split]]
    if limit == 5:
        ids = meta["splits"]["train"][:3] + meta["splits"]["val"][:2]
    elif limit is not None:
        ids = ids[:limit]
    totals = {"games": 0, "frames": 0, "non_increasing_frames": 0,
              "player_slots": 0, "missing_player_positions": 0,
              "events": 0, "events_at_or_before_first_frame": 0,
              "events_after_last_frame": 0, "events_outside_container_interval": 0,
              "events_exactly_on_previous_boundary": 0}
    for mid in tqdm(ids, desc="Audit replay", unit="game"):
        path = CONFIG.raw / "timelines" / f"{mid}.json"
        frames = (json.loads(path.read_text()).get("info") or {}).get("frames") or []
        if not frames:
            continue
        totals["games"] += 1
        totals["frames"] += len(frames)
        first, last = int(frames[0].get("timestamp") or 0), int(frames[-1].get("timestamp") or 0)
        for index, frame in enumerate(frames):
            time = int(frame.get("timestamp") or 0)
            if index and time <= int(frames[index - 1].get("timestamp") or 0):
                totals["non_increasing_frames"] += 1
            actors = frame.get("participantFrames") or {}
            for pid in range(1, 11):
                totals["player_slots"] += 1
                if not (actors.get(str(pid)) or actors.get(pid) or {}).get("position"):
                    totals["missing_player_positions"] += 1
            low = int(frames[index - 1].get("timestamp") or 0) if index else first
            for event in frame.get("events") or []:
                totals["events"] += 1
                stamp = int(event.get("timestamp") or time)
                totals["events_at_or_before_first_frame"] += stamp <= first
                totals["events_after_last_frame"] += stamp > last
                if index and not low < stamp <= time:
                    totals["events_outside_container_interval"] += 1
                    totals["events_exactly_on_previous_boundary"] += stamp == low
    return {"schema_version": 1, "scope": "Riot KR ranked timeline replay clock, all eligible split matches",
            "pilot": limit is not None, "public_aggregate_only": True,
            "counts": totals,
            "interpretation": "Events are assigned by timestamp; player positions are sampled at frame timestamps. No path or player POV is inferred."}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path, default=CONFIG.root / "docs/data/public_replay_audit.json")
    args = parser.parse_args()
    report = audit(args.limit)
    atomic_json(args.output, report)
    print(json.dumps(report["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
