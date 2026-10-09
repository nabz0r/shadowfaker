#!/usr/bin/env python3
"""Render public aggregate 64x64 figures; never reads raw Riot JSON."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm, LinearSegmentedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
FIGURES = ROOT / "docs" / "figures"
COLORS = {"faker_kill": "#ffbc77", "faker_death": "#ff5c7a", "ally_kill": "#69a9ff",
          "enemy_kill": "#dc5da2", "dragon": "#f7aa4a", "baron": "#b679ff",
          "herald": "#72d5e1", "grubs": "#aef670", "building": "#f3efac"}


def render_events() -> None:
    summary = json.loads((DATA / "public_events64.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(15, 6.6), facecolor="#091526")
    phase_names = (("early", "0–10 min"), ("middle", "10–20 min"), ("late", "20+ min"))
    for ax, (phase, title) in zip(axes, phase_names):
        ax.set_facecolor("#0c1c30")
        rows = summary["phases"][phase]
        # Dots are derived only from events with explicit Riot positions.
        for category, color in COLORS.items():
            counts = np.asarray(rows[category]["cells"]).reshape(64, 64)
            ys, xs = np.nonzero(counts)
            if len(xs):
                objective = category in ("dragon", "baron", "herald", "grubs")
                sizes = (5 if objective else 1) + (27 if objective else 8) * np.sqrt(counts[ys, xs] / max(1, counts.max()))
                ax.scatter(xs + .5, ys + .5, s=sizes, c=color, alpha=.9 if objective else .32, linewidths=0,
                           label=category.replace("_", " "))
        ax.set(xlim=(0,64), ylim=(0,64))
        ax.set_xlabel("map x",color="#b8a9b7")
        ax.set_ylabel("map y",color="#b8a9b7")
        ax.set_title(title, color="white", fontsize=15, weight="bold", pad=12)
        ax.tick_params(colors="#9ab3cb", labelsize=8)
        ax.grid(color="#35516a", alpha=.25)
        for spine in ax.spines.values(): spine.set_color("#35516a")
    legend_items = [(plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=color,
                                markersize=7, label=key.replace("_", " ")))
                    for key, color in COLORS.items()]
    fig.legend(handles=legend_items, loc="lower center", ncol=5, frameon=False,
               labelcolor="#dce9f4", fontsize=9, bbox_to_anchor=(.5, .07))
    fig.suptitle("Event geography on 64×64 cells · 465 ranked games", color="white", fontsize=19, weight="bold", x=.04, ha="left")
    fig.text(.04, .025, "Dots mark cells with timestamped events, not paths. Ward events without coordinates are counted separately.",
             color="#9ab3cb", fontsize=9)
    fig.subplots_adjust(left=.045,right=.99,top=.84,bottom=.26,wspace=.16)
    fig.savefig(FIGURES / "event_atlas64.png", dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def render_positions() -> None:
    path = DATA / "public_grid64.json"
    if not path.exists(): return
    summary = json.loads(path.read_text())
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.8), facecolor="#091526")
    maximum = max(*summary["observed_density"], *summary["predicted_density"])
    observed_map = LinearSegmentedColormap.from_list("observed", ["#0c1c30", "#15515a", "#55c6b9", "#fff0be"])
    shadow_map = LinearSegmentedColormap.from_list("shadow", ["#0c1c30", "#48192f", "#e7496b", "#fff0be"])
    for ax, key, title, cmap in zip(axes, ("observed_density", "predicted_density"),
                                    ("ACCOUNT · OBSERVED", "SHADOW · PREDICTED"), (observed_map, shadow_map)):
        ax.set_facecolor("#0c1c30")
        values = np.asarray(summary[key]).reshape(64, 64)
        ax.imshow(values, origin="lower", cmap=cmap, norm=PowerNorm(.25, vmin=0, vmax=maximum), interpolation="nearest")
        ax.set_title(title, color="#62e4d8" if key == "observed_density" else "#ffa1c9", fontsize=13, weight="bold")
        ax.set_xlabel("map x",color="#b8a9b7")
        ax.set_ylabel("map y",color="#b8a9b7")
        ax.tick_params(colors="#aabfd3", labelsize=8)
    fig.suptitle("Next-minute destinations · 64×64 map", color="white", fontsize=20, weight="bold", x=.05, ha="left")
    fig.text(.05,.045,f"Same {summary['samples']:,} observations · 46 historical ranked test games · colour = cell frequency, not accuracy.",
             color="#aabfd3", fontsize=9)
    fig.subplots_adjust(left=.06,right=.98,top=.87,bottom=.11,wspace=.14)
    fig.savefig(FIGURES / "grid64_observed_vs_predicted.png", dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    FIGURES.mkdir(parents=True, exist_ok=True)
    render_events()
    render_positions()
    print("Rendered 64×64 aggregate figures")
