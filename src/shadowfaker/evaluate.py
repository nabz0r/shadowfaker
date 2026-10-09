import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from .config import CONFIG
from .dataset import MatchDataset
from .model import MacroTransformer
from .train import signature
from .util import atomic_json, read_json


def load_model(meta: dict, checkpoint: Path, device: str = "cpu"):
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if saved.get("signature") != signature(meta):
        raise ValueError("Checkpoint and dataset split/vocabulary differ; retrain")
    config = saved.get("config") or {}
    model = MacroTransformer(meta["feature_dim"], len(meta["item_vocab"]) + 2,
                             width=config.get("width", 128), layers=config.get("layers", 2))
    model.load_state_dict(saved["state_dict"])
    model.to(device).eval()
    return model


def evaluate(processed: Path = CONFIG.processed, models: Path = CONFIG.models,
             artifacts: Path = CONFIG.artifacts, batch_size: int = 128) -> dict:
    meta = read_json(processed / "meta.json")
    model = load_model(meta, models / "best.pt")
    ds = MatchDataset(processed, meta, "test")
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=0)
    train_regions = Counter()
    for mid in meta["splits"]["train"]:
        with np.load(processed / "matches" / f"{mid}.npz") as z:
            train_regions.update(int(x) for x in z["region"])
    most_common = train_regions.most_common(1)[0][0]
    predictions, truths, item_pred, item_true, skill_pred, skill_true, champions, top5 = [], [], [], [], [], [], [], []
    with torch.no_grad():
        for x, champ, r, item, skill in tqdm(loader, desc="evaluate", unit="batch"):
            out_r, out_i, out_s = model(x, champ)
            predictions.extend(out_r.argmax(-1).numpy().tolist())
            top5.extend((out_r.topk(5, dim=-1).indices == r[:, None]).any(-1).numpy().tolist())
            truths.extend(r.numpy().tolist())
            item_pred.extend(out_i.argmax(-1).numpy().tolist())
            item_true.extend(item.numpy().tolist())
            skill_pred.extend(out_s.argmax(-1).numpy().tolist())
            skill_true.extend(skill.numpy().tolist())
            champions.extend(champ.numpy().tolist())
    previous = []
    for mid in meta["splits"]["test"]:
        with np.load(processed / "matches" / f"{mid}.npz") as z:
            previous.extend(z["previous"].tolist())
    true, pred, prev = np.asarray(truths), np.asarray(predictions), np.asarray(previous)
    items, item_predictions = np.asarray(item_true), np.asarray(item_pred)
    skills, skill_predictions = np.asarray(skill_true), np.asarray(skill_pred)
    conditional = items != 0
    skill_conditional = skills != 0
    result = {"test_matches": len(meta["splits"]["test"]), "samples": len(true),
              "model_region_top1": float((pred == true).mean()), "model_region_top5": float(np.mean(top5)),
              "baseline_most_frequent": float((true == most_common).mean()),
              "baseline_copy_previous": float((true == prev).mean()),
              "baseline_stay_mid": float((true == (8 * 16 + 8)).mean()),
              "model_item_accuracy": float((item_predictions == items).mean()),
              "baseline_item_none": float((items == 0).mean()),
              "item_event_rate": float(conditional.mean()),
              "item_accuracy_when_purchase": float((item_predictions[conditional] == items[conditional]).mean()) if conditional.any() else None,
              "model_skill_accuracy": float((skill_predictions == skills).mean()),
              "skill_event_rate": float(skill_conditional.mean()),
              "skill_accuracy_when_upgrade": float((skill_predictions[skill_conditional] == skills[skill_conditional]).mean()) if skill_conditional.any() else None,
              "most_frequent_region": most_common}
    by_champion = defaultdict(lambda: [0, 0])
    confusion = np.zeros((256, 256), dtype=np.int64)
    for champion, actual, guess in zip(champions, truths, predictions):
        by_champion[str(champion)][0] += int(actual == guess)
        by_champion[str(champion)][1] += 1
        confusion[actual, guess] += 1
    result["by_champion"] = {k: {"accuracy": a / n, "samples": n} for k, (a, n) in by_champion.items()}
    result["beats_all_region_baselines"] = result["model_region_top1"] > max(result[k] for k in
        ("baseline_most_frequent", "baseline_copy_previous", "baseline_stay_mid"))
    artifacts.mkdir(parents=True, exist_ok=True)
    np.save(artifacts / "region_confusion.npy", confusion)
    fig, ax = plt.subplots(figsize=(8, 7))
    image = ax.imshow(np.log1p(confusion), origin="lower", cmap="magma", aspect="auto")
    fig.colorbar(image, ax=ax, label="log(1 + count)")
    ax.set(xlabel="Predicted region", ylabel="Actual region", title="Test region confusion (16×16 labels)")
    fig.tight_layout()
    fig.savefig(artifacts / "region_confusion.png", dpi=140)
    plt.close(fig)
    atomic_json(artifacts / "evaluation.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()
    print(json.dumps(evaluate(batch_size=args.batch_size), indent=2))


if __name__ == "__main__":
    main()
