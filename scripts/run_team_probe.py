#!/usr/bin/env python3
"""Pilot five pro games, then run the locked chronological team-history ablation."""
import argparse

from shadowfaker.team_probe import pilot, run
from render_team_probe import main as render


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    print(f"Five-game team-history pilot: {pilot()}", flush=True)
    if args.pilot_only:
        return
    report = run()
    render()
    primary = report["endpoints"]["faker_mid"]
    print(f"Chronological test: {report['split']['games']['test']} games; "
          f"Faker mid MAE {primary['test']['ten_minute_context']['mae_gold']} "
          f"→ {primary['test']['context_plus_history']['mae_gold']} gold with prior co-play; "
          f"paired delta {primary['paired_test_delta_history_minus_context_mae_gold']:+.2f} gold.", flush=True)


if __name__ == "__main__":
    main()
