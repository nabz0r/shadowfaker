#!/usr/bin/env python3
"""Render aggregate-only event reconciliation; no raw match content leaves disk."""
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "data" / "public_event_validation.json"
OUT = ROOT / "docs" / "figures" / "event_validation.png"


def main() -> None:
    data = json.loads(SOURCE.read_text())
    plt.rcParams.update({"figure.facecolor": "#101820", "axes.facecolor": "#101820",
                         "axes.edgecolor": "#7493a0", "axes.labelcolor": "#d7e9ee",
                         "text.color": "#f2f7f8", "xtick.color": "#c7dce3",
                         "ytick.color": "#c7dce3", "font.size": 11})
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1, 1.1]})
    values = [data["raw_events"], data["indexed_events"],
              data["exact_index_rows"], sum(x["located"] for x in data["categories"].values())]
    labels = ["Raw timeline", "Legacy index", "Exact row match", "Located"]
    colors = ["#58758a", "#88c7df", "#ffcf85", "#ff6d88"]
    axes[0].barh(labels[::-1], values[::-1], color=colors[::-1], height=.57)
    axes[0].set_xlim(0, data["raw_events"] * 1.14)
    axes[0].set_title("Trace every event back to Riot", loc="left", pad=15, weight="bold")
    for i, value in enumerate(values[::-1]):
        axes[0].text(value + 5000, i, f"{value:,}", va="center", fontsize=10)
    axes[0].set_xlabel("Events across 465 KR ranked games")
    for spine in axes[0].spines.values(): spine.set_visible(False)
    axes[0].tick_params(axis="y", length=0)
    outside = data["excluded_types"]
    groups = {
        "Item lifecycle*": sum(outside.get(k, 0) for k in ("ITEM_SOLD", "ITEM_DESTROYED", "ITEM_UNDO")),
        "Level up": outside.get("LEVEL_UP", 0),
        "Tower plates": outside.get("TURRET_PLATE_DESTROYED", 0),
        "Special kill": outside.get("CHAMPION_SPECIAL_KILL", 0),
    }
    groups["Other"] = sum(outside.values()) - sum(groups.values())
    axes[1].barh(list(groups)[::-1], list(groups.values())[::-1], color="#a6dce8", height=.57)
    axes[1].set_xlim(0, max(groups.values()) * 1.22)
    axes[1].set_title("Outside the legacy event index", loc="left", pad=15, weight="bold")
    for i, value in enumerate(list(groups.values())[::-1]):
        axes[1].text(value + 1100, i, f"{value:,}", va="center", fontsize=10)
    axes[1].set_xlabel("*Item lifecycle is still used in the item proxy")
    for spine in axes[1].spines.values(): spine.set_visible(False)
    axes[1].tick_params(axis="y", length=0)
    fig.text(.03, .01, "Exact transcription of 353,409 rows. Attribution and Faker POV require separate evidence.",
             fontsize=9, color="#aabfc7")
    fig.tight_layout(rect=(0, .05, 1, 1), w_pad=4)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
