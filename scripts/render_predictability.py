#!/usr/bin/env python3
"""Publish aggregate predictability and visibility diagnostics, never match rows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs" / "data" / "public_predictability.json"
FIGURE = ROOT / "docs" / "figures" / "predictability_gap.png"


def build_summary() -> dict:
    comparison = json.loads((ROOT / "artifacts" / "hierarchical" / "comparison.json").read_text())
    transition = json.loads((ROOT / "artifacts" / "transition_probe.json").read_text())
    full = json.loads((ROOT / "artifacts" / "hierarchical" / "validation_full.json").read_text())
    proxy = json.loads((ROOT / "artifacts" / "hierarchical" / "validation_visible_proxy.json").read_text())
    expert = json.loads((ROOT / "artifacts" / "hierarchical-phase" / "validation_full.json").read_text())
    if comparison["status"] != "development_only" or transition["status"] != "development_only":
        raise ValueError("Expected development-only results")
    if full["samples"] != transition["validation"]["samples"] or expert["samples"] != full["samples"]:
        raise ValueError("Transition and model validation cohorts differ")
    curve = {k: full["topk8"][k] for k in sorted(full["topk8"], key=int)}
    first90 = next(int(k) for k, value in curve.items() if value >= .9)
    mids = list(full["by_match8"])
    if set(mids) != set(expert["by_match8"]):
        raise ValueError("Phase expert and standard model have different validation matches")
    rng = np.random.default_rng(42)
    deltas = []
    for _ in range(1000):
        pick = rng.integers(0, len(mids), len(mids))
        difference = sum(expert["by_match8"][mids[j]]["correct"] -
                         full["by_match8"][mids[j]]["correct"] for j in pick)
        samples = sum(full["by_match8"][mids[j]]["samples"] for j in pick)
        deltas.append(100 * difference / samples)
    return {
        "scope": "historical development validation; no old-test or prospective score",
        "validation_matches": comparison["val_matches"],
        "validation_samples": comparison["val_samples"],
        "position_alignment": {key: transition["alignment"][key] for key in ("train", "val")},
        "transition_rule": {"selected_fields": transition["selected"]["fields"],
                            "smoothing_strength": transition["selected"]["strength"],
                            "internal_top1": transition["selected"]["internal_top1"],
                            "validation_top1": transition["validation"]["top1"],
                            "validation_top5": transition["validation"]["top5"]},
        "location_topk8": curve, "first_listed_k_at_90_coverage": first90,
        "by_phase": {name: {phase: {"samples": row["samples"], "top1_8": row["top1_8"]}
                            for phase, row in result["by_phase"].items()}
                     for name, result in (("visible_proxy", proxy), ("full", full),
                                          ("phase_expert", expert))},
        "full_minus_visible_proxy": comparison["paired_context_deltas"][
            "full_minus_visible_proxy_calibrated_pp"],
        "phase_expert": {"top1_8": expert["top1_8"], "top5_8": expert["topk8"]["5"],
                         "parameters": expert["parameters"],
                         "selected_epoch": expert["selected_epoch"],
                         "macro_f1": expert["decision_macro_f1"],
                         "minus_full_pp": 100 * (expert["top1_8"] - full["top1_8"]),
                         "minus_full_bootstrap95_pp": np.quantile(deltas, [.025, .975]).tolist()},
        "warning": "A 90% top-k set is not 90% exact-cell accuracy; proxy visibility is not Faker POV."
    }


def render(summary: dict, path: Path = FIGURE) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.3), facecolor="#0b0b0f")
    for panel in (ax, ax2):
        panel.set_facecolor("#14141b")
        panel.tick_params(colors="#e8e5e0")
        panel.spines["left"].set_color("#66606a")
        panel.spines["bottom"].set_color("#66606a")
        panel.grid(axis="y", color="#534b52", alpha=.35)
        panel.set_axisbelow(True)
    curve = summary["location_topk8"]
    ks = np.asarray([int(k) for k in curve])
    values = 100 * np.asarray(list(curve.values()))
    ax.plot(ks, values, color="#ed284f", lw=2.6, marker="o", ms=5)
    ax.axhline(90, color="#f2db8b", ls="--", lw=1.4)
    first = summary["first_listed_k_at_90_coverage"]
    y = 100 * curve[str(first)]
    ax.scatter([first], [y], s=110, color="#70c5c3", zorder=5)
    ax.annotate(f"{first} of 64 cells\n{y:.1f}% covered", (first, y), xytext=(-80, -58),
                textcoords="offset points", color="white", weight="bold",
                arrowprops={"arrowstyle": "->", "color": "#70c5c3"})
    ax.scatter([1], [values[0]], s=100, color="#ed284f", zorder=5)
    ax.annotate(f"One cell  {values[0]:.1f}%", (1, values[0]), xytext=(12, 18),
                textcoords="offset points", color="white", weight="bold")
    ax.set_xlim(0, 65); ax.set_ylim(0, 105)
    ax.set_xlabel("Cells allowed in the answer  ·  8×8 map has 64", color="white")
    ax.set_ylabel("Observed destination covered  ·  %", color="white")
    ax.set_title("Why 90% needs a large area", color="white", fontsize=14,
                 weight="bold", loc="left", pad=14)
    phases = ("early", "middle", "late")
    x = np.arange(3)
    proxy = [100 * summary["by_phase"]["visible_proxy"][p]["top1_8"] for p in phases]
    full = [100 * summary["by_phase"]["full"][p]["top1_8"] for p in phases]
    expert = [100 * summary["by_phase"]["phase_expert"][p]["top1_8"] for p in phases]
    ax2.bar(x - .25, proxy, .23, color="#70c5c3", label="Vision proxy")
    ax2.bar(x, full, .23, color="#ed284f", label="Proxy + globals")
    ax2.bar(x + .25, expert, .23, color="#d7a44c", label="Phase expert")
    for xx, yy in zip(x, full):
        ax2.text(xx, yy + .55, f"{yy:.1f}%", color="white", ha="center", fontsize=9)
    ax2.set_xticks(x, ("0–10 min", "10–20 min", "20+ min"), color="white")
    ax2.set_ylim(0, 36)
    ax2.set_ylabel("Exact next 8×8 cell  ·  %", color="white")
    ax2.set_title("Late-game decisions remain hardest", color="white", fontsize=14,
                  weight="bold", loc="left", pad=14)
    ax2.legend(facecolor="#14141b", edgecolor="#514a52", labelcolor="white")
    fig.text(.03, .95, "SHADOW FAKER  /  PREDICTABILITY AUDIT", color="#ed284f", weight="bold", fontsize=9)
    fig.text(.03, .035,
             f"{summary['validation_matches']} validation games · {summary['validation_samples']:,} minute pairs · "
             "same model choices already used this split · not Faker POV or a future-game result",
             color="#c5bbc3", fontsize=9)
    fig.subplots_adjust(left=.075, right=.97, top=.85, bottom=.17, wspace=.27)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-summary", action="store_true")
    args = parser.parse_args()
    if args.from_summary:
        summary = json.loads(PUBLIC.read_text())
    else:
        summary = build_summary()
        PUBLIC.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    render(summary)
    print(f"Rendered {FIGURE}; public aggregate {PUBLIC}")


if __name__ == "__main__":
    main()
