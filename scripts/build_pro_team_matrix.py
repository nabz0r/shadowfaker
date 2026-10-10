#!/usr/bin/env python3
"""Five-game pilot, then private Faker/team warehouse and public aggregates."""
from shadowfaker.config import CONFIG
from shadowfaker.pro_team_matrix import build, summarize


def main() -> None:
    pilot = build(db_path=CONFIG.root / "data" / "pilot_pro_team_matrix.sqlite", pilot=5)
    if pilot["games"] != 5 or pilot["player_rows"] != 25 or pilot["pair_rows"] != 20:
        raise RuntimeError(f"Professional team pilot failed: {pilot}")
    print(f"Five-game team pilot: {pilot}", flush=True)
    full = build()
    report = summarize()
    print(f"Professional team matrix: {full['games']} games, "
          f"{full['complete_10_15']} complete snapshots, {len(report['years'])} calendar years.", flush=True)


if __name__ == "__main__":
    main()
