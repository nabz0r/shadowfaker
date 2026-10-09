# Shadow Faker

**A reproducible, local research pipeline for Faker-style macro decisions in League of Legends.** It predicts the next 16×16 map region, first item purchase, and skill upgrade from ranked solo-queue timelines. Only actions of the account resolved as `Hide on bush#KR1` are targets; the other nine players provide context. Riot account-v1 confirms the Riot ID and PUUID, but cannot establish a person's identity by itself.

The longer-term goal is a **Shadow Plus** policy that could improve on this behavioral prior. Prediction accuracy on old matches does not establish stronger play. [SHADOW_PLUS.md](SHADOW_PLUS.md) defines the evidence needed for that claim. [Version française](README.fr.md).

**Measured status:** 465 usable ranked matches and 12,510 observations were collected from the available 470 match IDs. The selected model predicts the exact next 16×16 region in 11.28% of held-out test observations, versus 11.61% for a train-only role/phase prior. The requested clear exact-region baseline win has **not** been demonstrated. An exploratory pooling of predictions into 8×8 and 4×4 macro regions shows a positive signal that requires a fresh confirmatory test. Purchases and skill upgrades exceed their no-event baselines after validation calibration. Exact figures and limits are in [RESULTS.md](RESULTS.md).

## One-command run

