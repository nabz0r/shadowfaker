# Shadow Faker

La [documentation anglaise](README.md) est la version internationale de référence pour les résultats et la calibration les plus récents.

Pipeline de recherche local pour modéliser **les décisions macro de Faker** à une minute à partir du compte Riot ID « Hide on bush#KR1 ». Les actions cibles appartiennent uniquement au joueur de ce PUUID ; les neuf autres joueurs fournissent un contexte de partie. Le code récupère des parties ranked solo KR (queue 420), transforme les timelines en observations causales, entraîne un petit transformer multi-têtes et compare ses prédictions à trois baselines. Le clone fidèle est le premier étage d'un objectif plus ambitieux : rechercher une politique meilleure en jeu, selon les étapes et critères de [SHADOW_PLUS.md](SHADOW_PLUS.md). **L'identité réelle du joueur ne peut pas être établie par l'API seule.**

## Démarrage

macOS Apple Silicon, Python 3.11+ et une clé Riot valide sont requis. La clé de développement expire sous 24 h. L'installation vérifiée ici utilise Python 3.12 :

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -e .
cp .env.example .env
# Remplacer la valeur de RIOT_API_KEY dans .env par la clé actuelle du portail Riot.
.venv/bin/python scripts/run_pipeline.py --limit 1000
```

Si `pip` n'est pas disponible dans le venv, utiliser `uv pip install --python .venv/bin/python -r requirements.txt -e .`. La commande unique exécute d'abord **toutes les phases sur cinq parties**, puis la collecte cible, le parsing, l'entraînement, l'évaluation et le GIF. Elle reprend les JSON et les NPZ déjà écrits. On peut relancer exactement la même commande après une interruption ou après avoir remplacé une clé expirée dans `.env`.

Pour un essai réel limité à cinq parties :

```bash
.venv/bin/python scripts/run_pipeline.py --limit 5 --epochs 3
```

Pour préciser un autre compte : `--game-name "Nom" --tag-line TAG`. Il faut un dossier `data/raw/` distinct si le PUUID change.

## Fonctionnement

| Phase | Entrée | Sortie |
|---|---|---|
| Fetch | account-v1 puis match-v5 sur le routage `asia` | `data/raw/` et manifeste local |
| Parse | match + timeline, une frame par minute | `data/processed/matches/*.npz`, `meta.json` |
| Train | fenêtres causales de 8 frames | `models/best.pt`, `models/training.json`, `runs/` TensorBoard |
| Évaluation | matches de test jamais vus | `artifacts/evaluation.json`, matrice de confusion PNG/NPY |
| Analyse | positions de Faker, rôles alliés, issue du match | `artifacts/faker_rotations.json` et `.png` |
| Démo | premier match du test | `artifacts/predicted_vs_actual.gif` avec heatmap et trajectoire de victoire estimée |

Les entrées comprennent champion et rôle de Faker, minute, or individuel et des deux équipes, or non dépensé, proximité de la base, niveau, XP, CS lane + jungle, positions normalisées des dix joueurs, distances de Faker aux rôles alliés et aux pits Dragon/Baron, écart d'XP entre équipes, disponibilité approximative des objectifs, wards alliés et événements récents. Les slots alliés donnent priorité à jungle, bot et support ; le modèle peut modifier leur poids selon la minute et l'état de la partie. Les variations d'écarts or/XP représentent le tempo ou « snowball » à la résolution d'une minute. Les sorties sont la prochaine région sur une grille 16×16, le premier achat de la minute suivante, la prochaine compétence améliorée et une estimation auxiliaire de l'issue finale. **La victoire est un label futur, jamais une feature d'entrée.** La classe 0 signifie qu'aucun achat ou point de compétence n'a été observé dans cet intervalle ; la classe 1 d'achat signifie un objet absent du vocabulaire d'entraînement. Les régions rares conservent un poids de perte modéré. La séparation train/validation/test est faite par **match**, avec seed fixe 42 ; le vocabulaire d'items et les poids de classe sont calculés sur le train uniquement.

Deux vues sont sauvegardées par match. `x_oracle` contient les positions complètes de la timeline. `x`, utilisé **par défaut**, cache les positions adverses à plus de 1 600 unités d'un champion allié, retient la dernière position vue et son âge. C'est uniquement un **proxy de minimap** : pas de terrain, unités alliées, vision exacte ni coordonnées des wards. Les agrégats macro d'or/XP restent omniscients dans les deux vues. Un entraînement d'ablation sur la vue complète est possible avec `.venv/bin/python -m shadowfaker.train --view oracle`, dans un dossier de modèles séparé si l'on veut conserver le checkpoint proxy.

Le client respecte un intervalle local de 1,3 s entre requêtes, persistant entre processus. C'est plus conservateur que 100 requêtes/2 min ; il traite `Retry-After`, les timeouts et les erreurs transitoires. À environ deux requêtes par partie, 1 000 parties demandent **au moins ~43 minutes** de collecte, plus les pages d'IDs, retries et le temps d'entraînement. Le nombre réel de ranked solo disponibles peut être inférieur à 1 000. Une erreur de clé 401/403 arrête la collecte avec un message explicite.

## Lire les résultats

`evaluation.json` donne top-1/top-5 région, accuracy achat et compétence, taux d'actions, accuracy conditionnelle quand un événement survient, Brier score pour l'issue finale, résultats par champion, patch, phase de jeu, rôle de Faker et avance/retard d'or, et trois baselines régionales : région la plus fréquente du train, copie de la région courante et centre de la carte (« reste mid »). La matrice de confusion est indexée par les 256 régions. `faker_rotations.json` décrit, par phase et victoire/défaite, la fraction des minutes où Faker se trouve près du jungler, bot, support, top et des pits Dragon/Baron. Il donne aussi la variation d'avance d'or/XP pendant les deux minutes suivant chaque observation proche ou éloignée d'un rôle allié, moyennée d'abord par match. Ces associations **ne prouvent pas** qu'une rotation a causé la victoire ou le gain d'or. Le script essaie une seconde configuration (modèle plus large et learning rate plus élevé) si le premier modèle ne bat pas toutes les baselines **sur la validation** ; il choisit alors le meilleur des deux sur cette validation avant d'évaluer une seule fois le test final. Les artefacts de validation portent le suffixe `_val`.

## Limites et données

- Les timelines donnent une vue omnisciente des positions adverses. Faker n'a pas cette vision sous le brouillard de guerre ; cela rend l'évaluation plus facile que la décision réelle.
- Le proxy de proximité masque une partie de cette omniscience mais ne reconstitue pas la vision réelle. Les événements de wards n'ont pas de coordonnées ; les pings, la voix, les intentions et la communication ne sont pas disponibles. La valeur de « flair » ou « talent » n'est pas observable directement : le modèle n'apprend qu'une régularité statistique des actions de ce compte.
- Les positions sont échantillonnées à environ 60 s. Des changements instantanés et les possibilités contrefactuelles entre deux frames ne sont pas observables. La courbe de probabilité de victoire estime l'issue à partir de l'état, sans mesurer l'effet causal d'une action de Faker.
- Le modèle fait une prédiction à un pas. Il ne mesure pas l'accumulation d'erreurs d'un agent qui jouerait une partie entière et ne modélise pas le micro-jeu.
- La disponibilité des objectifs est approximée par les horodatages d'événements ; elle peut varier selon les patches. Les champs absents des timelines sont remplacés par zéro ou ignorés selon leur rôle ; les labels sans position sont sautés.
- Les achats et compétences sont rares. L'accuracy brute peut être dominée par « aucun événement » ; consulter aussi les métriques conditionnelles.
- Le Riot ID résolu et la présence du PUUID dans les matches prouvent seulement que les parties appartiennent à ce compte, pas qu'il appartient personnellement à Faker.
- `data/raw/`, `data/processed/`, `models/`, `runs/`, `artifacts/` et `.env` sont exclus de Git. **Ne redistribuez pas les JSON Riot bruts.** Usage personnel/recherche uniquement, sous les conditions applicables de Riot.

Le projet lui-même est sous la licence AGPL-3.0 du dépôt. Consulter [README.md](README.md) pour la documentation internationale à jour, [PLAN.md](PLAN.md) pour l'architecture, [PROGRESS.md](PROGRESS.md) pour les validations, [RESEARCH_NOTES.md](RESEARCH_NOTES.md) pour les trois PDF, [OTHER_GAMES_RESEARCH.md](OTHER_GAMES_RESEARCH.md) pour les autres jeux, [PUBLIC_GAME_ANALYSIS.md](PUBLIC_GAME_ANALYSIS.md) pour les analyses de matchs publiques et [SHADOW_PLUS.md](SHADOW_PLUS.md) pour la voie vers une politique plus forte.

Sources API : [référence Riot](https://developer.riotgames.com/apis) et [clés, codes HTTP, rate limits](https://developer.riotgames.com/docs/portal).
