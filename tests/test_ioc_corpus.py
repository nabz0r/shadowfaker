import json
import sqlite3

import numpy as np
import pytest

from shadowfaker.faker_actions import CLASSES
from shadowfaker.ioc_corpus import FEATURE_NAMES, EXPORT_FEATURES, _rows, connect, context, export_train


def test_window_cannot_use_a_future_frame():
    match = {"info": {"gameVersion": "1.2", "participants": [
        {"puuid": "faker" if i == 1 else str(i), "participantId": i,
         "teamId": 100 if i <= 5 else 200, "championId": i, "teamPosition": "MIDDLE"}
        for i in range(1, 11)]}}
    frames = [{"timestamp": t, "participantFrames": {str(i): {"position": {"x": i*100, "y": i*100}}
              for i in range(1, 11)}, "events": []} for t in (0, 60_000)]
    sample = {"x": np.zeros((1, len(FEATURE_NAMES)), np.float32),
              "t_ms": np.array([50_000]), "frame_index": np.array([1]),
              "y": np.zeros((1, len(CLASSES)), np.uint8),
              "first_delay_ms": np.full((1, len(CLASSES)), -1, np.int16)}
    with pytest.raises(ValueError, match="future"):
        _rows("KR_fixture", match, {"info": {"frames": frames}}, "faker", sample,
              "train", "raw", "npz")


def test_context_excludes_future_events_and_export_excludes_validation(tmp_path):
    path = tmp_path / "ioc.sqlite"
    db = connect(path)
    feature_bytes = np.zeros(len(FEATURE_NAMES), dtype="<f4").tobytes()
    for mid, split in (("KR_train", "train"), ("KR_val", "val")):
        db.execute("INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                   (mid, split, "raw", "npz", "1.2", 1, 100, 1, 1, 2, 1))
        db.execute("INSERT INTO snapshots VALUES (?,?,?)", (mid, 0, 0))
        db.execute("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (mid, 0, 1, "faker", "MIDDLE", 1, .5, .5, 100, 50, 200, 2, 10, 0, .9, "[]"))
        for ei, ts in enumerate((9000, 11000)):
            db.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (mid, 0, ei, ts, "WARD_PLACED", "actor", 1, None, "[]",
                        .5, .5, None, None, None, None, None, None, None))
        for ei, ts, item in ((2, 9500, 1001), (3, 11000, 2002)):
            db.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (mid, 0, ei, ts, "ITEM_PURCHASED", "actor", 1, None, "[]",
                        None, None, item, None, None, None, None, None, None))
        db.execute("INSERT INTO windows VALUES (?,?,?,?,?,?,?)",
                   (mid, 0, 10_000, 0, feature_bytes, json.dumps([1]+[0]*(len(CLASSES)-1)),
                    json.dumps([1000]+[-1]*(len(CLASSES)-1))))
    db.commit()
    inp, target = context(db, "KR_train", 0)
    assert len(inp["past_60s_events"]) == 2
    assert inp["past_60s_events"][0]["timestamp_ms"] == 9000
    assert inp["actors"][0]["items_at_t"] == [1001]
    assert "role" not in inp["actors"][0]
    assert len(inp["causal_features"]) == len(EXPORT_FEATURES) == 38
    assert inp["snapshot_age_ms"] == 10_000
    assert target["observed_faker_events"]["purchase"]["first_delay_ms"] == 1000
    db.close()
    output = tmp_path / "train.jsonl"
    report = export_train(path, output)
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert report["train_examples"] == 1
    assert rows[0]["input"]["split"] == "train"
    assert rows[0]["input"]["source"]["match_id"] == "KR_train"
    assert "KR_val" not in output.read_text()
