# Shadow Faker — secondes, actions et espace continu

![Ce que les timelines observent vraiment à la seconde](docs/figures/second_scale_observability.png)

## Cible de recherche

Shadow doit apprendre une distribution sur **l'action suivante de Faker, son délai et son lieu éventuel** : `P(action, Δt, x, y | observations jusqu'à t)`. `x` et `y` sont des coordonnées normalisées continues sur la carte. Une matrice 16×16, 64×64 ou 512×512 est seulement un choix de **rendu ou d'approximation numérique**, modifiable sans changer le phénomène. La localisation ne suffit pas : reset, pression, déplacement vers jungle/bot, contestation, ward et action sur un allié/adversaire ont des significations différentes.

Le futur protocole préenregistrera des horizons **1/5/10/30 s**, une famille d'action, une tolérance de temps (par exemple ±2 s), un rayon en unités de jeu (par exemple 500), et la part des décisions couvertes. Le succès conjoint exige **action correcte + temps correct + lieu dans le rayon**, seulement lorsque le lieu de l'action est directement observable. Ces exemples de seuils ne sont **pas** des résultats ni un objectif adapté après lecture du test. On comparera aussi à la persistance de position, à la fréquence par phase et aux priors de rôle, par match et par famille d'action. Une classe « aucun événement » dominante ne peut pas valider 90 %.

Le module [`continuous.py`](src/shadowfaker/continuous.py) fixe dès maintenant la distance en unités de carte, l'horodatage, la provenance et la perspective de chaque label. Il refuse un label au temps `t` ou sans source ; les lieux manquants restent comptés comme tels. Un changement de grille d'affichage ne change pas le score géométrique. **Aucun modèle de déplacement à la seconde n'est encore évalué**, faute de labels observés à cette fréquence.

## Ce que les 465 timelines cached contiennent

| Preuve | Compte | Sens |
|---|---:|---|
| Événements avec timestamp | 563 198 | Types Riot bruts, y compris achats/skills et autres événements ; ce ne sont pas autant de décisions de Faker. |
| Lieux d'événement valides | 60 554 | Coordonnées du **lieu de l'événement**, parfois de la victime ou de l'objectif. |
| Événements impliquant Faker | 55 122 | Acteur, tueur, victime, créateur ou assistant explicitement attribué ; pas son intention. |
| Positions échantillonnées de Faker | 12 975 | Ancres de frames, écart médian **60,02 s** (P10 60,00 ; P90 60,03). |

Une fenêtre part d'une frame où la position de Faker est connue à `t`. L'audit cherche les événements de `(t,t+h]`. Les fenêtres ne sont pas des observations indépendantes et leurs comptes ne sont **pas** des prédictions.

| Horizon | Fenêtres | Avec un événement | Avec Faker impliqué | Avec combat Faker | Avec nouvelle position Faker |
|---:|---:|---:|---:|---:|---:|
| 1 s | 12 507 | 5 185 | 770 | 82 | **0** |
| 5 s | 12 481 | 11 358 | 3 159 | 374 | **0** |
| 10 s | 12 447 | 12 297 | 5 169 | 763 | **0** |
| 30 s | 12 280 | 12 280 | 9 702 | 2 134 | **0** |

Les événements sont souvent horodatés entre les frames ; cela aide à modéliser le **rythme de la partie** et les interactions, pas à retracer la position, les clics, la vision ou la communication de Faker à chaque seconde. Le modèle d'événements à 10 s déjà entraîné reste une expérience séparée : son score global reflète en grande partie les wards, et ses classes de kill/objectifs sont encore faibles.

## Chemin vers un modèle de décisions à la seconde

1. **Alignement de sources autorisées** : identifier cinq matchs et leurs replays ou VOD, relever une horloge commune et la perspective caméra/joueur. Chaque observation porte `match_id`, `source`, `perspective`, `issued_at_ms`, `observed_at_ms`, acteur, famille d'action et coordonnées facultatives. Une caméra spectateur n'est pas la vision de Faker.
2. **Annotation contrôlée** : deux annotateurs par pilote, accord temporel et sémantique mesuré, zones masquées quand l'information est invisible. Les frames manquantes restent manquantes ; aucune interpolation de 60 points n'est un label.
3. **Modèle** : contexte causal des dix joueurs et événements passés → intensité du prochain événement attribuable, famille d'action de Faker et densité spatiale continue conditionnelle. Les trajectoires futures ne deviennent jamais des features à `t`.
4. **Épreuve indépendante** : split par match et par époque, modèle et rayons gelés avant une nouvelle cohorte. Rapporter erreur temporelle, distance en unités, précision par action, calibration, couverture et baselines. Le seuil de 90 % n'a de sens qu'avec ces paramètres fixés et une cohorte réellement nouvelle.

L'[ancien audit 8×8 à la minute](NINETY_GATE.md) mesure un autre benchmark de développement. Il ne représente plus la cible de recherche à la seconde.

## Reproduire sans réseau

```bash
.venv/bin/python scripts/audit_second_scale.py --pilot-only
.venv/bin/python scripts/audit_second_scale.py
.venv/bin/python scripts/render_second_scale.py
.venv/bin/python -m pytest -q tests/test_second_scale.py
```

Les JSON de matchs, les identifiants et les traces restent sous `data/` et `artifacts/`, exclus de Git. Le [JSON public](docs/data/public_second_scale.json) ne contient que des totaux agrégés.
