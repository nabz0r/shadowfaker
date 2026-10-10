"""Render an aggregate-only view of the locked professional team-history backtest."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "data" / "public_team_probe.json"
OUTPUT = ROOT / "docs" / "figures" / "team_history_probe.png"


def main() -> None:
    report = json.loads(SOURCE.read_text())
    bg, panel, ink, muted = "#0b0c13", "#171c29", "#f7f0ee", "#b8aebb"
    plt.rcParams.update({"figure.facecolor": bg, "axes.facecolor": panel,
                         "axes.edgecolor": "#64485a", "axes.labelcolor": ink,
                         "xtick.color": muted, "ytick.color": muted, "text.color": ink,
                         "font.size": 11, "savefig.facecolor": bg})
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), layout="constrained")
    fig.suptitle("FAKER  /  DOES TEAM HISTORY HELP?", fontsize=23, fontweight="black", x=.06, ha="left")
    names = ["Persistence\n10 min", "10-min context\nno history", "Context + prior\nco-play"]
    colors = ["#8f92a5", "#71dae2", "#ff789d"]
    for ax, role, title in zip(axes, ("faker_mid", "bot"), ("FAKER MID · PRIMARY", "BOT · SECONDARY")):
        endpoint = report["endpoints"][role]
        values = [endpoint["test"][key]["mae_gold"] for key in
                  ("persistence", "ten_minute_context", "context_plus_history")]
        bars = ax.bar(np.arange(3), values, color=colors, width=.62, zorder=3)
        ax.set_xticks(np.arange(3), names)
        ax.set_ylim(0, max(values) * 1.32)
        ax.set_ylabel("Held-out mean absolute error · gold")
        ax.set_title(title, loc="left", pad=18, fontsize=14, fontweight="bold")
        ax.grid(axis="y", color="#615262", alpha=.55, zorder=0)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, value + max(values)*.025,
                    f"{value:,.2f}", ha="center", color=ink, fontsize=13, fontweight="bold")
        delta = endpoint["paired_test_delta_history_minus_context_mae_gold"]
        low, high = endpoint["paired_test_delta_ci95_day_bootstrap_gold"]
        ax.text(.02, .94, f"History − context: {delta:+.2f} gold\nDay bootstrap 95% CI [{low:+.2f}, {high:+.2f}]",
                transform=ax.transAxes, va="top", color="#ffd393", fontsize=11)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