Requires macOS Apple Silicon, Python 3.11+, and a current Riot development key. The validated local environment uses Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -e .
cp .env.example .env
# Set RIOT_API_KEY in .env to the current Riot developer key.
.venv/bin/python scripts/run_pipeline.py --limit 1000 --epochs 25
```

If `pip` is unavailable in the virtual environment, use `uv pip install --python .venv/bin/python -r requirements.txt -e .`. The command validates **every stage on five games first**, then collects all available games up to the target, parses, analyzes, trains, selects on validation, evaluates on held-out test games, and exports a GIF. JSON and match-level NPZ files are cached; rerun the same command after a crash or key renewal. For a five-game smoke run: `.venv/bin/python scripts/run_pipeline.py --limit 5 --epochs 3`.

Use `--game-name "Name" --tag-line TAG` for another account, with a separate `data/raw/` directory if its PUUID differs. The collector uses the `asia` route for KR, filters queue 420 (ranked solo), skips remakes shorter than five minutes and missing timelines, and paginates without duplicates. A persistent 1.3-second interval between requests respects the 100 requests per two minutes development quota. It also handles `Retry-After`, backoff, timeouts, and clear 401/403 key errors. At two requests per match, 1,000 games require **at least about 43 minutes**, excluding pagination and retries. The actual account history may contain fewer.

## Model and data

The versioned parser takes a causal window of eight one-minute frames. Inputs include Faker's champion and role, minute, gold and unspent gold, level/XP, lane plus jungle CS, recent deaths and purchases, team gold/XP advantage and its change, objective availability, ward and kill events, positions of ten players, and Faker's distances to allied roles and Dragon/Baron pits. Allied roles have stable slots ordered jungle, bot carry, support, mid, top. The transformer can learn different roles' importance at different phases. The next region, item, and skill are **Faker's actions only**. A fourth, auxiliary output estimates final match outcome; the future win label is never part of an input state.

Each match stores two views: `x_oracle` has full timeline positions; default `x` is a **minimap proximity proxy** that hides enemies farther than 1,600 map units from an ally and carries their last-seen position and age. This is not true fog of war: enemy team gold/XP aggregates remain omniscient in both views. Train an oracle ablation with `.venv/bin/python -m shadowfaker.train --view oracle` after preserving the proxy checkpoint if needed. Missing target positions are skipped; an isolated parsing failure is logged and excluded.

The 16×16 region loss mixes balanced and ordinary cross-entropy by default; no-purchase and no-skill labels are downweighted during training. A role- and phase-specific region prior is fitted on **training matches only**, then its smoothing and interpolation are selected on validation. No-purchase/no-skill output biases are also selected on validation to correct event-rate calibration. Splits are by **match**, never by frame. Item vocabulary and class weights are fitted on training matches only. The dataset holds at most two decompressed matches in RAM. Seed 42, dependency versions, schema, splits, and counts are recorded. CPU and MPS are benchmarked on a short epoch, then the faster backend is selected.

## Artifacts and evaluation

| Stage | Local output |
|---|---|
| Fetch | `data/raw/` JSON and manifest |
| Parse | `data/processed/matches/*.npz`, `meta.json` |
| Team analysis | `artifacts/faker_rotations.json` and `.png` |
| Train | `models/best.pt`, `models/training.json`, TensorBoard `runs/` |
| Validation | `artifacts/evaluation_val.json`, confusion image/array |
| Final test | `artifacts/evaluation.json`, `region_confusion.png` and `.npy` |
| Demo | `artifacts/predicted_vs_actual.gif` from a held-out match |

Region metrics include top-1/top-5 accuracy and mean distance in grid cells against the most frequent training region, copying the current region, staying at map center, and the train-only role/phase prior alone when calibration is available. Exploratory 8×8 and 4×4 scores pool the 16×16 output probabilities and recompute baselines at each resolution. The gain over the strongest baseline includes a paired 95% bootstrap interval sampled by match. Item and skill reports include event rates and accuracy conditional on a real purchase/upgrade. Final-outcome Brier score is compared with a constant training-win-rate baseline. Results are broken down by champion, patch, phase, Faker role, and team gold state. The confusion matrix covers all 256 regions. On a fresh full run, the runner compares the initial, wider three-layer, and explicit movement variants on **validation**, saves the selected configuration, then evaluates the test split. A rerun reuses that choice and the checkpoint.

`faker_rotations.json` describes proximity to allied jungle/bot/support/top and objective pits by phase and match result. It also measures the **observed** two-minute change in team gold/XP advantage after nearby and farther observations, averaging by match first. These are associations, not causal estimates of help or intent.

## Research, public material, and limitations

- [RESEARCH_NOTES.md](RESEARCH_NOTES.md): how the three supplied PDFs informed event/XP features and leak prevention.
- [OTHER_GAMES_RESEARCH.md](OTHER_GAMES_RESEARCH.md): methods from StarCraft, Dota, Minecraft, Atari, and other MOBA studies, with applicability boundaries.
- [PUBLIC_GAME_ANALYSIS.md](PUBLIC_GAME_ANALYSIS.md): Korean/English official VODs, T1 communications, interviews, and fan discussions, with provenance and an annotation contract.
- [REPLAY_FEASIBILITY.md](REPLAY_FEASIBILITY.md): replay/video path when matching local material exists.
- [PLAN.md](PLAN.md) and [PROGRESS.md](PROGRESS.md): architecture, risks, actual tests, counts, and results.
- [RESULTS.md](RESULTS.md): exact held-out scores, baselines, and the remaining region-prediction gap.

Professional LCK/Worlds games and ranked solo queue differ in roster, draft, communications, and incentives. Any future joint training must identify the domain and report separate held-out results. Reddit/X interpretations and translations are hypotheses until checked against match-specific evidence. No video, voice, or social-media text is silently treated as a numeric label.

Timelines sample roughly every 60 seconds. They miss instant reactions, exact fog of war, ward positions, cooldown details, pings, voice, and Faker's own screen. One-step cloning does not test accumulated errors in full games, micro play, or strength against opponents. The outcome head predicts state–result association, not an action's causal value. Objective respawns are approximated and may vary by patch.

Raw Riot JSON, processed samples, models, runs, artifacts, and `.env` are excluded from Git. **Do not redistribute Riot raw match data.** Use is local/personal research subject to Riot's applicable terms. Source documentation: [Riot API reference](https://developer.riotgames.com/apis), [developer portal limits](https://developer.riotgames.com/docs/portal), and [Replay documentation](https://developer.riotgames.com/docs/lol). Repository code follows its AGPL-3.0 license.
