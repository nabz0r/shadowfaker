#!/usr/bin/env python3
"""Five-game benchmark followed by full train/validation on cached matches."""
import argparse
import json

from shadowfaker.faker_action_model import run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    pilot = run(pilot=True, epochs=4)
    print(json.dumps({"pilot_matches": [pilot["train_matches"], pilot["validation_matches"]],
                      "pilot_nll": pilot["scores"]["model"]["nll"]}, indent=2))
    if not args.pilot_only:
        report = run()
        print(json.dumps({"train_matches": report["train_matches"],
                          "validation_matches": report["validation_matches"],
                          "validation_windows": report["validation_windows"],
                          "scores": report["scores"],
                          "phase_nll_gain_ci95_match_bootstrap":
                          report["phase_nll_gain_ci95_match_bootstrap"]}, indent=2))


if __name__ == "__main__":
    main()
