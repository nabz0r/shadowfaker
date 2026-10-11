![Shadow Faker visual research dashboard: observed account and model prediction](docs/figures/readme_hero_en.svg)

# Shadow Faker

[**Open the visual dashboard locally**](#visual-dashboard) · [**The second-scale target**](SECOND_SCALE.md) · [**Explore the 512×512 atlas**](#a-512512-atlas-and-its-accuracy-limit) · [**Six Worlds finals**](WORLD_FINALS.md) · [**Français**](README.fr.md)

**A reproducible, local research pipeline aimed at Faker's decisions on a seconds-scale clock.** The research target is the next **action, its timing and any continuous location**; 16×16, 64×64 and 512×512 grids are adjustable renderings. The current ranked spatial model still predicts from positions sampled roughly **once per minute**. Two ten-second heads predict event types: one covers marked game events, and the newer one targets seven explicitly Faker-attributed families. **No second-scale Faker movement score exists yet**. That requires aligned, authorized replay or player-view evidence and a new benchmark. Only actions of the account resolved as `Hide on bush#KR1` are targets in the original spatial model; the other nine players provide context. Riot account-v1 confirms the Riot ID and PUUID, but cannot establish a person's identity by itself. [Measured second-scale evidence and protocol](SECOND_SCALE.md).

**New: Faker's next ten seconds, measured by event family.** A dedicated 13,575-parameter model predicts seven events explicitly attributed to the account: purchase, skill point, ward placed/cleared, kill, death and assist. On 46 historical validation games (7,480 windows), log loss is **0.1943** versus **0.2048** for train-only phase frequencies; macro average precision is **0.121** versus **0.066**. Purchase AP reaches **24.1%**; kill-outcome AP is only **7.7%**. An always-none rule would score **94.51% binary accuracy** by missing all 2,872 positives, which is why we report log loss and average precision. These are ranking scores for observable events, not exact player actions, second-scale positions or proof of stronger play. [See every class, source rule and reproduction](FAKER_ACTIONS.md).

![Faker-attributed next-ten-second average precision by event family](docs/figures/faker_actions_10s.png)

The longer-term goal is a **Shadow Plus** policy that could improve on this behavioral prior. Prediction accuracy on old matches does not establish stronger play. [SHADOW_PLUS.md](SHADOW_PLUS.md) defines the evidence needed for that claim. [Version française](README.fr.md).

## A visual tour of the site

The dashboard now opens **one dynamic tab at a time**. Its six gold stars refer to T1's sixth Worlds title in 2025, [confirmed by T1 co-owner Comcast Spectacor](https://comcastspectacor.com/news/2025/12/t1-entertainment-sports-wins-2025-league-of-legends-world-championship/). Shadow Faker is an independent fan research project; the stars do not describe model accuracy or team affiliation. The README follows the same visual chapters as the site.

| Site tab | What you can inspect here in the README |
|---|---|
| **Atlas 512×512** | Observed cells, event layers and the exact-cell failure in [the atlas result](#a-512512-atlas-and-its-accuracy-limit) |
| **Legacy 16×16 / 3D** | [Observed versus predicted maps](#faker-on-the-map-shadow-on-the-map) and [the frequency surface](#the-landscape-of-next-moves) |
| **Evolution / Tempo / Pressure** | A local game clock, [team movement](#the-project-at-a-glance), a [selectable opponent zone](PRESSURE.md) and ten observed positions |
| **Scores / Research / Evidence** | [Second-scale observability](SECOND_SCALE.md), [measured baselines](#what-we-score), failed rare-event classes and [research gates](NEXT_RESEARCH.md) |
| **Strategies / Challenge** | [Hypotheses and the standard for stronger play](SHADOW_PLUS.md); compose five lanes or challenge the [Faker episode memory](FAKER_MEMORY.md) |
| **Faker × team** | [Shared-game history and 10→15-minute resource matrices](TEAM_MATRIX.md) |
| **Finals BO5 / Corpus / Archives** | [Six sourced Worlds finals and 25 games](WORLD_FINALS.md), [the IoC matrix](IOC_VISION.md), plus private ranked match cards |

The horizontal tab strip stays available on mobile; [see the 390-pixel capture](DESIGN.md#dynamic-chapter-tabs). The shared clock changes the linked views according to their own cohorts; it does not add observations between one-minute Riot frames.

![Six-star Shadow Faker home screen, with the shared game clock](docs/figures/dashboard_hero.png)

**Map → possible moves.** The atlas colours aggregate observed destinations and match events on a 512×512 canvas. The 3D view raises those frequencies into a surface; its height is an observed frequency, not terrain or a winning strategy.

![Interactive 512×512 atlas tab](docs/figures/dashboard_atlas.png)

![Three-dimensional observed-position surface tab](docs/figures/dashboard_surface.png)

**An opponent zone with units.** On the Pressure tab, change the radius from 1,000 to 5,000 map units. A selected game's map and roster now show all ten observed positions, champion and item icons **at the selected minute**; Faker, allies, opponents, lanes, role and items can be filtered. Phase bars, entry rate and 0/1 or 0/2 slices use counts recalculated across 465 games. These are roughly one-minute observations; enemy dots include information Faker might not have seen. [See the formulas, denominators and limits](PRESSURE.md).

![Interactive pressure zone with measured phase bars](docs/figures/dashboard_pressure.png)

**A visible corpus, readable games.** The Corpus tab separates 470 KR ranked IDs from 465 usable games, lists exact Riot IDs and each event category, and explains why just 33,329 of 353,409 indexed events have coordinates. The local Archives tab shows UTC time, team compositions, K/D/A, damage, vision and final items for each indexed game, with 169 champion and 160 item icons packed into two local sprite atlases. These final-game facts support exploration only; they never enter prediction at time `t`. [Open the data ledger](CORPUS.md).

![Auditable corpus inventory](docs/figures/dashboard_corpus.png)

![Searchable ranked games with champion and item sprites](docs/figures/dashboard_library.png)

**Evidence → history.** The research tab shows which event classes the model misses. The new [Finals BO5 archive](WORLD_FINALS.md) covers all **25 games across six winning Worlds finals** plus three sourced landmark semifinals, separately from the ranked training data. Select a year to see every game result, duration and source.

![Research evidence tab with the next measurement gates](docs/figures/dashboard_research.png)

![Animated tour through Faker and T1's six winning Worlds finals](docs/figures/six_finals.gif)

**Faker × team.** A separate professional-match index now tracks Faker's previous shared games with Doran, Oner and Keria before each match. The interactive tab offers year, cumulative or 90-day decayed exposure, a shared-game matrix, five-role gold/XP scoreboard changes from minute 10 to 15, and a 5×5 correlation of those changes. In the available mirror, 671 games have five T1 player rows and 645 have complete snapshots; the 2026 CSV ends on 10 April. Exposure is a proxy for opportunities to learn each other's play, **not** measured trust, communication or Faker's causal influence. These pro summaries do not train the ranked spatial model. [Method and provenance](TEAM_MATRIX.md).

**Does prior co-play help predict a later scoreboard?** A chronological 534/39/72-game train/validation/test experiment predicts Faker's 15-minute mid gold gap from 10-minute context. On the 72 test games, copying the 10-minute gap has **412.64 gold** mean absolute error, a context ridge has **442.17**, and context plus prior shared games has **441.88**. The history difference from context is only **−0.29 gold**, 95% day-bootstrap interval **[−2.89, +2.10]**. The signal is unconfirmed and the persistence baseline wins. This is a separate professional scoreboard task, **not a gain in Shadow's movement accuracy**. [Full protocol and limits](TEAM_PROBE.md).

**The corrected target: seconds and actions.** Across **465 games**, the source audit finds **563,198 timestamped events** but only **12,975 sampled Faker positions**, with a **60.02-second median gap**. At 1, 5, 10 and 30 seconds after a frame there is **no new Faker position observation**. An event locus is not a player position. The new Scores slider changes the time horizon; it shows **data availability, not model accuracy**. [Continuous-target protocol and the path to second-scale labels](SECOND_SCALE.md).

![Second-scale events and missing player positions between frames](docs/figures/second_scale_observability.png)

![The seconds slider in the redesigned Scores tab](docs/figures/dashboard_second_scale.png)

**Archived minute-scale development benchmark.** The selected M3 model gets one next-minute 8×8 cell right on **17.49%** of 1,275 reused validation transitions; its most confident **5%** reach **31/64 = 48.44%**. This is no longer Shadow's primary research target. [Historical exact-cell diagnostic](NINETY_GATE.md).

![Exact next-cell accuracy as Shadow abstains on less confident transitions](docs/figures/ninety_exact_gate.png)

![The 90% exact-cell gate in the live Shadow Faker dashboard](docs/figures/dashboard_ninety_gate.png)

![Chronological professional scoreboard backtest: history versus context and persistence](docs/figures/team_history_probe.png)

![Live Faker × team challenge showing the chronological backtest and its limits](docs/figures/dashboard_team_probe.png)

![Prior shared games with Faker and 2025 role gold differences](docs/figures/team_matrix.png)

![Interactive Faker × team tab, with annual co-play and five-role scoreboard matrices](docs/figures/dashboard_team_matrix.png)

![Interactive role co-movement matrix, with correlation units and causal limits](docs/figures/dashboard_team_correlation.png)

[Open the visual design and mobile view](DESIGN.md) · [Read every final's provenance](WORLD_FINALS.md) · [Inspect exact model results](RESULTS.md).

### New: an item-aware index of context

![The live Corpus tab explains causal features, sources and their limits](docs/figures/dashboard_ioc.png)

![Item-context ablation and the map area required for 90 percent coverage](docs/figures/ioc_challenge.png)

At each observed minute the local **IoC** estimates ten players' items from timestamped purchases, sales, destruction and undos. It adds **350 item-event channels** to the 147 existing state and interaction channels. Another **120 channels** describe the items tracked with official, **played-patch-matched Riot Data Dragon** catalogs. Five games passed the pilot; all **465 games / 12,510 transitions** were then rebuilt from cache with no parse errors. The per-game matrix remains local. A retrospective audit finds only **29.05%** of final actor item-ID sets exactly reconstructed (mean Jaccard **0.839**); initial trinkets and automatic upgrades can be missed. Finished-match items are used for that audit only, never as model input at `t`.

On the same **46 reused validation games**, the 617-channel candidate scores **17.41%** exact next 8×8 cell, versus **17.18%** without patch descriptors, **16.94%** without the new item channels, and **15.29%** for the strongest simple rule. The paired lift over no added item channels is **+0.47 percentage points**, with a match-bootstrap 95% interval of **−0.16 to +1.13 points**. It is exploratory and does **not** improve on the earlier 147-channel candidate's **17.49%**. Covering **90.75%** of arrivals requires naming **40/64 cells, or 62.5% of the map**; it is not 90% exact prediction. The archived 16×16 and 512×512 results remain separate.

The Corpus tab shows an [external-source register](IOC_VISION.md): official [Riot Data Dragon](https://developer.riotgames.com/docs/lol#data-dragon) is used for patch-matched static descriptors; [U.GG](https://u.gg/lol/champions/azir/build) is a build-context reference (its direct automated access was denied and current builds cannot label a historical minute); [Google Custom Search](https://developers.google.com/custom-search/v1/overview) is a discovery route requiring credentials and closed to new customers. No search snippet, current-patch win rate or final-game item enters an old state. The game dashboard remains an independent fan project.

![Which timeline events are indexed, and which remain outside the old index](docs/figures/event_validation.png)

An independent [event validation](EVENT_VALIDATION.md) reconciles **563,198 raw Riot events** with the local warehouse: **353,409/353,409 indexed rows** reproduce their source fields. It flags **1,288 purchases/skill points without a player ID**, **62 deaths without a player killer** and **23,610 tower plates outside the old index**. Exact transcription does not prove that Faker saw an event or explain his decision.

![Live Corpus audit with exact event counts and source caveats](docs/figures/dashboard_event_validation.png)

![Faker episode retrieval challenged against a simple rule and Shadow IoC](docs/figures/faker_memory_challenge.png)

The new [Faker Memory](FAKER_MEMORY.md) keeps **10,038 training decisions** as private state→next-move episodes. A match-disjoint calibration chooses a retrieval policy, then the 46 reused validation matches challenge it: **11.53%** exact next 8×8 region, behind the role/phase rule (**15.29%**) and Shadow IoC (**17.41%**). Its nearest example gets **0%** exact 512×512 cells. The Challenge tab includes an anonymous case quiz with revealable observed destinations; browser answers do not retrain anything. This is an inspectable memory and a measured failed challenger, not an LLM fine-tune or evidence of 90% prediction.

![Interactive Faker Memory quiz with live validation scores](docs/figures/dashboard_faker_memory.png)

Rebuild from local raw caches with **one command**: `.venv/bin/python scripts/run_ioc_challenge.py`. It tests five games first, resumes per-game outputs, validates event transcription, trains matched ablations, updates the aggregate figures and the local replay. [Matrix schema, causal rule and next evidence gate](IOC_VISION.md) · [exact scores](RESULTS.md#item-aware-index-of-context--development-only-2026-10-10).

![Compose five hypothetical bot players and observe the abstract opponent response at minute 15](docs/figures/dashboard_challenge_custom.png)

The Challenge tab now lets a reader assign all five hypothetical players to any of four zones and watch a declared opponent-response rule at each five-minute tick. The 5-bot screenshot shows the resource and coverage cost in **arbitrary, uncalibrated units**. [Simulation assumptions and playable evidence gate](GAME_THEORY_LAB.md#interactive-five-role-composition-with-explicit-opponent-response).

### New: more games, a faster prediction target

![Separate game domains, ten-second event frequencies and validation scores](docs/figures/corpus_event_clock.png)

The latest refresh still returns **465 usable KR ranked timelines**. A historically attributed EUW Worlds 2024 alias adds **31 ranked timelines**; a public, unverified and partly stale professional-data mirror adds **671 match summaries without trajectories**. The database now distinguishes these sources instead of treating all **1,167 game records** as equivalent. A second model predicts the **first macro event in the next 10 seconds** from the latest frame and past events: **73,482 KR windows**, plus **5,383 EUW training windows**. On 46 KR validation matches, its log loss is **1.3847** with EUW auxiliary training versus **1.4472** for a train-only phase rule. This is event prediction, not 10-second Faker position tracking; the original exact 512×512 position result remains unchanged. [Evidence, aliases, scientific basis and caveats](DATA_EXPANSION.md).

Run the new expansion from a prepared local pipeline with one command: `.venv/bin/python scripts/run_expansion.py`. It caches Riot and CSV inputs, pilots five games first, trains both event variants, builds the separate [Faker/team matrix](TEAM_MATRIX.md) and renders aggregate figures. The pro CSV mirror never enters the event model.

Next evidence gate: [matched replay alignment, rare-event detection and player-visible evaluation](NEXT_RESEARCH.md). The role-context ablation is complete.

![Whether role-distance features improve the ten-second event model](docs/figures/event_context_ablation.png)

An equal-capacity ablation on the KR development split found **no gain** from the current minute-spaced ally/opponent distance proxies for the ward-heavy ten-second event target. The full model scores **F1 = 0** on Faker kills, Faker deaths and objectives: global accuracy mostly reflects wards. That result does not establish the roles' strategic importance; [see the numbers and limits](NEXT_RESEARCH.md#first-completed-experiment-role-context-ablation).

```mermaid
flowchart LR
  A["Now: 465 KR timelines<br/>positions ~60 s"] --> B["One matched Faker replay<br/>verify clock and map alignment"]
  B --> C["Five-game pilot<br/>positions + visible context"]
  C --> D["New match-level split<br/>10-second spatial baseline"]
  A --> E["Existing event clock<br/>rare-class precision / recall"]
  E --> F["New prospective event cohort"]
```

The [site's research panel](#visual-dashboard) plots **all nine event classes**, including the 3,934 ward-placement targets out of 7,480 KR validation windows. It loads only [published aggregates](docs/data/public_event_ablation.json). A replay pilot needs an authorized matched file; no such replay has been acquired yet.

**Measured status:** 465 usable ranked matches and 12,510 observations were collected from the available 470 match IDs. The selected model predicts the exact next 16×16 region in 11.28% of held-out test observations, versus 11.61% for a train-only role/phase prior. The requested clear exact-region baseline win has **not** been demonstrated. An exploratory pooling of predictions into 8×8 and 4×4 macro regions shows a positive signal that requires a fresh confirmatory test. Purchases and skill upgrades exceed their no-event baselines after validation calibration. Exact figures and limits are in [RESULTS.md](RESULTS.md).

### New: predicting the kind of move

![Four same-capacity models with Faker-only, team, visibility proxy and global timeline fields](docs/figures/hierarchical_ablation.png)

A separate **development-only** policy predicts a coherent broad-to-fine destination and whether the account stays nearby, returns to base, approaches Dragon/Baron, or makes another observed move. The `x` proxy plus global timeline fields reaches **17.49%** next-region accuracy at 8×8 versus a **15.29%** simple role/phase rule on 46 validation games. Removing the global resource fields yields **16.86%**, with no reliable paired difference. The match-level interval for the gain over the simple rule still includes zero, and the same validation set chose the model and calibration. Its five-class macro F1 is **44.9%** versus **16.5%** for always choosing the common class, but reset detection remains weak. The enemy positions in both variants are a heuristic last-seen proxy, not complete oracle positions or Faker POV. [See the full ablation and limitations](RESULTS.md#new-development-experiment--a-decision-shaped-shadow-2026-10-10).

![How much of the map a model must name to cover 90% of observed destinations](docs/figures/predictability_gap.png)

The exact next **one** of 64 broad cells remains **17.49%**. On this already-used validation set, naming **41 of 64 cells** reaches **90.12% coverage**—an answer covering **64.1% of the map**, not 90% exact accuracy. The 8×8 exact score falls to **7.5% after minute 20**. An independent current-position audit found no saved-cell misalignment across train and validation. [Read the visibility and predictability audit](VISIBILITY.md).

A targeted three-head model for early, middle and late game was also trained. It scored **16.39% overall and 5.91% late**, below the simpler model's **17.49% overall and 7.53% late**; it was kept as a documented negative experiment. This is why the next work focuses on better observation and fresh matches, not a larger phase head.

### A 512×512 atlas and its accuracy limit

![Observed and predicted next-minute destinations across the 512×512 validation grid](docs/figures/atlas512_validation.png)

The new atlas uses **512×512 actual spatial cells**, or 262,144 possible destinations. It is not an enlarged 64×64 image: a 25,280-parameter conditional head selects one of 64 subcells inside a frozen 64×64 parent, then combines the parent and subcell at inference. A five-game pilot checked label alignment before full training. The **46-match / 1,275-transition development validation** shows **0.00% exact-cell accuracy**, versus **0.63%** for copying the current position and **0.31%** for the most frequent training cell. Shadow lands within 16 fine cells in **8.94%** of transitions, versus **7.29%** for copying. The paired match-bootstrap 95% interval for exact-cell gain over the best simple baseline is **−1.04 to −0.32 percentage points**. This candidate is not promoted; its historical test split and the future-game lockbox were not scored. A fine cell is about 29 map units wide, while observations remain roughly one minute apart.

![Smoothed, privacy-preserving geography of ranked match events on the 512×512 canvas](docs/figures/atlas512_events.png)

The local interactive atlas keeps sparse 512-cell counts for destinations, ten-player positions and events from the 465 ranked games. The public event figure first groups rare events into **16×16 coarse bins**, hides bins with fewer than three events, then smooths them for display. It does not expose exact rare-event coordinates. The downloadable repository contains only aggregate scores and figures; raw games, sparse local atlas, weights and per-game traces stay outside Git. [Full 512 experiment and limits](RESULTS.md#512512-development-atlas-and-prediction).

### A higher resolution, but harder question: the 64×64 archive

![Observed and predicted next locations in a 64×64 historical map](docs/figures/grid64_observed_vs_predicted.png)

The new **64×64** candidate scores **1.09% exact cell** on 1,197 previously inspected test decisions; the strongest simple baseline scores **1.92%**. Within four cells, Shadow scores **22.89%** versus **16.88%** for copying the current location. A validation-calibrated prediction set covers **91.9%** of actual test destinations, but contains **1,791 of 4,096 cells on average: 43.7% of the entire map**. This is uncertainty disclosure, not 90% pinpoint accuracy or stronger play. No result in this historical set is prospective confirmation.

![64×64 atlas of observed match events](docs/figures/event_atlas64.png)

The event atlas distinguishes Faker kills and deaths, allies, opponents, Dragon, Baron, Herald, Void Grubs, buildings and wards. Events without positions remain counted but unplaced. A separate local state warehouse holds **12,975 frames, 12,510 transitions and 353,409 indexed events** across the 465 ranked games, with all ten players at each frame. The dashboard follows one game's ten-player ecosystem in an isometric **3D projection** and displays a Faker-centred transition matrix and an anisotropic adjacent-cell field. Its 13 enemy-reaction and ally-cover variables are also **inputs to a separate training candidate**, not merely decoration. That candidate scores **8.71% exact 16×16 on validation**, below the frozen model's **10.59%**, so it is not promoted or tested. Read [STATE_ECOSYSTEM.md](STATE_ECOSYSTEM.md), [DESIGN.md](DESIGN.md) and the measured [RESULTS.md](RESULTS.md).

![Enemy proximity around Faker, with phase and score context](docs/figures/enemy_pressure.png)

The account's **519 all-queue IDs** include the same 470 ranked-solo IDs plus **49 different-mode matches**. Those 49 timelines were cached locally but were not added to the ranked training set or relabeled as new ranked evidence. The first fresh ranked snapshot still contains **0/100** eligible new games for the frozen prospective test. Expanding to hundreds or thousands of comparable decisions requires verified new games or a separately sourced domain, never invented samples. [Roadmap and acquisition gates](ROADMAP.md).

### The landscape of next moves

![Three-dimensional comparison of observed and predicted map-cell frequencies](docs/figures/probability_surface_3d.png)

The horizontal plane is the **16×16 legacy map grid**; bar height is the **share of next-minute locations** in a cell, aggregated over 46 historical test matches. It is not game terrain, an individual replay, or a set of counterfactual futures. The model's dominant central spike is a measurable failure mode, not a discovered strategy. The [interactive local dashboard](#visual-dashboard) lets you rotate an isometric version, inspect cells, scrub team tempo, and replay one held-out match minute by minute.

### Faker on the map, Shadow on the map

![Observed next-minute locations beside Shadow Faker's predictions](docs/figures/faker_vs_shadow_minimap.png)

In the historical test, the account's next position lands in the most common cell **11.28%** of the time. Shadow predicts that same cell **39.43%** of the time. This visible overconcentration is one reason the exact-region baseline remains hard to beat. These are aggregate distributions from 46 matches, not a single game replay or player POV. [Read the map and diagnosis](RESULTS.md).

### What we score

![Model versus strongest baseline at three map scales](docs/figures/benchmark_scales.png)

The 8×8 and 4×4 gains were examined **after** the old test was seen. They suggest a direction; they are not a new independent win. The [prospective protocol](BENCHMARK_PROTOCOL.md) freezes that question for future games. Its first refresh found **0 of the required 100 new matches**.

## The project at a glance

```mermaid
flowchart LR
    A[KR ranked solo IDs] --> B[Cached match + timeline]
    B --> C[One-minute causal states]
    C --> D[Only Faker's next action]
    C --> E[Allies, enemies, objectives as context]
    D --> F[Transformer: region, item, skill]
    E --> F
    F --> G[Match-split baselines + visual replay]
    G --> H[Future-game lockbox: pending 0/100]
```

The model asks **where this account moves next**, given the evolving game and team positions. The additional movement tags describe approaches toward allies and objectives; they do not measure intent or prove that a rotation helped win.

![Five-minute tempo of observed movement toward allied roles](docs/figures/team_tempo.png)

The lines follow *observed* movement toward jungle, bot carry and support in five-minute bins. They are not estimates of a teammate's fixed contribution to winning. For the broader phase view and top-lane comparison:

![Observed movement toward allied roles by game phase](docs/figures/role_approach_by_phase.png)

### A radical formation needs evidence

![Allied clustering near the bot carry in early, middle and late game](docs/figures/team_clustering.png)

Only **one early minute in one match** places all five allied champions within 2,500 units of the bot carry. This proximity audit cannot tell whether a deliberate five-bot lane would work; it says the current corpus gives almost no examples of that shape. [GAME_THEORY_LAB.md](GAME_THEORY_LAB.md) turns unconventional strategies into testable questions with explicit costs and played-game evidence.

The public figures and README banners use [published aggregate counts and metrics](docs/data/public_summary.json), so they can be read without downloading or distributing Riot match data. Regenerate the original figures with `.venv/bin/python scripts/render_results.py --from-summary`, the model ablation with `.venv/bin/python scripts/render_hierarchical.py --from-summary`, and the 90% coverage audit with `.venv/bin/python scripts/render_predictability.py --from-summary`. The 512 event/destination figures require the ignored local atlas: `.venv/bin/python scripts/render_atlas512.py`.

## Visual dashboard

Run the local dashboard after setup, then open [http://127.0.0.1:8008/](http://127.0.0.1:8008/). It shows the **observed account, Shadow and evidence side by side** in French or English. It uses the published aggregates for its public views. If the full pipeline has run, a held-out match replay and GIF are served locally from ignored files.

Opening [dashboard/index.html](dashboard/index.html) as a `file://` page now acts as a **launcher**: it redirects to the running local server or displays the start command. The interactive dashboard needs that server for its allowlisted aggregate JSON and optional private replay. The research panel explains the current rare-event failure and links the next evidence protocol.

```bash
.venv/bin/python scripts/serve_dashboard.py
# Optional: generate the local minute-by-minute replay before opening the page.
.venv/bin/python -m shadowfaker.demo --max-frames 30
```

The dashboard server binds to `127.0.0.1` and serves an allowlist of public visuals plus optional local replay files. A sticky **shared timeline** lets you scrub minute 0–39 with a slider, keyboard or mouse wheel over the slider. It synchronizes the local **512×512 atlas**, sparse 3D frequency surface, five-minute team tempo, opponent pressure, one-game replay and synthetic scenario cursor. The colour key travels with the timeline. Atlas and surface show **phase aggregates** (0–10, 10–20, 20+ minutes): the 512 observed/modelled destinations use 46 **validation** games (460, 443 and 372 transitions by phase), while player/event layers use 465 ranked games. If the local 512 atlas is absent, the page labels its 64×64 historical fallback. The replay shows **one selected game with the legacy 16×16 model**, sampled about every minute; it stops at that game's final frame. The local metric field remains an explicitly labelled 64×64 historical view. Fixed historical score figures remain labelled as such rather than pretending to change with the slider.

The score section now includes an **8×8 development validation** panel: exact-cell accuracy, the map area needed for 90% candidate-set coverage, and three candidate models by game phase. Its bars respond to the shared timeline. Its **46 validation matches are separate from the 46 historical test matches** shown in the atlas.

The dashboard can open any **locally indexed ranked game** by match ID and search 930 locally generated English/French summaries plus separately sourced multilingual case studies. A private end-of-game card accompanies the selected replay. [Riot Data Dragon](https://developer.riotgames.com/docs/lol#data-dragon) supplies the champion/item static sprites and bilingual item names; the pinned atlas version is described in [CORPUS.md](CORPUS.md). The replay remains local and is excluded from Git. [Dashboard source](dashboard/), [reproducible aggregate renderer](scripts/render_results.py), and [research evidence](RESULTS.md) are in the repository.

## Where 470, 465, and 12,510 come from

```mermaid
flowchart LR
    A[470 match IDs returned<br/>KR ranked solo, queue 420] --> B[5 remakes under 5 min removed]
    B --> C[465 matches with timelines]
    C --> D[12,510 adjacent one-minute frame pairs]
    D --> E[12,510 states at t → account actions at t+1]
```

The API returned **470 IDs in five pages** (100 + 100 + 100 + 100 + 70) for this PUUID at the 2026-10-09 snapshot. It did not provide 1,000 games, and this number is not a claim about every game Faker has ever played. The collector checked queue, account, region, duration and timeline for each ID. Five games lasted under five minutes; none of the other 465 lacked a usable timeline. For each remaining game with `F` timeline frames, parsing made `F − 1` one-minute examples: the state at one frame predicts the account's position, first purchase and skill upgrade in the next. Summed across games, this is **12,510 candidate pairs**, and no target position was missing in this corpus. Each game contributes 13–47 examples (median 27). The eight-frame input window is left padded near game start, so it does not discard early pairs. These observations are correlated within a match; evaluation splits and uncertainty calculations therefore operate by **match**.

## One-command run

Requires macOS Apple Silicon, Python 3.11+, and a current Riot development key. The validated local environment uses Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -e .
cp .env.example .env
# Set RIOT_API_KEY in .env to the current Riot developer key.
# Full five-game pilot → ranked pipeline → 64×64 and 512×512, ten-player warehouse,
# interaction training, validation, vectors, summaries, charts and replay:
.venv/bin/python scripts/run_next_level.py --limit 1000 --epochs 25
```

If `pip` is unavailable in the virtual environment, use `uv pip install --python .venv/bin/python -r requirements.txt -e .`. The base ranked pipeline validates **every stage on five games first**, then collects all available games up to the target, parses, analyzes, trains, selects on validation, evaluates on held-out test games, and exports a GIF. JSON and match-level NPZ files are cached; rerun the same command after a crash or key renewal. For a five-game base smoke run: `.venv/bin/python scripts/run_pipeline.py --limit 5 --epochs 3`.

`run_next_level.py` also works as the one-command entry point on a fresh checkout: it invokes the base pipeline if the ranked dataset or checkpoint is missing, then validates its new stages on five games and builds the full local research extension, including the item-aware IoC experiment. After the 64×64 parent exists, it pilots the 512 adapter on five games before full training and validation. A rerun reuses matching checkpoints and cached source data. Its 512, interaction and IoC candidates are scored on validation only; its 64×64 historical test report is explicitly marked as previously inspected. The local text index and per-game media are ignored by Git. Use `--pilot-only` to check the base extensions on five games without scaling.

To refresh just the **private ranked cards, search index, local sprites and aggregate corpus ledger** from existing caches, run `.venv/bin/python scripts/refresh_catalog.py`. This runs the five-game pilot first and leaves model checkpoints alone. The static Data Dragon art requires CDN access only when its ignored local cache is empty.

Use `--game-name "Name" --tag-line TAG` for another account, with a separate `data/raw/` directory if its PUUID differs. The collector uses the `asia` route for KR, filters queue 420 (ranked solo), skips remakes shorter than five minutes and missing timelines, and paginates without duplicates. A persistent 1.3-second interval between requests respects the 100 requests per two minutes development quota. It also handles `Retry-After`, backoff, timeouts, and clear 401/403 key errors. At two requests per match, 1,000 games require **at least about 43 minutes**, excluding pagination and retries. The actual account history may contain fewer.

## Next level: frozen macro benchmark

The current model and development split are frozen under [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md). The primary future metric is 8×8 next-region accuracy versus four frozen baselines, with a match-level confidence interval. The original 16×16 metric remains separately reported. The lockbox requires **100 genuinely new Faker-account ranked matches** after the frozen cutoff; it returns `pending` before then and scores once. On the first live refresh on 2026-10-09, there were **0/100** new matches.

```bash
.venv/bin/python -m shadowfaker.macro_actions --limit 5
.venv/bin/python -m shadowfaker.macro_actions
.venv/bin/python scripts/run_prospective.py --offline
# Use a new snapshot name for a fresh match-ID listing; reuse it to resume a crash.
.venv/bin/python scripts/run_prospective.py --snapshot 20261010
```

The macro-action parser adds eight **observable movement proxies**: moving toward allied jungle, bot, support, mid or top, toward a live Dragon/Baron pit, or back to base. Missing player positions are masked. These are labels about where Faker moved, not verified intent, communications, assistance or causal contribution to winning. See [ROADMAP.md](ROADMAP.md) for the hierarchical-model and stronger-play milestones. A newly trained model needs its **own** future lockbox; it cannot replace the current frozen candidate.

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
- [ROADMAP.md](ROADMAP.md) and [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md): next-level milestones and the frozen prospective test.
- [GAME_THEORY_LAB.md](GAME_THEORY_LAB.md): a falsifiable research path for unusual formations and stronger played-game strategies.
- [DIAMOND.md](DIAMOND.md): a multi-facet model of Faker's decision space, observability, and the route to sub-minute study.
- [STATE_ECOSYSTEM.md](STATE_ECOSYSTEM.md): ten-player state matrix, enemy-response training channels, vector index, and geometric field.
- [DESIGN.md](DESIGN.md): fan-made six-star visual system, responsive tabs and how to read the two 3D projections.
- [WORLD_FINALS.md](WORLD_FINALS.md): six winning Worlds finals, 25 games and three landmark semifinals with per-game sources.

Professional LCK/Worlds games and ranked solo queue differ in roster, draft, communications, and incentives. Any future joint training must identify the domain and report separate held-out results. Reddit/X interpretations and translations are hypotheses until checked against match-specific evidence. No video, voice, or social-media text is silently treated as a numeric label.

Timelines sample roughly every 60 seconds. They miss instant reactions, exact fog of war, ward positions, cooldown details, pings, voice, and Faker's own screen. One-step cloning does not test accumulated errors in full games, micro play, or strength against opponents. The outcome head predicts state–result association, not an action's causal value. Objective respawns are approximated and may vary by patch.

Raw Riot JSON, processed samples, models, runs, artifacts, and `.env` are excluded from Git. **Do not redistribute Riot raw match data.** Use is local/personal research subject to Riot's applicable terms. Source documentation: [Riot API reference](https://developer.riotgames.com/apis), [developer portal limits](https://developer.riotgames.com/docs/portal), and [Replay documentation](https://developer.riotgames.com/docs/lol). Repository code follows its AGPL-3.0 license.
