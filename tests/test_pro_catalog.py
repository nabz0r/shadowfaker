import sqlite3

from shadowfaker.pro_catalog import import_csv


def test_refreshed_year_replaces_old_snapshot(tmp_path):
    first = tmp_path / "old_2024.csv"
    second = tmp_path / "new_2024.csv"
    header = "gameid,playername,teamname,position,date,champion,result\n"
    first.write_text(header + "g1,Faker,T1,mid,2024-01-01,Azir,1\n")
    second.write_text(header + "g1,Faker,T1,mid,2024-01-01,Orianna,1\n")
    database = tmp_path / "catalog.sqlite"

    assert import_csv([first], database)["unique_games"] == 1
    assert import_csv([second], database)["unique_games"] == 1
    assert import_csv([second], database)["unique_games"] == 1
    with sqlite3.connect(database) as cx:
        assert cx.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 1
        assert cx.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 1
        assert cx.execute("SELECT champion FROM games").fetchone()[0] == "Orianna"
