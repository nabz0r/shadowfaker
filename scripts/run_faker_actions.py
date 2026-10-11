#!/usr/bin/env python3
"""Build five-game pilot, then cached Faker-specific ten-second labels."""
import argparse
import json

from shadowfaker.config import CONFIG
from shadowfaker.faker_actions import build, DATA


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pilot-only", action="store_true")
    args = p.parse_args()
    pilot = build(pilot=True, out=CONFIG.processed / "faker_actions_10s_pilot")
    if pilot["errors"] or pilot["counts"].get("matches") != 5:
        raise RuntimeError(f"Five-game pilot failed: {pilot['errors']}")
    print(json.dumps({"pilot": pilot["counts"]}, indent=2))
    if not args.pilot_only:
        full = build(out=DATA)
        if full["errors"]:
            raise RuntimeError(f"Full corpus label errors: {full['errors']}")
        print(json.dumps({"full": full["counts"],
                          "source_event_counts": full["source_event_counts"]}, indent=2))


if __name__ == "__main__":
    main()
