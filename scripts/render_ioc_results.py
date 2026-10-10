#!/usr/bin/env python3
"""Publish aggregate-only item-context ablation and a readable visual result."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from shadowfaker.util import atomic_json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "static-ioc-hierarchical"
PUBLIC = ROOT / "docs" / "data" / "public_ioc_challenge.json"
FIGURE = ROOT / "docs" / "figures" / "ioc_challenge.png"


def paired(a: dict, b: dict, seed: int = 42) -> dict:
    keys=sorted(set(a) & set(b))
    rng=np.random.default_rng(seed)
    total=sum(a[k]["samples"] for k in keys)
    delta=100*sum(a[k]["correct"]-b[k]["correct"] for k in keys)/total
    draws=[]
    for _ in range(2000):
        pick=rng.integers(0,len(keys),len(keys))
        draws.append(100*sum(a[keys[j]]["correct"]-b[keys[j]]["correct"] for j in pick)
                     /sum(a[keys[j]]["samples"] for j in pick))
    return {"delta_pp":round(float(delta),4),
            "bootstrap95_pp":[round(float(v),4) for v in np.quantile(draws,[.025,.975])]}


def main() -> dict:
    report=json.loads((SOURCE/"comparison.json").read_text())
    if report["status"]!="development_only" or report["pilot"] or report["val_matches"]!=46:
        raise ValueError("Expected full 46-match development validation")
    variants=report["variants"]
    private={name:json.loads((SOURCE/f"validation_{name}.json").read_text()) for name in variants}
    contrasts={f"full_minus_{name}":paired(private["full"]["by_match8"],private[name]["by_match8"])
               for name in ("static_off","item_off")}
    public={"scope":"Development validation, 46 matches; same matches used to select epoch and calibration",
            "train_matches":report["train_matches"],"validation_matches":report["val_matches"],
            "validation_observations":report["val_samples"],
            "features_per_frame":{"core":147,"item_lifecycle":350,"patch_descriptors":120,"total":617},
            "baseline8":report["baseline8"],"selected_variant":report["selected_variant"],
            "variants":{name:{key:row[key] for key in ("top1_8","top1_16","top1_64","raw_top1_8",
                     "topk8","active_features","parameters","selected_epoch","prior_alpha")}
                     for name,row in variants.items()},
            "paired_ablations":contrasts,
            "prior_hierarchical_full_top1_8":0.17490196078431373,
            "warning":"Items do not show a statistically robust lift; no old-test or future-game score."}
    atomic_json(PUBLIC,public)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,
                         "axes.spines.top":False,"axes.spines.right":False})
    fig,axes=plt.subplots(1,2,figsize=(14,5.4),facecolor="#0b0910")
    for ax in axes:
        ax.set_facecolor("#1a111b");ax.tick_params(colors="#f1e8e8")
        ax.spines["left"].set_color("#7c5565");ax.spines["bottom"].set_color("#7c5565")
        ax.grid(axis="y",alpha=.22,color="#e4b5ba");ax.set_axisbelow(True)
    names=("item_off","static_off","full")
    labels=("147 core\n(no new item channels)","+350 item\nevents","+120 patch\ndescriptors")
    colors=("#7899bd","#fa8a9d","#ffcf86")
    values=[100*variants[n]["top1_8"] for n in names]
    axes[0].bar(range(3),values,color=colors,width=.58)
    for i,v in enumerate(values):axes[0].text(i,v+.22,f"{v:.2f}%",ha="center",color="white",weight="bold")
    baseline=100*max(report["baseline8"].values())
    axes[0].axhline(baseline,color="#f8f5ed",ls="--",label=f"Best simple rule  {baseline:.2f}%")
    axes[0].axhline(17.49019607843137,color="#aa9aa6",ls=":",label="Previous 147-channel candidate  17.49%")
    axes[0].set_xticks(range(3),labels,color="white");axes[0].set_ylim(0,23)
    axes[0].set_ylabel("Exact next 8×8 cell · top-1 %",color="white")
    axes[0].set_title("Does item context help?",loc="left",color="white",weight="bold",fontsize=15,pad=17)
    axes[0].legend(facecolor="#1a111b",edgecolor="#684555",labelcolor="white",fontsize=9)
    ks=[1,5,10,20,32,40,64]
    coverage=[100*variants["full"]["topk8"][str(k)] for k in ks]
    axes[1].plot(ks,coverage,color="#ffcf86",marker="o",lw=3)
    axes[1].axhline(90,color="#ff6d88",ls="--",label="90% coverage")
    axes[1].axvline(40,color="#a5cfeb",ls=":",label="40/64 cells = 62.5% of map")
    axes[1].set_xlim(0,65);axes[1].set_ylim(0,104);axes[1].set_xticks(ks)
    axes[1].set_xlabel("Number of cells named out of 64",color="white")
    axes[1].set_ylabel("Observed destination inside set · %",color="white")
    axes[1].set_title("90% requires a wide answer",loc="left",color="white",weight="bold",fontsize=15,pad=17)
    axes[1].legend(facecolor="#1a111b",edgecolor="#684555",labelcolor="white",fontsize=9,loc="lower right")
    fig.text(.055,.025,"373 train · 46 reused validation matches · 1,275 decisions · not a future-game or win-rate result",
             color="#decbd3",fontsize=9)
    fig.subplots_adjust(left=.07,right=.98,bottom=.18,top=.87,wspace=.22)
    FIGURE.parent.mkdir(parents=True,exist_ok=True);fig.savefig(FIGURE,dpi=170,facecolor=fig.get_facecolor());plt.close(fig)
    return public


if __name__=="__main__":
    result=main()
    print({"validation_matches":result["validation_matches"],
           "exact8":{k:v["top1_8"] for k,v in result["variants"].items()},
           "contrasts":result["paired_ablations"]})
