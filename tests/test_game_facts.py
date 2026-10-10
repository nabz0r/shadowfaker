"""Post-game cards stay resumable and separate from causal training states."""
import json

import pytest

from shadowfaker.game_facts import build, parse_match


def fixture_match():
    own = {"puuid": "target", "teamId": 100, "championName": "Azir", "win": True,
           "kills": 4, "deaths": 2, "assists": 9, "totalMinionsKilled": 200,
           "neutralMinionsKilled": 7, "totalDamageDealtToChampions": 24500,
           "visionScore": 31, "item0": 3089, "item1": 3020, "item2": 0}
    ally = {"puuid": "ally", "teamId": 100, "championName": "LeeSin"}
    enemy = {"puuid": "enemy", "teamId": 200, "championName": "Ahri"}
    return {"metadata": {"matchId": "KR_42"}, "info": {
        "gameStartTimestamp": 1760000000000, "gameDuration": 1800,
        "gameVersion": "15.20.1", "participants": [own, ally, enemy]}}


def test_postgame_facts_parse_and_resume(tmp_path):
    payload = fixture_match()
    raw = tmp_path / "raw"; raw.mkdir()
    (raw / "KR_42.json").write_text(json.dumps(payload))
    index = tmp_path / "facts.sqlite"
    first = build(["KR_42"], "target", raw, index)
    second = build(["KR_42"], "target", raw, index)
    assert first == {"requested": 1, "indexed": 1, "reused": 0, "total": 1, "errors": {}}
    assert second["reused"] == 1 and second["total"] == 1
    parsed = parse_match(payload, "target")
    assert parsed["side"] == "BLUE" and parsed["won"] == 1
    assert parsed["patch"] == "15.20" and parsed["items"] == [3089, 3020]
    assert parsed["allies"] == ["Azir", "LeeSin"] and parsed["enemies"] == ["Ahri"]
    assert parsed["damage_champions"] == 24500 and parsed["cs"] == 207


def test_postgame_facts_reject_wrong_account():
    with pytest.raises(ValueError, match="Target account absent"):
        parse_match(fixture_match(), "someone-else")
