# Shadow Faker — plan d'exécution

## M20 — atlas de preuves visuelles et trajectoire vérifiable vers 90 % (2026-10-11)

1. Recalculer sur le registre IoC privé un **pilote de cinq parties** (trois train, deux validation), puis des agrégats train/validation sans exposer de match, de ligne Riot ou de label test : fréquence des sept cibles et âge réel des snapshots dans les fenêtres de dix secondes.
2. Générer des graphiques reproductibles et un JSON public agrégé : densité des actes, horloges positions/événements, écart entre la précision spatiale historique et la porte exacte de 90 %. Chaque visuel indique cible, dénominateur et statut de validation.
3. Refaire les README FR/EN et les documents de recherche autour d'un contrat de mesure : prochaine action/temps/lieu à l'échelle des secondes, archive 8×8 à une minute séparée, baselines et cas sans action explicites. Documenter une roadmap avec hypothèses falsifiables, besoins de données, garde-fous de causalité et verrouillage prospectif.
4. Vérifier figures, liens, chiffres, tests et confidentialité ; publier tous les fichiers sur `main`, puis comparer l'arbre Git distant aux fichiers testés localement.

Risque : des milliers de fenêtres se recouvrent dans seulement 465 matchs, tandis que les positions sont prises environ chaque minute. Une exactitude « 90 % » obtenue en prédisant toujours l'absence d'événement, en agrandissant la zone ou en réutilisant la validation serait trompeuse. La feuille de route ne présente aucun seuil non atteint comme un résultat.

## M19 — registre IoC causal, prêt pour un futur entraînement textuel (2026-10-11)

1. Auditer les quatre dépôts existants (entrepôt de frames, fenêtres Faker à 10 s, mémoire de décisions, index textuel) et documenter les jointures manquantes. L'or n'est qu'un canal parmi les positions, XP, vie, CS, niveaux, vision par événements de wards, objectifs, itemisation et interactions des dix joueurs.
2. Construire `data/processed/faker_ioc.sqlite`, privé et versionné. Pour chaque match : identité et split, snapshots des dix joueurs à l'horloge réellement observée, événements Riot horodatés avec rôle de Faker et pointeur source, et fenêtres `(t,t+10 s]` avec 48 variables causales, labels futurs séparés. Vérifier les cinq premiers matchs (trois train/deux validation), puis les 465, avec empreinte des sources et reprise sans refetch. Chaque erreur de match est isolée.
3. Fournir un export JSONL **train seulement** pour un futur modèle de langage : état structuré et événements `<= t`, étiquettes futures séparées, provenance et âge du dernier snapshot. Ne pas prétendre disposer des clics, des communications ou de la vision réelle. La génération de texte rétrospectif et les sources externes non alignées restent hors des entrées prédictives.
4. Tester causalité, attribution, séparation par match, reprise et correspondance exacte des labels avec le corpus assaini. Publier seulement schéma, agrégats, mode d'emploi et bilan dans les Markdown/README, jamais les lignes de Riot ou l'export privé. Aucun entraînement ni score nouveau ne sera revendiqué sans protocole prospectif.

Risque principal : les événements ont une horloge fine mais les positions des dix joueurs n'existent qu'aux frames d'environ 60 s. La timeline donne une vision omnisciente ; le registre doit marquer ces limites au lieu d'inventer une décision ou une influence causale de Faker.

## M18 — assainir le corpus causal et rechallenger la prédiction Faker (2026-10-11)

1. Geler les scores du modèle à 10 s et les splits par match. Auditer d'abord cinq parties puis les 465 JSON cachés : identité de Faker, queue ranked solo, durée, correspondance match/timeline, cadence des frames et intégrité des événements attribués. Chaque exclusion est expliquée et comptée ; les détails par match restent locaux.
2. Versionner un jeu assaini. Une partie dont l'identité, la timeline ou l'horizon est incohérent est mise en quarantaine. Les événements malformés ne deviennent pas silencieusement des négatifs. Recréer les échantillons avec empreinte des sources et cache reprenable, sans charger tout le corpus en RAM.
3. Tester sur les mêmes matchs train/validation un challenger qui ajoute des variables connues à `t` utiles à l'action de Faker, notamment l'or disponible et les changements d'état depuis la frame précédente. Comparer aux fréquences train et au modèle M16 sur les mêmes fenêtres ; séparer actes observables et issues de combat. Le vieux test consulté et le futur lockbox ne servent pas à choisir.
4. Mettre à jour la documentation et les figures publiques avec couverture, exclusions, résultats et limites. Publier code, tests et documentation sur `main`, sans JSON Riot, NPZ, poids ou secrets.

Risque central : une timeline omnisciente et des frames espacées d'environ une minute ne révèlent ni la minimap réellement vue, ni les clics, ni le sang-froid. L'assainissement et les nouvelles variables ne rendent pas l'objectif de 90 % acquis ; tout gain doit être mesuré à cible et population constantes.

## M17 — rejeu analytique des parties indexées (2026-10-11)

1. Vérifier sur cinq parties que les horodatages des frames et des événements Riot sont ordonnés et que les dix positions peuvent manquer sans casser l'affichage. Exporter ces temps dans la trace locale versionnée, avec cache et reprise.
2. Permettre de chercher une des parties indexées, jouer/mettre en pause et parcourir la partie à la seconde, à plusieurs vitesses. Montrer les dix joueurs à leur **dernière position observée**, l'âge de cette observation et les événements à leur horodatage réel. Un événement sur la carte représente son lieu, pas un déplacement continu d'un joueur.
3. Garder la prédiction spatiale historique et la destination réelle dans une analyse rétrospective séparée, car cette dernière révèle le futur. Expliquer que ce lecteur n'est ni la vidéo/POV du client LoL, ni une mesure de position à chaque seconde.
4. Tester cinq traces puis des parties de durées et de schémas différents, l'interface FR/EN et mobile, les routes locales, les tests et la publication sur `main`. Mettre README et PROGRESS à jour.


