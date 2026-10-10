#!/usr/bin/env python3
"""Render public aggregate M3 development results without distributing match data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "artifacts" / "hierarchical" / "comparison.json"
PUBLIC = ROOT / "docs" / "data" / "hierarchical_summary.json"
FIGURE = ROOT / "docs" / "figures" / "hierarchical_ablation.png"


def public_summary(report: dict) -> dict:
    if report["status"] != "development_only" or report["pilot"]:
        raise ValueError("Expected a full development-only validation report")
    return {
        "scope": "historical development validation; epoch, variant and calibration selected here",
        "train_matches": report["train_matches"], "val_matches": report["val_matches"],
        "train_samples": report["train_samples"], "val_samples": report["val_samples"],
        "selected_variant": report["selected_variant"],
        "baseline8": report["baseline8"],
        "paired_context_deltas": report["paired_context_deltas"],
        "variants": {name: {key: row[key] for key in (
            "active_features", "parameters", "selected_epoch", "checkpoint_sha256",
            "raw_top1_8", "top1_8", "topk8",
            "top1_16", "top1_64", "prior_alpha", "gain_vs_best_pp", "gain_bootstrap95_pp",
            "decision_accuracy", "decision_most_frequent_baseline", "decision_macro_f1",
            "decision_majority_macro_f1")}
            for name, row in report["variants"].items()},
        "warning": "No old-test or prospective score; omniscient global features remain in the full variant."
    }


def render(summary: dict, path: Path = FIGURE) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13.8, 5.2), facecolor="#0b0b0f")
    for panel in (ax, ax2):
        panel.set_facecolor("#14141b")
        panel.tick_params(colors="#e8e5e0")
        panel.spines["left"].set_color("#66606a")
        panel.spines["bottom"].set_color("#66606a")
        panel.grid(axis="y", color="#534b52", alpha=.35)
        panel.set_axisbelow(True)
    names = ("faker", "allies", "visible_proxy", "full")
    variants = summary["variants"]
    positions = np.arange(4)
    labels = ("Faker only", "+ team", "Vision proxy", "Proxy + globals")
    colors = ("#a7a7b2", "#d7a44c", "#70c5c3", "#ed284f")
    raw = np.array([100 * variants[name]["raw_top1_8"] for name in names])
    calibrated = np.array([100 * variants[name]["top1_8"] for name in names])
    ax.bar(positions - .17, raw, .30, color="#66616e", label="Raw model")
    for x, value, color in zip(positions + .17, calibrated, colors):
        ax.bar(x, value, .30, color=color)
        ax.text(x, value + .23, f"{value:.2f}%", ha="center", color="white", fontsize=10, weight="bold")
    baseline = 100 * max(summary["baseline8"].values())
    ax.axhline(baseline, color="#f2db8b", ls="--", lw=1.5,
               label=f"Best simple rule  {baseline:.2f}%")
    ax.set_xticks(positions, labels, color="white")
    ax.set_ylim(0, 24)
    ax.set_ylabel("8×8 next-region top-1  ·  %", color="white")
    ax.set_title("Where does Faker go next?", color="white", fontsize=14, weight="bold", loc="left", pad=16)
    ax.legend(loc="upper left", facecolor="#14141b", edgecolor="#514a52", labelcolor="white")

    decision = np.array([100 * variants[name]["decision_macro_f1"] for name in names])
    for x, value, color in zip(positions, decision, colors):
        ax2.bar(x, value, .56, color=color)
        ax2.text(x, value + .8, f"{value:.1f}%", ha="center", color="white", fontsize=10, weight="bold")
    majority = 100 * variants["full"]["decision_majority_macro_f1"]
    ax2.axhline(majority, color="#f2db8b", ls="--", lw=1.5,
                label=f"Most common decision  {majority:.1f}%")
    ax2.set_xticks(positions, labels, color="white")
    ax2.set_ylim(0, 60)
    ax2.set_ylabel("Five observed decision types  ·  macro F1 %", color="white")
    ax2.set_title("What kind of move?", color="white", fontsize=14, weight="bold", loc="left", pad=16)
    ax2.legend(loc="upper left", facecolor="#14141b", edgecolor="#514a52", labelcolor="white")
    fig.text(.03, .945, "SHADOW FAKER  /  DEVELOPMENT LAB", color="#ed284f", weight="bold", fontsize=9)
    fig.text(.03, .035,
             f"{summary['val_matches']} validation games · {summary['val_samples']:,} minute pairs · "
             "same split tunes checkpoint, variant and calibration · proxy is not Faker POV · no future-game confirmation",
             color="#c5bbc3", fontsize=9)
    fig.subplots_adjust(left=.065, right=.975, top=.85, bottom=.17, wspace=.26)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-summary", action="store_true",
                        help="Regenerate the figure from published aggregate metrics only")
    args = parser.parse_args()
    if args.from_summary:
        summary = json.loads(PUBLIC.read_text())
    else:
        summary = public_summary(json.loads(PRIVATE.read_text()))
        PUBLIC.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    render(summary)
    print(f"Rendered {FIGURE}; aggregate summary {PUBLIC}")


if __name__ == "__main__":
    main()
