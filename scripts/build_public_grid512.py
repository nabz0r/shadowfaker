#!/usr/bin/env python3
"""Export only aggregate development metrics for the 512² candidate."""
from pathlib import Path

from shadowfaker.config import CONFIG
from shadowfaker.util import atomic_json, read_json

SOURCE = CONFIG.artifacts / "grid512" / "evaluation_val.json"
TARGET = CONFIG.root / "docs" / "data" / "public_grid512.json"


def main() -> None:
    source = read_json(SOURCE)
    if not source or source.get("status") != "development_validation_only" or source.get("grid") != 512:
        raise ValueError("512 development validation report missing")
    allowed = ("grid", "parent_grid", "status", "parent_beam", "matches", "samples", "model_top1",
               "copy_previous_top1", "train_frequent_top1", "chosen_parent64_top1",
               "oracle_parent_subcell_top1", "mean_distance_cells", "within_radius_cells",
               "gain_vs_best_baseline_bootstrap95_pp", "note")
    result = {"schema_version": 1, "test_scored": False,
              "not_prospective_confirmation": True, "source": "46 development validation ranked matches",
              **{key: source[key] for key in allowed},
              "phase_samples": {phase: row["samples"] for phase, row in source["phases"].items()}}
    atomic_json(TARGET, result)
    print({"samples": result["samples"], "model_exact512": result["model_top1"],
           "copy_exact512": result["copy_previous_top1"]})


if __name__ == "__main__": main()
