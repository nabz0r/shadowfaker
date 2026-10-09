#!/usr/bin/env python3
"""One-command resumable fetch → parse → train → evaluate → demo."""
import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import shutil

from shadowfaker.fetch import fetch
from shadowfaker.features import parse
from shadowfaker.train import train
from shadowfaker.evaluate import evaluate
from shadowfaker.demo import demo
from shadowfaker.config import CONFIG


def record(message: str):
    with (CONFIG.root / "PROGRESS.md").open("a") as stream:
        stream.write(f"\n- [{datetime.now().isoformat(timespec='minutes')}] {message}\n")


def run_stage(limit: int, epochs: int, game_name: str | None = None, tag_line: str | None = None):
    manifest = fetch(limit, game_name, tag_line)
    count = len(manifest["order"])
    record(f"Fetch {limit}: {count} usable ranked matches cached.")
    meta = parse(limit=limit)
    record(f"Parse {limit}: {len(meta['counts'])} matches, {meta['observations']} observations, {len(meta['errors'])} errors.")
    training = train(epochs=epochs)
    record(f"Train {limit}: {training['epochs_ran']} epochs, device {training['device']}, {training['parameters']} parameters.")
    metrics = evaluate()
    record(f"Evaluate {limit}: region top-1 {metrics['model_region_top1']:.4f}, best baseline {max(metrics[k] for k in ('baseline_most_frequent', 'baseline_copy_previous', 'baseline_stay_mid')):.4f}.")
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
    if args.limit > 5:
        print("Validating every stage on five matches first...")
        run_stage(5, min(args.epochs, 3), args.game_name, args.tag_line)
    metrics = run_stage(args.limit, args.epochs, args.game_name, args.tag_line)
    if args.limit > 5 and not metrics["beats_all_region_baselines"]:
        record("Initial model did not beat all region baselines; trying wider 3-layer model and higher learning rate.")
        best = metrics["model_region_top1"]
        saved = CONFIG.models / "initial.pt"
        shutil.copy2(CONFIG.models / "best.pt", saved)
        train(epochs=max(args.epochs, 30), lr=1e-3, width=192, layers=3, force=True)
        retry = evaluate()
        record(f"Iteration: region top-1 {retry['model_region_top1']:.4f} after width/LR change.")
        if retry["model_region_top1"] < best:
            shutil.copy2(saved, CONFIG.models / "best.pt")
            metrics = evaluate()
            record("Restored stronger initial checkpoint after iteration.")
        else:
            metrics = retry
        demo()
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
