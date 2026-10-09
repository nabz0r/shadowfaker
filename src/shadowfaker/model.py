import torch
from torch import nn
from torch.nn import functional as F

from .features import FEATURE_NAMES


class MacroTransformer(nn.Module):
    def __init__(self, feature_dim: int, items: int, width: int = 128, layers: int = 2, heads: int = 4,
                 spatial_head: bool = False):
        super().__init__()
        self.numeric = nn.Linear(feature_dim, width)
        self.champion = nn.Embedding(1000, width)
        self.time = nn.Embedding(64, width)
        block = nn.TransformerEncoderLayer(width, heads, width * 3, dropout=.1, batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(block, layers)
        self.norm = nn.LayerNorm(width)
        self.region_head = nn.Linear(width, 256)
        self.coord_head = nn.Linear(width, 2) if spatial_head else None
        if self.coord_head is not None:
            nn.init.zeros_(self.coord_head.weight)
            nn.init.zeros_(self.coord_head.bias)
        self.item_head = nn.Linear(width, items)
        self.skill_head = nn.Linear(width, 5)
        self.value_head = nn.Linear(width, 1)
        self.prior_scale = nn.Parameter(torch.tensor(1.0))
        yy, xx = torch.meshgrid(torch.arange(16), torch.arange(16), indexing="ij")
        self.register_buffer("centers", torch.stack(((xx.flatten() + .5) / 16, (yy.flatten() + .5) / 16), dim=1).float())
        self.register_buffer("region_log_prior", torch.zeros(6, 3, 256), persistent=False)
        self.prior_alpha = 0.0
        self.item_none_bias = 0.0
        self.skill_none_bias = 0.0
        self.role_feature_index = FEATURE_NAMES.index("faker_role")

    def forward(self, x, champion):
        batch, steps, _ = x.shape
        position = self.time(torch.arange(steps, device=x.device))[None]
        h = self.numeric(x) + self.champion(champion.clamp(0, 999))[:, None, :] + position
        h = self.norm(self.encoder(h)[:, -1])
        current_xy = x[:, -1, 17:19]
        forecast_xy = (current_xy + .35 * torch.tanh(self.coord_head(h))).clamp(0, 1) if self.coord_head is not None else current_xy
        distance = ((forecast_xy[:, None, :] - self.centers[None]) ** 2).sum(-1)
        region = self.region_head(h) - F.softplus(self.prior_scale) * 20 * distance
        if self.prior_alpha:
            role = (x[:, -1, self.role_feature_index] * 5).round().long().clamp(0, 5)
            minute = x[:, -1, 0] * 50
            phase = (minute >= 10).long() + (minute >= 20).long()
            region = region + self.prior_alpha * self.region_log_prior[role, phase]
        item = self.item_head(h)
        skill = self.skill_head(h)
        if self.item_none_bias:
            item = item.clone()
            item[:, 0] += self.item_none_bias
        if self.skill_none_bias:
            skill = skill.clone()
            skill[:, 0] += self.skill_none_bias
        return region, item, skill, self.value_head(h).squeeze(-1)


def parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