## M16 — prochaines actions de Faker à 10 secondes (2026-10-11)

**Contrat figé avant entraînement.** Depuis les mêmes états causaux du modèle d'événements, prédire pour chaque fenêtre `(t,t+10 s]` plusieurs événements explicitement attribués à Faker : achat, point de compétence, ward posée/détruite, kill, mort et assistance. Achat/skill/ward sont des actes observables ; kill/mort/assistance sont des issues, sans prétention sur l'intention. Ne pas utiliser `LEVEL_UP`, `ITEM_DESTROYED` ou un événement de toute l'équipe comme une action de Faker. Un lieu d'événement n'est jamais sa position.

1. Vérifier la construction et la causalité sur cinq matchs (trois train, deux validation), puis sur les 465. Sauvegarder un NPZ par match, versionné, sans corpus entier en RAM et avec reprise. Les fenêtres se recouvrent dans un match : toute incertitude est groupée par match.
2. Entraîner une petite tête multilabel depuis les features à `t`, avec arrêt sur la perte de validation. Comparer à la fréquence globale et à la fréquence par phase ajustées **sur train seulement**. Rapporter log loss, Brier et AUPRC par classe avec prévalence, et une métrique globale qui n'est pas dominée par « aucun événement ». Ne pas ouvrir l'ancien test déjà consulté pour sélectionner le modèle.
3. Publier uniquement des agrégats et un visuel. Une amélioration de log loss ne sera pas présentée comme une capacité à anticiper les kills si l'AUPRC de cette classe ne gagne pas. Le futur lockbox requiert de nouveaux matchs ; la clé Riot actuellement refusée par HTTP 401 bloque seulement ce rafraîchissement, pas le travail depuis cache.


## M15 — horloge à la seconde, espace continu (2026-10-11)

La cible de recherche est une **décision de Faker à l'échelle de la seconde** : à l'instant `t`, avec seulement l'information disponible jusqu'à `t`, prévoir un type d'action, son délai et, si l'action a un lieu, une distribution sur des coordonnées continues normalisées `(x,y)`. Une grille 8/16/64/512 n'est qu'un rendu ou une approximation numérique de cette distribution ; son nombre de cases ne définit plus le succès. Le score spatial futur sera une erreur en unités de jeu et une couverture dans un rayon préenregistré, conditionnée à une action réellement observable. Le seuil de 90 % reste une hypothèse, pas une propriété actuelle.

1. Auditer **cinq parties** puis tout le corpus cached : timestamps des événements, coordonnées de lieux d'événement, horodatage des positions des joueurs et écarts entre observations. Aucun événement ne sera converti en position de Faker. Publier seulement des agrégats sans ID ni trace.
2. Créer un contrat d'annotations haute fréquence local : match, source, point de vue, temps en millisecondes, acteur, famille d'action, coordonnées normalisées facultatives, qualité de l'alignement. Refuser les trajectoires à 1 s inventées par interpolation et les observations issues du futur. Préparer des métriques continues indépendantes de la taille de la grille, avec baseline de persistance et intervalles par match lorsque des annotations fiables existeront.
3. Montrer l'horloge et les trous d'observation dans le tableau de bord : un curseur 1/5/10/30 s fait varier les comptes d'événements vérifiables, tandis qu'un relevé clair rappelle que la position de Faker n'est connue qu'aux frames disponibles. Afficher la différence entre lieu d'un événement, état des dix joueurs et cible Faker.
4. Reclasser l'audit précédent de précision 8×8 à une minute comme **archive de développement**. Mettre README FR/EN, NINETY_GATE, RESULTS, ROADMAP et PROGRESS à jour ; vérifier l'UI FR/EN/mobile, les tests et publier sur `main`.

Risque : les timestamps d'événements sont plus fins que les positions. Un modèle des événements à dix secondes existe, mais ses scores dominés par les wards ne prouvent ni une prédiction de clics ni une connaissance de l'intention de Faker. Une future VOD, même alignée, doit porter provenance, droits, visibilité et accord d'annotation. Aucun 90 % ne sera revendiqué par élargissement artificiel d'un rayon, agrandissement de grille ou majorité « aucun événement ».

## M11 — mémoire de Faker et challenger apprenant (2026-10-10)

Construire une base SQLite **privée** de décisions `(état à t, contexte IoC, arrivée observée à t+1)` depuis les NPZ déjà générés. Une ligne correspond à une observation, le match entier garde son split ; le test historique n'est pas ouvert. Les vecteurs compacts conservent des dimensions choisies de l'état actuel et le patch/rôle/minute comme métadonnées. Indexer et interroger les cas de train, jamais une étiquette val/test pendant la recherche. Publier seulement la taille, le schéma et des scores agrégés.

Le challenger est un récupérateur de situations similaires, distinct du transformer Shadow. Il calibre ses poids et son nombre de voisins sur une partition de calibration **par match** prise dans le train, reconstruit sa mémoire avec tout le train, puis évalue une fois sur validation contre copie-position et prior rôle/phase. Journaliser les propositions et écarts dans la base locale, avec preuve d'étiquette et séparation du test. Aucune réponse du navigateur ne met à jour automatiquement un modèle ; un nouveau candidat ne remplace Shadow qu'après un nouveau jeu de validation. La grille 512×512 reste une mesure de destination dérivée des coordonnées t+1, pas une observation par pixel à chaque instant.

