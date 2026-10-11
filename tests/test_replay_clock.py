from shadowfaker.demo import _observed_context


def test_replay_keeps_event_time_separate_from_sampled_positions():
    players = [
        {"puuid": "faker" if pid == 1 else str(pid), "participantId": pid,
         "teamId": 100 if pid <= 5 else 200, "teamPosition": "MIDDLE",
         "championName": f"Champion{pid}"}
        for pid in range(1, 11)
    ]
    match = {"info": {"participants": players}}
    first = {"timestamp": 0, "participantFrames": {
        "1": {"position": {"x": 1000, "y": 1000}, "level": 1}}}
    second = {"timestamp": 60_000, "participantFrames": {
        "1": {"position": {"x": 2000, "y": 2000}, "level": 2}},
        "events": [
            {"type": "CHAMPION_KILL", "timestamp": 12_345,
             "killerId": 1, "victimId": 6, "position": {"x": 9000, "y": 7000}},
            {"type": "WARD_PLACED", "timestamp": 45_678, "creatorId": 7},
            {"type": "WARD_PLACED", "timestamp": 61_000, "creatorId": 7},
        ]}
    timeline = {"info": {"frames": [first, second]}}
    empty_inventory = {pid: {} for pid in range(1, 11)}
    result = _observed_context(match, timeline, "faker", 0,
                               [empty_inventory, empty_inventory])
    assert result["frame_seconds"] == 0
    assert result["next_frame_seconds"] == 60
    assert [event["time_seconds"] for event in result["events_next"]] == [12.345, 45.678]
    assert result["events_next"][0]["cell64"] is not None
    assert result["events_next"][1]["cell64"] is None
    assert result["actors_t"][0]["xy"] != result["actors_next"][0]["xy"]
    assert sum(actor["xy"] is None for actor in result["actors_t"]) == 9
