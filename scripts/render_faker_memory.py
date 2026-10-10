#!/usr/bin/env python3
"""Plot the public, aggregate-only retrieval challenger result."""
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures" / "faker_memory_challenge.png"


def main() -> None:
    memory = json.loads((ROOT / "docs" / "data" / "public_faker_memory.json").read_text())
    ioc = json.loads((ROOT / "docs" / "data" / "public_ioc_challenge.json").read_text())
    values = [memory["validation_top1_8"], memory["validation_baselines"]["role_phase_prior"],
              ioc["variants"]["full"]["top1_8"]]
    labels = ["Faker Memory\nretrieval", "Role + phase\nrule", "Shadow IoC\ntransformer"]
    colors = ["#8eb9d2", "#ffd08b", "#ff6b8a"]
    plt.rcParams.update({"figure.facecolor": "#12141f", "axes.facecolor": "#12141f",
                         "text.color": "#f7f0f1", "xtick.color": "#d9c9d1",
                         "ytick.color": "#d9c9d1", "axes.labelcolor": "#d9c9d1",
                         "axes.edgecolor": "#8d6778", "font.size": 12})
    fig, ax = plt.subplots(figsize=(8.2, 5.1))
    bars = ax.bar(labels, [100*x for x in values], color=colors, width=.57)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.4, f"{100*value:.2f}%",
                ha="center", va="bottom", fontsize=16, weight="bold")
    ax.set_ylim(0, 21)
    ax.set_ylabel("Exact next 8×8 cell · reused validation")
    ax.set_title("A memory can be useful without winning prediction", loc="left", fontsize=17, weight="bold", pad=18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, alpha=.12)
    ax.set_axisbelow(True)
    fig.text(.07, .015, "373 training games · 75 train games for tuning · 46 validation games · historical test untouched",
             fontsize=9, color="#bcb0bd")
    fig.tight_layout(rect=(0, .06, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
