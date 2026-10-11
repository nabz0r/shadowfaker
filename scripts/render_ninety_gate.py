#!/usr/bin/env python3
"""Render the aggregate-only exact-cell risk/coverage diagnostic."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs" / "data" / "public_ninety_gate.json"
OUTPUT = ROOT / "docs" / "figures" / "ninety_exact_gate.png"


def main() -> None:
    report = json.loads(PUBLIC.read_text())
    rows = report["accuracy_at_fixed_served_coverage"]
    x = np.asarray([100 * row["coverage_actual"] for row in rows])
    y = np.asarray([100 * row["exact_accuracy"] for row in rows])
    low = np.asarray([100 * row["wilson_lower95"] for row in rows])
    bg, panel, ink, muted = "#0b0c13", "#171c29", "#f7f0ee", "#b8aebb"
    plt.rcParams.update({"figure.facecolor": bg, "axes.facecolor": panel,
                         "axes.edgecolor": "#64485a", "axes.labelcolor": ink,
                         "xtick.color": muted, "ytick.color": muted, "text.color": ink,
                         "font.size": 11, "savefig.facecolor": bg})
    fig, ax = plt.subplots(figsize=(12.6, 6.3), layout="constrained")
    fig.suptitle("FAKER  /  THE 90% EXACT-CELL GATE", fontsize=23, fontweight="black", x=.04, ha="left")
    ax.plot(x, y, color="#ff789d", marker="o", lw=3, markersize=9, label="Exact 8×8 accuracy")
    ax.plot(x, low, color="#71dae2", marker="s", lw=2, linestyle="--", label="95% Wilson lower bound")
    ax.axhline(90, color="#ffd393", lw=2, linestyle=":", label="90% goal")
    ax.fill_between(x, low, y, color="#ff789d", alpha=.13)
    for px, py, row in ((x[0], y[0], rows[0]), (x[-1], y[-1], rows[-1])):
        ax.annotate(f"{py:.1f}%\n{row['served']:,} transitions", (px, py),
                    xytext=(0, 15), textcoords="offset points", ha="center", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 105); ax.set_ylim(0, 103)
    ax.set_xlabel("Transitions answered · % of the 1,275 validation cases")
    ax.set_ylabel("One exact next-minute 8×8 cell · % correct")
    ax.set_xticks([5, 10, 20, 50, 100])
    ax.grid(alpha=.25)
    ax.legend(loc="upper right", facecolor=panel, edgecolor="#64485a", labelcolor=ink)
    ax.text(.02, .12, "Top 5% confidence: 31/64 correct = 48.44%\n"
            "No calibrated threshold clears 90%.\n"
            "Existing model and validation: exploratory only.",
            transform=ax.transAxes, va="bottom", color="#ffd393", fontsize=12,
            bbox={"facecolor": "#2d2734", "edgecolor": "#765565", "boxstyle": "round,pad=.6"})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