L'interface doit permettre de lire un cas de validation, sa prédiction et des analogies d'entraînement **sans divulguer de match ID** dans les agrégats publics, avec un mode « révéler puis juger ». La documentation explique pourquoi ce n'est pas l'entraînement d'un LLM textuel, et comment un LLM pourrait plus tard résumer des décisions sourcées sans fabriquer des labels.

## M10 — validation des événements et de leurs exclusions (2026-10-10)

Comparer, sur cinq parties puis sur tout le corpus KR, chaque événement indexé au JSON Riot d'origine : type, timestamp, acteur, victime, objet/skill et coordonnées. Vérifier séparément les types ignorés et leur volume, les kills sans tueur joueur, les plaques de tourelle et les événements d'inventaire. Publier uniquement des comptes agrégés et des statuts de fiabilité par famille ; les match IDs et les JSON restent locaux. Une coordonnée de kill désigne le lieu de l'événement, pas la position ou la vision de Faker. Un champ présent prouve la fidélité du parsing, pas l'intention tactique du joueur.

Afficher l'audit dans Corpus avec une légende « contrôlé / partiel / exclu », documenter les erreurs et mettre à jour README, CORPUS et PROGRESS. Ne pas modifier les labels du modèle sans nouveau dataset, ablation et évaluation par match. Vérifier le script sur un petit échantillon, le corpus complet, les tests, l'UI et la publication `main`.

## M9 — pression située et contexte d'objets à l'instant t (2026-10-10)

1. Relier Pression au rejeu local sélectionné : représenter sur la carte les dix positions *observées* à la minute choisie, un cercle métrique centré sur Faker, les alliés et ennemis proches, les positions absentes et les inventaires connus. Le rayon et la frise doivent modifier réellement le relevé ; les moyennes de 465 parties restent dans un panneau distinct. Cette carte Riot omnisciente n'est pas la vision de Faker.
2. Construire un IoC temporel par match depuis les événements `ITEM_PURCHASED`, `ITEM_SOLD`, `ITEM_DESTROYED` et `ITEM_UNDO` horodatés. Un état à `t` ne peut consommer que des événements `timestamp <= t`; le résultat, le score et les objets finaux du JSON match ne sont jamais des entrées. Conserver les positions déjà parsées, l'identité d'objets en représentation compacte, les comptes de changements et des masques de visibilité pour les ennemis. Versionner le schéma et cacher chaque match pour reprise.
3. Piloter cinq parties avec tests de causalité et d'inventaire, puis préparer 465 parties en streaming. Rechallenger sur les seuls 373 train / 46 validation un candidat de même architecture que la politique hiérarchique. Comparer au modèle courant, à la fréquence/copier et aux métriques 8×8, 16×16, 64×64 et à la surface nécessaire pour 90 % de couverture. Garder le vieux test et le lockbox hors sélection.
4. Enrichir les objets détenus à `t` par le catalogue officiel Data Dragon du patch joué ; cacher les 12 versions nécessaires, tester la source en pilote puis comparer complet / sans propriétés / sans objets. Traiter U.GG et les recherches Google comme pistes de provenance, pas comme features historiques sans match, timestamp, patch et perspective vérifiés.
5. Publier sur `main` le code, les tests, un graphique de comparaison, README/RESULTS/PRESSURE/PROGRESS à jour et des captures réelles du site. Les états par partie, modèles et JSON Riot restent locaux. Ne revendiquer aucune amélioration si la validation ne la montre pas.

Risques : les événements d'inventaire peuvent être incomplets ou corrigés par `ITEM_UNDO`, l'art des objets est d'un patch récent et la position ennemie de la timeline est omnisciente. La résolution temporelle des positions reste ~60 s. L'objectif 90 % doit toujours nommer sa cible et la surface de carte correspondante. Une page U.GG actuelle ou un extrait Google ne porte pas l'état historique d'une partie ; HTTP 403 ou une API commerciale fermée ne seront pas contournés ni présentés comme données d'entraînement.

```mermaid
flowchart TD
    API[Riot API KR/asia] --> RAW[JSON locaux en cache]
    RAW --> PARSE[Frames causales + split par match]
    PARSE --> BASE[Transformer actuel]
    PARSE --> TAG[Tags macro observables]
    BASE --> OLD[Test historique déjà inspecté]
    BASE --> LOCK[Checkpoint figé]
    LOCK --> FUT[100 nouvelles parties minimum]
    FUT --> SCORE[Un score prospectif]
    TAG --> DEV[Variantes macro sur validation]
    DEV --> NEW[Nouveau modèle, futur test séparé]
```

Les [graphiques de résultats](RESULTS.md) et la [roadmap M0–M5](ROADMAP.md) rendent visibles les étapes réellement terminées. Le futur test du modèle figé et les variantes d'entraînement restent deux expériences distinctes.

## Architecture

1. `src/shadowfaker/riot.py` : client Riot avec quota conservateur persistant, cache JSON atomique, reprise, erreurs explicites.
2. `fetch.py` : résolution Riot ID, pagination de l'historique ranked solo (queue 420), contrôle du match et de la timeline, manifeste des parties utilisables.
3. `features.py` : échantillons à chaque frame de ~60 s, fenêtre causale, vue macro complète et proxy de minimap, trois labels d'action de Faker, issue du match comme label auxiliaire, fichiers par match et manifeste train/val/test.
4. `model.py` et `train.py` : petit transformer multi-têtes, entraînement MPS/CPU mesuré, early stopping et checkpoints.
5. `evaluate.py`, `analyze.py` et `demo.py` : métriques sur matches jamais vus, baselines, associations descriptives des rotations de Faker avec l'issue et GIF d'une partie test.
6. `scripts/run_pipeline.py` : une commande, reprise automatique de chaque phase.
7. `RESEARCH_NOTES.md`, `OTHER_GAMES_RESEARCH.md`, `PUBLIC_GAME_ANALYSIS.md`, `REPLAY_FEASIBILITY.md` et `SHADOW_PLUS.md` : provenance des méthodes et des analyses publiques multilingues, puis chemin expérimental allant du clone à une éventuelle politique meilleure, avec conditions de preuve distinctes.
8. `macro_actions.py`, `prospective.py` et `scripts/render_results.py` : tags de mouvement avec masques, collecte/score futurs figés, puis graphiques agrégés reproductibles sans publier les JSON Riot.

