#!/usr/bin/env python3
"""Export the public 147-channel ablation matrix from the code, not match data."""
import json
from pathlib import Path

from shadowfaker.features import FEATURE_NAMES
from shadowfaker.hierarchical import VARIANTS, feature_mask
from shadowfaker.interaction_core import NAMES

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "data" / "feature_visibility.json"


def main() -> None:
    names = FEATURE_NAMES + NAMES
    masks = {variant: feature_mask(names, variant).astype(bool).tolist() for variant in VARIANTS}
    payload = {
        "schema_version": 1,
        "source_view": "x: heuristic last-seen enemy position, not x_oracle or actual player POV",
        "note": "Full retains all x channels, including true timeline resource fields. Visible proxy removes selected global resource channels but is not verified fog of war.",
        "counts": {name: sum(mask) for name, mask in masks.items()},
        "features": [{"name": name, "included": {variant: masks[variant][i] for variant in VARIANTS}}
                     for i, name in enumerate(names)]}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"Exported {len(names)} feature provenance rows to {OUTPUT}")


if __name__ == "__main__":
    main()
