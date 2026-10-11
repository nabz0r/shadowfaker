#!/usr/bin/env python3
"""Publish only aggregate second-scale observation coverage; five games first."""
import argparse
import json

from shadowfaker.config import CONFIG
from shadowfaker.second_scale import build


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    pilot = build(5, CONFIG.root / "data" / "second_scale_pilot.json")
    if pilot["source_matches"] != 5 or pilot["parse_errors"]:
        raise RuntimeError("Five-game pilot did not pass")
    report = pilot if args.pilot_only else build()
    print(json.dumps({"matches": report["source_matches"],
                      "events": report["totals"]["timestamped_events"],
                      "faker_position_gap_seconds": report["faker_position_gap_seconds"],
                      "horizons_seconds": report["horizons_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