## Invariants

- Aucun secret ni JSON brut dans Git ; les données Riot restent locales.
- Chaque observation utilise uniquement les frames et événements connus avant le label.
- La séparation train/validation/test se fait par match et est figée par seed.
- Les fichiers JSON et les échantillons sont écrits atomiquement ; une reprise ne retélécharge pas les succès.
- Le chargeur lit un match à la fois ; le corpus complet n'est jamais chargé en RAM.
- Les erreurs isolées d'une partie sont journalisées et n'arrêtent pas les autres parties.
- Les sources médiatiques doivent conserver langue, perspective, match et horodatage ; aucun commentaire rétrospectif ne devient une feature à l'instant `t`.

## Risques et limites

- Une clé Riot valide est nécessaire aux nouveaux appels. Le premier instantané réel a réussi ; les clés de développement expirent et doivent être renouvelées pour un rafraîchissement ultérieur.
- Un historique peut contenir moins de 1 000 ranked solo disponibles. Le nombre collecté sera documenté exactement.
- Le débit de développement annoncé (100 requêtes/120 s) impose au minimum ~40 min pour 2 000 requêtes, hors retries et entraînement.
- Le compte « hide on bush » doit être vérifié par account-v1, puis confirmé par la région KR des match IDs ; le nom seul ne prouve pas l'identité de Faker.
- La timeline est une vue omnisciente. Les résultats mesurent la prédiction one-step hors ligne, pas le jeu réel ni les décisions sous brouillard de guerre.
- Le proxy de minimap masque les positions adverses éloignées des alliés mais ne reconstruit pas la vision réelle : Riot ne fournit ni visibilité exacte, ni positions des wards, ni communication/pings. Les champs macro d'or et d'XP restent omniscients, même dans le proxy.
- Le signal de victoire est un label futur auxiliaire, jamais une entrée. Sa trajectoire estimée décrit l'association état/issue à une minute, pas la valeur causale d'une action.
- Les actions achat et compétence sont rares ; des métriques conditionnelles et le taux d'événements seront affichés en plus de l'accuracy globale.
- La supériorité sur Faker ne peut pas être établie par une accuracy de replay ni par une tête de victoire associative. Il faut une valeur d'action validée et des parties comparables en environnement jouable ; le présent pipeline fournit le prior comportemental et les analyses descriptives.
- La nouvelle mesure 8×8 a été choisie après examen du test historique. Le [protocole prospectif](BENCHMARK_PROTOCOL.md) attend 100 nouvelles parties ; **0** étaient disponibles au premier rafraîchissement. Un modèle de développement différent exigera un autre futur jeu de confirmation.

## Ordre de validation

Phase 0 plan → setup → résolution et cinq parties → parsing cinq parties → mini-entraînement → évaluation et GIF → collecte cible → entraînement final → vérification et publication sur `main`.

Suite : gel du candidat actuel → tags macro sur cinq puis 465 parties → variantes macro entraînées sur train, choisies sur validation → collecte des nouvelles parties pour le score unique du modèle figé → validation jouée, si un environnement fiable existe. Les comptes rendus effectifs sont dans [PROGRESS.md](PROGRESS.md).
# Extension 64×64 et atlas des événements (2026-10-09)

Le modèle 16×16, son checkpoint et son benchmark prospectif restent figés comme point de comparaison. La nouvelle branche de recherche travaille dans des dossiers locaux séparés : labels 64×64 dérivés des mêmes positions, entraînement et évaluation propres, vues 64×64 et événements horodatés. Les scores 64×64 doivent être comparés à des baselines calculées sur les matches d'entraînement uniquement, par match de validation/test et par domaine de queue.

1. Rafraîchir la liste Riot avec un instantané nommé. Explorer aussi les matches du **même PUUID** sans filtre de queue, mais garder ranked solo, autres parties éligibles et sources professionnelles dans des domaines distincts. Conserver chaque réponse en cache, sous quota. Un compte différent exige une provenance vérifiée avant fusion.
2. Déduire des timelines les destinations 64×64 et les événements passés/présents (kills, morts du compte, Dragon, Baron, Herald, Void Grubs `HORDE`, bâtiments, wards). Si un événement n'a pas de coordonnées, le montrer dans la bande temporelle et non inventer une position.
3. Entraîner une tête spatiale 64×64 avec aide 16×16 sur un split par match ; bench CPU/MPS, val d'abord, test séparé. Ne pas remplacer le modèle figé sans preuve.
4. Donner à l'interface une carte et une surface 64×64, une colorimétrie par type d'événement et un rejeu horodaté. La timeline Riot reste à ~60 s pour les positions ; les événements ont leur propre timestamp milliseconde. Préserver cette distinction dans les légendes.
5. Publier code, visuels **agrégés**, résultats et limites sur `main`. Garder les JSON Riot, les traces par partie, les poids et la clé hors Git.

