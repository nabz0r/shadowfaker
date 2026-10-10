"""Causal chronology and missing-field behavior in the separate pro warehouse."""
import csv
from datetime import datetime, timedelta
import sqlite3

from shadowfaker import pro_team_matrix as team


def test_prior_exposure_excludes_current_and_future():
    now = datetime(2025, 5, 1, 12)
    history = [now - timedelta(days=90), now, now + timedelta(days=1)]
    n, effective, days = team.prior_exposure(history, now)
    assert n == 1
    assert effective == 0.5
    assert days == 90


def test_build_pilot_uses_previous_games_only_and_skips_missing_snapshots(tmp_path, monkeypatch):
    catalog = tmp_path / "catalog.sqlite"
    with sqlite3.connect(catalog) as db:
        db.execute("CREATE TABLE games(game_id TEXT, game_date TEXT)")
        db.executemany("INSERT INTO games VALUES (?,?)", [
            ("g1", "2025-01-01 12:00:00"), ("g2", "2025-01-02 12:00:00")])
    monkeypatch.setattr(team, "CATALOG", catalog)
    monkeypatch.setattr(team, "ROOT", tmp_path)
    source = tmp_path / "data" / "raw" / "pro" / "oracle_mirror_2025.csv"
    source.parent.mkdir(parents=True)
    fields = ["gameid", "teamname", "position", "playername", "date", "year", "league",
              "patch", "result", "champion", *team.SNAPSHOT,
              "kills", "deaths", "assists", "damagetochampions", "visionscore"]
    roster = {"top": "Doran", "jng": "Oner", "mid": "Faker", "bot": "Gumayusi", "sup": "Keria"}
    with source.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for game_id, date in [("g1", "2025-01-01 12:00:00"), ("g2", "2025-01-02 12:00:00")]:
            for role, name in roster.items():
                row = {field: 1 for field in fields}
                row.update(gameid=game_id, teamname="T1", position=role, playername=name,
                           date=date, year="2025", league="LCK", patch="25.1", champion="Azir")
                if game_id == "g2" and role == "bot":
                    row["golddiffat15"] = ""
                    row["playername"] = ""
                writer.writerow(row)
    db_path = tmp_path / "matrix.sqlite"
    outcome = team.build(db_path=db_path, pilot=2)
    assert (outcome["games"], outcome["player_rows"], outcome["pair_rows"],
            outcome["complete_10_15"]) == (2, 10, 8, 1)
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT prior_games FROM pair_history WHERE game_id='g1' AND teammate='Doran'").fetchone()[0] == 0
        assert db.execute("SELECT prior_games FROM pair_history WHERE game_id='g2' AND teammate='Doran'").fetchone()[0] == 1
        assert db.execute("SELECT gold_diff15 FROM players WHERE game_id='g2' AND role='bot'").fetchone()[0] is None
        assert db.execute("SELECT player FROM players WHERE game_id='g2' AND role='bot'").fetchone()[0] == "UNKNOWN"
    assert team.build(db_path=db_path, pilot=2)["cached"]
