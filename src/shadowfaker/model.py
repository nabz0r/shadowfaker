import torch
from torch import nn
from torch.nn import functional as F


class MacroTransformer(nn.Module):
    def __init__(self, feature_dim: int, items: int, width: int = 128, layers: int = 2, heads: int = 4):
        super().__init__()
        self.numeric = nn.Linear(feature_dim, width)
        self.champion = nn.Embedding(1000, width)
        self.time = nn.Embedding(64, width)
        block = nn.TransformerEncoderLayer(width, heads, width * 3, dropout=.1, batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(block, layers)
        self.norm = nn.LayerNorm(width)
        self.region_head = nn.Linear(width, 256)
        self.item_head = nn.Linear(width, items)
        self.skill_head = nn.Linear(width, 5)
        self.prior_scale = nn.Parameter(torch.tensor(1.0))
        yy, xx = torch.meshgrid(torch.arange(16), torch.arange(16), indexing="ij")
        self.register_buffer("centers", torch.stack(((xx.flatten() + .5) / 16, (yy.flatten() + .5) / 16), dim=1).float())

    def forward(self, x, champion):
        batch, steps, _ = x.shape
        position = self.time(torch.arange(steps, device=x.device))[None]
        h = self.numeric(x) + self.champion(champion.clamp(0, 999))[:, None, :] + position
        h = self.norm(self.encoder(h)[:, -1])
        current_xy = x[:, -1, 17:19]
        distance = ((current_xy[:, None, :] - self.centers[None]) ** 2).sum(-1)
        region = self.region_head(h) - F.softplus(self.prior_scale) * 20 * distance
        return region, self.item_head(h), self.skill_head(h)


def parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