Risques : forte sparsité de 4 096 classes pour ~12 510 observations initiales ; attention au surapprentissage et à la concentration centrale. Les historiques Riot peuvent ne pas fournir plus de ranked solo pour ce PUUID. Les queues non classées sont un autre domaine et peuvent contenir d'autres modes/cartes ; ne pas les appeler ranked. Les événements sont visibles dans la timeline omnisciente ; ils ne prouvent pas la vision du joueur. Les résultats déjà consultés restent exploratoires.

## Axe actuel : interaction entraînable et produit lisible

L'unité d'analyse est la transition observée **Faker à t → Faker à t+1** dans un état des dix joueurs. En parallèle, on conserve les réactions adverses observées entre les deux états pour l'analyse rétrospective. Les 13 canaux ennemis/alliés entrant dans le candidat neural sont calculés seulement depuis l'état passé et présent. Le champ géométrique coloré autour de Faker est une autre hypothèse explicative et ne doit pas être confondu avec la sortie probabiliste du modèle.

La base SQLite locale garde états, acteurs, événements et transitions ; la matrice 64×64→64×64 reste sparse. Les vecteurs d'état servent au rapprochement de contextes, les vecteurs de match terminé seulement à la recherche rétrospective. Les résumés TXT français/anglais et les notes professionnelles vérifiées sont indexés avec provenance, langue, statut et domaine. Aucune narration ou archive terminée n'entre automatiquement comme feature à t.

La livraison publique comprend quatre agrégats JSON, plusieurs figures calculées, un README cohérent avec l'interface et un serveur local borné à `127.0.0.1`. Le tableau de bord expose atlas, projection 3D de dix acteurs, pression adverse, moments de partie, recherche, cinq scénarios synthétiques et métriques 64×64 avec **couverture + surface couverte**. Les visuels par match et le corpus Riot restent ignorés par Git. Un test UI doit parcourir au moins 100 transitions de contrôles avec lectures d'état avant publication.

## Navigation temporelle commune

La frise de 0 à 39 minutes pilote chaque vue interactive selon la résolution disponible : atlas/surface/pression par phase, tempo par cinq minutes, rejeu sur la frame la plus proche d'une seule partie, scénario sur son point simulé le plus proche. Les légendes rappellent les cohortes distinctes et les codes couleur. Les figures de résultat et l'ancien modèle 16×16 sont identifiés comme archives fixes, faute de prédictions par phase sauvegardées. Test de cohérence : trois histogrammes de phase dont la somme doit reproduire exactement l'histogramme public initial pour chacune des 4 096 cases, observées et prédites ; parcours UI de 40 positions sans erreur console.

## M3 : décision macro et ablations du contexte (2026-10-10)

Objectif de développement : tester si la structure des dix joueurs améliore la prédiction de la prochaine action du compte, sans consulter le test historique pour sélectionner un modèle. Même split 373/46/46 par match ; train et validation seulement pour ce candidat. Les données d'entrée sont les fenêtres `x` proxy déjà calculées, enrichies des 13 interactions causales à `t` ; les destinations 64×64 et les tags macro observés à `t+1` sont uniquement des cibles.

1. Définir cinq classes mutuellement exclusives **observables** : rester proche, retour base, approche Dragon vivant, approche Baron vivant, autre déplacement. Priorité explicite retour > Dragon > Baron > rester > autre ; l'absence de position courante masque cette tête. Les huit tags macro existants restent une tête auxiliaire multilabel avec masques de validité. Aucun label ne prétend décrire le clic, l'intention ou la communication.
2. Partager un encodeur <5 M paramètres, puis factoriser la position en `8×8 → 16×16 → 64×64` avec probabilités conditionnelles normalisées. Trois modèles de même capacité et même seed reçoivent respectivement : Faker seul, Faker + alliés, état complet avec adversaires/objectifs. Le masque porte uniquement sur les colonnes d'entrée ; architecture, split et budget restent identiques.
3. Pilote cinq matches avant corpus, benchmark CPU/MPS, caches par match limités en mémoire, checkpoints et logs locaux ignorés. Comparer la validation 8×8 contre fréquence, copie et prior rôle/phase issus du train ; rapporter aussi 16×16, 64×64, décisions et tags, par phase/champion et bootstrap par match. Choisir au plus un candidat sur validation, sans promotion du checkpoint M0 et sans score sur le test ancien.

Risques : 12 510 paires corrélées et seulement 46 matches de validation ; les tags objectifs sont rares ; l'état proxy n'est pas la vision réelle ; certaines features globales restent omniscientes même si les positions ennemies sont masquées. Dans ce plan, « complet » signifie **tous les canaux de `x`**, pas `x_oracle` : les positions ennemies restent celles du proxy de dernière vue. Les ablations donnent une contribution prédictive, pas une influence causale. Un meilleur score validation n'est pas une confirmation indépendante.

## M3b : audit du plafond prédictif et visibilité (2026-10-10)

Objectif : comprendre pourquoi l'exactitude 8×8 reste vers 17 % avant d'augmenter la capacité du modèle ou de viser 90 %. Vérifier l'alignement de chaque position `t`/`t+1`, la densité des déplacements et les informations réellement disponibles au joueur. Garder le test historique hors de la sélection et M0 gelé.

1. Définir des références de transition conditionnées par la case actuelle, l'heure, la direction passée et le rôle. Calculer leurs comptes sur les matches train, choisir le lissage sur un sous-ensemble interne de train, puis mesurer une fois sur la validation de développement. Rapporter exactitude top-1, top-5 et concentration ; ne pas masquer une faible précision sous une catégorie grossière.
2. Documenter le statut de chaque famille de features : état propre, alliés/minimap, proxy de vision adversaire, informations globales de la timeline. Entraîner une variante conservatrice sans chiffres adverses ni ressources globales invisibles, à budget et split identiques au modèle M3. Quantifier ce que coûte l'information omnisciente.
3. Diagnostiquer les décisions tardives et les déplacements rares par phase/événement. Mesurer la masse maximale d'un choix 8×8 à état géométrique similaire. Une accuracy de 90 % ne peut être annoncée que pour une cible clairement spécifiée et évaluée sur des parties futures ; la minute suivante exacte 8×8 reste la cible publiée actuelle.

