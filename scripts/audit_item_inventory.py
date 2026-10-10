#!/usr/bin/env python3
"""Aggregate-only audit of event-reconstructed items against final match slots.

Final slots are used solely for retrospective quality checking, never features.
"""
from __future__ import annotations

import json
from pathlib import Path

from tqdm import tqdm

from shadowfaker.config import CONFIG
from shadowfaker.ioc import inventory_snapshots
from shadowfaker.util import atomic_json, read_json

PUBLIC = CONFIG.root / "docs" / "data" / "public_ioc_quality.json"


def audit() -> dict:
    meta = read_json(CONFIG.processed / "meta.json")
    if not meta: raise FileNotFoundError("Parse ranked matches before auditing items")
    actors = frames = exact = over7_distinct = over7_quantity = 0
    jaccard_sum = 0.0
    failures = 0
    for mid in tqdm(meta["counts"],desc="item-event quality",unit="game"):
        try:
            match=json.loads((CONFIG.raw/"matches"/f"{mid}.json").read_text())
            timeline=json.loads((CONFIG.raw/"timelines"/f"{mid}.json").read_text())
            history,_=inventory_snapshots(timeline)
            if not history: raise ValueError("No timeline frames")
            for frame in history:
                for inv in frame.values():
                    frames+=1
                    over7_distinct+=len(inv)>7
                    over7_quantity+=sum(inv.values())>7
            for player in (match.get("info") or {}).get("participants") or []:
                pid=int(player.get("participantId") or 0)
                if pid not in history[-1]:continue
                observed={int(player.get(f"item{i}") or 0) for i in range(7)}-{0}
                rebuilt=set(history[-1][pid]);union=observed|rebuilt
                actors+=1
                exact+=observed==rebuilt
                jaccard_sum+=len(observed&rebuilt)/len(union) if union else 1
        except (OSError,ValueError,KeyError,TypeError):
            failures+=1
    result={"schema_version":1,"scope":"retrospective quality audit; final items never used as state-t inputs",
            "ranked_matches":len(meta["counts"]),"failed_matches":failures,
            "actor_frames":frames,"actor_frames_over_seven_distinct_ids":over7_distinct,
            "actor_frames_over_seven_quantities":over7_quantity,
            "final_actor_comparisons":actors,"exact_final_id_sets":exact,
            "exact_final_id_set_fraction":exact/actors if actors else None,
            "mean_final_id_jaccard":jaccard_sum/actors if actors else None,
            "limits":"Initial trinkets, automatic upgrades, stackable consumables and the final-match clock may differ from the event ledger. This is a proxy inventory, not complete slots."}
    atomic_json(PUBLIC,result)
    return result


if __name__=="__main__":
    print(audit())
