#!/usr/bin/env python3
"""One-command resumable fetch → parse → train → evaluate → demo."""
import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import shutil
import torch

from shadowfaker.fetch import fetch
from shadowfaker.features import parse
from shadowfaker.train import train, signature
from shadowfaker.evaluate import evaluate
from shadowfaker.demo import demo
from shadowfaker.analyze import analyze
from shadowfaker.calibrate import calibrate
from shadowfaker.config import CONFIG
from shadowfaker.util import atomic_json, read_json


def record(message: str):
    with (CONFIG.root / "PROGRESS.md").open("a") as stream:
        stream.write(f"\n- [{datetime.now().isoformat(timespec='minutes')}] {message}\n")


def best_baseline(metrics: dict) -> float:
    names = ("baseline_most_frequent", "baseline_copy_previous", "baseline_stay_mid", "baseline_role_phase_prior")
    return max(metrics[name] for name in names if name in metrics)


def run_stage(limit: int, epochs: int, game_name: str | None = None, tag_line: str | None = None):
    manifest = fetch(limit, game_name, tag_line)
    count = min(limit, len(manifest["order"]))
    record(f"Fetch {limit}: {count} usable ranked matches available for this stage.")
    meta = parse(limit=limit)
    record(f"Parse {limit}: {len(meta['counts'])} matches, {meta['observations']} observations, {len(meta['errors'])} errors.")
    rotations = analyze()
    record(f"Analyze {limit}: proximity by role/phase/outcome from {rotations['matches']} matches.")
    selected = read_json(CONFIG.models / "selection.json", {})
    params = selected.get("hyperparams", {}) if selected.get("signature") == signature(meta) else {}
    training = train(epochs=epochs, **params)
    record(f"Train {limit}: {training['epochs_ran']} epochs, device {training['device']}, {training['parameters']} parameters.")
    calibration = calibrate()
    record(f"Calibrate {limit}: train-only role/phase spatial prior, alpha {calibration['alpha']}, validation accuracy {calibration['accuracy']:.4f}.")
    metrics = evaluate(split="val")
    record(f"Validate {limit}: region top-1 {metrics['model_region_top1']:.4f}, best baseline {best_baseline(metrics):.4f}.")
    gif = demo()
    record(f"Demo {limit}: {gif.name} generated from held-out test match.")
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--game-name")
    parser.add_argument("--tag-line")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    marker = CONFIG.root / "data" / "mini_validation.json"
    validated = read_json(marker, {})
    if args.limit > 5 and validated.get("schema_version") != CONFIG.schema_version:
        print("Validating every stage on five matches first...")
        run_stage(5, min(args.epochs, 3), args.game_name, args.tag_line)
        atomic_json(marker, {"schema_version": CONFIG.schema_version, "games": 5})
    metrics = run_stage(args.limit, args.epochs, args.game_name, args.tag_line)
    selected = read_json(CONFIG.models / "selection.json", {})
    meta = read_json(CONFIG.processed / "meta.json")
    already_selected = selected.get("signature") == signature(meta)
    if args.limit > 5 and not already_selected:
        record("Comparing wider 3-layer model with the initial model on the same validation split.")
        best = metrics["model_region_top1"]
        saved = CONFIG.models / "initial.pt"
        shutil.copy2(CONFIG.models / "best.pt", saved)
        train(epochs=max(args.epochs, 30), lr=1e-3, width=192, layers=3, force=True)
        calibrate()
        retry = evaluate(split="val")
        record(f"Iteration: region top-1 {retry['model_region_top1']:.4f} after width/LR change.")
        if retry["model_region_top1"] <= best:
            shutil.copy2(saved, CONFIG.models / "best.pt")
            metrics = evaluate(split="val")
            record("Restored stronger initial checkpoint after iteration.")
        else:
            metrics = retry
            best = retry["model_region_top1"]
        selected_candidate = CONFIG.models / "selected_candidate.pt"
        shutil.copy2(CONFIG.models / "best.pt", selected_candidate)
        train(epochs=args.epochs, spatial_head=True, force=True)
        calibrate()
        spatial = evaluate(split="val")
        record(f"Spatial movement variant: validation region top-1 {spatial['model_region_top1']:.4f}.")
        if spatial["model_region_top1"] <= best:
            shutil.copy2(selected_candidate, CONFIG.models / "best.pt")
            metrics = evaluate(split="val")
            record("Restored stronger validation checkpoint after spatial iteration.")
        else:
            metrics = spatial
        demo()
    if args.limit > 5:
        checkpoint = torch.load(CONFIG.models / "best.pt", map_location="cpu", weights_only=False)
        atomic_json(CONFIG.models / "training.json", checkpoint["training"])
        atomic_json(CONFIG.models / "selection.json", {"signature": signature(meta),
                                                        "hyperparams": checkpoint["hyperparams"],
                                                        "validation_region_top1": metrics["model_region_top1"]})
    metrics = evaluate(split="test")
    record(f"Final test {args.limit}: region top-1 {metrics['model_region_top1']:.4f}, best baseline {best_baseline(metrics):.4f}.")
    if not metrics["region_gain_clear_by_bootstrap"]:
        message = "Performance gate unmet: test region gain is not clearly above the strongest baseline."
        logging.warning(message)
        record(message)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