Tous les artefacts par partie restent locaux. Le résultat autorisé ici est un diagnostic reproductible et, si une variante gagne, un candidat de développement ; pas un nouveau score prospectif.

## M3c : expert spatial dépendant de la phase (2026-10-10)

Le diagnostic M3b montre une forte baisse après 20 minutes avec 2 751 observations tardives dans le train. Tester **un seul** candidat à entrée `x`/147 identique : encodeur partagé et ajout d'un résidu spatial 8×8 conditionné par la phase 0–10, 10–20 ou 20+ minutes. Entraîner sur les mêmes 373 matches, avec pilote cinq parties, seed et budget identiques. Choisir l'époque sur la moyenne des exactitudes par phase sur validation, puis reporter exactitude globale, par phase et macro F1 décision. Comparer au M3 complet par bootstrap apparié par match ; ne lire ni le vieux test ni le lockbox. L'expert de phase peut accroître le surapprentissage ; sa capacité supplémentaire sera rapportée et il ne remplace pas le candidat gelé M0.
# Extension 512×512 — 2026-10-10

Objectif : passer l'atlas de recherche à **512×512 positions** (262 144 cases) sans présenter l'ancien classifieur 64×64 comme un modèle 512. Les coordonnées Riot restent échantillonnées environ une fois par minute ; une case 512 n'apporte aucune observation temporelle supplémentaire. Conserver les modèles 16/64, leurs scores historiques et le lockbox M0 comme archives figées.

1. Pilote sur cinq ranked : calculer les labels 512 depuis les coordonnées normalisées sauvegardées, vérifier l'alignement exact avec les parents 64/16 et les frames, journaliser les valeurs absentes. Puis préparer le corpus entier en streaming par match.
2. Entraîner un petit adaptateur conditionnel `64 → 8×8` sur le train seulement, avec encodeur 64 gelé et une tête de 64 sous-cases. Le coût de sortie est constant plutôt qu'une tête dense de 262 144 classes. Choisir sur les 46 matches de validation, sans consulter les 46 matches du vieux test. Comparer à copie de position et fréquence du train ; publier les scores uniquement comme développement.
3. Agréger les destinations 512 de validation et les événements horodatés ranked en compteurs *sparse*. Ne publier aucun match ID, trace ou JSON Riot. Le serveur local peut lire les cellules exactes depuis un artefact ignoré par Git ; la figure publique d'événements regroupe les cellules en 16×16 blocs, masque les blocs de fréquence inférieure à trois et lisse seulement pour l'affichage. Garder localement les totaux et le nombre non placé.
4. Faire de la grille 512 l'atlas interactif principal et une surface 3D agrégée, avec légende indiquant validation pour les destinations, 465 ranked pour les événements et environ 60 s pour les positions. Garder la vue 64 et ses métriques comme archive nommée ; aucune interpolation ne doit se faire passer pour une mesure.
5. Tests de projection, conservation des masses, masquage, API locale, curseur et rendu navigateur. Mettre README FR/EN, RESULTS, ROADMAP et PROGRESS à jour ; publier sur `main` après vérification.

Risques : forte sparsité (12 510 transitions pour 262 144 cases), exactitude attendue faible, corrélation des frames d'une partie, visibilité ennemie approximative, coûts mémoire/DOM. Utiliser un modèle factorisé et des tableaux sparse ; rapporter les limites sans cible de 90 % artificielle.

## M4 : agrandir le corpus et prédire les événements (2026-10-10)

1. Rafraîchir les IDs Riot du PUUID vérifié avec un nouvel instantané et conserver le plafond réellement renvoyé. Explorer une source indépendante de parties professionnelles de Faker, mais enregistrer sa provenance et son domaine séparément. Les statistiques pro de fin de match ne constituent pas des trajectoires et ne sont jamais ajoutées aux 465 timelines classées.
2. Former un second jeu supervisé à intervalles **10 secondes** : état du dernier frame disponible et historique d'événements strictement antérieur au temps `t` → premier événement macro durant `(t,t+10s]` ou aucun. Prévoir `Faker kill/death`, kill allié/ennemi, objectif, bâtiment ; garder type, timestamp et lieu de l'événement comme annotations distinctes. Une coordonnée d'événement n'est pas une position de Faker. Split par match inchangé. Pilote cinq parties puis corpus complet, cache par match, journal d'erreurs, baseline de fréquence et score probabiliste.
3. L'hypothèse vient des processus ponctuels marqués : une intensité d'événements dépend d'une série régulière et d'événements irréguliers passés. L'analogie biologique porte sur le voisinage dynamique autour d'un individu focal. Tester les contributions de Faker, jungle, support, bot et adversaires par ablation, jamais interpréter les poids comme des effets causaux.
4. Évaluer séparément la cible à 10 secondes et la destination à ~60 secondes. Rapporter taux de non-événement, log loss, précision/rappel événement et scores par classe ; éviter une accuracy dominée par `aucun`. Ne jamais gonfler les observations de position 512 par interpolation. Le test ancien et le lockbox restent clos pour la sélection.
# M5a — ablation du contexte autour de Faker (2026-10-10)

