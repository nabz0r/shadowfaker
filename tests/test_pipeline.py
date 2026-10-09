import json
from pathlib import Path

import numpy as np
import pytest
import torch

from shadowfaker.features import extract_match, parse
from shadowfaker.fetch import fetch_ids
from shadowfaker.riot import RiotClient, RiotError
from shadowfaker.util import atomic_json
from shadowfaker.train import loss_parts, train
from shadowfaker.evaluate import evaluate
from shadowfaker.demo import demo, export_trace
from shadowfaker.analyze import analyze
from shadowfaker.calibrate import calibrate
from shadowfaker.prospective import freeze, prepare, score
from shadowfaker.macro_actions import build as build_macro_actions, extract_tags
from shadowfaker.formations import build as build_formations, extract as extract_formation


def synthetic_game(game_number: int, frames: int = 14):
    puuid = "fixture-player"
    participants = [{"puuid": puuid if i == 1 else f"player-{i}", "participantId": i,
                     "teamId": 100 if i <= 5 else 200, "championId": 238 if i == 1 else i,
                     "teamPosition": ("TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY")[(i - 1) % 5],
                     "win": game_number % 2 == 0}
                    for i in range(1, 11)]
    match = {"info": {"queueId": 420, "gameDuration": frames * 60, "participants": participants,
                      "gameStartTimestamp": 1790000000000 + game_number * 3600000}}
    timeline_frames = []
    for t in range(frames):
        pf = {}
        for i in range(1, 11):
            # Different games have different paths; test has a learnable but nontrivial path.
            x = (1300 + i * 80 + t * (330 + game_number * 3)) if i <= 5 else (11000 + i * 60 + t * 100)
            y = (1200 + i * 70 + t * (260 + game_number * 5)) if i <= 5 else (11000 + i * 50 + t * 100)
            p = {"participantId": i, "totalGold": 500 + 220 * t + i * 10,
                 "level": 1 + t // 2, "xp": t * 470, "minionsKilled": t * 6,
                 "jungleMinionsKilled": t * 2 if i == 1 else 0}
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
    assert a["x"].shape[1:] == (8, 134)
    assert a["x_oracle"].shape == a["x"].shape
    assert a["x"][0, -1, 62] == 0  # distant enemy hidden in minimap proxy
    assert a["x_oracle"][0, -1, 62] > 0
    assert a["x"][0, -1, 4] == pytest.approx(0.0)
    assert a["x"][1, -1, 4] == pytest.approx(8 / 400)
    tags = extract_tags(match, timeline, "fixture-player", a)
    assert tags["tags"].shape == (12, 8)
    assert tags["valid"].shape == tags["tags"].shape
    assert (~tags["valid"].any(axis=1)).any()  # Faker's current position is absent in one frame.
    formation = extract_formation(match, timeline, "fixture-player")
    assert formation["by_phase"]["early_3_10"]["valid"] == 6
    assert formation["by_phase"]["early_3_10"]["all_5"] == 6


def test_coarse_training_loss_pools_correct_cells():
    region = torch.zeros(1, 256, requires_grad=True)
    outputs = (region, torch.zeros(1, 2), torch.zeros(1, 5), torch.zeros(1))
    # Fine cell 35 is row 2, col 3; its 8x8 parent is row 1, col 1 (index 9).
    targets = (None, None, torch.tensor([35]), torch.tensor([0]),
               torch.tensor([0]), torch.tensor([0.0]))
    weights = torch.ones(256)
    ordinary = loss_parts(outputs, targets, weights, coarse_loss_weight=0)[0]
    macro = loss_parts(outputs, targets, weights, coarse_loss_weight=1)[0]
    assert (macro - ordinary).item() == pytest.approx(np.log(64), rel=1e-5)
    macro.backward()
    assert region.grad is not None and torch.isfinite(region.grad).all()


def test_deduplicated_pagination():
    class Client:
        def ids(self, puuid, start, count, snapshot=None):
            if snapshot is not None:
                assert snapshot == "fresh_20261009"
            return [f"KR_{i}" for i in range(100)] if start == 0 else ["KR_99", "KR_100"]
    ids = fetch_ids(Client(), "x", 110)
    assert len(ids) == 101 and len(set(ids)) == 101
    assert fetch_ids(Client(), "x", 110, "fresh_20261009") == ids


