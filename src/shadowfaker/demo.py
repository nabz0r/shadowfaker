import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import torch

from .config import CONFIG
from .evaluate import load_model
from .util import read_json


def demo(processed: Path = CONFIG.processed, models: Path = CONFIG.models,
         artifacts: Path = CONFIG.artifacts, match_id: str | None = None, max_frames: int = 30) -> Path:
    meta = read_json(processed / "meta.json")
    if not meta:
        raise FileNotFoundError("Process matches first")
    match_id = match_id or meta["splits"]["test"][0]
    if match_id not in meta["splits"]["test"]:
        raise ValueError("Demo match must belong to the held-out test split")
    model = load_model(meta, models / "best.pt")
    with np.load(processed / "matches" / f"{match_id}.npz") as z:
        x = torch.from_numpy(z["x_oracle" if model.view == "oracle" else "x"].copy())
        champ = torch.from_numpy(z["champion"].copy())
        actual = z["region"].copy()
        minutes = z["minute"].copy()
        won = bool(z["win"][0])
    with torch.no_grad():
        predictions = [model(x[i:i + 128], champ[i:i + 128]) for i in range(0, len(x), 128)]
        probs = torch.cat([out[0].softmax(-1) for out in predictions]).numpy()
        value = torch.cat([out[3].sigmoid() for out in predictions]).numpy()
    frames = min(max_frames, len(actual))
    fig, (ax, value_ax) = plt.subplots(1, 2, figsize=(11.5, 5.8), gridspec_kw={"width_ratios": [1.2, 1]})
    heat = ax.imshow(probs[0].reshape(16, 16), origin="lower", extent=(0, 16, 0, 16), vmin=0, vmax=max(.04, float(probs.max())), cmap="viridis")
    dot_actual, = ax.plot([], [], "ro", markersize=10, label="Actual next region")
    dot_pred, = ax.plot([], [], "wx", markersize=10, markeredgewidth=2, label="Predicted top-1")
    ax.set(xlim=(0, 16), ylim=(0, 16), xlabel="Map grid X", ylabel="Map grid Y")
    ax.legend(loc="upper left")
    fig.colorbar(heat, ax=ax, label="Predicted probability")
    value_ax.plot(minutes, value, color="tab:blue", lw=2, label="Estimated eventual win P")
    value_ax.axhline(float(won), color="tab:green", linestyle="--", alpha=.6, label=f"Final outcome: {'win' if won else 'loss'}")
    marker, = value_ax.plot([], [], "o", color="tab:red", markersize=9)
    value_ax.set(xlim=(0, max(1, float(minutes[-1]))), ylim=(-.03, 1.03), xlabel="Game minute", ylabel="P(eventual win)",
                 title="Estimated eventual win probability\n(state association, not action value)")
    value_ax.legend(loc="lower right", fontsize=8)

    def update(i):
        heat.set_data(probs[i].reshape(16, 16))
        r = int(actual[i]); p = int(probs[i].argmax())
        dot_actual.set_data([r % 16 + .5], [r // 16 + .5])
        dot_pred.set_data([p % 16 + .5], [p // 16 + .5])
        ax.set_title(f"Held-out match {match_id}\nMinute {minutes[i]:.0f}: next region")
        marker.set_data([minutes[i]], [value[i]])
        return heat, dot_actual, dot_pred, marker

    animation = FuncAnimation(fig, update, frames=frames, interval=500, blit=False)
    artifacts.mkdir(parents=True, exist_ok=True)
    output = artifacts / "predicted_vs_actual.gif"
    animation.save(output, writer=PillowWriter(fps=2))
    plt.close(fig)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--match-id")
    parser.add_argument("--max-frames", type=int, default=30)
    args = parser.parse_args()
    print(demo(match_id=args.match_id, max_frames=args.max_frames))


if __name__ == "__main__":
    main()
