import copy

import numpy as np

from shadowfaker.action_sanitation import (EXTRAS, audit_match, extra_features)
from shadowfaker.faker_actions import extract as labels


def fixture():
    players = [{"participantId": i, "puuid": "faker" if i == 1 else f"other-{i}",
                "teamId": 100 if i <= 5 else 200} for i in range(1, 11)]
    match = {"metadata": {"matchId": "KR_test"},
             "info": {"queueId": 420, "gameDuration": 360, "participants": players}}
    def frame(t, gold):
        return {"timestamp": t, "participantFrames": {
            "1": {"position": {"x": 1000, "y": 2000}, "currentGold": gold,
                  "totalGold": gold + 500, "xp": gold, "minionsKilled": gold // 10,
                  "championStats": {"health": 500, "healthMax": 1000}}}, "events": []}
    timeline = {"metadata": {"matchId": "KR_test"},
                "info": {"frames": [frame(0, 500), frame(60_000, 700),
                                    frame(360_000, 2000)]}}
    return match, timeline


def test_identity_queue_clock_and_uncertain_event_are_quarantined():
    match, timeline = fixture()
    assert audit_match(match, timeline, "KR_test", "faker")["eligible"]
    wrong = copy.deepcopy(match)
    wrong["info"]["queueId"] = 430
    assert "not_complete_ranked_solo" in audit_match(wrong, timeline, "KR_test", "faker")["reasons"]
    missing = copy.deepcopy(timeline)
    missing["info"]["frames"][1]["events"] = [{"type": "ITEM_PURCHASED", "participantId": 1}]
    assert "targetable_event_clock_invalid" in audit_match(match, missing, "KR_test", "faker")["reasons"]
    unordered = copy.deepcopy(timeline)
    unordered["info"]["frames"][1]["timestamp"] = -1
    assert "frame_clock_invalid" in audit_match(match, unordered, "KR_test", "faker")["reasons"]


def test_system_actor_and_identical_purchase_are_not_fake_labels():
    match, timeline = fixture()
    event = {"type": "ITEM_PURCHASED", "participantId": 0, "timestamp": 5000}
    timeline["info"]["frames"][0]["events"] = [event, copy.deepcopy(event)]
    audit = audit_match(match, timeline, "KR_test", "faker")
    assert audit["eligible"]
    assert audit["counts"]["system_actor_zero"] == 2
    assert audit["counts"]["identical_event_records"] == 1
    assert not labels(timeline, 1, np.asarray([0]))["y"].any()


def test_added_state_uses_last_frame_and_previous_frame_only():
    _, timeline = fixture()
    frames = timeline["info"]["frames"]
    index = np.asarray([0, 0, 1, 1])
    before = extra_features(frames, index, 1, 100)
    assert before.shape == (4, len(EXTRAS))
    assert np.allclose(before[0], before[1])
    assert np.allclose(before[2], before[3])
    assert before[0, EXTRAS.index("own_current_gold")] == .1
    assert before[2, EXTRAS.index("own_gold_delta_frame")] > 0
    mutated = copy.deepcopy(frames)
    mutated[2]["participantFrames"]["1"]["currentGold"] = 9999
    after = extra_features(mutated, index, 1, 100)
    assert np.array_equal(before, after)
