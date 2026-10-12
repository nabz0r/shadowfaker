import json

from shadowfaker.demo import _cached_patch_items, _observed_context, _source_fingerprint


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


def test_replay_attribution_and_event_details_remain_on_event_clock():
    players=[{"puuid":"faker" if pid==1 else str(pid),"participantId":pid,
              "teamId":100 if pid<=5 else 200,"teamPosition":"MIDDLE",
              "championName":f"C{pid}"} for pid in range(1,11)]
    events=[
        {"type":"CHAMPION_KILL","timestamp":1000,"killerId":7,"victimId":1,
         "assistingParticipantIds":[8,9],"position":{"x":9000,"y":8000}},
        {"type":"ELITE_MONSTER_KILL","timestamp":2000,"killerId":2,"killerTeamId":100,
         "monsterType":"DRAGON","monsterSubType":"WATER_DRAGON"},
        {"type":"BUILDING_KILL","timestamp":3000,"killerId":2,"teamId":200,
         "buildingType":"TOWER_BUILDING","towerType":"OUTER_TURRET","laneType":"BOT_LANE"},
        {"type":"WARD_PLACED","timestamp":4000,"creatorId":8,"wardType":"UNDEFINED"},
    ]
    frames=[{"timestamp":stamp,"participantFrames":{},"events":items}
            for stamp,items in [(0,[]),(60_000,events)]]
    inventory=[{pid:{} for pid in range(1,11)} for _ in frames]
    result=_observed_context({"info":{"participants":players}},{"info":{"frames":frames}},
                             "faker",0,inventory)
    death,dragon,building,ward=result["events_next"]
    assert death["victim_id"]==1 and death["acting_team_id"]==200
    assert death["assisting_ids"]==[8,9] and death["time_seconds"]==1
    assert dragon["monster_subtype"]=="WATER_DRAGON" and dragon["acting_team_id"]==100
    assert dragon["team_attribution"]=="riot_team" and dragon["xy"] is None
    assert building["destroyed_team_id"]==200 and building["acting_team_id"]==100
    assert building["team_attribution"]=="opposite_of_destroyed_team"
    assert building["tower_type"]=="OUTER_TURRET" and building["lane_type"]=="BOT_LANE"
    assert ward["ward_type"]=="UNDEFINED" and ward["acting_team_id"]==200
    assert all(e["time_seconds"]<=60 for e in result["events_next"])


def test_patch_catalog_comes_from_cached_played_release(tmp_path):
    root=tmp_path/"ddragon"/"16.19.1"
    root.mkdir(parents=True)
    (tmp_path/"ddragon"/"versions.json").write_text(json.dumps(["16.20.1","16.19.1"]))
    (root/"en_US_item.json").write_text(json.dumps({"data":{"1056":{"name":"Doran's Ring","gold":{"total":400},"tags":["SpellDamage"]}}}))
    release,items,paths=_cached_patch_items({"info":{"gameVersion":"16.19.723.999"}},tmp_path)
    assert release=="16.19.1" and items["1056"]["gold"]["total"]==400
    assert len(paths)==2
    missing,items,_=_cached_patch_items({"info":{"gameVersion":"16.18.2"}},tmp_path)
    assert missing=="" and items=={}
