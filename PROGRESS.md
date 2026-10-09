# Shadow Faker — journal d'avancement

## 2026-10-09

- [x] Phase 0 : plan, architecture, invariants et risques consignés.
- [x] Prévol : `/Users/n/shadowFaker` était vide ; `nabz0r/shadowfaker` existe sur GitHub avec `main` comme branche par défaut et les droits d'écriture.
- [x] `.env` ajouté localement par l'utilisateur, ignoré par Git et protégé en mode `600`. La première clé a reçu HTTP 401 ; la clé renouvelée a ensuite reçu HTTP 200 après un délai d'activation.
- [x] Phase 1 : Python 3.12 virtuel créé, dépendances épinglées et installées ; structure `src/`, `data/`, `models/`, `scripts/` définie, configuration centralisée.
- [x] Client Riot et fetch implémentés avec pacing persistant, cache atomique, pagination, filtrage queue 420 / remakes / timeline, reprise, retries, 429 et erreurs de clé.
- [x] Phase 2 sur cinq parties : account-v1 résout exactement `Hide on bush#KR1`, cinq matches `KR_` ranked solo avec match et timeline récupérés, aucun remake dans cet échantillon.
- [x] Phases 3 à 7 : parseur causal, split par match, chargeur limité à deux matches, transformer d'environ 525 000 paramètres (selon vocabulaire d'items), benchmark MPS/CPU, entraînement et arrêt anticipé, baselines et démo GIF implémentés.
- [x] Validation hors ligne : `pytest -q` passe (4 tests), dont un cycle complet avec cinq parties synthétiques, reprise du parse, entraînement, évaluation et GIF. Cela ne constitue pas une mesure sur Faker.
- [x] Phase 8 (documentation) : README de setup, sorties, limites et sources ; `PLAN.md` et ce journal.
- [x] Phases 3 à 7 sur cinq parties réelles : parsing réussi, 23 observations pour le match test, checkpoint et GIF produits. Top-1 région 0,0435 ; meilleure baseline 0,0870. Cette taille ne permet pas de conclusion ; collecte cible lancée.
- [x] Benchmark mini-époque sur cinq parties réelles : CPU 0,034 s, MPS 1,513 s ; sélection CPU conformément au benchmark.
- [ ] Collecte cible `--limit 1000 --epochs 25` lancée. Journal local `data/pipeline.log`, exclu de Git.

## Checklist explicite

- [x] 429 + `Retry-After`, backoff et message de clé expirée ; tests simulés.
- [x] Pagination d'IDs dédupliquée ; test simulé.
- [x] Champs timeline facultatifs tolérés ; un match impossible à parser est journalisé et les autres continuent.
- [x] Frame cible sans position sautée ; positions d'état absentes reportées depuis la dernière position connue.
- [x] Split par match ; features limitées aux frames/événements courants ou antérieurs.
- [x] Perte région pondérée ; pertes événements pondérées pour la classe « rien ».
- [x] Lecture NPZ par match, cache maximal de deux matches ; corpus non chargé entièrement en RAM.
- [x] Seed 42 et versions directes épinglées dans `requirements.txt`.
- [x] Mesure réelle sur cinq parties effectuée.
- [ ] ~1 000 parties et comparaison finale aux baselines : en cours.
- [ ] Phase 2 : fetch cinq parties, puis cible ~1 000.
- [ ] Phase 3 : parse et split.
- [ ] Phase 4-5 : benchmark et entraînement.
- [ ] Phase 6 : évaluation et baselines.
- [ ] Phase 7 : GIF.
- [ ] Phase 8 : README, validation et publication.

- [2026-10-09T20:51] Fetch 5: 5 usable ranked matches cached.

- [2026-10-09T20:51] Parse 5: 5 matches, 136 observations, 0 errors.

- [2026-10-09T20:51] Train 5: 3 epochs, device cpu, 516133 parameters.

- [2026-10-09T20:51] Evaluate 5: region top-1 0.0435, best baseline 0.0870.

- [2026-10-09T20:51] Demo 5: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T20:51] Fetch 5: 5 usable ranked matches cached.

- [2026-10-09T20:51] Parse 5: 5 matches, 136 observations, 0 errors.

- [2026-10-09T20:51] Train 5: 3 epochs, device cpu, 516133 parameters.

- [2026-10-09T20:51] Evaluate 5: region top-1 0.0435, best baseline 0.0870.

- [2026-10-09T20:51] Demo 5: predicted_vs_actual.gif generated from held-out test match.
