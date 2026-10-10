"""Checks that the high-resolution target is a real next-frame cell."""
import numpy as np
import torch

from shadowfaker.features import extract_match
from shadowfaker.finegrid import _target_labels, coarse_labels
from shadowfaker.fine512 import GRID, SubcellHead, cell512, combine, parent64, subcell
from test_pipeline import synthetic_game


def test_512_cell_roundtrip_and_edge_clamping():
    rng = np.random.default_rng(42)
    xy = np.concatenate((rng.random((1000, 2)), [[0, 0], [1, 1], [-.1, 1.1]]))
    targets = cell512(xy)
    np.testing.assert_array_equal(combine(parent64(targets), subcell(targets)), targets)
    assert targets.min() >= 0 and targets.max() < GRID * GRID
    assert targets[-2] == GRID * GRID - 1
    assert torch.equal(cell512(torch.tensor(xy, dtype=torch.float32)), torch.tensor(targets))


def test_512_targets_align_with_saved_parent_and_no_future_state():
    match, timeline = synthetic_game(2)
    labels = _target_labels(match, timeline, "fixture-player")
    features = extract_match(match, timeline, "fixture-player")
    assert len(labels["xy"]) == len(features["x"]) == 12
    np.testing.assert_array_equal(parent64(cell512(labels["xy"])), labels["region"])
    xy16 = np.clip((labels["xy"] * 16).astype(int), 0, 15)
    np.testing.assert_array_equal(coarse_labels(labels["region"], 16), xy16[:, 1] * 16 + xy16[:, 0])
    assert not np.array_equal(cell512(features["x"][:, -1, 17:19]), cell512(labels["xy"]))


def test_conditional_head_supports_parent_beam_without_dense_output():
    head = SubcellHead(32)
    encoded = torch.zeros(2, 32)
    forecast = torch.full((2, 2), .5)
    parents = torch.tensor([[0, 1, 64], [4095, 4000, 2048]])
    logits = head(encoded, forecast, parents)
    assert logits.shape == (2, 3, 64)
    assert torch.isfinite(logits).all()
    assert sum(p.numel() for p in head.parameters()) < 30_000
