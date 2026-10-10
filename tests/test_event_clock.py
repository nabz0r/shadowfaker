import numpy as np

from shadowfaker.event_clock import CLASSES, FEATURES, extract


def test_ten_second_window_uses_only_current_frame_and_past_events():
    match = {"info": {"participants": [
        {"puuid": "faker", "participantId": 1, "teamId": 100, "teamPosition": "MIDDLE"},
        {"puuid": "opponent", "participantId": 2, "teamId": 200, "teamPosition": "MIDDLE"}]}}
    def frame(time, own_x, events=()):
        return {"timestamp": time, "participantFrames": {
            "1": {"position": {"x": own_x, "y": 7500}, "totalGold": 1000, "xp": 500, "level": 2},
            "2": {"position": {"x": 8000, "y": 7500}, "totalGold": 1000, "xp": 500, "level": 2}},
            "events": list(events)}
    kill = {"type": "CHAMPION_KILL", "timestamp": 65_000, "killerId": 1,
            "victimId": 2, "position": {"x": 9000, "y": 7000}}
    tl = {"info": {"frames": [frame(0, 1000), frame(60_000, 2000, [kill]),
                              frame(120_000, 13000)]}}
    samples = extract(match, tl, "faker")
    at_60 = int(np.where(samples["t_ms"] == 60_000)[0][0])
    at_70 = int(np.where(samples["t_ms"] == 70_000)[0][0])
    assert samples["y"][at_60] == CLASSES.index("faker_kill")
    assert samples["event_t_ms"][at_60] == 65_000
    assert samples["y"][at_70] == 0
    assert samples["x"][at_60,FEATURES.index("recent_faker_kill")] == 0
    assert samples["x"][at_70,FEATURES.index("recent_faker_kill")] > 0
    assert np.isclose(samples["x"][at_70,FEATURES.index("own_x")],2000/15000)
    assert samples["event_cell64"][at_60] >= 0


def test_missing_position_is_event_without_fake_coordinate():
    match = {"info": {"participants": [{"puuid": "faker", "participantId": 1,
                                          "teamId": 100, "teamPosition": "MIDDLE"}]}}
    def frame(time, events=()):
        return {"timestamp": time, "participantFrames": {"1": {"position": {"x": 100,"y": 100}}},
                "events": list(events)}
    ward = {"type": "WARD_PLACED", "timestamp": 5_000, "creatorId": 1}
    tl = {"info": {"frames": [frame(0,[ward]),frame(60_000)]}}
    z = extract(match,tl,"faker")
    assert z["y"][0] == CLASSES.index("ward_placed")
    assert z["event_cell64"][0] == -1
