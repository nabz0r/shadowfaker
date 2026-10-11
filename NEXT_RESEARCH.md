# Next research gate: observe the game that Faker could act on

**M20 evidence atlas (2026-10-11):** the [visual 90% roadmap](MODEL_90_ROADMAP.md) now puts train/validation Faker-label prevalence beside the age of each sampled position, then defines the next measurable gates. The five-game pilot and all 465 ranked games are accounted for; these descriptive charts do not create a new model score. The rare-event and replay experiments below remain the next sources of progress.

**M16 update (2026-10-11):** The cached-data branch now trains a separate [Faker-attributed 10-second event model](FAKER_ACTIONS.md) after a five-game pilot. It improves historical validation log loss and per-class average precision over train-only phase rates, but kill-outcome AP remains 7.67%. This completes the initial rare-event measurement below, without unlocking sub-minute positions, player vision, a future-game confirmation or a better-playing policy. Replay alignment and a new independent cohort remain the leading gates.

Status: 2026-10-10. This is a source audit, work plan and completed development ablation. The current ranked corpus has 465 usable KR timelines with player positions about once a minute. The separate ten-second target predicts the first event **type**, not Faker's ten-second position, click, vision or contribution to a win. The exact 512×512 spatial candidate scored 0/1,275 on development validation. Increasing its grid or parameter count without new observations does not solve that measurement gap.

## Ranked priorities

