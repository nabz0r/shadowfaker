from collections import OrderedDict
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


class MatchDataset(Dataset):
    """Index only sample offsets; retain at most two decompressed matches in memory."""

    def __init__(self, processed: Path, meta: dict, split: str, max_cached: int = 2):
        self.processed = processed
        self.meta = meta
        self.index = [(mid, i) for mid in meta["splits"][split] for i in range(meta["counts"][mid])]
        self.cache: OrderedDict[str, dict] = OrderedDict()
        self.max_cached = max_cached
        self.item_vocab = {int(k): int(v) for k, v in meta["item_vocab"].items()}

    def __len__(self):
        return len(self.index)

    def _match(self, match_id: str):
        if match_id not in self.cache:
            with np.load(self.processed / "matches" / f"{match_id}.npz") as z:
                self.cache[match_id] = {k: z[k] for k in z.files}
            if len(self.cache) > self.max_cached:
                self.cache.popitem(last=False)
        self.cache.move_to_end(match_id)
        return self.cache[match_id]

    def __getitem__(self, index):
        mid, i = self.index[index]
        a = self._match(mid)
        item = int(a["item"][i])
        return (torch.from_numpy(a["x"][i].copy()), torch.tensor(int(a["champion"][i]), dtype=torch.long),
                torch.tensor(int(a["region"][i]), dtype=torch.long),
                torch.tensor(0 if item == 0 else self.item_vocab.get(item, 1), dtype=torch.long),
                torch.tensor(int(a["skill"][i]), dtype=torch.long))
