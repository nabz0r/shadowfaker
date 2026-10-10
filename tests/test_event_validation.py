from shadowfaker.event_validation import audit_match, independent_category, strict_cell


def test_neutral_death_and_unattributed_item_are_not_enemy_actions():
    players = [{"participantId": i, "teamId": 100 if i <= 5 else 200,
                "puuid": "faker" if i == 1 else f"player-{i}"} for i in range(1, 11)]
    match = {"info": {"participants": players}}
    events = [
        {"type": "CHAMPION_KILL", "timestamp": 1000, "killerId": 0, "victimId": 6,
         "position": {"x": 7000, "y": 7000}},
        {"type": "CHAMPION_KILL", "timestamp": 2000, "killerId": 0, "victimId": 1,
         "position": {"x": 6000, "y": 6000}},
        {"type": "ITEM_PURCHASED", "timestamp": 0, "participantId": 0, "itemId": 3865},
    ]
    timeline = {"info": {"frames": [{"timestamp": 0, "events": events}]}}
    indexed = {(0, 1): (2000, "faker_death", 25 * 64 + 25, 0, 1, 0, 0),
               (0, 2): (0, "ITEM_PURCHASED", None, 0, 0, 3865, 0)}
    result = audit_match(match, timeline, "faker", indexed)
    assert independent_category(events[0], 1, 100, {i: 100 if i <= 5 else 200 for i in range(1, 11)}) is None
    assert result["neutral"] == {"other_victim": 1, "faker_victim": 1}
    assert result["excluded"] == {"CHAMPION_KILL": 1}
    assert result["categories"]["faker_death"]["exact"] == 1
    assert result["categories"]["ITEM_PURCHASED"]["missing_required"] == 1
    assert not result["issues"]


def test_event_locus_rejects_out_of_map_coordinates():
    assert strict_cell({"position": {"x": 15001, "y": 3000}}) == (None, True)
    assert strict_cell({"position": {"x": 15000, "y": 15000}}) == (4095, False)
