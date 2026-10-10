#!/usr/bin/env python3
"""Rebuild the causal item IoC experiment from cached Riot timelines in one command."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from shadowfaker.config import CONFIG
from shadowfaker.ioc import ROOT as ITEM_ROOT, prepare as prepare_items
from shadowfaker.external_ioc import ROOT as STATIC_ROOT, prepare as prepare_static
from shadowfaker.hierarchical import run as train
from shadowfaker.demo import export_trace
from render_ioc_results import main as render_results
from build_corpus_inventory import build as build_inventory
from audit_item_inventory import audit as audit_inventory
from shadowfaker.event_validation import audit as audit_events
from render_event_validation import main as render_event_validation
from shadowfaker.faker_memory import build as build_memory, challenge as challenge_memory
from render_faker_memory import main as render_memory


def log(message: str) -> None:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{stamp}] {message}", flush=True)
    with (CONFIG.root / "PROGRESS.md").open("a", encoding="utf-8") as file:
        file.write(f"\n- [{stamp}] {message}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    pilot_root = CONFIG.root / "data" / "pilot_ioc"
    result=prepare_items(5,pilot_root/"items")
    if len(result["counts"]) != 5 or result["errors"]:
        raise RuntimeError(f"Item five-game pilot failed: {result['errors']}")
    log(f"Item IoC pilot: five games, {result['observations']} observations, zero errors.")
    result=prepare_static(5,pilot_root/"static",base_root=pilot_root/"items")
    if len(result["counts"]) != 5 or result["errors"]:
        raise RuntimeError(f"Static item five-game pilot failed: {result['errors']}")
    log(f"Static item IoC pilot: five games, {result['observations']} observations, zero errors.")
    event_pilot=audit_events(limit=5,output=None)
    if event_pilot["failed_matches"] or event_pilot["issues"] or event_pilot["indexed_events"]!=event_pilot["exact_index_rows"]:
        raise RuntimeError(f"Event validation pilot failed: {event_pilot['issues']}")
    log(f"Event validation pilot: five games, {event_pilot['exact_index_rows']} exact indexed events.")
    memory_pilot=build_memory(CONFIG.root/"data"/"pilot_faker_memory.sqlite",limit=5)
    if memory_pilot["matches"]!={"train":5,"val":5}:
        raise RuntimeError(f"Faker memory pilot failed: {memory_pilot['matches']}")
    log(f"Faker memory pilot: {sum(memory_pilot['episodes'].values())} train/validation episodes across ten games.")
    train(pilot=True,epochs=2,source=pilot_root/"static",experiment="static-ioc-hierarchical",
          variants=("full","static_off","item_off"))
    if args.pilot_only: return
    item=prepare_items(output=ITEM_ROOT)
    if item["errors"]: raise RuntimeError(f"Item IoC errors: {item['errors']}")
    log(f"Item IoC: {len(item['counts'])} games, {item['observations']} observations, {item['feature_dim']} channels.")
    static=prepare_static(output=STATIC_ROOT)
    if static["errors"]: raise RuntimeError(f"Static IoC errors: {static['errors']}")
    log(f"Patch-matched Data Dragon IoC: {len(static['counts'])} games, {static['feature_dim']} channels, {len(static['static_ioc']['releases_by_patch'])} patches.")
    quality=audit_inventory()
    log(f"Event-inventory audit: {quality['exact_final_id_sets']}/{quality['final_actor_comparisons']} exact final ID sets; proxy caveat documented.")
    event_audit=audit_events()
    if event_audit["failed_matches"] or event_audit["issues"] or event_audit["indexed_events"]!=event_audit["exact_index_rows"]:
        raise RuntimeError(f"Event validation failed: {event_audit['issues']}")
    render_event_validation()
    log(f"Event validation: {event_audit['exact_index_rows']}/{event_audit['indexed_events']} exact indexed rows across {event_audit['audited_matches']} games; exclusions documented.")
    result=train(epochs=args.epochs,source=STATIC_ROOT,experiment="static-ioc-hierarchical",
                 variants=("full","static_off","item_off"))
    log(f"Static IoC validation: {result['val_matches']} games; selected {result['selected_variant']} at 8x8={result['variants'][result['selected_variant']]['top1_8']:.4f}.")
    memory=build_memory()
    challenge=challenge_memory()
    render_memory()
    log(f"Faker memory: {memory['episodes']['train']} train and {memory['episodes']['val']} validation decisions; retrieval 8x8={challenge['validation_top1_8']:.4f}, no promotion over baseline.")
    build_inventory()
    render_results()
    export_trace(max_frames=80)
    log("Public IoC figure, corpus inventory and local game replay refreshed.")


if __name__ == "__main__": main()
