#!/usr/bin/env python3
"""Resume the local ranked pipeline and its high-resolution ecosystem in one command.

Raw Riot files, per-match traces, indexes, and checkpoints stay in ignored paths.
The historical 64x64 test is descriptive; the interaction candidate is scored
only on validation and never silently promoted over the frozen checkpoint.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

from shadowfaker.challenge import generate as generate_challenges
from shadowfaker.config import CONFIG
from shadowfaker.demo import export_trace
from shadowfaker.events64 import aggregate
from shadowfaker.finegrid import ROOT64, MODELS64, ARTIFACTS64
from shadowfaker.finegrid import prepare as prepare64, train as train64, evaluate as evaluate64
from shadowfaker.fine512 import train as train512, evaluate as evaluate512
from shadowfaker.atlas512 import build as build_atlas512
from shadowfaker.hierarchical import run as run_hierarchical
from shadowfaker.transition_probe import run as run_transition_probe
from shadowfaker.interaction_core import ROOT as INTERACTION
from shadowfaker.interaction_core import prepare as prepare_interaction
from shadowfaker.pressure import summarize as summarize_pressure
from shadowfaker.pvectors import ROOT as PVECTORS
from shadowfaker.pvectors import build as build_vectors, validate_knn
from shadowfaker.state_matrix import DB, TRANSITIONS, build as build_warehouse
from shadowfaker.game_facts import build as build_game_facts
from shadowfaker.text_index import INDEX, generate as generate_text, import_note, import_world_finals
from shadowfaker.train import train as train_interaction
from shadowfaker.evaluate import evaluate as evaluate_interaction
from shadowfaker.util import atomic_json, read_json
from build_sprites import build as build_sprites
from build_corpus_inventory import build as build_inventory


def stage(message: str) -> None:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{stamp}] {message}", flush=True)
    with (CONFIG.root / "PROGRESS.md").open("a", encoding="utf-8") as file:
        file.write(f"\n- [{stamp}] {message}\n")


def command(*parts: str) -> None:
    subprocess.run([str(part) for part in parts], cwd=CONFIG.root, check=True)


def pilot() -> None:
    marker = CONFIG.root / "data" / "next_level_pilot.json"
    if read_json(marker, {}).get("schema_version") == 1:
        stage("Next-level five-game pilot reused from checkpoint.")
        return
    pilot_root = CONFIG.root / "data" / "pilot_next_level"
    meta = prepare64(5, pilot_root / "grid64")
    if len(meta["counts"]) != 5 or meta["errors"]:
        raise RuntimeError(f"64x64 pilot failed: {meta['errors']}")
    aggregate(5, pilot_root / "events64.json")
    report = build_warehouse(5, pilot_root / "states.sqlite", pilot_root / "transitions.npz")
    if report["errors"] or report["matches_in_database"] < 5:
        raise RuntimeError(f"State pilot failed: {report['errors']}")
    summarize_pressure(5, pilot_root / "states.sqlite", pilot_root / "pressure.json")
    meta = prepare_interaction(5, pilot_root / "interaction")
    if meta["errors"]: raise RuntimeError(f"Interaction pilot failed: {meta['errors']}")
    generate_text(5, pilot_root / "text.sqlite", pilot_root / "states.sqlite")
    atomic_json(marker, {"schema_version": 1, "games": 5})
    stage("Five-game atlas, warehouse, pressure, interaction and text pilot passed.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000, help="Ranked ID target, subject to actual Riot availability")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    if not read_json(CONFIG.processed / "meta.json") or not (CONFIG.models / "best.pt").is_file():
        stage("Starting cached or fresh ranked fetch, parse and original training.")
        command(sys.executable, CONFIG.root / "scripts" / "run_pipeline.py", "--limit", str(args.limit),
                "--epochs", str(args.epochs))
    pilot()
    if args.pilot_only: return

    meta64 = prepare64()
    stage(f"64x64 labels: {len(meta64['counts'])} matches, {meta64['observations']} pairs, {len(meta64['errors'])} errors.")
    report = aggregate()
    stage(f"Event atlas: {report['source_matches']} ranked matches, {report['parse_errors']} errors.")
    warehouse = build_warehouse(db_path=DB, matrix_path=TRANSITIONS)
    stage(f"Warehouse: {warehouse['states']} states, {warehouse['transitions']} transitions, {warehouse['events']} events.")
    fact_ids = sorted(read_json(CONFIG.processed / "meta.json")["counts"])
    fact_puuid = read_json(CONFIG.raw / "resolved_account.json")["puuid"]
    fact_pilot = build_game_facts(fact_ids[:5], fact_puuid, CONFIG.raw / "matches")
    if fact_pilot["errors"]: raise RuntimeError(f"Five-game facts pilot failed: {fact_pilot['errors']}")
    facts = build_game_facts(fact_ids, fact_puuid, CONFIG.raw / "matches")
    stage(f"Post-game facts: {facts['total']} private ranked cards; {len(facts['errors'])} errors. These are retrospective, not time-t model inputs.")
    sprites = build_sprites()
    stage(f"Data Dragon sprites: {sprites['champions']} champions, {sprites['items']} items; pinned static version.")
    inventory = build_inventory()
    stage(f"Corpus inventory: {inventory['warehouse']['events']} events, {inventory['warehouse']['events_with_coordinates']} positioned.")
    pressure = summarize_pressure()
    stage(f"Enemy pressure: {pressure['states_with_faker_position']} positional frames.")
    generate_challenges()
    summaries = generate_text(index=INDEX, state_db=DB)
    stage(f"Text: {summaries['generated_documents']} EN/FR summaries, {len(summaries['errors'])} errors.")
    import_world_finals(index=INDEX)
    for path in sorted((CONFIG.root / "docs" / "cases").glob("*.txt")):
        import_note(path, index=INDEX)

    vectors = build_vectors(PVECTORS)
    retrieval = validate_knn(PVECTORS)
    stage(f"Vectors: {vectors['states']} states; kNN val exact64={retrieval['exact64']:.4f}.")

    training64 = train64(epochs=args.epochs)
    validation64 = evaluate64("val")
    test64 = evaluate64("test")
    stage(f"64x64 historical test: {test64['model_top1']:.4f} exact, best baseline {max(test64['baseline'].values()):.4f}; prospective claim pending.")
    command(sys.executable, CONFIG.root / "scripts" / "build_public_grid64.py")

    pilot512 = train512(epochs=2, pilot=True)
    pilot512_score = evaluate512(pilot=True)
    stage(f"512x512 five-game pilot: {pilot512['train_matches']} train + {pilot512['val_matches']} val games, {pilot512_score['samples']} targets; parent-label alignment passed.")
    training512 = train512(epochs=min(args.epochs, 12))
    score512 = evaluate512()
    stage(f"512x512 development validation: {score512['matches']} games, {score512['samples']} targets; exact model={score512['model_top1']:.4f}, copy={score512['copy_previous_top1']:.4f}; test untouched.")
    atlas512 = build_atlas512()
    stage(f"512x512 sparse atlas: {atlas512['ranked_matches']} ranked games, {len(atlas512['errors'])} errors; sparse cells stay local.")
    command(sys.executable, CONFIG.root / "scripts" / "build_public_grid512.py")
    command(sys.executable, CONFIG.root / "scripts" / "render_atlas512.py")

    interaction = prepare_interaction()
    stage(f"Interaction training states: {interaction['observations']} pairs, {len(interaction['errors'])} errors.")
    training = train_interaction(processed=INTERACTION,models=CONFIG.root/"models"/"interaction",
                                 runs=CONFIG.root/"runs"/"interaction",epochs=args.epochs)
    score = evaluate_interaction(processed=INTERACTION,models=CONFIG.root/"models"/"interaction",
                                  artifacts=CONFIG.root/"artifacts"/"interaction",split="val")
    stage(f"Interaction candidate validation exact16={score['model_region_top1']:.4f}; test intentionally unscored.")

    hierarchy_pilot = run_hierarchical(pilot=True, epochs=2)
    stage(f"Hierarchical pilot: {hierarchy_pilot['train_matches']} train + {hierarchy_pilot['val_matches']} val games; validation only.")
    hierarchy = run_hierarchical(epochs=args.epochs)
    selected = hierarchy["selected_variant"]
    stage(f"Hierarchical ablations: selected {selected} on validation 8x8={hierarchy['variants'][selected]['top1_8']:.4f}; historical test unscored.")
    phase_pilot = run_hierarchical(pilot=True, epochs=2, variants=("full",), phase_gate=True)
    stage(f"Phase-expert pilot: {phase_pilot['train_matches']} train + {phase_pilot['val_matches']} val games; validation only.")
    phase_expert = run_hierarchical(epochs=args.epochs, variants=("full",), phase_gate=True)
    stage(f"Phase-expert candidate: validation 8x8={phase_expert['variants']['full']['top1_8']:.4f}; historical test unscored.")
    command(sys.executable, CONFIG.root / "scripts" / "render_hierarchical.py")
    command(sys.executable, CONFIG.root / "scripts" / "export_feature_visibility.py")
    geometry_pilot = run_transition_probe(pilot=True)
    stage(f"Transition geometry pilot: {geometry_pilot['train_matches']} train + {geometry_pilot['val_matches']} val games; alignment checked.")
    geometry = run_transition_probe()
    stage(f"Transition geometry: {geometry['validation']['top1']:.4f} validation top-1; {geometry['alignment']['val']['current_vs_previous64_mismatches']} alignment mismatches.")
    command(sys.executable, CONFIG.root / "scripts" / "render_predictability.py")
    command(sys.executable, CONFIG.root / "scripts" / "run_ninety_gate.py", "--pilot-only")
    command(sys.executable, CONFIG.root / "scripts" / "run_ninety_gate.py")
    command(sys.executable, CONFIG.root / "scripts" / "render_ninety_gate.py")
    stage("Exact-cell confidence gate refreshed on development validation; prospective claims remain locked.")
    command(sys.executable, CONFIG.root / "scripts" / "audit_second_scale.py", "--pilot-only")
    command(sys.executable, CONFIG.root / "scripts" / "audit_second_scale.py")
    command(sys.executable, CONFIG.root / "scripts" / "render_second_scale.py")
    stage("Second-scale source availability refreshed; grids remain display choices, not temporal labels.")
    command(sys.executable, CONFIG.root / "scripts" / "run_faker_actions.py")
    command(sys.executable, CONFIG.root / "scripts" / "train_faker_actions.py")
    command(sys.executable, CONFIG.root / "scripts" / "render_faker_actions.py")
    stage("Faker-attributed 10-second action probabilities and validation baselines refreshed.")

    export_trace(max_frames=30)
    command(sys.executable, CONFIG.root / "scripts" / "render_atlas64.py")
    command(sys.executable, CONFIG.root / "scripts" / "render_ecosystem.py")
    command(sys.executable, CONFIG.root / "scripts" / "render_identity.py")
    stage("Dashboard aggregates, replay and public figures refreshed. Open http://127.0.0.1:8008/ with serve_dashboard.py.")
    command(sys.executable, CONFIG.root / "scripts" / "run_ioc_challenge.py", "--epochs", str(args.epochs))
    stage("Causal item IoC, played-patch catalogs, matched ablations and public IoC figure refreshed.")
    if (CONFIG.processed / "pro_catalog.sqlite").is_file():
        command(sys.executable, CONFIG.root / "scripts" / "build_pro_team_matrix.py")
        command(sys.executable, CONFIG.root / "scripts" / "render_pro_team_matrix.py")
        stage("Professional Faker/team co-play and 10/15-minute score aggregates refreshed from a separate cached corpus.")
        command(sys.executable, CONFIG.root / "scripts" / "run_team_probe.py", "--pilot-only")
        command(sys.executable, CONFIG.root / "scripts" / "run_team_probe.py")
        stage("Chronological professional team-history backtest and aggregate figure refreshed.")


if __name__ == "__main__": main()
