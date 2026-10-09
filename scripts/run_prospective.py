#!/usr/bin/env python3
"""Freeze today's model, collect genuinely later matches, and score once when ready."""
import argparse
import json
import logging

from shadowfaker.prospective import run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", help="ID listing snapshot (default: current UTC date); reuse to resume")
    parser.add_argument("--offline", action="store_true", help="Use local cache only; do not call Riot")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    result = run(snapshot=args.snapshot, offline=args.offline)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
