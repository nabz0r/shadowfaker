#!/usr/bin/env python3
"""Render smoothed public 512² summaries; never export exact sparse cells."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
import numpy as np

from shadowfaker.atlas512 import ATLAS
from shadowfaker.config import CONFIG
from shadowfaker.util import read_json

OUT = CONFIG.root / "docs" / "figures"
GRID = 512
PHASES = (("early", "0–10 min"), ("middle", "10–20 min"), ("late", "20+ min"))


def density(pairs: list[list[int]], min_count: int = 1) -> np.ndarray:
    result = np.zeros(GRID * GRID, dtype=np.float32)
    for index, count in pairs:
        if count >= min_count: result[index] = count
    return result.reshape(GRID, GRID)


def public_event_density(pairs: list[list[int]]) -> np.ndarray:
    """Hide exact rare-event cells by grouping 32x32 fine cells before plotting."""
    coarse = np.zeros((16, 16), dtype=np.float32)
    for index, count in pairs:
        coarse[index // GRID // 32, index % GRID // 32] += count
    coarse[coarse < 3] = 0
    return np.repeat(np.repeat(coarse / 1024, 32, axis=0), 32, axis=1)


def smooth(value: np.ndarray, sigma: float = 6.0) -> np.ndarray:
    radius = int(3 * sigma)
    offset = np.arange(-radius, radius + 1)
    kernel = np.exp(-.5 * (offset / sigma) ** 2)
    kernel /= kernel.sum()
    padded = np.pad(value, ((0, 0), (radius, radius)))
    horizontal = sum(float(weight) * padded[:, i:i + GRID] for i, weight in enumerate(kernel))
    padded = np.pad(horizontal, ((radius, radius), (0, 0)))
    return sum(float(weight) * padded[i:i + GRID, :] for i, weight in enumerate(kernel))


def positions(summary: dict) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(10, 15), facecolor="#140d18")
    maps = (LinearSegmentedColormap.from_list("observed512", ["#170d1c", "#1c5361", "#4bcabb", "#fff0c4"]),
            LinearSegmentedColormap.from_list("predicted512", ["#170d1c", "#5a1f48", "#ed4f78", "#fff0c4"]))
    for row, (phase, label) in enumerate(PHASES):
        for col, key in enumerate(("positions_real", "positions_model")):
            ax = axes[row, col]
            field = smooth(density(summary["phases"][phase][key]["cells"]))
            ax.imshow(field, origin="lower", cmap=maps[col], norm=PowerNorm(.38, vmin=0, vmax=max(.01, field.max())))
            ax.set(title=f"{label} · {'OBSERVED' if col == 0 else '512 ADAPTER'}")
            ax.tick_params(colors="#beacbd", labelsize=8)
            ax.title.set_color("#fff7f5")
            ax.set_xlabel("512-cell x", color="#bc9caa")
            ax.set_ylabel("512-cell y", color="#bc9caa")
            for spine in ax.spines.values(): spine.set_color("#5c3b52")
    fig.suptitle("SHADOW FAKER / 512×512 DESTINATIONS", color="#fff4f3", fontsize=20, weight="bold", y=.995)
    fig.text(.05, .043, "46 validation games · 1,275 next-minute targets · Gaussian smoothing for display only.",
             color="#dbb9c5", fontsize=9)
    fig.text(.05, .021, "Exact 512 cell: model 0.00% · copy previous position 0.63%.",
             color="#dbb9c5", fontsize=9)
    fig.subplots_adjust(left=.08, right=.97, top=.96, bottom=.095, hspace=.24, wspace=.17)
    fig.savefig(OUT / "atlas512_validation.png", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def events(summary: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.9), facecolor="#140d18")
    layers = (("faker_kill", (1.0, .45, .56)), ("enemy_kill", (.60, .40, 1.0)),
              ("dragon", (1.0, .76, .37)), ("baron", (.55, .86, 1.0)),
              ("grubs", (.62, 1.0, .48)))
    for ax, (phase, label) in zip(axes, PHASES):
        canvas = np.zeros((GRID, GRID, 3), dtype=np.float32) + np.array([.055, .035, .085])
        for key, rgb in layers:
            field = smooth(public_event_density(summary["phases"][phase][key]["cells"]), sigma=8)
            if field.max() <= 0: continue
            strength = (field / field.max()) ** .55
            canvas += strength[..., None] * np.asarray(rgb)[None, None] * .58
        ax.imshow(np.clip(canvas, 0, 1), origin="lower")
        ax.set_title(label, color="#fff7f5", fontsize=15, weight="bold")
        ax.tick_params(colors="#beacbd", labelsize=8)
        ax.set_xlabel("512-cell x", color="#bc9caa")
        for spine in ax.spines.values(): spine.set_color("#5c3b52")
    fig.suptitle("EVENT GEOGRAPHY / 512×512", color="#fff4f3", fontsize=20, weight="bold", y=.98)
    fig.text(.05, .065, "465 ranked games · pink Faker kills · violet enemy kills · gold Dragon · ice Baron · green Grubs.",
             color="#dbb9c5", fontsize=9)
    fig.text(.05, .030, "Events grouped in 16×16 bins (bins <3 hidden), then smoothed · unplaced wards excluded.",
             color="#dbb9c5", fontsize=9)
    fig.subplots_adjust(left=.045, right=.99, top=.88, bottom=.18, wspace=.16)
    fig.savefig(OUT / "atlas512_events.png", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    summary = read_json(ATLAS)
    if not summary or summary.get("grid") != GRID: raise FileNotFoundError("Build the local 512 atlas first")
    OUT.mkdir(parents=True, exist_ok=True)
    positions(summary)
    events(summary)
    print("Rendered two smoothed 512x512 aggregate figures")


if __name__ == "__main__": main()
