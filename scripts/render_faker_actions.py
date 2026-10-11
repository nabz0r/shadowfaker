#!/usr/bin/env python3
"""Render class-wise validation precision from public aggregates only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "data" / "public_faker_actions_10s.json"
OUTPUT = ROOT / "docs" / "figures" / "faker_actions_10s.png"
NAMES = ("Purchase", "Skill point", "Ward placed", "Ward cleared",
         "Kill outcome", "Death outcome", "Assist outcome")


def main() -> None:
    report = json.loads(SOURCE.read_text())
    scores = report["scores"]
    keys = list(scores["model"]["per_class"])
    model = np.array([scores["model"]["per_class"][k]["average_precision"] for k in keys])
    phase = np.array([scores["phase_train_frequency"]["per_class"][k]["average_precision"] for k in keys])
    prevalence = np.array([scores["model"]["per_class"][k]["prevalence"] for k in keys])
    n = [scores["model"]["per_class"][k]["positives"] for k in keys]
    plt.rcParams.update({"figure.facecolor": "#0b0c13", "axes.facecolor": "#171c29",
                         "axes.edgecolor": "#64485a", "axes.labelcolor": "#f7f0ee",
                         "text.color": "#f7f0ee", "xtick.color": "#b8aebb",
                         "ytick.color": "#f7f0ee", "font.size": 11,
                         "savefig.facecolor": "#0b0c13"})
    fig, ax = plt.subplots(figsize=(12.5, 6.8), layout="constrained")
    fig.suptitle("SHADOW FAKER  /  NEXT 10 SECONDS", fontsize=21,
                 fontweight="black", x=.03, ha="left")
    y = np.arange(len(keys))
    ax.barh(y + .22, model * 100, height=.23, color="#ef4d70", label="Faker action model")
    ax.barh(y, phase * 100, height=.23, color="#64cdd5", label="Train-only phase rule")
    ax.barh(y - .22, prevalence * 100, height=.23, color="#a99aaa", label="Class prevalence")
    for index in y:
        ax.text(model[index] * 100 + .18, index + .22, f"{model[index]*100:.1f}",
                va="center", fontsize=9, color="#ffe2e9")
        ax.text(phase[index] * 100 + .18, index, f"{phase[index]*100:.1f}",
                va="center", fontsize=9, color="#9df1f2")
    ax.set_yticks(y, [f"{label}  ·  {count} positives" for label, count in zip(NAMES, n)])
    ax.invert_yaxis()
    ax.set_xlabel("Average precision on 46 validation games · %  |  higher is better")
    ax.set_xlim(0, max(model) * 100 * 1.3)
    ax.grid(axis="x", alpha=.22)
    ax.legend(loc="lower right", facecolor="#171c29", edgecolor="#64485a",
              labelcolor="#f7f0ee")
    ax.text(.99, .98, "7,480 overlapping windows  ·  match split  ·  historical validation",
            transform=ax.transAxes, ha="right", va="top", fontsize=10, color="#d4bdca")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=170)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
