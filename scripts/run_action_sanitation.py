#!/usr/bin/env python3
"""Pilot five cached games, then audit and build all Faker action windows."""
import argparse
import json

from shadowfaker.action_sanitation import DATA, build
from shadowfaker.config import CONFIG


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pilot-only", action="store_true")
    args = p.parse_args()
    pilot = build(pilot=True, out=CONFIG.processed / "faker_actions_sanitized_10s_pilot")
    if pilot["counts"].get("matches") != 5:
        raise RuntimeError(f"Five-game pilot quarantined: {pilot['quarantine_reasons']}")
    print(json.dumps({"pilot": pilot["counts"], "anomalies": pilot["anomalies"]}, indent=2))
    if not args.pilot_only:
        full = build(out=DATA)
        print(json.dumps({"full": full["counts"], "anomalies": full["anomalies"],
                          "quarantine_reasons": full["quarantine_reasons"]}, indent=2))


if __name__ == "__main__":
    main()
