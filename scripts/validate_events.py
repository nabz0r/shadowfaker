#!/usr/bin/env python3
"""Run the five-game gate, then validate all cached ranked events."""
import argparse
from shadowfaker.event_validation import audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    pilot = audit(limit=5, output=None)
    if pilot["failed_matches"] or pilot["issues"] or pilot["indexed_events"] != pilot["exact_index_rows"]:
        raise SystemExit(f"Five-game event validation failed: {pilot['issues']}")
    print(f"Pilot: {pilot['audited_matches']} games, {pilot['exact_index_rows']} exact indexed events")
    if args.pilot_only:
        return
    full = audit()
    if full["failed_matches"] or full["issues"] or full["indexed_events"] != full["exact_index_rows"]:
        raise SystemExit(f"Full event validation failed: {full['issues']}; failed games={full['failed_matches']}")
    print(f"Full: {full['audited_matches']} games, {full['exact_index_rows']}/{full['indexed_events']} exact indexed events; "
          f"{sum(full['excluded_types'].values())} raw events intentionally excluded")


if __name__ == "__main__":
    main()
