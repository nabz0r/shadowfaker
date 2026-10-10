# Event validation: what the Riot timeline actually says

![Raw events, exact local rows and categories outside the old index](docs/figures/event_validation.png)

The source is the cached [Riot match-v5 timeline](https://developer.riotgames.com/apis#match-v5/GET_getTimeline), not a build guide, search snippet or broadcast interpretation. `scripts/validate_events.py` runs a five-game gate and then independently classifies every raw event in the **465 usable KR ranked games**. It joins each indexed row back to `(match, frame index, event index)` locally and checks its timestamp, category, grid cell, actor, victim, item and skill fields. The public [aggregate audit](docs/data/public_event_validation.json) contains no match IDs or raw event payloads.

| Question | Audited result | Meaning |
|---|---:|---|
| Raw timeline events | 563,198 | All Riot event types, including metadata and events intentionally outside the old warehouse |
| Events in the existing warehouse | 353,409 | Exact row-for-row transcription: **353,409 / 353,409**, zero parsing failures or classifier disagreements |
| Indexed events with coordinates | 33,329 | Event loci, not player positions or Faker's point of view |
| Indexed purchases / skill points without a player ID | 930 / 358 | Actor 0 in the source; event is present but cannot be attributed to Faker or another player |
| Champion deaths without a player killer | 62 | Three victims are Faker and remain `faker_death`; 59 others are outside ally/enemy **kill** labels |
| Tower plates outside the older index | 23,610 | Real timestamped Riot events, not yet a model class or causal feature |

The **209,789** events outside the older SQLite event index are accounted for by raw type. Of these, **119,033** are item sales, destruction and undo events that *do* feed the later event-derived inventory proxy; **61,494** are `LEVEL_UP`, **23,610** tower plates, **3,556** `CHAMPION_SPECIAL_KILL`, and **2,096** other metadata or excluded events. `CHAMPION_SPECIAL_KILL` describes a special kill condition, not an extra champion death to double-count. The raw-to-index difference is a deliberate selection, not 209,789 lost JSON records.

## Status has three separate meanings

1. **Transcription:** all 13 indexed categories reproduce their raw fields exactly. This catches parser drift and missing rows; it does not prove the event's strategic interpretation.
2. **Attribution:** a nonzero actor ID is required before assigning an event to a player. The 1,288 source events with actor 0 remain unattributed. For building/objective events, a missing killer ID can be normal; team/objective fields are kept distinct.
3. **Visibility and location:** champion-kill coordinates are the event/victim locus, objective coordinates the monster locus, and building coordinates the destroyed structure. Wards and purchases in this corpus have **no coordinates**. Riot's spectator timeline can show things Faker never saw.

The [inventory audit](IOC_VISION.md) is separate: exact event transcription does **not** make the reconstructed held-item set exact. Only 29.05% of final actor item-ID sets match the post-game list. Current item channels are a causal proxy with known omissions.

`TURRET_PLATE_DESTROYED`, `LEVEL_UP` and other excluded types are now explicit **candidates** for a later IoC revision. Adding one requires a patch-aware definition, a five-game pilot, a train-only feature rebuild and an evaluation on match-disjoint data. No existing model result was quietly reinterpreted or retrained in this audit.

Reproduce locally after building the warehouse:

```bash
.venv/bin/python scripts/validate_events.py
.venv/bin/python scripts/render_event_validation.py
```
