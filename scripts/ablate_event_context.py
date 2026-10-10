"""Equal-capacity KR-only role-context ablation; publish aggregates, not matches."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from shadowfaker.config import CONFIG
from shadowfaker.event_model import run
from shadowfaker.util import atomic_json, read_json

GROUPS = (None, "allies", "enemies", "jungle_bot_support")
PUBLIC = CONFIG.root / "docs" / "data" / "public_event_ablation.json"
FIGURE = CONFIG.root / "docs" / "figures" / "event_context_ablation.png"


def report_path(group: str | None) -> Path:
    name = "event_clock_validation.json" if group is None else f"event_clock_ablate_{group}.json"
    return CONFIG.artifacts / name


def summarize() -> dict:
    reports = {group or "full": read_json(report_path(group)) for group in GROUPS}
    if any(not row or row.get("pilot") or row.get("with_euw") for row in reports.values()):
        raise ValueError("Need four complete KR-only validation reports")
    full = reports["full"]
    ids = tuple(full["per_match_logloss"])
    if len(ids) != 46 or any(tuple(row["per_match_logloss"]) != ids for row in reports.values()):
        raise ValueError("Ablation reports do not share exactly 46 ordered validation matches")
    counts = np.array([full["per_match_logloss"][mid]["n"] for mid in ids], dtype=np.float64)
    if any(any(row["per_match_logloss"][mid]["n"] != counts[i] for i,mid in enumerate(ids))
           for row in reports.values()):
        raise ValueError("Ablation reports have mismatched windows")
    rng = np.random.default_rng(42)
    draw = rng.integers(0,len(ids),(5000,len(ids)))
    variants = []
    full_sums = np.array([full["per_match_logloss"][mid]["sum"] for mid in ids])
    for group in GROUPS:
        key = group or "full"
        row = reports[key]
        sums = np.array([row["per_match_logloss"][mid]["sum"] for mid in ids])
        # Positive gain means keeping this feature group helped the full model.
        delta = sums - full_sums
        gain = float(delta.sum()/counts.sum())
        boot = delta[draw].sum(axis=1)/counts[draw].sum(axis=1)
        variants.append({"name": key, "masked_features": row["masked_features"],
                         "nll": round(float(row["model"]["nll"]),6),
                         "accuracy": round(float(row["model"]["accuracy"]),6),
                         "macro_f1": round(float(row["model"]["macro_f1"]),6),
                         "by_class_f1": {name: round(float(value),6)
                                         for name,value in row["model"]["by_class_f1"].items()},
                         "gain_from_kept_context": round(gain,6),
                         "gain_ci95_match_bootstrap": [round(float(v),6) for v in np.quantile(boot,[.025,.975])]})
    public = {"schema_version":1,"target":"first marked event in next 10 seconds",
              "population":"same 373 KR train and 46 KR validation matches; no EUW supplement",
              "validation_windows":int(counts.sum()),"parameters":full["parameters"],
              "class_counts_validation":full["class_counts_validation"],
              "variants":variants,
              "limits":"Feature masking is predictive ablation, not causal attribution. Validation was already used for model development; no historical test or prospective score read. Per-match losses and IDs stay local."}
    atomic_json(PUBLIC,public)
    plot(public)
    return public


def plot(public: dict) -> None:
    bg, panel, white, red, gold, blue = "#0a0a10", "#17151d", "#f5f0e9", "#ee324a", "#e1b76a", "#63c8d8"
    plt.rcParams.update({"figure.facecolor":bg,"axes.facecolor":panel,"axes.edgecolor":"#57505b",
                         "axes.labelcolor":white,"xtick.color":white,"ytick.color":white,
                         "text.color":white,"savefig.facecolor":bg})
    fig, ax = plt.subplots(figsize=(12,5.5))
    fig.subplots_adjust(left=.37,right=.94,top=.72,bottom=.25)
    fig.suptitle("SHADOW FAKER  /  DOES THE TEN-PLAYER CONTEXT HELP?",fontsize=18,fontweight="bold",y=.96)
    fig.text(.37,.82,"Full-context log loss: 1.3923  ·  7,480 windows / 46 KR validation matches",fontsize=12,color=gold)
    rows = public["variants"][1:]
    labels = ["Remove all allied geometry", "Remove all enemy geometry", "Remove jungle/bot/support roles"]
    colors = [gold,blue,"#8e85c8"]
    for i,(row,color) in enumerate(zip(rows,colors)):
        value=row["gain_from_kept_context"]
        lo,hi=row["gain_ci95_match_bootstrap"]
        ax.errorbar(value,i,xerr=[[value-lo],[hi-value]],fmt="o",markersize=10,
                    color=color,ecolor=color,elinewidth=3,capsize=6)
        ax.text(.0011,i,f"NLL {row['nll']:.4f}",va="center",color=white,fontsize=11)
    ax.set_yticks(range(3),labels)
    ax.set_ylim(2.55,-.55)
    ax.set_xlim(-.0042,.0022)
    ax.axvline(0,color=red,linewidth=2,alpha=.9)
    ax.grid(axis="x",alpha=.14)
    ax.set_xlabel("Log-loss gain from keeping those inputs  ·  positive = helpful",labelpad=14)
    fig.text(.04,.055,"Dots: masked minus full log loss. Whiskers: 95% match bootstrap on the same adaptive validation set.\n"
             "All models have 22,537 parameters. Predictive association is not Faker's causal influence or a future test.",
             fontsize=10,color=gold)
    FIGURE.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(FIGURE,dpi=160)
    plt.close(fig)


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--from-reports",action="store_true",help="Render only from completed local reports")
    a=p.parse_args()
    if not a.from_reports:
        for group in tqdm(GROUPS,desc="5-game ablation pilots",unit="variant"):
            run(pilot=True,epochs=4,mask_group=group)
        for group in tqdm(GROUPS,desc="KR development ablations",unit="variant"):
            run(mask_group=group)
    print(summarize())


if __name__ == "__main__":
    main()
