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
    result=train(epochs=args.epochs,source=STATIC_ROOT,experiment="static-ioc-hierarchical",
                 variants=("full","static_off","item_off"))
    log(f"Static IoC validation: {result['val_matches']} games; selected {result['selected_variant']} at 8x8={result['variants'][result['selected_variant']]['top1_8']:.4f}.")
    build_inventory()
    render_results()
    export_trace(max_frames=80)
    log("Public IoC figure, corpus inventory and local game replay refreshed.")


if __name__ == "__main__": main()