def test_429_and_expired_key(tmp_path, monkeypatch):
    client = RiotClient("fixture-key", tmp_path)
    with pytest.raises(ValueError, match="snapshot"):
        client.ids("fixture-puuid", 0, snapshot="../escape")
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
    assert len(meta["patches"]) == 5
    assert set(meta["faker_wins"].values()) == {True, False}
    # Parsing again leaves checkpointed match arrays unchanged.
    before = (processed / "matches" / "KR_0.npz").stat().st_mtime_ns
    parse(raw, processed)
    assert (processed / "matches" / "KR_0.npz").stat().st_mtime_ns == before
    tagged = build_macro_actions(raw, processed, limit=5)
    assert tagged["matches"] == 5 and not tagged["errors"]
    tags_path = processed / "macro_actions" / "KR_0.npz"
    tags_before = tags_path.stat().st_mtime_ns
    build_macro_actions(raw, processed, limit=5)
    assert tags_path.stat().st_mtime_ns == tags_before
    formations = build_formations(raw, processed, limit=5)
    assert formations["matches"] == 5 and not formations["errors"]
    formation_path = processed / "formations" / "matches" / "KR_0.json"
    formation_before = formation_path.stat().st_mtime_ns
    build_formations(raw, processed, limit=5)
    assert formation_path.stat().st_mtime_ns == formation_before
    trained = train(processed, tmp_path / "models", tmp_path / "runs", epochs=2, batch_size=16)
    assert trained["parameters"] < 5_000_000
    macro_trained = train(processed, tmp_path / "macro_models", tmp_path / "macro_runs",
                          epochs=1, batch_size=16, coarse_loss_weight=.5)
    assert macro_trained["hyperparams"]["coarse_loss_weight"] == .5
    macro_calibration = calibrate(processed, tmp_path / "macro_models" / "best.pt", region_grid=8)
    assert macro_calibration["region_grid"] == 8
    calibration = calibrate(processed, tmp_path / "models" / "best.pt")
    assert 0 <= calibration["accuracy"] <= 1
    metrics = evaluate(processed, tmp_path / "models", tmp_path / "artifacts")
    assert metrics["samples"] == 12
    assert "by_patch" in metrics
    assert "by_phase" in metrics and "value_brier" in metrics
    rotations = analyze(processed, tmp_path / "artifacts")
    assert rotations["matches"] == 5
    output = demo(processed, tmp_path / "models", tmp_path / "artifacts", max_frames=3)
    assert output.stat().st_size > 1000
    trace_path = export_trace(processed, tmp_path / "models", tmp_path / "artifacts", max_frames=3)
    trace = json.loads(trace_path.read_text())
    assert len(trace["rows"]) == 3 and trace["source_step_seconds"] == 60
    trace_before = trace_path.stat().st_mtime_ns
    export_trace(processed, tmp_path / "models", tmp_path / "artifacts", max_frames=3)
    assert trace_path.stat().st_mtime_ns == trace_before
    prospective = tmp_path / "prospective"
    protocol = freeze(processed, tmp_path / "models", raw, prospective, minimum_matches=2)
    assert protocol["source_matches"] == 5
    for i in (5, 6):
        mid = f"KR_{i}"
        match, timeline = synthetic_game(i)
        atomic_json(raw / "matches" / f"{mid}.json", match)
        atomic_json(raw / "timelines" / f"{mid}.json", timeline)
        games[mid] = {"status": "ok"}
        order.insert(0, mid)
        atomic_json(raw / "manifest.json", {"account": {"puuid": "fixture-player"}, "games": games, "order": order})
        prepared = prepare(raw, processed, prospective)
        assert prepared["new_matches"] == i - 4
        if i == 5:
            assert score(processed, tmp_path / "models", tmp_path / "artifacts", prospective)["status"] == "pending"
    result = score(processed, tmp_path / "models", tmp_path / "artifacts", prospective)
    assert result["status"] == "scored_once" and result["new_matches"] == 2
    assert score(processed, tmp_path / "models", tmp_path / "artifacts", prospective) == result
    assert (tmp_path / "artifacts" / "evaluation_prospective.json").exists()
