"""Publish aggregate-only evidence for added sources and 10-second targets."""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from shadowfaker.config import CONFIG
from shadowfaker.event_clock import CLASSES
from shadowfaker.event_model import DATA, EventMLP
from shadowfaker.util import atomic_json, read_json

ROOT = CONFIG.root


def build() -> dict:
    meta = read_json(CONFIG.processed / "meta.json")
    event = read_json(DATA / "meta.json")
    euw = read_json(DATA / "alias_meta.json")
    pro = read_json(CONFIG.processed / "pro_catalog.meta.json")
    solo = read_json(CONFIG.artifacts / "event_clock_validation.json")
    transfer = read_json(CONFIG.artifacts / "event_clock_euw_validation.json")
    nets = []
    for name in ("event_clock.pt", "event_clock_euw.pt"):
        net = EventMLP()
        net.load_state_dict(torch.load(CONFIG.models/name, map_location="cpu", weights_only=True))
        net.eval()
        nets.append(net)
    per_match = []
    temporal = defaultdict(lambda: {"n": 0, "observed": np.zeros(len(CLASSES)),
                                    "predicted": np.zeros(len(CLASSES))})
    for mid in meta["splits"]["val"]:
        with np.load(DATA/f"{mid}.npz") as z:
            x, y = z["x"], z["y"].astype(int)
        with torch.no_grad():
            p0 = nets[0](torch.from_numpy(x)).softmax(-1).numpy()
            p1 = nets[1](torch.from_numpy(x)).softmax(-1).numpy()
        rows = np.arange(len(y))
        loss0 = -np.log(np.maximum(p0[rows,y],1e-9))
        loss1 = -np.log(np.maximum(p1[rows,y],1e-9))
        per_match.append((len(y),float(loss0.sum()),float(loss1.sum())))
        bins = np.minimum(19,(x[:,0]*60//2).astype(int))
        for b in np.unique(bins):
            sel = bins == b
            temporal[int(b)]["n"] += int(sel.sum())
            temporal[int(b)]["observed"] += np.bincount(y[sel],minlength=len(CLASSES))
            temporal[int(b)]["predicted"] += p1[sel].sum(axis=0)
    array = np.asarray(per_match)
    rng = np.random.default_rng(42)
    draws = rng.integers(0,len(array),(5000,len(array)))
    sampled = array[draws]
    gain = (sampled[:,:,1].sum(axis=1)-sampled[:,:,2].sum(axis=1))/sampled[:,:,0].sum(axis=1)
    exact_gain = (array[:,1].sum()-array[:,2].sum())/array[:,0].sum()
    curve = []
    for b in sorted(temporal):
        row = temporal[b]
        if row["n"] < 30:
            continue
        curve.append({"minute_start": b*2, "n": row["n"],
                      "observed_faker_kill": round(float(row["observed"][1]/row["n"]),5),
                      "predicted_faker_kill": round(float(row["predicted"][1]/row["n"]),5),
                      "observed_objective": round(float(row["observed"][5]/row["n"]),5),
                      "predicted_objective": round(float(row["predicted"][5]/row["n"]),5)})
    report = {"schema_version": 1,
              "corpora": {"kr_ranked_timeline": event["matches"],
                          "euw_attributed_ranked_timeline": euw["matches"],
                          "pro_match_summary_only": pro["unique_games"]},
              "pro_by_year": pro["accepted_by_year_hint"],
              "pro_mirror_status": pro["provenance"],
              "alias_source": euw["source_url"],
              "windows_10s": {"kr": event["windows"], "euw": euw["windows"],
                              "kr_validation": solo["validation_windows"]},
              "kr_window_classes": event["class_counts"],
              "validation": {"phase_frequency": {k:solo["phase_frequency"][k] for k in ("nll","accuracy","macro_f1")},
                             "kr_only": {k:solo["model"][k] for k in ("nll","accuracy","macro_f1")},
                             "kr_plus_euw": {k:transfer["model"][k] for k in ("nll","accuracy","macro_f1")},
                             "nll_gain_from_euw": round(float(exact_gain),6),
                             "nll_gain_ci95_match_bootstrap": [round(float(v),6) for v in np.quantile(gain,[.025,.975])]},
              "temporal_curve_2min_validation": curve,
              "limits": "Public aggregates only. Ten-second target is event type, not Faker position. EUW account historically attributed; pro mirror unverified/stale. Validation selected models; no fresh test claim."}
    atomic_json(ROOT/"docs"/"data"/"public_expansion.json",report)
    render(report)
    return report


def render(report: dict) -> None:
    bg, panel, white, red, gold, blue = "#0a0a10", "#17151d", "#f5f0e9", "#ee324a", "#e1b76a", "#63c8d8"
    plt.rcParams.update({"figure.facecolor": bg, "axes.facecolor": panel,
                         "axes.edgecolor": "#57505b", "axes.labelcolor": white,
                         "xtick.color": white, "ytick.color": white, "text.color": white,
                         "font.size": 11, "savefig.facecolor": bg})
    fig, ax = plt.subplots(2,2,figsize=(16,10),layout="constrained")
    fig.suptitle("SHADOW FAKER  /  MORE GAMES, MORE HONEST CLOCKS",fontsize=20,fontweight="bold",color=white)
    corp = report["corpora"]
    names = ["KR solo Q\ntrajectories", "EUW attributed\ntrajectories", "Pro summaries\nno trajectories"]
    values = list(corp.values())
    bars=ax[0,0].bar(names,values,color=[red,blue,gold],width=.65)
    for bar,v in zip(bars,values): ax[0,0].text(bar.get_x()+bar.get_width()/2,v+10,str(v),ha="center",color=white,fontweight="bold")
    ax[0,0].set_title("Three domains, never silently merged",loc="left",fontweight="bold")
    ax[0,0].set_ylim(0,max(values)*1.18)
    counts=report["kr_window_classes"]
    keys=["none","faker_kill","faker_death","ally_kill","enemy_kill","objective","structure","ward_placed","ward_cleared"]
    ax[0,1].barh([k.replace("_"," ") for k in keys[::-1]],[counts[k]/report["windows_10s"]["kr"]*100 for k in keys[::-1]],color=[red if k.startswith("faker") else blue if k.startswith("ward") else gold for k in keys[::-1]])
    ax[0,1].set_title("First macro event in the next 10 seconds · KR",loc="left",fontweight="bold")
    ax[0,1].set_xlabel("Share of 73,482 risk windows (%)")
    val=report["validation"]
    labels=["Phase prior", "KR model", "KR + EUW model"]
    scores=[val["phase_frequency"]["nll"],val["kr_only"]["nll"],val["kr_plus_euw"]["nll"]]
    bars=ax[1,0].bar(labels,scores,color=["#777078",red,blue],width=.6)
    for bar,v in zip(bars,scores): ax[1,0].text(bar.get_x()+bar.get_width()/2,v+.02,f"{v:.3f}",ha="center",color=white)
    ax[1,0].set_ylim(0,max(scores)*1.2)
    ax[1,0].set_title("Validation log loss · lower is better",loc="left",fontweight="bold")
    ci=val["nll_gain_ci95_match_bootstrap"]
    ax[1,0].text(.02,.96,f"EUW gain {val['nll_gain_from_euw']:.3f} · 95% match CI [{ci[0]:.3f}, {ci[1]:.3f}]",transform=ax[1,0].transAxes,va="top",color=gold)
    curve=report["temporal_curve_2min_validation"]
    minute=[r["minute_start"] for r in curve]
    for key,label,color,style in (("observed_faker_kill","Faker kill observed",red,"-"),
                                  ("predicted_faker_kill","Faker kill predicted",red,"--"),
                                  ("observed_objective","Objective observed",blue,"-"),
                                  ("predicted_objective","Objective predicted",blue,"--")):
        ax[1,1].plot(minute,[100*r[key] for r in curve],label=label,color=color,linestyle=style,linewidth=2)
    ax[1,1].set_title("Validation event risk by game minute",loc="left",fontweight="bold")
    ax[1,1].set_xlabel("Game minute · 2-minute bins")
    ax[1,1].set_ylabel("Percent of 10-second windows")
    ax[1,1].legend(frameon=False,fontsize=9,labelcolor=white)
    for a in ax.flat: a.spines[["top","right"]].set_visible(False)
    fig.text(.01,.012,"Event timestamps add prediction targets, not intermediate Faker positions. EUW attribution and pro metadata remain separate evidence domains.",color=gold,fontsize=10)
    out=ROOT/"docs"/"figures"/"corpus_event_clock.png"
    fig.savefig(out,dpi=145,bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    print(json.dumps(build()["validation"],indent=2))
