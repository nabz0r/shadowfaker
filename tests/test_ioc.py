from collections import Counter

import numpy as np

from shadowfaker.ioc import (ACTOR_FIELDS, HASH_BINS, apply_item_event,
                             inventory_snapshots, match_channels)
from shadowfaker.external_ioc import item_vector, match_channels as static_channels, match_patch


def _sample():
    players = [{"participantId": p, "teamId": 100 if p <= 5 else 200,
                "teamPosition": "MIDDLE", "puuid": "faker" if p == 1 else f"other-{p}"}
               for p in range(1, 11)]
    def frame(timestamp, enemy_xy, events):
        positions = {p: {"position": {"x": 1500, "y": 1500}} for p in range(1, 11)}
        positions[6] = {"position": {"x": enemy_xy[0], "y": enemy_xy[1]}}
        return {"timestamp": timestamp, "participantFrames": {str(p): state for p, state in positions.items()},
                "events": events}
    # The 30 s purchase is deliberately placed in the zero-minute event list.
    timeline = {"info": {"frames": [
        frame(0, (12000, 12000), [{"type":"ITEM_PURCHASED","participantId":6,"itemId":3006,"timestamp":30000}]),
        frame(60000, (1500, 1500), [{"type":"ITEM_PURCHASED","participantId":6,"itemId":1001,"timestamp":90000}]),
        frame(120000, (12000, 12000), [])]}}
    return {"info": {"participants": players}}, timeline


def test_inventory_lifecycle_and_timestamp_boundary():
    match, timeline = _sample()
    history, _ = inventory_snapshots(timeline)
    assert history[0][6] == Counter()
    assert history[1][6] == Counter({3006: 1})
    assert history[2][6] == Counter({3006: 1, 1001: 1})
    inventory = Counter({3006: 2, 2003: 1})
    assert apply_item_event(inventory, {"type":"ITEM_UNDO","beforeId":3006,"afterId":1055})
    assert inventory == Counter({3006: 1, 2003: 1, 1055: 1})
    assert apply_item_event(inventory, {"type":"ITEM_DESTROYED","itemId":2003})
    assert inventory[2003] == 0
    assert not apply_item_event(inventory, {"type":"ITEM_SOLD","itemId":9999})


def test_proxy_uses_last_seen_enemy_inventory_without_future_purchase():
    match, timeline = _sample()
    proxy, oracle = match_channels(match, timeline, "faker")
    width = len(ACTOR_FIELDS)
    enemy = slice(5*width, 6*width)
    assert proxy.shape == oracle.shape == (3, 10*width)
    assert oracle[0, enemy][HASH_BINS] == 0
    assert oracle[1, enemy][HASH_BINS] == 1/7
    assert oracle[2, enemy][HASH_BINS] == 2/7
    assert proxy[0, enemy][HASH_BINS + 2] == 0  # no invented enemy inventory
    assert proxy[1, enemy][HASH_BINS] == 1/7
    assert np.isclose(proxy[2, enemy][HASH_BINS], 1/7)
    assert np.isclose(proxy[2, enemy][HASH_BINS + 1], 0)


def test_patch_matched_static_descriptors_are_time_causal():
    match, timeline = _sample()
    match["info"]["gameVersion"] = "16.19.123.456"
    assert match_patch(match) == "16.19"
    catalogue = {"3006":{"gold":{"total":1100},"tags":["Boots"]},
                 "1001":{"gold":{"total":300},"tags":["Boots"]}}
    proxy, oracle = static_channels(match, timeline, "faker", catalogue)
    width = oracle.shape[1] // 10
    enemy = slice(5*width, 6*width)
    assert item_vector({3006:1}, catalogue)[0] == 1100/30000
    assert oracle[0, enemy][0] == 0
    assert np.isclose(oracle[1, enemy][0], 1100/30000)
    assert np.isclose(oracle[2, enemy][0], 1400/30000)
    assert np.isclose(proxy[2, enemy][0], 1100/30000)
