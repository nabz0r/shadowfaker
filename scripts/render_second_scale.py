#!/usr/bin/env python3
"""Render source-resolution evidence from public aggregate counts only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "data" / "public_second_scale.json"
OUTPUT = ROOT / "docs" / "figures" / "second_scale_observability.png"


def main() -> None:
    report = json.loads(SOURCE.read_text())
    horizons = [1, 5, 10, 30]
    rows = [report["horizons_seconds"][str(h)] for h in horizons]
    y = np.arange(len(horizons))
    any_event = np.array([100 * r["with_event"] / r["windows"] for r in rows])
    related = np.array([100 * r["with_faker_involvement"] / r["windows"] for r in rows])
    new_position = np.array([100 * r["with_new_faker_position"] / r["windows"] for r in rows])
    plt.rcParams.update({"figure.facecolor": "#0b0c13", "axes.facecolor": "#171c29",
                         "axes.edgecolor": "#64485a", "axes.labelcolor": "#f7f0ee",
                         "text.color": "#f7f0ee", "xtick.color": "#b8aebb",
                         "ytick.color": "#f7f0ee", "font.size": 11,
                         "savefig.facecolor": "#0b0c13"})
    fig, (left, right) = plt.subplots(1, 2, figsize=(13.5, 5.8),
                                      gridspec_kw={"width_ratios": [1.4, .9]},
                                      layout="constrained")
    fig.suptitle("FAKER  /  THE SECOND-SCALE EVIDENCE GAP", fontsize=21,
                 fontweight="black", x=.03, ha="left")
    left.barh(y + .17, any_event, height=.25, color="#ff789d", label="Some API event")
    left.barh(y - .10, related, height=.25, color="#71dae2", label="Faker involved")
    left.scatter(new_position, y, s=48, facecolors="none", edgecolors="#ffd393",
                 linewidths=2, label="New Faker position")
    left.set_yticks(y, [f"next {h} s" for h in horizons])
    left.invert_yaxis(); left.set_xlim(0, 105)
    left.set_xlabel("Share of windows after an observed frame · %")
    left.grid(axis="x", alpha=.25)
    left.legend(loc="upper right", facecolor="#171c29", edgecolor="#64485a", labelcolor="#f7f0ee")
    right.axis("off")
    totals = report["totals"]
    lines = [
        (f"{report['source_matches']:,}", "ranked games audited"),
        (f"{totals['timestamped_events']:,}", "timestamped API events"),
        (f"{totals['faker_position_anchors']:,}", "sampled Faker positions"),
        (f"{report['faker_position_gap_seconds']['median']:.2f} s", "median position gap"),
        ("0", "new Faker positions within 30 s"),
    ]
    for i, (value, label) in enumerate(lines):
        yy = .85 - i * .18
        right.text(.06, yy, value, fontsize=24, fontweight="bold",
                   color="#ffd393" if i == 4 else "#f7f0ee", transform=right.transAxes)
        right.text(.06, yy - .07, label, fontsize=11, color="#b8aebb", transform=right.transAxes)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=175)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
