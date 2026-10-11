import pytest

from shadowfaker.continuous import (ForecastAction, ObservedAction, display_cell,
                                    distance_units, score)
from shadowfaker.second_scale import strict_xy, summarize_match


def test_second_clock_event_timing_does_not_invent_faker_positions():
    match = {"info": {"participants": [
        {"puuid": "faker", "participantId": 1, "teamId": 100},
        {"puuid": "opponent", "participantId": 2, "teamId": 200}]}}
    def frame(t, x, events=()):
        return {"timestamp": t, "participantFrames": {
            "1": {"position": {"x": x, "y": 7500}},
            "2": {"position": {"x": 8000, "y": 7500}}}, "events": list(events)}
    kill = {"type": "CHAMPION_KILL", "timestamp": 5_000, "killerId": 1,
            "victimId": 2, "position": {"x": 9000, "y": 7000}}
    timeline = {"info": {"frames": [frame(0, 1000, [kill]), frame(60_000, 2000),
                                    frame(120_000, 13000)]}}
    result = summarize_match(match, timeline, "faker")
    assert result["faker_position_anchors"] == 3
    assert result["faker_position_gaps_ms"] == [60_000, 60_000]
    assert result["events_off_frame"] == 1
    assert result["located_event_loci"] == 1
    assert result["horizons"]["5"] == {"windows": 2, "with_event": 1,
                                      "with_faker_involvement": 1,
                                      "with_faker_combat": 1,
                                      "with_new_faker_position": 0}


def test_continuous_score_is_independent_of_display_grid():
    truth = ObservedAction("m", 0, 3_000, "rotate_bot", (.502, .501), "POV clip", "player")
    prediction = ForecastAction("m", 0, 3_500, "rotate_bot", (.500, .500))
    assert display_cell(truth.xy, 16) != display_cell(truth.xy, 512)
    assert distance_units(prediction.xy, truth.xy) == pytest.approx(33.541, abs=.01)
    result = score([(prediction, truth)], horizon_seconds=5, radius_units=50,
                   time_tolerance_seconds=1)
    assert result["joint_action_time_place_accuracy"] == 1
    assert result["mean_distance_units"] == pytest.approx(33.541, abs=.01)


def test_missing_location_is_reported_and_future_label_rejected():
    pred = ForecastAction("m", 0, 1_000, "ward", None)
    observation = ObservedAction("m", 0, 1_000, "ward", None, "Riot event", "timeline")
    result = score([(pred, observation)], horizon_seconds=5, radius_units=100,
                   time_tolerance_seconds=1)
    assert result["spatial_label_missing"] == 1
    assert result["joint_action_time_place_accuracy"] is None
    with pytest.raises(ValueError):
        score([(pred, ObservedAction("m", 0, 0, "ward", None, "Riot event", "timeline"))],
              horizon_seconds=5, radius_units=100, time_tolerance_seconds=1)
    assert strict_xy(None) is None
    assert strict_xy({"x": 16000, "y": 2}) is None
