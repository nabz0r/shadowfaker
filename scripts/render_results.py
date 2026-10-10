#!/usr/bin/env python3
"""Publish aggregate-only benchmark charts; no Riot match data or player traces."""
import argparse
from html import escape
import json
import os
from pathlib import Path
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs" / "data" / "public_summary.json"
FIGURES = ROOT / "docs" / "figures"
ROLE_NAMES = ("approach_jungle", "approach_bot", "approach_support", "approach_top")
PHASES = ("early_0_10", "mid_10_20", "late_20_plus")
TEMPO_TAGS = ("approach_jungle", "approach_bot", "approach_support")


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
        temp = Path(stream.name)
    os.replace(temp, path)


def collect() -> dict:
    with (ROOT / "artifacts" / "evaluation.json").open() as stream:
        test = json.load(stream)
    with (ROOT / "artifacts" / "evaluation_val.json").open() as stream:
        validation = json.load(stream)
    with (ROOT / "data" / "processed" / "macro_actions" / "meta.json").open() as stream:
        actions = json.load(stream)
    with (ROOT / "data" / "prospective" / "manifest.json").open() as stream:
        prospective = json.load(stream)
    with (ROOT / "data" / "processed" / "formations" / "meta.json").open() as stream:
        formation = json.load(stream)
    with (ROOT / "data" / "processed" / "meta.json").open() as stream:
        processed_meta = json.load(stream)
    confusion = np.load(ROOT / "artifacts" / "region_confusion.npy")
    if confusion.shape != (256, 256) or int(confusion.sum()) != int(test["samples"]):
        raise ValueError("Test confusion array is inconsistent with aggregate evaluation")
    tempo = {}
    for start in range(0, 40, 5):
        tempo[f"{start}_{start + 5}"] = {name: {"positive": 0, "valid": 0} for name in TEMPO_TAGS}
    tag_names = tuple(actions["tag_names"])
    for mid in actions["source_match_ids"]:
        with np.load(ROOT / "data" / "processed" / "macro_actions" / f"{mid}.npz") as z:
            tags, valid = z["tags"], z["valid"]
        with np.load(ROOT / "data" / "processed" / "matches" / f"{mid}.npz") as z:
            minute = z["minute"]
        if len(minute) != len(tags):
            raise ValueError(f"Tag-minute alignment failed for {mid}")
        for start in range(0, 40, 5):
            selected = (minute >= start) & (minute < start + 5)
            for name in TEMPO_TAGS:
                index = tag_names.index(name)
                row = tempo[f"{start}_{start + 5}"][name]
                row["positive"] += int((tags[selected, index] * valid[selected, index]).sum())
                row["valid"] += int(valid[selected, index].sum())
    coarse = {}
    for grid in ("8x8", "4x4"):
        item = test["macro_grids_exploratory"][grid]
        val = validation["macro_grids_exploratory"][grid]
        coarse[grid] = {"model_top1": item["model_top1"],
                        "best_baseline": max(item["baselines"].values()),
                        "gain_pp": item["gain_vs_best_baseline_pp"],
                        "bootstrap95_pp": item["gain_bootstrap95_pp"],
                        "validation_gain_pp": val["gain_vs_best_baseline_pp"],
                        "validation_bootstrap95_pp": val["gain_bootstrap95_pp"]}
    return {"schema_version": 2,
            "description": "Aggregate-only metrics; 8x8 and 4x4 were examined after the existing test was seen.",
            "source_matches": actions["matches"], "source_observations": processed_meta["observations"],
            "test_matches": test["matches"],
            "prospective_new_matches": prospective["new_matches"],
            "prospective_minimum_matches": prospective["minimum_new_matches"],
            "exact_16x16": {"model_top1": test["model_region_top1"],
                            "best_baseline": max(test[key] for key in
                                                 ("baseline_most_frequent", "baseline_copy_previous",
                                                  "baseline_stay_mid", "baseline_role_phase_prior")),
                            "gain_pp": test["region_gain_vs_best_baseline_pp"],
                            "bootstrap95_pp": test["region_gain_bootstrap95_pp"]},
            "pooled_exploratory": coarse,
            "role_approach_by_phase": {phase: {name: actions["by_phase"][phase][name]
                                                for name in ROLE_NAMES} for phase in PHASES},
            "macro_tag_definition": actions["definition"],
            "test_map_density": {"actual": confusion.sum(axis=1).astype(int).tolist(),
                                 "predicted": confusion.sum(axis=0).astype(int).tolist(),
                                 "samples": int(confusion.sum())},
            "tempo_5min": tempo,
            "formation": {"matches": formation["matches"],
                          "matches_with_early_all_five": formation["matches_with_early_all_five"],
                          "definition": formation["definition"],
                          "by_phase": formation["by_phase"]}}


