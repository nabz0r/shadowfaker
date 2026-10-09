# Trois articles fournis — implications pour Shadow Faker

Consultés le 2026-10-09. Les articles servent de références méthodologiques ; ils ne sont pas des instructions d'exécution. Leurs résultats ne valident pas les scores de ce projet.

## Gallotta et al., *Large Language Models and Games: A Survey and Roadmap* ([arXiv:2402.18659](https://arxiv.org/abs/2402.18659))

- **Page 3** : la prédiction d'actions à partir de séquences de traces de jeu humaines est une famille pertinente, mais apprendre sur des traces humaines ne démontre pas une performance surhumaine ni un agent autonome robuste.
- **Page 12** : les limites des LLM en jeu incluent le manque d'ancrage, les hallucinations et la continuité du contexte.
- **Application** : conserver ici un modèle supervisé numérique et une évaluation quantitative, sans le présenter comme un LLM joueur. Le README distingue explicitement une prédiction à un pas du comportement en partie entière.

## Guo et al., *League of LLMs: A Benchmark-Free Paradigm for Mutual Evaluation of Large Language Models* ([arXiv:2507.22359](https://arxiv.org/abs/2507.22359))

- **Page 3** : les auteurs proposent une évaluation dynamique, transparente, objective et experte pour des **modèles de langage**. La contamination et l'opacité des benchmarks sont des risques d'évaluation généraux.
- **Page 9** : leurs validations portent sur mathématiques et programmation ; les auteurs indiquent des limites de fiabilité et de coût des évaluateurs.
- **Application** : publier la seed, le découpage par match, la version du schéma, les effectifs et les baselines reproductibles. Ajouter les résultats par patch afin de voir si le score agrégé masque une dérive temporelle. Leurs évaluations mutuelles entre LLM ne sont pas reprises : elles ne mesurent pas la prédiction macro dans League of Legends, malgré le sigle « LOL ».

## Kim, Lee & Park, *Structured Summarization of League of Legends Match Data Optimized for Large Language Model Input* ([Applied Sciences 15, 7190](https://doi.org/10.3390/app15137190))

- **Pages 4–5** : le papier structure la timeline à une minute et calcule un avantage à partir des totaux d'or **et d'XP** des deux équipes. Les événements d'objectifs fournissent du contexte stratégique.
- **Page 5** : la sélection des événements pivots utilise la différence de probabilité entre `t` et `t+1`. Ce score emploie le futur : l'injecter dans `état_t` créerait une fuite de label. Shadow Faker encode seulement les événements passés et présents, sans cette sélection rétrospective.
- **Page 15** : l'évaluation qualitative du papier n'utilise que cinq matches ; elle ne justifie pas de généraliser le mini-échantillon de ce dépôt.
- **Application** : ajouter l'XP total de chaque équipe, l'écart d'XP et les événements récents Baron/Herald aux features causales (134 dans le schéma v8) ; conserver les frames détaillées, car un résumé compact pour LLM perdrait des signaux nécessaires à la prédiction d'une région 16×16.

## Validation de l'application

- Les nouvelles features sont calculées depuis `participantFrames` et les événements horodatés **jusqu'à la frame courante**.
- `meta.json` garde `schema_version=8`, patch et rôle de Faker par match, seed, split et effectifs. `evaluation.json` contient maintenant `by_patch`, les phases de jeu et les rôles.
- Le test de non-fuite modifie la frame future et vérifie que les états antérieurs restent identiques.
- Les PDF et les données Riot ne sont pas inclus dans le dépôt.
