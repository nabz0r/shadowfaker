import argparse
import hashlib
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import torch
from PIL import Image, ImageDraw

from .config import CONFIG
from .evaluate import load_model
from .util import read_json
from .util import atomic_json


def export_trace(processed: Path = CONFIG.processed, models: Path = CONFIG.models,
                 artifacts: Path = CONFIG.artifacts, match_id: str | None = None,
                 max_frames: int = 30) -> Path:
    """Export one local test game's observed minute states and model forecasts.

    The output is ignored by Git and served only on localhost. It is a replay
    of one-minute timeline frames, never a claim of second-level data or POV.
    """
    meta = read_json(processed / "meta.json")
    if not meta:
        raise FileNotFoundError("Process matches first")
    mid = match_id or meta["splits"]["test"][0]
    if mid not in meta["splits"]["test"]:
        raise ValueError("Trace match must belong to the held-out test split")
    checkpoint = models / "best.pt"
    checkpoint_hash = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    output = artifacts / "replay_trace.json"
    existing = read_json(output)
    if (existing and existing.get("match_id") == mid and existing.get("checkpoint_sha256") == checkpoint_hash
            and existing.get("max_frames") == max_frames
            and all((artifacts / "replay_frames" / row["image"]).is_file() for row in existing["rows"])):
        return output
    model = load_model(meta, checkpoint)
    with np.load(processed / "matches" / f"{mid}.npz") as arrays:
        x = torch.from_numpy(arrays["x_oracle" if model.view == "oracle" else "x"].copy())
        champion = torch.from_numpy(arrays["champion"].copy())
        actual = arrays["region"].copy()
        minute = arrays["minute"].copy()
    count = min(max_frames, len(actual))
    with torch.no_grad():
        outputs = [model(x[i:i + 128], champion[i:i + 128]) for i in range(0, count, 128)]
        probabilities = torch.cat([o[0].softmax(-1) for o in outputs]).numpy()
        values = torch.cat([o[3].sigmoid() for o in outputs]).numpy()
    vmax = max(.04, float(probabilities.max()))
    folder = artifacts / "replay_frames"
    folder.mkdir(parents=True, exist_ok=True)
    palette = plt.get_cmap("magma")
    rows = []
    for i in range(count):
        p = probabilities[i]
        image = Image.new("RGB", (512, 512), "#091526")
        draw = ImageDraw.Draw(image)
        for region in range(256):
            col, row = region % 16, region // 16
            strength = min(1.0, float(p[region]) / vmax) ** .55
            colour = tuple(int(v * 255) for v in palette(strength)[:3])
            xy = (col * 32, (15 - row) * 32, (col + 1) * 32 - 1, (16 - row) * 32 - 1)
            draw.rectangle(xy, fill=colour, outline="#23334a", width=1)
        current = x[i, -1].numpy()
        for ally in range(5):
            offset = 17 + ally * 9
            if current[offset + 2] <= .5:
                continue
            cx, cy = float(current[offset]) * 512, (1 - float(current[offset + 1])) * 512
            radius = 7 if ally == 0 else 4
            colour = "#5ff0df" if ally == 0 else "#63a5d9"
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=colour, outline="white", width=1)
        actual_region = int(actual[i])
        guess_region = int(p.argmax())
        for region, colour in ((actual_region, "#ff95bd"), (guess_region, "#ffffff")):
            cx, cy = (region % 16 + .5) * 32, (15 - region // 16 + .5) * 32
            radius = 12 if region == actual_region else 8
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=colour, width=3)
        filename = f"{i:02d}.png"
        image.save(folder / filename)
        entropy = -float(np.sum(p * np.log(np.maximum(p, 1e-12))) / np.log(256))
        rows.append({"minute": float(minute[i]), "actual_region": actual_region,
                     "predicted_region": guess_region, "actual_probability": float(p[actual_region]),
                     "predicted_probability": float(p[guess_region]), "forecast_entropy_0_1": entropy,
                     "gold_diff": round(float(current[7] * 30000)), "xp_diff": round(float(current[109] * 50000)),
                     "level": round(float(current[2] * 18)), "cs": round(float(current[4] * 400)),
                     "estimated_final_win_probability": float(values[i]), "image": filename})
    artifacts.mkdir(parents=True, exist_ok=True)
    atomic_json(output, {"schema_version": 1, "match_id": mid, "max_frames": max_frames,
                         "checkpoint_sha256": checkpoint_hash, "source_step_seconds": 60,
                         "view": model.view, "rows": rows})
    return output


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
