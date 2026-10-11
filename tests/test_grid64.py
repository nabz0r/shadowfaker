import numpy as np
import torch

from shadowfaker.challenge import SCENARIOS, allocation, simulate
from shadowfaker.events64 import summarize_match
from shadowfaker.finegrid import GRID, _target_labels, cell, coarse_labels, coarse_logits, Grid64Transformer
from shadowfaker.expand import discover
from shadowfaker.geometry64 import local_metric, field64
from shadowfaker.interaction_core import interaction_channels, NAMES
from shadowfaker.state_matrix import _frame_rows
from shadowfaker.text_index import import_note, search
from test_pipeline import synthetic_game
import json


def test_grid64_labels_align_only_with_next_observed_position():
    match = {"info": {"participants": [{"puuid": "target", "participantId": 1, "teamId": 100}]}}
    def frame(time, pos):
        return {"timestamp": time, "participantFrames": {"1": {"position": pos}}}
    timeline = {"info": {"frames": [frame(0, {"x": 1500, "y": 3000}),
                                    frame(60000, {"x": 3000, "y": 4500}),
                                    frame(120000, {})]}}
    labels = _target_labels(match, timeline, "target")
    assert labels["region"].tolist() == [19 * GRID + 12]
    assert labels["previous"].tolist() == [12 * GRID + 6]
    assert labels["minute"].tolist() == [0]
    assert cell(np.array([.2, .3])) == labels["region"][0]
    assert coarse_labels(labels["region"], 16).tolist() == [4 * 16 + 3]


def test_grid64_head_and_probability_pooling():
    model = Grid64Transformer(width=32, layers=1)
    with torch.no_grad():
        logits, xy = model(torch.zeros(2, 8, 134), torch.tensor([1, 2]))
    assert logits.shape == (2, 4096)
    assert xy.shape == (2, 2)
    fine = logits.log_softmax(-1).exp().sum(-1)
    coarse = coarse_logits(logits).log_softmax(-1).exp().sum(-1)
    assert torch.allclose(fine, coarse, atol=1e-5)
    assert sum(p.numel() for p in model.parameters()) < 5_000_000


def test_events_64_have_explicit_location_or_unplaced_count():
    match = {"info": {"participants": [{"puuid": "target", "participantId": 1, "teamId": 100},
                                      {"puuid": "enemy", "participantId": 2, "teamId": 200}]}}
    events = [{"type": "CHAMPION_KILL", "timestamp": 1000, "killerId": 1, "victimId": 2,
               "position": {"x": 3000, "y": 4500}},
              {"type": "ELITE_MONSTER_KILL", "timestamp": 2000, "monsterType": "HORDE",
               "position": {"x": 5000, "y": 10000}},
              {"type": "WARD_PLACED", "timestamp": 3000, "creatorId": 1}]
    result = summarize_match(match, {"info": {"frames": [{"events": events}]}}, "target")
    assert result["totals"]["early"]["faker_kill"] == 1
    assert result["cells"]["early"]["grubs"].sum() == 1
    assert result["totals"]["early"]["ward_placed"] == 1
    assert result["missing"]["early"]["ward_placed"] == 1
    assert result["cells"]["early"]["ward_placed"].sum() == 0


def test_all_queue_pagination_deduplicates_and_challenges_are_synthetic():
    class Fake:
        def ids(self, puuid, start, count, snapshot, queue):
            assert queue is None
            return ["A"] * 99 + ["B"] if start == 0 else ["B", "C"]
    assert discover(Fake(), "p", "s") == ["A", "B", "C"]
    for scenario in SCENARIOS:
        assert sum(allocation(scenario, 0)) == 5
        rows = simulate(scenario)
        assert len(rows) == 8
        assert all(0 <= row["map_coverage"] <= 1 for row in rows)
    assert simulate("five_bot")[0]["map_coverage"] == .25
    assert simulate("five_faker")[0]["map_coverage"] == 1
    rotating=simulate("five_faker",response_delay=1)
    assert rotating[0]["opponent_allocation"]==dict(top=1,mid=1,jungle=1,bot=2)
    assert rotating[1]["opponent_allocation"]==dict(top=0,mid=1,jungle=1,bot=3)
    assert rotating[3]["opponent_allocation"]==dict(top=1,mid=1,jungle=2,bot=1)


def test_interaction_channels_cannot_read_the_next_frame():
    window = np.zeros((3, 134), dtype=np.float32)
    window[:, 17:19] = [.5, .5]
    window[:, 19] = 1
    enemy = 17 + 5 * 9
    window[0, enemy:enemy + 3] = [.9, .9, 1]
    window[1, enemy:enemy + 3] = [.55, .55, 1]
    initial = interaction_channels(window)
    assert initial.shape == (3, len(NAMES))
    assert initial[1, NAMES.index("enemy_moves_toward_prior_faker")] == .2
    changed = window.copy()
    changed[2, enemy:enemy + 3] = [.01, .01, 1]
    np.testing.assert_array_equal(initial[:2], interaction_channels(changed)[:2])


def test_metric_positive_and_state_warehouse_keeps_ten_actors():
    metric = np.asarray(local_metric((.4, .5), (.35, .5), [(.5, .55)]))
    assert np.allclose(metric, metric.T)
    assert np.linalg.eigvalsh(metric).min() > 0
    field = field64((.4, .5), metric.tolist())
    assert field.shape == (64, 64) and 0 < field.max() <= 1
    match, timeline = synthetic_game(2)
    states, actors, events, transitions = _frame_rows(match, timeline, "fixture-player", "KR_2")
    assert len(states) == 14 and len(actors) == 140
    assert len(transitions) == 12  # One next position is missing.
    assert any(row[3] == "faker" for row in actors)
    assert any(row[3] == "enemy" for row in actors)
    assert all(row[3] is not None for row in transitions)


def test_multilingual_case_import_preserves_provenance(tmp_path):
    note = tmp_path / "case.txt"
    note.write_text("한국어 분석 · Faker Nidalee", encoding="utf-8")
    note.with_suffix(".json").write_text(json.dumps({"language": "ko", "source_kind": "annotated_video",
      "provenance": "test source", "status": "unverified"}), encoding="utf-8")
    index = tmp_path / "notes.sqlite"
    imported = import_note(note, index=index)
    assert imported["language"] == "ko"
    rows = search("한국어", "ko", index=index)
    assert len(rows) == 1 and rows[0]["provenance"] == "test source"