def render_benchmark(summary: dict) -> None:
    labels = ("16×16 exact", "8×8 pooled*", "4×4 pooled*")
    cells = (summary["exact_16x16"], summary["pooled_exploratory"]["8x8"],
             summary["pooled_exploratory"]["4x4"])
    model = np.array([100 * item["model_top1"] for item in cells])
    baseline = np.array([100 * item["best_baseline"] for item in cells])
    positions = np.arange(3)
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    fig.patch.set_facecolor("white")
    ax.bar(positions - .19, model, width=.36, color="#2457A7", label="Shadow Faker")
    ax.bar(positions + .19, baseline, width=.36, color="#8D99A8", label="Strongest baseline")
    for i, item in enumerate(cells):
        ax.text(positions[i] - .19, model[i] + .35, f"{model[i]:.2f}%", ha="center", fontsize=10, weight="bold")
        ax.text(positions[i] + .19, baseline[i] + .35, f"{baseline[i]:.2f}%", ha="center", fontsize=10)
        lo, hi = item["bootstrap95_pp"]
        ax.text(positions[i], -3.1, f"Δ {item['gain_pp']:+.2f} pp  [95% {lo:+.2f}, {hi:+.2f}]",
                ha="center", fontsize=9, color="#334155")
    ax.set_xticks(positions, labels)
    ax.set_ylim(-4, 29)
    ax.set_ylabel("Exact next-region accuracy")
    ax.set_title("Prediction improves at broader map scales", loc="left", fontsize=16, weight="bold", pad=20)
    ax.text(0, 1.01, "Held-out matches already inspected during development · same frozen model at every scale",
            transform=ax.transAxes, fontsize=10, color="#475569")
    ax.axhline(0, color="#CBD5E1", linewidth=.8)
    ax.grid(axis="y", color="#E2E8F0", linewidth=.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper left")
    fig.text(.11, .015, "* Pooled scales were chosen after viewing the 16×16 test; positive intervals here are exploratory, not independent proof.",
             fontsize=9, color="#475569")
    fig.tight_layout(rect=(0, .055, 1, 1))
    fig.savefig(FIGURES / "benchmark_scales.png", dpi=190)
    plt.close(fig)


def render_role_approach(summary: dict) -> None:
    names = (("approach_jungle", "Jungle", "#0F766E"),
             ("approach_bot", "Bot carry", "#2457A7"),
             ("approach_support", "Support", "#B45309"),
             ("approach_top", "Top", "#7C3AED"))
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(10.5, 5.7))
    fig.patch.set_facecolor("white")
    end_label_offsets = {"approach_jungle": 0, "approach_bot": 9,
                         "approach_support": 8, "approach_top": -19}
    for key, label, color in names:
        y = []
        for phase in PHASES:
            item = summary["role_approach_by_phase"][phase][key]
            y.append(100 * item["positive"] / item["valid"] if item["valid"] else np.nan)
        ax.plot(x, y, marker="o", markersize=8, linewidth=2.5, label=label, color=color)
        if np.isfinite(y[-1]):
            ax.annotate(f"{y[-1]:.1f}%", (x[-1], y[-1]),
                        xytext=(10, end_label_offsets[key]), textcoords="offset points",
                        ha="left", fontsize=9, color=color)
    ax.set_xticks(x, ("0–10 min", "10–20 min", "20+ min"))
    ax.set_xlim(-.2, 2.28)
    ax.set_ylim(0, 23)
    ax.set_ylabel("Valid minutes with an approach tag")
    ax.set_title("Which ally Faker moves toward changes with game phase", loc="left", fontsize=16, weight="bold", pad=20)
    ax.text(0, 1.01, "465 ranked matches · geometric movement proxies, not measured assistance or intent",
            transform=ax.transAxes, fontsize=10, color="#475569")
    ax.grid(axis="y", color="#E2E8F0", linewidth=.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=4, loc="upper left")
    fig.text(.11, .015, "Tags can overlap. Rates use only minutes with both Faker and the ally positioned; no causal win claim.",
             fontsize=9, color="#475569")
    fig.tight_layout(rect=(0, .055, 1, 1))
    fig.savefig(FIGURES / "role_approach_by_phase.png", dpi=190)
    plt.close(fig)


