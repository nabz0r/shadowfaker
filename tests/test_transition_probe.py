import numpy as np

import shadowfaker.transition_probe as probe


def test_transition_prior_is_normalized_and_backs_off_for_unseen_start():
    rows = [{"start": 8, "phase": 0, "direction": 2, "target": 9},
            {"start": 8, "phase": 0, "direction": 2, "target": 9},
            {"start": 8, "phase": 1, "direction": 3, "target": 16},
            {"start": 24, "phase": 1, "direction": 3, "target": 25}]
    prior = probe.TransitionPrior(rows, ("start", "direction"), strength=4)
    seen = prior.probabilities({"start": 8, "direction": 2})
    unseen = prior.probabilities({"start": 63, "direction": 9})
    assert np.isclose(seen.sum(), 1) and np.isclose(unseen.sum(), 1)
    assert seen.argmax() == 9
    assert np.all(unseen > 0)


def test_geometry_audit_detects_saved_previous_cell_mismatch(tmp_path, monkeypatch):
    source = tmp_path / "source"
    labels = tmp_path / "labels"
    (source / "matches").mkdir(parents=True)
    labels.mkdir()
    x = np.zeros((2, 8, 147), np.float32)
    x[:, -1, 17:19] = [.5, .5]
    x[:, -1, 19] = 1
    x[:, -2, 17:19] = [.4, .5]
    x[:, -2, 19] = 1
    minute = np.array([5, 6], np.float32)
    np.savez_compressed(source / "matches" / "M.npz", x=x, minute=minute)
    previous = np.array([2080, 2080])  # floor(.5 * 64) on both axes
    np.savez_compressed(labels / "M.npz", region=np.array([100, 101]),
                        previous=previous, minute=minute)
    monkeypatch.setattr(probe, "SOURCE", source)
    monkeypatch.setattr(probe, "LABELS", labels)
    rows, audit = probe.rows_for_matches(["M"], progress=False)
    assert len(rows) == 2
    assert audit == {"current_positions_checked": 2,
                     "current_vs_previous64_mismatches": 0,
                     "current_positions_missing": 0}
    previous[1] = 0
    np.savez_compressed(labels / "M.npz", region=np.array([100, 101]),
                        previous=previous, minute=minute)
    _, audit = probe.rows_for_matches(["M"], progress=False)
    assert audit["current_vs_previous64_mismatches"] == 1


def test_ballistic_extrapolation_uses_only_prior_observations():
    row = {"current_xy": np.array([.6, .5]), "previous_xy": np.array([.4, .5]),
           "current_known": True, "previous_known": True}
    assert probe.ballistic_cell(row, 1) == 4 * 8 + 6
    row["current_known"] = False
    assert probe.ballistic_cell(row, 1) == -1
