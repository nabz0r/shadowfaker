#!/usr/bin/env python3
"""Publish aggregate-only figures for the Shadow Faker 90% research roadmap.

The SQLite source stays private. No match ID, row, raw event, or test label is
written to the public JSON or figures. The historical benchmark is read from
an already-published aggregate rather than recomputed from the old test.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/processed/faker_ioc.sqlite"
OUT = ROOT / "docs" / "data" / "public_roadmap90.json"
FIG = ROOT / "docs" / "figures"
CLASSES = ("purchase", "skill_point", "ward_placed", "ward_cleared", "kill", "death", "assist")
COLORS = {"ink": "#f6f1eb", "muted": "#bbc0cc", "bg": "#0d1019", "panel": "#1b2230",
          "red": "#f36b85", "cyan": "#76dce4", "gold": "#eed09d", "grid": "#53606b"}


def summarize(cursor, pilot_ids: set[str] | None = None) -> dict:
    counts = Counter()
    positives = Counter()
    any_positive = Counter()
    age_bins = {"train": Counter(), "val": Counter()}
    query = """SELECT g.split,w.match_id,w.labels_json,w.t_ms-s.timestamp_ms
               FROM windows w JOIN games g USING(match_id)
               JOIN snapshots s ON s.match_id=w.match_id AND s.frame_index=w.frame_index
               WHERE g.split IN ('train','val') ORDER BY g.split,w.match_id,w.window_index"""
    for split, match_id, raw, age_ms in cursor.execute(query):
        if pilot_ids is not None and match_id not in pilot_ids:
            continue
        labels = json.loads(raw)
        if len(labels) != len(CLASSES) or age_ms < 0:
            raise ValueError("Unexpected label schema or future snapshot in IoC window")
        counts[split] += 1
        any_positive[split] += int(any(labels))
        # 0, 10, ... 60+ seconds since the last *observed* player position.
        age_bins[split][min((age_ms // 10_000) * 10, 60)] += 1
        for name, value in zip(CLASSES, labels):
            if value not in (0, 1):
                raise ValueError("Labels must be binary")
            positives[(split, name)] += value
    if not counts["train"] or not counts["val"]:
        raise ValueError("Missing train or validation windows")
    return {
        split: {"windows": counts[split], "any_faker_event": any_positive[split],
                "positive_labels": {name: positives[(split, name)] for name in CLASSES},
                "snapshot_age_10s_bins": {str(n): age_bins[split][n] for n in range(0, 61, 10)}}
        for split in ("train", "val")
    }


def configure() -> None:
    plt.rcParams.update({"figure.facecolor": COLORS["bg"], "savefig.facecolor": COLORS["bg"],
                         "axes.facecolor": COLORS["panel"], "axes.edgecolor": COLORS["grid"],
                         "text.color": COLORS["ink"], "axes.labelcolor": COLORS["ink"],
                         "xtick.color": COLORS["muted"], "ytick.color": COLORS["muted"],
                         "font.family": "DejaVu Sans", "font.size": 11,
                         "svg.fonttype": "none", "svg.hashsalt": "shadowfaker-roadmap-v1"})


def save(fig, name: str) -> None:
    path = FIG / name
    fig.savefig(path, format="svg", metadata={"Date": None, "Creator": "Shadow Faker"})
    plt.close(fig)
    # Matplotlib emits spaces at the end of many multiline path commands.
    # Normalize text so the committed SVGs pass the same whitespace gate as docs.
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")


def action_density(report: dict) -> None:
    fig, ax = plt.subplots(figsize=(13.5, 7.1))
    fig.subplots_adjust(left=.14, right=.97, top=.87, bottom=.20)
    fig.suptitle("FAKER  /  THE NEXT 10 SECONDS", x=.035, y=.97, ha="left", fontsize=23, fontweight="bold")
    names = ["Purchase", "Skill point", "Ward placed", "Ward cleared", "Kill", "Death", "Assist"]
    y = np.arange(len(names))
    for offset, split, color, label in ((-.18, "train", COLORS["red"], "Train · 373 games"),
                                         (.18, "val", COLORS["cyan"], "Validation · 46 games")):
        values = [100 * report["splits"][split]["positive_labels"][name] /
                  report["splits"][split]["windows"] for name in CLASSES]
        ax.barh(y + offset, values, height=.32, color=color, label=label)
        for i, (pct, name) in enumerate(zip(values, CLASSES)):
            n = report["splits"][split]["positive_labels"][name]
            ax.text(pct + .16, y[i] + offset, f"{pct:.1f}% · {n:,}", va="center", fontsize=10,
                    color=COLORS["ink"])
    ax.invert_yaxis()
    ax.set_yticks(y, names)
    ax.set_xlim(0, 16)
    ax.set_xlabel("Windows with a Faker-attributed event · % within each split")
    ax.grid(axis="x", color=COLORS["grid"], alpha=.42)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", frameon=False, labelcolor=COLORS["ink"])
    fig.text(.035, .04, "Overlapping labels are possible. Outcomes (kill, death, assist) are not actions."
             "  ·  Source: private IoC ledger, aggregate only  ·  No test labels", color=COLORS["muted"], fontsize=10)
    save(fig, "ioc_action_density.svg")


def observation_clock(report: dict) -> None:
    fig, (ax, side) = plt.subplots(1, 2, figsize=(14, 6.4), gridspec_kw={"width_ratios": [1.7, 1]})
    fig.subplots_adjust(left=.09, right=.97, top=.85, bottom=.22, wspace=.20)
    fig.suptitle("TWO CLOCKS  /  ONE FAKER DECISION", x=.035, y=.97, ha="left", fontsize=23, fontweight="bold")
    bins = [0, 10, 20, 30, 40, 50, 60]
    for offset, split, color in ((-.18, "train", COLORS["red"]),
                                  (.18, "val", COLORS["cyan"])):
        part = report["splits"][split]
        values = [100 * part["snapshot_age_10s_bins"][str(n)] / part["windows"] for n in bins]
        ax.bar(np.arange(7) + offset, values, width=.35, color=color)
    ax.set_xticks(np.arange(7), ["0–9", "10–19", "20–29", "30–39", "40–49", "50–59", "60+"])
    ax.set_xlabel("Age of latest sampled ten-player frame at decision time t · seconds")
    ax.set_ylabel("Share of 10-second windows · %")
    ax.set_ylim(bottom=0)
    ax.grid(color=COLORS["grid"], alpha=.4)
    side.axis("off")
    side.text(.07, .98, "■  Train · 58,974 windows", color=COLORS["red"],
              fontsize=11, transform=side.transAxes)
    side.text(.07, .92, "■  Validation · 7,480 windows", color=COLORS["cyan"],
              fontsize=11, transform=side.transAxes)
    for y, large, small, color in ((.83, "563,198", "timestamped Riot events", COLORS["gold"]),
                                    (.59, "12,975", "sampled game frames", COLORS["cyan"]),
                                    (.35, "73,482", "10-second Faker windows", COLORS["red"])):
        side.text(.07, y, large, fontsize=25, fontweight="bold", color=color, transform=side.transAxes)
        side.text(.07, y-.09, small, fontsize=12, color=COLORS["ink"], transform=side.transAxes)
    side.text(.07, .08, "An event timestamp does not reveal\nFaker's location every second.",
              fontsize=11, color=COLORS["muted"], transform=side.transAxes)
    fig.text(.035, .04, "Position clock: ~60 s  ·  Event clock: source timestamp  ·  Train/validation only in the age plot",
             color=COLORS["muted"], fontsize=10)
    save(fig, "ioc_observation_clock.svg")


def score_gate(report: dict) -> None:
    gate = report["archived_exact_cell"]
    fig, (ax, right) = plt.subplots(1, 2, figsize=(14.5, 6.4),
                                    gridspec_kw={"width_ratios": [1.45, 1]})
    fig.subplots_adjust(left=.09, right=.97, top=.85, bottom=.21, wspace=.18)
    fig.suptitle("90%  /  A CLAIM THAT MUST SURVIVE A NEW COHORT", x=.035, y=.97, ha="left",
                 fontsize=22, fontweight="bold")
    ax.axhline(90, color=COLORS["gold"], linestyle="--", lw=2, label="Aspirational exact-cell gate")
    ax.plot([100*x["coverage_actual"] for x in gate["accuracy_by_coverage"]],
            [100*x["exact_accuracy"] for x in gate["accuracy_by_coverage"]],
            color=COLORS["red"], lw=3, marker="o", markersize=8, label="Observed exact 8×8 accuracy")
    ax.set_xlim(0, 105); ax.set_ylim(0, 103)
    ax.set_xticks([5, 10, 20, 50, 100])
    ax.set_xlabel("Decisions served · % of 1,275 historical validation cases")
    ax.set_ylabel("One exact next-minute 8×8 cell · % correct")
    ax.grid(color=COLORS["grid"], alpha=.4)
    ax.legend(loc="lower right", frameon=False, labelcolor=COLORS["ink"])
    right.axis("off")
    blocks = [(.82, "01  OBSERVE", "Player-view clock and visibility\n5-game pilot first"),
              (.59, "02  LEARN", "Strict t-only features + sequence model\nBeat train-only baselines"),
              (.36, "03  CALIBRATE", "Freeze target, coverage and thresholds\nValidation by whole match"),
              (.13, "04  CONFIRM", "100+ truly new ranked games\nMatch-clustered interval")]
    for y, head, body in blocks:
        right.text(.06, y, head, transform=right.transAxes, color=COLORS["gold"],
                   fontsize=13, fontweight="bold")
        right.text(.06, y-.10, body, transform=right.transAxes, color=COLORS["ink"], fontsize=11)
    fig.text(.035, .04, "Historical checkpoint chosen on these validation games: exploratory. "
             "0 future games scored. 90% is not achieved.", color=COLORS["muted"], fontsize=10)
    save(fig, "roadmap90_gate.svg")


def main() -> None:
    if not DB.is_file():
        raise SystemExit(f"Private IoC database missing: {DB}; run scripts/build_ioc_corpus.py first")
    original_split = json.loads((ROOT / "data/processed/meta.json").read_text())["splits"]
    pilot_ids = set(original_split["train"][:3] + original_split["val"][:2])
    with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as conn:
        splits = dict(conn.execute("SELECT split,COUNT(*) FROM games GROUP BY split"))
        pilot = summarize(conn, pilot_ids)
        full = summarize(conn)
    ledger = json.loads((ROOT / "docs/data/public_ioc_ledger.json").read_text())
    gate = json.loads((ROOT / "docs/data/public_ninety_gate.json").read_text())
    if (pilot["train"]["windows"] + pilot["val"]["windows"] != 737 or
            {split: full[split]["windows"] for split in full} !=
            {split: ledger["windows_by_split"][split] for split in ("train", "val")} or
            splits != {"train": 373, "val": 46, "test": 46}):
        raise ValueError("IoC cohort drift: review the split and pilot before publishing")
    report = {"schema_version": 1, "source": "private faker_ioc.sqlite; aggregate counts only",
              "selection": "three train and two validation games in original pilot; all train/validation games",
              "target": "seven Faker-attributed events in (t,t+10s]",
              "games_by_split": splits, "pilot": pilot, "splits": full,
              "archived_exact_cell": {"target": gate["target"],
                  "validation_matches": gate["validation_matches"],
                  "validation_transitions": gate["validation_transitions"],
                  "accuracy_by_coverage": gate["accuracy_at_fixed_served_coverage"],
                  "selection": gate["status"], "prospective_new_games": gate["prospective"]["new_games_scored"]},
              "clock_counts": {"events": ledger["tables"]["events"],
                               "sampled_frames": ledger["tables"]["snapshots"],
                               "windows": ledger["tables"]["windows"]},
              "limits": "Train/validation windows overlap within matches; positions are sampled about once per minute; no test labels or match rows are published."}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    configure()
    action_density(report)
    observation_clock(report)
    score_gate(report)
    print(f"Five-game pilot: {pilot['train']['windows']} train + {pilot['val']['windows']} validation windows")
    print(f"Full: {full['train']['windows']} train + {full['val']['windows']} validation windows")
    print(f"Wrote {OUT} and three SVG figures; no test labels read")


if __name__ == "__main__":
    main()
