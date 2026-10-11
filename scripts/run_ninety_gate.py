#!/usr/bin/env python3
"""Five-game pilot, then the exact-cell 90% confidence/coverage audit."""
import argparse
import json

from shadowfaker.ninety_gate import run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    print("Five-game pilot:", json.dumps(run(pilot=True)), flush=True)
    if not args.pilot_only:
        report = run()
        print("Full validation:", json.dumps({
            "matches": report["validation_matches"],
            "transitions": report["validation_transitions"],
            "exact_accuracy": report["all_transitions_accuracy"],
            "gate": report["selective_gate"]["status"]}), flush=True)


if __name__ == "__main__":
    main()
