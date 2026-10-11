# Pressure around Faker: a selectable measurement zone

![The measured pressure panel with its radius diagram, units and phase bars](docs/figures/dashboard_pressure.png)

This panel asks a precise question: **how many opponents had a known Riot timeline position within a chosen radius of the account at a sampled frame?** It does not measure enemy intent, a spell spent, team communication, what Faker could see, or whether Faker caused an opponent to move. The ten-player replay shows individual observations; this chart aggregates the **465 usable KR ranked games**.

The user chooses a radius of **1,000, 1,500, 2,500, 3,500 or 5,000 map units**. The approximate width of the game map in these normalized data is 15,000 units. The square/circle illustration is a scale diagram, not a match replay. Each choice loads counts recomputed directly from player positions. The shared game clock selects early (0–10), middle (10–20) or late (20+) minutes; phase bars remain averages over the same games, not a second-by-second time series.

| Quantity | Definition | Unit |
|---|---|---|
| Nearby opponents | Number of enemies with known position at Euclidean distance ≤ radius, averaged over frames with Faker position | Enemy players per frame, 0–5 |
| Observed entries | Enemy has known positions in consecutive frames, outside the circle first and inside second | Net entries per frame; exact entry second unknown |
| 0/1 and 0/2 slices | Frames when Faker's cumulative kill/death score is exactly 0/1 or 0/2 | Frames and average nearby opponents |

At **2,500 units**, mean nearby opponents are **0.88** early, **1.15** middle and **1.75** late. At **1,000 units**, they are **0.37**, **0.36**, **0.53**; at **5,000 units**, **1.58**, **2.06**, **3.03**. These changes reflect the zone definition and team grouping over time. They are not model predictions or a causal effect of Faker. Full numerator, denominator and five-radius values live in [the public aggregate](docs/data/public_pressure.json).

The calculation excludes first-frame entries and frames with a missing Faker location; an enemy whose previous position is missing cannot create an entry. A known opponent may move out and back between minute frames without that path being visible. The score slices mix different minutes, opponents, champion picks and match states. Comparing 0/1 with 0/2 therefore cannot establish that Faker deliberately absorbs pressure or converts it into a team advantage. A causal study would need player-visible evidence, counterfactual controls and an independent match cohort.

Recompute after the state warehouse exists:

```bash
.venv/bin/python -m shadowfaker.pressure
```

The script reads one match at a time from the ignored local SQLite warehouse, then publishes only aggregate counts. Its five-game pilot and full 465-game run are logged in [PROGRESS.md](PROGRESS.md). [Corpus provenance](CORPUS.md) · [Research roadmap](ROADMAP.md).

## One observed game beside the aggregate pressure curves

The Pressure tab now pairs the population curves above with **one selected game's** ten player positions at the shared minute. Its background is Riot Data Dragon minimap art pinned to version 16.20.1, while champion portraits and the distance circle come from the selected frame. The art is not a historical patch capture. The map highlights actors inside the chosen radius; the roster shows champion, role, distance, level and item IDs inferred from events at that minute. Filters independently show Faker, allies, enemies, lanes, item icons, the circle and a role. The same overlays appear on the 512×512 atlas and the projected 3D frequency surface, where the item toggle shows a small Faker tracked-item count. A background density always aggregates multiple games; overlay points always come from **one** game. When the global slider extends beyond that game's last frame, the readout explicitly says it is showing the last available frame. [Visual evidence guide](VISUAL_SYSTEM.md).

The complete enemy dots in the UI are **Riot oracle positions**, not a reconstruction of what Faker saw. The item icons/counts are an incomplete event-derived proxy, with [29.05% exact final item-ID sets in a retrospective audit](docs/data/public_ioc_quality.json). The model's item input uses a separate last-seen proxy for enemies; even that proxy is not real fog of war. Proximity does not measure spells spent, attention, team communication or causal pressure drawn. See [the feature and source matrix](IOC_VISION.md).
