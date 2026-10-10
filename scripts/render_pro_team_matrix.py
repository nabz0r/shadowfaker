"""Render public, aggregate-only Faker/team evidence from the published JSON."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "data" / "public_team_matrix.json"
OUTPUT = ROOT / "docs" / "figures" / "team_matrix.png"


def main() -> None:
    data = json.loads(SOURCE.read_text())
    bg, panel, ink, muted = "#0b0c13", "#171c29", "#f7f0ee", "#b8aebb"
    colors = {"Doran": "#ffcf8b", "Oner": "#7ce2e9", "Keria": "#ff779f"}
    plt.rcParams.update({"figure.facecolor": bg, "axes.facecolor": panel,
                         "axes.edgecolor": "#64485a", "axes.labelcolor": ink,
                         "xtick.color": muted, "ytick.color": muted, "text.color": ink,
                         "font.size": 11, "savefig.facecolor": bg})
    fig, axes = plt.subplots(1, 3, figsize=(21, 7), layout="constrained")
    fig.suptitle("FAKER  /  THE TEAM REMEMBERS", fontsize=24, fontweight="black", x=.06, ha="left")
    months = data["monthly_prior"]
    x = np.arange(len(months))
    for name, color in colors.items():
        y = [row.get(name, {}).get("prior_games", 0) for row in months]
        axes[0].plot(x, y, lw=3, color=color, label=name)
        axes[0].scatter([x[-1]], [y[-1]], color=color, s=65, zorder=3)
    ticks = np.unique(np.linspace(0, len(x)-1, 6, dtype=int))
    axes[0].set_xticks(ticks, [months[i]["month"] for i in ticks], rotation=30, ha="right")
    axes[0].set_title("Shared games strictly before each month's last match", loc="left", fontsize=14, pad=18)
    axes[0].set_ylabel("Prior professional games with Faker · count")
    axes[0].grid(axis="y", color="#544557", alpha=.55)
    axes[0].legend(frameon=False, ncol=3, loc="upper left")

    roles = ["Top · Doran", "Jungle · Oner", "Mid · Faker", "Bot", "Support · Keria"]
    record = data["by_year"]["2025"]
    gold10 = [record["roles"][r]["gold_diff10"] for r in data["roles"]]
    gold15 = [record["roles"][r]["gold_diff15"] for r in data["roles"]]
    yy = np.arange(5)
    axes[1].axvline(0, color="#c8b9c3", lw=1)
    for i, (start, end) in enumerate(zip(gold10, gold15)):
        axes[1].plot([start, end], [i, i], color="#b77990", lw=5, zorder=1)
    axes[1].scatter(gold10, yy, color="#ffcf8b", s=100, label="10 min", zorder=3)
    axes[1].scatter(gold15, yy, color="#ff698e", s=100, label="15 min", zorder=3)
    axes[1].set_yticks(yy, roles)
    axes[1].invert_yaxis()
    axes[1].set_xlim(-190, 290)
    axes[1].set_title("2025 · scoreboard gap to lane opponent", loc="left", fontsize=14, pad=18)
    axes[1].set_xlabel("Mean gold difference · 187 complete games")
    axes[1].grid(axis="x", color="#544557", alpha=.55)
    axes[1].legend(frameon=False, ncol=2, loc="lower right")
    correlation = np.asarray(record["gold_swing_correlations"], dtype=float)
    cmap = LinearSegmentedColormap.from_list("team", ["#427590", panel, "#e65c7f"])
    heat = axes[2].imshow(correlation, cmap=cmap, vmin=-1, vmax=1)
    labels = ["Top", "Jng", "Faker", "Bot", "Sup"]
    axes[2].set_xticks(range(5), labels)
    axes[2].set_yticks(range(5), labels)
    axes[2].set_title("2025 · co-movement of gold-gap changes", loc="left", fontsize=14, pad=18)
    for i in range(5):
        for j in range(5):
            axes[2].text(j, i, f"{correlation[i,j]:+.2f}", ha="center", va="center",
                         color=ink, fontsize=12, fontweight="bold")
    cbar = fig.colorbar(heat, ax=axes[2], shrink=.72, pad=.035)
    cbar.set_label("Pearson r · 10→15 min gold-gap swings")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