- Question : les géométries alliées, ennemies et les six canaux jungle/bot/support ajoutent-elles du signal pour prédire le premier événement des dix secondes suivantes ?
- Garder le même classifieur, seed, parties KR train/validation et nombre de paramètres ; masquer des canaux à zéro **à l'entraînement et à la validation**. Comparer au modèle KR complet, jamais au test historique. Pilote 3/2 parties avant 373/46.
- Mesure : perte log pondérée par nombre de fenêtres et différence appariée bootstrap par match ; macro F1 et classes rares en diagnostics. Un effet observé reste prédictif, pas une attribution causale à Faker.
- Artefacts détaillés et pertes par match restent locaux ; seuls les scores agrégés entrent dans Git. Conserver le lockbox prospectif intact.

## M5b — accès et lecture des preuves sur le site (2026-10-10)

- Un fichier `dashboard/index.html` ouvert en `file://` ne peut pas charger le backend local et ses routes absolues. Le traiter comme un lanceur qui sonde `127.0.0.1:8008` et donne la commande de démarrage si le serveur n'est pas disponible.
- Exposer exclusivement l'agrégat public de l'ablation via une nouvelle route autorisée. Tracer les neuf classes avec leur fréquence et F1, distinguer le modèle KR seul du modèle avec appoint EUW et nommer la validation réutilisée.
- Rendre les prochaines preuves visibles : une partie replay assortie, cinq parties alignées, puis baseline spatiale à dix secondes ; en parallèle, mesurer précision/rappel des événements rares et contexte visible par Faker. Garder les hypothèses séparées des résultats.
- Synchroniser README EN/FR, RESULTS, ROADMAP, NEXT_RESEARCH et PROGRESS. Vérifier serveur, fichier local, langues FR/EN, mobile, absence de fuite brute, tests et `main` distant.

## M6 — six étoiles, onglets dynamiques et archives des finales (2026-10-10)

1. Vérifier le nombre de titres sur une source de T1, corriger le poster SVG, le site et la documentation. Les six étoiles célèbrent l'histoire de l'équipe, pas la précision de Shadow ni une affiliation.
2. Donner au tableau de bord de vrais onglets URL : une section visible à la fois, retour navigateur et menu horizontal accessible sur mobile. Préserver le curseur temporel commun et les contrôles de chaque vue.
3. Créer un corpus **professionnel public distinct** : six finales mondiales gagnées, 25 manches avec résultat, durée et lien source, puis quelques demi-finales remarquables. Tester la cohérence des séries, indexer en FR/EN dans la recherche locale sans ajouter ces matchs aux labels ranked.
4. Capturer l'interface réelle en PNG public et faire un GIF des six finales à partir de frames versionnées. Le README FR/EN doit suivre les chapitres visuels du site ; `WORLD_FINALS.md` documente chaque source et les limites de granularité.
5. Contrôler visuellement desktop/mobile, année/langue/onglet, route de données et absence d'erreurs console ; lancer les tests. Publier uniquement les faits, les agrégats et les images sans trace privée sur `main`.

Risque principal : les pages de statistiques pro décrivent la fin de chaque manche et non la perception ou les clics de Faker. Aucune fiche de finale ne devient un exemple d'entraînement avant alignement d'un replay autorisé, annotation de son point de vue et validation séparée.
# M7 — lire les grilles et les parties indexées (2026-10-10)

Les cellules de l'atlas, la carte historique et le rejeu doivent dire explicitement **ce que représente un point** : couche, cohorte, fenêtre de temps, compte et coordonnées. La carte d'événements distingue les événements comptés de ceux dont Riot donne une position. Une vue « Corpus » expose uniquement des **comptes agrégés** et la chaîne raw → états → prédictions, avec les manques et le prochain test. Les données Riot brutes restent locales.

Un index SQLite privé, reconstruit depuis les 465 JSON de match déjà cachés, ajoute à chaque partie ranked une date UTC, patch, durée, champion, côté, victoire, K/D/A, dégâts aux champions, vision, objets finaux et compositions alliée/adverse. Ces statistiques de **fin de partie** servent à explorer/rechercher les parties ; elles ne deviennent jamais des entrées de prédiction à t. Le moteur textuel FR/EN reçoit une fiche rétrospective par partie. Pilote cinq parties, audit des 465, puis interface et tests.

Risques : champs absents selon patch, sens de « équipe » en solo queue (Blue/Red, pas T1), dommages finaux pouvant créer une fuite future, comptage d'événements sans coordonnées, recherche sur 465 parties côté navigateur. Le parseur met `NULL` pour les champs manquants, relance sans doublon, affiche l'horodatage en UTC et limite les cartes visibles tout en gardant la recherche locale. Aucun objectif de 90 % n'est revendiqué à partir d'un enrichissement documentaire ; un nouveau modèle causal et un test futur seraient requis.

# M8 — zone de pression réglable et sprites locaux (2026-10-10)

Le panneau Pression doit exposer l'unité exacte de chaque grandeur et recalculer les agrégats à partir des positions des dix joueurs pour cinq rayons (1 000–5 000 unités). Le cercle est un **schéma d'échelle**, jamais la position réelle d'un ennemi. Une entrée exige deux positions connues consécutives, dehors puis dedans ; première frame et position manquante ne comptent pas. Les vues 0/1 et 0/2 restent descriptives, sans interprétation causale. Piloter cinq parties puis publier l'agrégat des 465, tester invariants et changement réel du curseur/temps en navigateur.

