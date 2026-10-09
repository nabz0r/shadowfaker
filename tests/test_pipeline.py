import json
from pathlib import Path

import numpy as np
import pytest

from shadowfaker.features import extract_match, parse
from shadowfaker.fetch import fetch_ids
from shadowfaker.riot import RiotClient, RiotError
from shadowfaker.util import atomic_json
from shadowfaker.train import train
from shadowfaker.evaluate import evaluate
from shadowfaker.demo import demo


def synthetic_game(game_number: int, frames: int = 14):
    puuid = "fixture-player"
    participants = [{"puuid": puuid if i == 1 else f"player-{i}", "participantId": i,
                     "teamId": 100 if i <= 5 else 200, "championId": 238 if i == 1 else i}
                    for i in range(1, 11)]
    match = {"info": {"queueId": 420, "gameDuration": frames * 60, "participants": participants}}
    timeline_frames = []
    for t in range(frames):
        pf = {}
        for i in range(1, 11):
            # Different games have different paths; test has a learnable but nontrivial path.
            x = 1300 + i * 80 + t * (330 + game_number * 3)
            y = 1200 + i * 70 + t * (260 + game_number * 5)
            p = {"participantId": i, "totalGold": 500 + 220 * t + i * 10,
                 "level": 1 + t // 2, "xp": t * 470, "minionsKilled": t * 6}
            if not (t == 5 and i == 1):
                p["position"] = {"x": x, "y": y}
            pf[str(i)] = p
        events = []
        if t in (2, 7, 11):
            events.append({"type": "ITEM_PURCHASED", "participantId": 1,
                           "itemId": 1001 + (t % 2), "timestamp": t * 60000 - 1000})
        if t in (2, 4, 7, 9):
            events.append({"type": "SKILL_LEVEL_UP", "participantId": 1,
                           "skillSlot": (t % 4) + 1, "timestamp": t * 60000 - 2000})
        if t == 8:
            events.append({"type": "ELITE_MONSTER_KILL", "monsterType": "DRAGON", "timestamp": t * 60000 - 1000})
        timeline_frames.append({"timestamp": t * 60000, "participantFrames": pf, "events": events})
    return match, {"info": {"frames": timeline_frames}}


def test_causal_features_and_missing_position():
    match, timeline = synthetic_game(0)
    a = extract_match(match, timeline, "fixture-player")
    assert len(a["region"]) == 12  # target frame 5 lacks position
    changed = json.loads(json.dumps(timeline))
    changed["info"]["frames"][-1]["events"].append({"type": "CHAMPION_KILL", "killerId": 1, "timestamp": 13 * 60000})
    changed["info"]["frames"][-1]["participantFrames"]["1"]["totalGold"] = 999999
    b = extract_match(match, changed, "fixture-player")
    np.testing.assert_array_equal(a["x"], b["x"])
    assert a["x"].shape[1:] == (8, 87)


def test_deduplicated_pagination():
    class Client:
        def ids(self, puuid, start, count):
            return [f"KR_{i}" for i in range(100)] if start == 0 else ["KR_99", "KR_100"]
    ids = fetch_ids(Client(), "x", 110)
    assert len(ids) == 101 and len(set(ids)) == 101


def test_429_and_expired_key(tmp_path, monkeypatch):
    client = RiotClient("fixture-key", tmp_path)
    client._pace = lambda: None
    sleeps = []
    monkeypatch.setattr("shadowfaker.riot.time.sleep", sleeps.append)
    class Response:
        def __init__(self, code, headers=None):
            self.status_code = code
            self.headers = headers or {}
        def json(self):
            return {"ok": True}
    responses = iter([Response(429, {"Retry-After": "3"}), Response(200)])
    client.session.get = lambda *a, **kw: next(responses)
    assert client.get("/x", tmp_path / "cached.json") == {"ok": True}
    assert sleeps == [3.25]
    client.session.get = lambda *a, **kw: Response(403)
    with pytest.raises(RiotError, match="expired"):
        client.get("/y", tmp_path / "missing.json")


def test_split_by_match_and_resume(tmp_path):
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    games = {}
    order = []
    for i in range(5):
        mid = f"KR_{i}"
        match, timeline = synthetic_game(i)
        atomic_json(raw / "matches" / f"{mid}.json", match)
        atomic_json(raw / "timelines" / f"{mid}.json", timeline)
        games[mid] = {"status": "ok"}
        order.append(mid)
    atomic_json(raw / "manifest.json", {"account": {"puuid": "fixture-player"}, "games": games, "order": order})
    meta = parse(raw, processed)
    assert set(meta["splits"]["train"]).isdisjoint(meta["splits"]["test"])
    assert len(meta["counts"]) == 5
    assert meta["observations"] == 60
    # Parsing again leaves checkpointed match arrays unchanged.
    before = (processed / "matches" / "KR_0.npz").stat().st_mtime_ns
    parse(raw, processed)
    assert (processed / "matches" / "KR_0.npz").stat().st_mtime_ns == before
    trained = train(processed, tmp_path / "models", tmp_path / "runs", epochs=2, batch_size=16)
    assert trained["parameters"] < 5_000_000
    metrics = evaluate(processed, tmp_path / "models", tmp_path / "artifacts")
    assert metrics["samples"] == 12
    output = demo(processed, tmp_path / "models", tmp_path / "artifacts", max_frames=3)
    assert output.stat().st_size > 1000