def render_formations(summary: dict) -> None:
    by_phase = summary["formation"]["by_phase"]
    phases = ("early_3_10", "mid_10_20", "late_20_plus")
    groups = (("at_least_3", "3+ allies", "#2457A7"),
              ("at_least_4", "4+ allies", "#0F766E"),
              ("all_5", "All 5", "#B45309"))
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    fig.patch.set_facecolor("white")
    for i, (key, label, color) in enumerate(groups):
        values = [100 * by_phase[p][key] / by_phase[p]["valid"] if by_phase[p]["valid"] else 0
                  for p in phases]
        bars = ax.bar(x + (i - 1) * .23, values, width=.22, label=label, color=color)
        for j, bar in enumerate(bars):
            value = values[j]
            ax.annotate(f"{value:.2f}%" if value < 1 else f"{value:.1f}%",
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8.5)
    ax.set_xticks(x, ("3–10 min", "10–20 min", "20+ min"))
    ax.set_ylim(0, 68)
    ax.set_ylabel("Valid frames with nearby allied champions")
    ax.set_title("Five-player grouping is rare early in this corpus", loc="left", fontsize=16, weight="bold", pad=20)
    ax.text(0, 1.01, "Within 2,500 units of allied bot carry · 465 ranked matches · proximity only",
            transform=ax.transAxes, fontsize=10, color="#475569")
    ax.grid(axis="y", color="#E2E8F0", linewidth=.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.text(.11, .015, "Only 1 match had an early all-five frame. This does not test a five-bot strategy or professional play.",
             fontsize=9, color="#475569")
    fig.tight_layout(rect=(0, .055, 1, 1))
    fig.savefig(FIGURES / "team_clustering.png", dpi=190)
    plt.close(fig)


def render_minimap(summary: dict) -> None:
    density = summary["test_map_density"]
    samples = density["samples"]
    actual = 100 * np.asarray(density["actual"]).reshape(16, 16) / samples
    predicted = 100 * np.asarray(density["predicted"]).reshape(16, 16) / samples
    maximum = max(float(actual.max()), float(predicted.max()))
    fig, axes = plt.subplots(1, 2, figsize=(11, 6.4), facecolor="#091526")
    fig.suptitle("Faker moved here. Shadow Faker guessed here.", x=.06, y=.98,
                 ha="left", color="white", fontsize=18, weight="bold")
    fig.text(.06, .91, f"Next-minute position · {samples:,} observations from 46 held-out matches · same colour scale",
             color="#A8B9CE", fontsize=10)
    norm = PowerNorm(gamma=.55, vmin=0, vmax=maximum)
    for ax, matrix, title, color in zip(axes, (actual, predicted),
                                        ("FAKER · OBSERVED", "SHADOW · PREDICTED"),
                                        ("#59E1D4", "#FC9DC8")):
        ax.set_facecolor("#0F2035")
        image_map = ax.imshow(matrix, origin="lower", cmap="magma", norm=norm,
                              extent=(0, 16, 0, 16), interpolation="nearest")
        ax.set_title(title, loc="left", color=color, fontsize=12, weight="bold", pad=12)
        ax.set_xticks((0, 4, 8, 12, 16))
        ax.set_yticks((0, 4, 8, 12, 16))
        ax.tick_params(colors="#C8D5E5", labelsize=8)
        ax.set_xticks(np.arange(0, 17), minor=True)
        ax.set_yticks(np.arange(0, 17), minor=True)
        ax.grid(which="minor", color="white", alpha=.08, linewidth=.4)
        for spine in ax.spines.values():
            spine.set_color("#566A82")
        ax.scatter((.7, 15.3), (.7, 15.3), c=("#59E1D4", "#FC9DC8"),
                   s=32, edgecolors="white", linewidth=.5)
        ax.text(.9, .25, "blue base", color="#D2DEEB", fontsize=8)
        ax.text(11.2, 15.35, "red base", color="#D2DEEB", fontsize=8)
    bar_axis = fig.add_axes([.91, .23, .018, .48])
    colour_bar = fig.colorbar(image_map, cax=bar_axis)
    colour_bar.set_label("Share of next-minute positions per cell (%)", color="#D2DEEB", fontsize=9)
    colour_bar.ax.tick_params(colors="#D2DEEB", labelsize=8)
    fig.text(.06, .035, "Aggregate 16×16 grid, not a replay or player POV. Bright cells show where each distribution concentrates.",
             color="#A8B9CE", fontsize=9)
    fig.subplots_adjust(left=.06, right=.88, top=.85, bottom=.1, wspace=.16)
    fig.savefig(FIGURES / "faker_vs_shadow_minimap.png", dpi=190, facecolor=fig.get_facecolor())
    plt.close(fig)
    for filename, matrix in (("actual_minimap.png", actual), ("predicted_minimap.png", predicted)):
        single, axis = plt.subplots(figsize=(5, 5), facecolor="#091526")
        axis.set_facecolor("#091526")
        axis.imshow(matrix, origin="lower", cmap="magma", norm=norm,
                    extent=(0, 16, 0, 16), interpolation="nearest")
        axis.set_xlim(0, 16)
        axis.set_ylim(0, 16)
        axis.set_xticks(np.arange(0, 17), minor=True)
        axis.set_yticks(np.arange(0, 17), minor=True)
        axis.grid(which="minor", color="white", alpha=.10, linewidth=.6)
        axis.set_xticks(())
        axis.set_yticks(())
        for spine in axis.spines.values():
            spine.set_visible(False)
        axis.scatter((.7, 15.3), (.7, 15.3), c=("#59E1D4", "#FC9DC8"),
                     s=55, edgecolors="white", linewidth=.6)
        single.subplots_adjust(0, 0, 1, 1)
        single.savefig(FIGURES / filename, dpi=160, facecolor=single.get_facecolor())
        plt.close(single)


def render_tempo(summary: dict) -> None:
    tempo = summary["tempo_5min"]
    names = (("approach_jungle", "Jungle", "#0F766E"),
             ("approach_bot", "Bot carry", "#2457A7"),
             ("approach_support", "Support", "#B45309"))
    bins = [f"{start}_{start + 5}" for start in range(0, 40, 5)]
    x = np.arange(8) * 5 + 2.5
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    fig.patch.set_facecolor("white")
    for name, label, color in names:
        values = [100 * tempo[b][name]["positive"] / tempo[b][name]["valid"]
                  if tempo[b][name]["valid"] else np.nan for b in bins]
        ax.plot(x, values, marker="o", markersize=7, linewidth=2.5, color=color, label=label)
    ax.set_xticks(x, tuple(f"{start}–{start + 5}" for start in range(0, 40, 5)))
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 35)
    ax.set_xlabel("Game minute")
    ax.set_ylabel("Valid minutes with approach tag (%)")
    ax.set_title("Team movement changes minute by minute", loc="left", fontsize=16, weight="bold", pad=20)
    ax.text(0, 1.01, "Five-minute bins · 465 ranked games · moving closer, not proven assistance",
            transform=ax.transAxes, fontsize=10, color="#475569")
    ax.grid(axis="y", color="#E2E8F0", linewidth=.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    valid_counts = [tempo[b]["approach_bot"]["valid"] for b in bins]
    fig.text(.11, .015, "Eligible minutes per bin (bot): " + " · ".join(str(n) for n in valid_counts),
             fontsize=8.5, color="#475569")
    fig.tight_layout(rect=(0, .06, 1, 1))
    fig.savefig(FIGURES / "team_tempo.png", dpi=190)
    plt.close(fig)


def render_readme_hero(summary: dict, language: str) -> None:
    # Keep the report pipeline aligned with the dashboard identity.
    from render_identity import poster

    (FIGURES / f"readme_hero_{language}.svg").write_text(poster(language), encoding="utf-8")


def render_probability_surface(summary: dict) -> None:
    density = summary["test_map_density"]
    sample_count = density["samples"]
    fig = plt.figure(figsize=(11.5, 6.1), facecolor="#091526")
    for index, (key, name, colour) in enumerate((("actual", "FAKER · OBSERVED", "#56dfd1"),
                                                  ("predicted", "SHADOW · PREDICTED", "#ef86b8")), start=1):
        ax = fig.add_subplot(1, 2, index, projection="3d")
        ax.set_facecolor("#0f2338")
        values = 100 * np.asarray(density[key], dtype=float) / sample_count
        x = np.tile(np.arange(16), 16)
        y = np.repeat(np.arange(16), 16)
        keep = values > 0
        ax.bar3d(x[keep], y[keep], np.zeros(int(keep.sum())), .85, .85, values[keep],
                 color=colour, shade=True, alpha=.83, zsort="average")
        ax.view_init(elev=30, azim=-55)
        ax.set_xlim(0, 16); ax.set_ylim(0, 16); ax.set_zlim(0, 42)
        ax.set_xticks((0, 8, 16)); ax.set_yticks((0, 8, 16)); ax.set_zticks((0, 20, 40))
        ax.tick_params(colors="#b4c9db", labelsize=7)
        ax.set_xlabel("map x", color="#b4c9db", fontsize=8)
        ax.set_ylabel("map y", color="#b4c9db", fontsize=8)
        ax.set_zlabel("share %", color="#b4c9db", fontsize=8)
        ax.set_title(name, color=colour, fontsize=12, weight="bold", pad=14)
        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.pane.fill = False
            axis.line.set_color("#4a647c")
            axis._axinfo["grid"]["color"] = (0.35, .5, .65, .18)
    fig.suptitle("The landscape of next moves", x=.08, ha="left", color="white", fontsize=19, weight="bold")
    fig.text(.08, .035, "Height = fraction of next-minute positions per map cell. Historical aggregate, not game terrain or a counterfactual.",
             color="#b4c9db", fontsize=9)
    fig.subplots_adjust(left=.025, right=.975, top=.85, bottom=.09, wspace=0)
    fig.savefig(FIGURES / "probability_surface_3d.png", dpi=190, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-summary", action="store_true", help="Regenerate charts from published aggregates only")
    args = parser.parse_args()
    FIGURES.mkdir(parents=True, exist_ok=True)
    summary = json.loads(PUBLIC.read_text()) if args.from_summary else collect()
    if not args.from_summary:
        _write_json(PUBLIC, summary)
    render_benchmark(summary)
    render_role_approach(summary)
    render_formations(summary)
    render_minimap(summary)
    render_tempo(summary)
    render_readme_hero(summary, "en")
    render_readme_hero(summary, "fr")
    render_probability_surface(summary)
    print(f"Rendered aggregate figures and two README banners from {PUBLIC}")


if __name__ == "__main__":
    main()
