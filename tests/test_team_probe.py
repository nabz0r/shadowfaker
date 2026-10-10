"""Leakage and reproducibility checks for the separate pro scoreboard probe."""
from copy import deepcopy

import numpy as np
import pytest

from shadowfaker.pro_team_matrix import ROLES
from shadowfaker.team_probe import cluster_interval, ridge_fit, ridge_predict, split_for, vector


def _row():
    roles = {role: {"player": role, "champion": "Orianna", "gold_diff10": 100,
                    "gold_diff15": 500, "xp_diff10": 50, "kills10": 1,
                    "assists10": 2, "deaths10": 0, "final_damage": 30000}
             for role in ROLES}
    return {"day": "2025-06-01", "league": "LCK", "roles": roles,
            "history": {"Doran": {"prior_games": 3, "prior_effective90": 2.0, "days_since": 7}}}


def test_chronological_boundaries():
    assert [split_for(x) for x in ("2025-07-31", "2025-08-01", "2025-09-30", "2025-10-01")] == [0, 1, 1, 2]


def test_future_targets_and_final_fields_cannot_change_features():
    original = _row()
    edited = deepcopy(original)
    for role in ROLES:
        edited["roles"][role]["gold_diff15"] = -99999
        edited["roles"][role]["final_damage"] = 999999
    assert vector(original, [("league", "LCK")]) == vector(edited, [("league", "LCK")])
    edited["history"]["Doran"]["prior_games"] = -1
    with pytest.raises(ValueError, match="future or negative"):
        vector(edited, [])


def test_ridge_and_day_cluster_interval_deterministic():
    x = np.array([[0., 1.], [1., 0.], [2., 1.], [3., 2.]])
    y = np.array([[10., 20.], [11., 21.], [12., 22.], [13., 23.]])
    model = ridge_fit(x, y, 1.)
    assert np.array_equal(ridge_predict(model, x), ridge_predict(ridge_fit(x, y, 1.), x))
    days = np.array(["2025-10-01", "2025-10-01", "2025-10-02"])
    left = np.array([2., -2., 4.])
    right = np.array([1., -1., 3.])
    assert cluster_interval(days, left, right, draws=200) == [1., 1.]
