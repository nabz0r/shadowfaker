import numpy as np
import torch

from shadowfaker.features import FEATURE_NAMES
from shadowfaker.hierarchical import (HierarchicalPolicy, MatchBatchSampler,
                                      adjusted_hierarchy, decision_labels, feature_mask)
from shadowfaker.interaction_core import NAMES


def test_context_masks_are_nested_and_do_not_smuggle_enemy_or_objectives():
    names = FEATURE_NAMES + NAMES
    own, ally, full = (feature_mask(names, variant) for variant in ("faker", "allies", "full"))
    assert own.shape == ally.shape == full.shape == (147,)
    assert np.all(own <= ally) and np.all(ally <= full)
    for name in ("minute", "p0_x", "own_gold", "faker_role"):
        assert own[names.index(name)] == 1
    for name in ("p1_x", "p4_gold", "ally_jungle_distance", "allies_within_2500"):
        assert own[names.index(name)] == 0 and ally[names.index(name)] == 1
    for name in ("p5_x", "enemy_gold", "dragon_alive", "enemy_within_2500"):
        assert ally[names.index(name)] == 0 and full[names.index(name)] == 1


def test_observed_decision_priority_and_missing_current_position():
    x = np.zeros((5, 8, 147), np.float32)
    x[:, -1, 17:19] = [.5, .5]
    x[:, -1, 19] = 1
    x[4, -1, 19] = 0
    next_xy = np.array([[.51,.5],[.9,.9],[.9,.9],[.9,.9],[.1,.1]], np.float32)
    tags = np.zeros((5, 8), np.int8)
    valid = np.ones((5, 8), bool)
    tags[1, 6] = 1
    tags[2, 5:7] = 1
    tags[3, 5:8] = 1
    assert decision_labels(x, next_xy, tags, valid).tolist() == [0, 3, 2, 1, -100]
    valid[2, 5] = False
    assert decision_labels(x, next_xy, tags, valid)[2] == 3


def test_hierarchical_probabilities_aggregate_exactly():
    model = HierarchicalPolicy(147, width=32, layers=1)
    model.eval()
    with torch.no_grad():
        log8, log16, log64, decision, tags = model(torch.zeros(2, 8, 147), torch.tensor([1, 2]))
    assert (log8.shape, log16.shape, log64.shape) == ((2, 64), (2, 256), (2, 4096))
    assert decision.shape == (2, 5) and tags.shape == (2, 8)
    assert sum(p.numel() for p in model.parameters()) < 5_000_000
    assert torch.allclose(log64.exp().sum(-1), torch.ones(2), atol=1e-5)
    pooled16 = log64.reshape(2, 16, 4, 16, 4).logsumexp(-1).logsumexp(2).reshape(2, 256)
    pooled8 = log16.reshape(2, 8, 2, 8, 2).logsumexp(-1).logsumexp(2).reshape(2, 64)
    assert torch.allclose(pooled16, log16, atol=1e-5)
    assert torch.allclose(pooled8, log8, atol=1e-5)


def test_train_prior_shift_preserves_fine_grid_probability_masses():
    model = HierarchicalPolicy(147, width=32, layers=1)
    model.eval()
    with torch.no_grad():
        log8, log16, log64, _, _ = model(torch.zeros(2, 8, 147), torch.tensor([1, 2]))
        shifted = adjusted_hierarchy(log8, log16, log64, torch.randn(2, 64), .75)
    adjusted8, adjusted16, adjusted64 = shifted
    assert torch.allclose(adjusted64.exp().sum(-1), torch.ones(2), atol=1e-5)
    pooled16 = adjusted64.reshape(2, 16, 4, 16, 4).logsumexp(-1).logsumexp(2).reshape(2, 256)
    pooled8 = adjusted16.reshape(2, 8, 2, 8, 2).logsumexp(-1).logsumexp(2).reshape(2, 64)
    assert torch.allclose(pooled16, adjusted16, atol=1e-5)
    assert torch.allclose(pooled8, adjusted8, atol=1e-5)


def test_match_sampler_visits_each_row_once_with_reproducible_shuffle():
    class Tiny:
        index = [("a", i) for i in range(5)] + [("b", i) for i in range(4)] + [("c", i) for i in range(3)]
        def __len__(self): return len(self.index)
    first = list(MatchBatchSampler(Tiny(), batch_size=4, seed=42))
    second = list(MatchBatchSampler(Tiny(), batch_size=4, seed=42))
    assert first == second
    assert sorted(i for batch in first for i in batch) == list(range(12))
    assert len(first) == 3 and all(len(batch) == 4 for batch in first)
