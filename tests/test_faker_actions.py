import numpy as np

from shadowfaker.faker_actions import CLASSES, attributed, extract
from shadowfaker.faker_action_model import average_precision


def test_only_explicit_faker_events_are_labels():
    assert attributed({"type": "WARD_PLACED", "creatorId": 2}, 1) == ()
    assert attributed({"type": "ITEM_DESTROYED", "participantId": 1}, 1) == ()
    assert attributed({"type": "LEVEL_UP", "participantId": 1}, 1) == ()
    assert attributed({"type": "CHAMPION_KILL", "killerId": 2,
                       "victimId": 3, "assistingParticipantIds": [1]}, 1) == ("assist",)
    assert attributed({"type": "CHAMPION_KILL", "killerId": 2,
                       "victimId": 1, "assistingParticipantIds": []}, 1) == ("death",)


def test_ten_second_labels_exclude_present_and_future_outside_window():
    events = [
        {"type": "ITEM_PURCHASED", "participantId": 1, "timestamp": 10_000},
        {"type": "SKILL_LEVEL_UP", "participantId": 1, "timestamp": 10_001},
        {"type": "WARD_PLACED", "creatorId": 1, "timestamp": 20_000},
        {"type": "CHAMPION_KILL", "killerId": 2, "victimId": 3,
         "assistingParticipantIds": [1], "timestamp": 20_001},
        {"type": "CHAMPION_KILL", "killerId": 1, "victimId": 2,
         "timestamp": 40_000},
    ]
    timeline = {"info": {"frames": [{"timestamp": 0, "events": events}]}}
    sample = extract(timeline, 1, np.asarray([10_000, 20_000, 30_000]))
    assert sample["y"].shape == (3, len(CLASSES))
    assert sample["y"][0, CLASSES.index("purchase")] == 0
    assert sample["y"][0, CLASSES.index("skill_point")] == 1
    assert sample["first_delay_ms"][0, CLASSES.index("skill_point")] == 1
    assert sample["y"][0, CLASSES.index("ward_placed")] == 1
    assert sample["y"][1, CLASSES.index("ward_placed")] == 0
    assert sample["y"][1, CLASSES.index("assist")] == 1
    assert sample["y"][2, CLASSES.index("kill")] == 1


def test_average_precision_ties_are_not_order_sensitive():
    label = np.asarray([1, 0, 1, 0], dtype=np.uint8)
    constant = np.full(4, .5)
    assert average_precision(label, constant) == .5
    assert average_precision(label[::-1], constant) == .5
    assert average_precision(np.zeros(4), constant) is None
