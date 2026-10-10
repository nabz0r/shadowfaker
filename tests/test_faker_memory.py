"""Evidence gates for the episodic split and a privacy-safe local quiz."""
import json
from pathlib import Path

import numpy as np

from shadowfaker.faker_memory import cell_at, partition_train


def test_calibration_is_match_disjoint_and_reproducible():
    matches = np.repeat(np.asarray([f"M{i:03d}" for i in range(25)]), 4)
    train_a, held_a = partition_train(matches, seed=42)
    train_b, held_b = partition_train(matches, seed=42)
    assert np.array_equal(train_a, train_b)
    assert np.array_equal(held_a, held_b)
    assert not set(matches[train_a]) & set(matches[held_a])
    assert len(set(matches[held_a])) == 5


def test_512_destination_is_a_cell_not_a_time_sample():
    assert cell_at(0.0, 0.0, 512) == 0
    assert cell_at(1.0, 1.0, 512) == 512 * 512 - 1
    assert cell_at(0.5, 0.5, 512) == 256 * 512 + 256


def test_public_memory_result_has_aggregates_only():
    path = Path(__file__).resolve().parents[1] / "docs/data/public_faker_memory.json"
    if not path.exists():
        return  # A fresh clone has no locally built corpus.
    report = json.loads(path.read_text())
    assert report["historical_test_read"] is False
    assert report["validation_matches"] > 0
    assert "examples" not in report
    assert "match_id" not in json.dumps(report)