Les fiches privées affichent les champions et objets finaux par sprites générés depuis les métadonnées et feuilles officielles Data Dragon. Version d'art épinglée, manifest de coordonnées public sans match ID, caches CDN locaux, repli visible si icône absente. La version iconographique ne remplace pas le patch historique de chaque partie. L'UI et les README/FR doivent montrer de vraies captures de Pression, Corpus et Archives, et renvoyer vers les définitions et limites. Risques : art CDN temporairement indisponible, noms d'objets historiques divergents, surcharge visuelle mobile et taille des assets Git ; vérifier avant publication.
# M12 — Faker et l'expérience de ses coéquipiers (2026-10-11)

Construire depuis les cinq CSV professionnels déjà cachés un index **séparé** de la solo queue : exactement cinq lignes T1 par `gameid` contenant Faker, date, patch, rôle, joueur, champion et états à 10/15 minutes. Faire un pilote cinq manches, puis les 671 manches disponibles ; résister aux trous de champs et dédoublonner par `gameid`. Les années de saison de la source peuvent différer de l'année civile de la date : garder les deux et utiliser la date réelle pour ordonner les épisodes.

Avant chaque manche, calculer pour Faker–Doran, Faker–Oner et Faker–Keria les parties déjà jouées ensemble, l'exposition avec décroissance de 90 jours et la récence du dernier match commun. Ne jamais inclure la manche cible ou les résultats futurs dans cette expérience préalable. Construire une matrice par année des parties communes et une matrice de gameplay **descriptive** : avantage d'or/XP à 10 et 15 minutes et variation 10→15 par rôle, nombre de parties sans valeurs manquantes explicite. Les statistiques de fin de match (dégâts, wards, score) restent des résultats, jamais des entrées à 10 minutes. Comparer un pilote, vérifier chronologie, doublons et provenance ; publier seulement agrégats et figures, conserver lignes CSV/SQLite locales.

Interface : nouvel onglet Faker × équipe avec sélection d'année, matrice de cojeu, courbes d'expérience préalable, heatmap de ressources 10→15, définitions des unités et limites visibles. Lire les composantes réelles du roster 2026 sur LoL Esports ; le CSV est un miroir tiers incomplet après avril 2026, pas un replay ni une preuve d'intention. Toute hypothèse d'une « chimie » ou d'une influence causale requiert un nouveau protocole match-disjoint ou des replays alignés.

# M13 — L'expérience commune prédit-elle quelque chose ? (2026-10-11)

Utiliser le corpus pro comme **expérience auxiliaire de scoreboard**, jamais comme labels de déplacement Faker ou preuve de causalité. Cible primaire : écart d'or de Faker contre son mid adverse à 15 minutes. Cible secondaire : même écart pour bot. Entrées au plus tard à 10 minutes : cinq rôles, écarts or/XP, kills/assists/deaths, identité du roster, date et ligue connues, et historique de cojeu strictement antérieur. Comparer une règle de persistance, un ridge sans historique et le **même ridge** enrichi de l'historique. Même entraînement, même budget, mêmes hyperparamètres candidats ; sélectionner la régularisation sur validation seulement.

Séparer par journées entières dans l'ordre : entraînement jusqu'au 31 juillet 2025, validation août–septembre 2025, test octobre 2025–avril 2026. Vérifier aucune journée partagée et aucun résultat à 15 minutes ou après dans l'entrée. Pilote cinq manches pour parser/aligner, puis expérience complète depuis SQLite local et cache idempotent. Mesurer MAE en or et intervalle bootstrap regroupé par journée sur la différence des erreurs test, sans choisir une nouvelle variante après le test. Décrire explicitement le caractère omniscient des écarts de lane et la confondance patch/adversaire/roster. Publier seulement agrégats, code et figure ; pas de lignes individuelles ni de game IDs. Si l'historique n'améliore pas le test, le garder comme hypothèse réfutée dans cette forme et expliquer pourquoi des replays/POV alignés restent nécessaires.

# M14 — Porte 90 % exacte et reconnaissance de l'incertitude (2026-10-11)

La cible reste **une seule case 8×8 exacte à la prochaine minute observée**, sur les transitions Faker. Une liste de 40 cases, une classe majoritaire et un score d'événement ne satisfont pas ce critère. En complément du score sur 100 % des transitions, mesurer si le modèle sait s'abstenir sur les cas incertains : précision exacte parmi les cas servis **et part des cas servis**. Le seuil opérationnel à étudier exige au moins 10 % des transitions et 50 décisions sur la moitié de calibration, avec borne inférieure Wilson 95 % ≥ 90 %. La même condition doit tenir sur l'autre moitié de matchs ; aucune sélection par frame.

Utiliser le checkpoint M3 déjà choisi, sans le réentraîner ni consulter le test historique ou le futur lockbox. Vérifier son SHA-256, le schéma, les splits et l'alignement. Pilote cinq parties avant les 46 de validation. Deux plis de 23 matchs : chaque moitié choisit un seuil de confiance sur ses seuls labels, puis l'applique à l'autre. Rapporter en plus des couvertures fixes 5/10/20/50/100 % et l'exactitude par phase. **Limite majeure : le checkpoint et son poids de prior ont déjà été sélectionnés sur ces 46 matchs ; ce diagnostic est exploratoire et ne peut certifier 90 %.** Un futur modèle doit être sélectionné sans regarder un nouveau lockbox d'au moins 100 parties.

Tenter un nouveau snapshot Riot horodaté pour mesurer l'arrivée de parties strictement postérieures au gel M0. Si la clé a expiré, garder le statut de collecte `blocked_by_key`, ne jamais avancer le compteur ni ouvrir le score prospectif. Publier uniquement agrégats, figure, site, README/RESULTS/ROADMAP et tests ; les prédictions individuelles, IDs et clé restent locaux. L'expérience guidera la collecte de POV/replays horodatés nécessaires à une cible sous la minute.
