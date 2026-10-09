#!/usr/bin/env python3
"""Publish only aggregate 64x64 metrics and densities, never source matches."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
private=ROOT/"artifacts"/"grid64"
public=ROOT/"docs"/"data"/"public_grid64.json"

def main():
    test=json.loads((private/"evaluation_test.json").read_text())
    val=json.loads((private/"evaluation_val.json").read_text())
    allowed=("grid","matches","samples","model_top1","model_top5","model_top25","model_top100",
             "mean_distance_cells","previous_mean_distance_cells","within_radius_cells","set90","raw_set90",
             "baseline","gain_vs_best_pp","gain_bootstrap95_pp","pooled16_top1")
    report={"schema_version":2,"domain":"historical same-PUUID ranked solo, 46 test matches",
            "test_previously_inspected":True,"not_prospective_confirmation":True,
            "source_matches":465,"calibration_split":"46 separate development validation matches",
            "validation":{key:val[key] for key in allowed},
            "test":{key:test[key] for key in allowed},
            "observed_density":test["observed_density"],
            "predicted_density":test["predicted_density"],"samples":test["samples"],
            "phases":test["phase_densities"]}
    public.parent.mkdir(parents=True,exist_ok=True)
    public.write_text(json.dumps(report,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print({"samples":report["samples"],"exact64":report["test"]["model_top1"],
           "set90_coverage":report["test"]["set90"]["empirical_coverage"],
           "set90_area":report["test"]["set90"]["mean_map_area_fraction"]})

if __name__=="__main__": main()
