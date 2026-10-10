"""The adjustable radius must be recomputed from actor positions, not scaled in the UI."""
import sqlite3

from shadowfaker.pressure import summarize


def test_radius_profiles_count_distinct_enemy_entries(tmp_path):
    database = tmp_path / "states.sqlite"
    with sqlite3.connect(database) as db:
        db.executescript("""
            CREATE TABLE matches (match_id TEXT);
            CREATE TABLE states (match_id TEXT, frame_index INTEGER, timestamp_ms INTEGER);
            CREATE TABLE actors (match_id TEXT, frame_index INTEGER, participant_id INTEGER,
                                 side TEXT, x REAL, y REAL, cell64 INTEGER);
            CREATE TABLE events (match_id TEXT, frame_index INTEGER, category TEXT);
        """)
        db.execute("INSERT INTO matches VALUES ('KR_1')")
        db.executemany("INSERT INTO states VALUES ('KR_1',?,?)", [(0, 0), (1, 60000)])
        # Enemy 6 moves from 3,000 to 750 map units from Faker; enemy 7 stays at 2,250.
        db.executemany("INSERT INTO actors VALUES ('KR_1',?,?,?,?,?,?)", [
            (0, 1, "faker", .5, .5, 1), (0, 6, "enemy", .7, .5, 2),
            (0, 7, "enemy", .65, .5, 3), (1, 1, "faker", .5, .5, 1),
            (1, 6, "enemy", .55, .5, 2), (1, 7, "enemy", .65, .5, 3),
        ])
    report = summarize(database=database, output=tmp_path / "pressure.json")
    assert report["schema_version"] == 2
    assert report["states_with_faker_position"] == 2
    assert report["radius_profiles"]["1000"]["phases"]["early"]["near_enemies"] == 1
    assert report["radius_profiles"]["2500"]["phases"]["early"]["near_enemies"] == 3
    assert report["radius_profiles"]["2500"]["phases"]["early"]["enemy_arrivals"] == 1
    assert report["radius_profiles"]["5000"]["phases"]["early"]["enemy_arrivals"] == 0
    assert report["radius_profiles"]["5000"]["phases"]["early"]["near_enemies"] == 4
    assert report["phases"]["early"]["near_enemies"] == 3  # Default profile preserved.