| Priority | Research question | First falsifiable pilot | Gate to scale |
|---|---|---|---|
| 1. Replay resolution | Can a legally available, patch-compatible `.rofl` from a **matched Faker game** yield reliable ten-second positions of all ten players and ward locations? | On one matched game, compare replay coordinates at each Riot minute anchor, inspect identities, time offsets, missing intervals and event/ward alignment. Keep raw files local. | Five matched games with documented patch, match ID, source perspective and a prespecified alignment-error report; then build a new match-level split and 10-second spatial baseline. No click or player vision label is inferred from spectator coordinates. |
| 2. Observable context | Which jungle, support, bot and opponent cues add information beyond game phase and past events? | **Completed:** equal-capacity masks of allied, enemy and jungle/bot/support distances on the same KR train/validation matches and seed. | The existing distance proxies showed no useful gain. Next test rare-event detection with class-specific precision/recall and early/mid/late slices. Promote only after a fresh cohort; global accuracy is dominated by ward events. |
| 3. Perspective | How much does spectator knowledge exaggerate macro predictability? | For each verified replay/POV, tag whether an opponent was visible to Faker's team at `t`, with uncertain cases explicit. | Compare player-visible, timeline proxy and omniscient inputs on the **same** held-out games. Video broadcast or team voice must never be relabelled as Faker POV or communication. |
| 4. Agency and outcomes | Does a candidate action improve the next state or merely resemble Faker? | Specify a fixed-seed, legal-action, opponent-response scenario protocol inspired by [When Agents Rule](https://github.com/asp67/when-agents-rule), with per-turn JSONL state/action/result and latency. | Only a calibrated playable environment or matched real-game trials can support a winning-strategy claim. Synthetic formation curves remain hypotheses. |

## Source audit and decision

The [six-final / 25-game professional catalogue](WORLD_FINALS.md) and three landmark semifinals provide **specific replay candidates and source links** for this gate. Their public game summaries have no Faker coordinates or player-visible state. The local text index keeps those facts searchable in French and English without mixing them into the 465 KR ranked training trajectories. A selected professional game must still pass the replay identity, clock and visibility checks above before it can contribute labels.

- [Riot Replay API](https://developer.riotgames.com/docs/lol) controls playback and recording of a replay **already open in a local game client**. It does not provide a historical `.rofl` download by match ID. [Riot's replay FAQ](https://support.riotgames.com/fr-fr/league-of-legends/gameplay/replays-faq-pro-tips/) says client replays last one patch and only a limited recent history is available. No `.rofl` was found in the local Downloads/Documents check; the existing [feasibility audit](REPLAY_FEASIBILITY.md) also found no local LoL client. Hence a current Faker replay is an acquisition gate, not a hidden property of match-v5.
- [Mowokuma/ROFL](https://github.com/Mowokuma/ROFL) claims one-second champion positions and ward position/duration from replay files. The repository is archived and demonstrates a Windows executable; compatibility with a current patch and Apple Silicon has **not** been established. Treat it as a schema/prototype reference, not a validated dependency. Its code license and Riot usage conditions must be verified before reuse.
- [TLoL](https://github.com/MiscellaneousStuff/tlol) reports four observations per second in older, mostly early-game datasets, with large storage and an incomplete conversion success rate. Those games are neither matched Faker observations nor evidence for modern patches. Its scraper uses Windows process-memory tooling, so it is not an immediate macOS path.
- The [Riot/GRID professional data page](https://riotesportsdata.com/en-us/league-of-legends/) lists live positions, objectives and A/V feeds, but currently describes those products as commercial; LCK data is listed for media purposes only. A non-commercial portal is described as upcoming. The local 671 pro summaries therefore remain **metadata**, with no invented movement labels.
- [AlphaStar Unplugged](https://arxiv.org/abs/2308.03526) supplies the useful pattern of a standardized offline dataset, behavior-cloning baseline and evaluation protocol in a partially observable multi-agent game. [COMA](https://arxiv.org/abs/1705.08926) shows a research route for multi-agent credit assignment, but its counterfactual actor-critic requires an environment and action-level feedback that our timelines do not provide. Neither paper licenses a causal claim from observed Faker rotations.

## Decision rule

The role-geometry ablation below is complete. Seek one matched, authorized replay or player-view recording and prove temporal/spatial alignment **before** scaling extraction. In the existing corpus, a separate rare-event detector is the next falsifiable model experiment; measure each event type rather than reporting only global accuracy. If the replay pilot fails, invest in prospective collection and player-visible annotation rather than denser labels invented from one-minute positions. Keep the frozen 100-new-KR-match spatial lockbox and any future ten-second-event lockbox separate.

## First completed experiment: role-context ablation

![Equal-capacity masks around Faker](docs/figures/event_context_ablation.png)

The five-game pilots passed, then four models of **22,537 parameters** each were trained on the same **373 KR matches** and compared on **46 KR validation matches / 7,480 windows**. Masking is applied in both training and validation; all model inputs retain time, own state and prior events. Results are in [aggregate JSON](docs/data/public_event_ablation.json). Positive gain means the full model benefited from the removed inputs.

| Masked at training and validation | Validation log loss ↓ | Full-model gain, 95% match bootstrap |
|---|---:|---:|
| None, full context | 1.3923 | reference |
| All six allied distance channels | **1.3903** | −0.0020 [−0.0032, −0.0009] |
| All six enemy distance channels | 1.3914 | −0.0009 [−0.0026, +0.0008] |
| Six jungle/bot/support role distances across both teams | 1.3919 | −0.0004 [−0.0018, +0.0009] |

The distance proxies have **not** shown a useful gain for this particular ten-second event target. That is a finding about our proxy features and ward-heavy objective, not evidence that jungle, bot, support or opponents do not matter to Faker's decisions. The same validation set was used during earlier model development, so even the interval excluding zero for allied distances is exploratory. No masked model is promoted, and the historical test and prospective spatial lockbox remain unread. The next useful measurement is actual visibility and denser matched trajectories, plus event-specific rather than global-ward metrics.

**Failure mode made visible:** 3,934 of 7,480 validation windows (52.6%) have `ward_placed` as their first marked event. The full model's F1 is **0** for Faker kills, Faker deaths and objectives, despite 119, 90 and 135 such labels. Its ~54% overall event accuracy therefore cannot be read as strategic foresight. The next event experiment should report class-specific precision/recall, calibration and match-level uncertainty for these rare targets, ideally with an explicit choice to abstain.

The [dashboard research gate](dashboard/index.html) now renders the nine class counts and F1 scores directly from [aggregate JSON](docs/data/public_event_ablation.json). It labels the cohort as the **KR-only** model and the next replay/visibility steps separately from measured results. Open it through the local server described in the README; opening the HTML file directly acts only as a launcher. No per-match scores or raw Riot data are served by this panel.
