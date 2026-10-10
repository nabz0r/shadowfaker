#!/usr/bin/env python3
"""Rebuild the public six-finals UI animation from checked-in screen frames."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "docs" / "figures" / "finals_frames"
OUT = ROOT / "docs" / "figures" / "six_finals.gif"
YEARS = (2013, 2015, 2016, 2023, 2024, 2025)


def main():
    frames = []
    for year in YEARS:
        path = FRAMES / f"{year}.png"
        with Image.open(path) as original:
            image = original.convert("RGB")
            # Keep the source screenshot's proportions and focus on title + games.
            image = image.crop((0, 0, original.width, min(980, original.height)))
            image = image.resize((900, round(image.height * 900 / image.width)), Image.Resampling.LANCZOS)
            frames.append(image.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=[1100, 1100, 1100, 1100, 1100, 1800],
                   loop=0, optimize=True, disposal=2)
    print(f"{len(frames)} frames -> {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
