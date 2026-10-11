from shadowfaker.demo import _observed_context, _source_fingerprint


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
    assert result["events_next"][0]["xy"] == [0.6, round(7000/15000,5)]
    assert result["events_next"][1]["cell64"] is None
    assert result["events_next"][1]["xy"] is None
    assert result["actors_t"][0]["xy"] != result["actors_next"][0]["xy"]
    assert sum(actor["xy"] is None for actor in result["actors_t"]) == 9


def test_boundary_events_use_own_clock_and_initial_events_are_visible():
    players=[{"puuid":"faker" if pid==1 else str(pid),"participantId":pid,
              "teamId":100 if pid<=5 else 200,"teamPosition":"MIDDLE",
              "championName":f"C{pid}"} for pid in range(1,11)]
    frames=[{"timestamp":stamp,"participantFrames":{
        "1":{"position":{"x":1000+index*100,"y":1000},"championStats":{"health":80,"healthMax":100}}},
        "events":events} for index,(stamp,events) in enumerate([
            (0,[{"type":"ITEM_PURCHASED","timestamp":0,"participantId":1,"itemId":1056},
                {"type":"SKILL_LEVEL_UP","timestamp":0,"participantId":0,"skillSlot":4}]),
            (60000,[]),
            (120000,[{"type":"CHAMPION_KILL","timestamp":60000,"killerId":1,"victimId":6},
                     {"type":"WARD_PLACED","timestamp":60234,"creatorId":7}])])]
    timeline={"info":{"frames":frames}}
    inventory=[{pid:{} for pid in range(1,11)} for _ in frames]
    now=_observed_context({"info":{"participants":players}},timeline,"faker",0,inventory)
    later=_observed_context({"info":{"participants":players}},timeline,"faker",1,inventory)
    assert [e["time_seconds"] for e in now["events_initial"]]==[0]
    assert [e["time_seconds"] for e in now["events_next"]]==[60]
    assert [e["time_seconds"] for e in later["events_next"]]==[60.234]
    assert now["actors_t"][0]["health_fraction"]==.8


def test_trace_fingerprint_changes_when_a_source_changes(tmp_path):
    source=tmp_path/"timeline.json"
    source.write_text('{"frames":1}')
    first=_source_fingerprint(source)
    source.write_text('{"frames":2}')
    assert _source_fingerprint(source)!=first
