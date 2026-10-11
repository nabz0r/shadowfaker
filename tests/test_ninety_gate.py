"""The 90% gate checks exact answers and served coverage separately."""
import numpy as np
import pytest

from shadowfaker.ninety_gate import fixed_coverage, score_fold, select_threshold, wilson_lower


def test_wilson_bound_rejects_small_or_mixed_samples():
    assert wilson_lower(1, 1) < .9
    assert wilson_lower(50, 50) > .9
    assert wilson_lower(45, 50) < .9
    with pytest.raises(ValueError):
        wilson_lower(2, 1)


def test_fixed_coverage_counts_exact_hits_and_abstentions():
    confidence = np.array([.9, .8, .7, .6])
    correct = np.array([True, False, True, False])
    rows = fixed_coverage(confidence, correct, (.25, .5, 1.))
    assert [(row["served"], row["correct"], row["exact_accuracy"]) for row in rows] == [
        (1, 1, 1.), (2, 1, .5), (4, 2, .5)]


def test_threshold_uses_only_calibration_match_labels():
    confidence = np.tile(np.linspace(1, .01, 100), 2)
    correct = np.ones(200, dtype=bool)
    correct[100:] = False
    matches = np.array(["cal"] * 100 + ["assessment"] * 100)
    first = score_fold(confidence, correct, matches, {"cal"})
    assert first["threshold_selected"]
    changed = correct.copy(); changed[100:] = True
    second = score_fold(confidence, changed, matches, {"cal"})
    assert first["calibration"] == second["calibration"]
    assert first["assessment"]["gate_pass"] is False
    assert second["assessment"]["gate_pass"] is True


def test_no_90_threshold_when_confident_cases_are_wrong():
    confidence = np.linspace(1, 0, 100)
    correct = np.zeros(100, dtype=bool)
    assert select_threshold(confidence, correct) is None
