# Shadow Faker — journal d'avancement

## M22 — carte du rejeu et lecture des traces (2026-10-11)

- [x] Audit de départ : le lecteur servait un carré schématique, trois lanes et des points anonymes ; le flux possédait les timestamps mais ne conservait que la case 64×64 des lieux d'événement. La minimap officielle Data Dragon `map11.png` version 16.20.1 est accessible et correspond à l'atlas de sprites déjà épinglé. Le patch de l'art ne représente pas tous les patchs historiques.
- [x] Export causal des lieux : `xy` normalisé ajouté à la trace v9, `cell64` conservée en repli, champ absent laissé à `null`. Les événements d'achat et compétence à `participantId=0`, détectés dans une ouverture réelle, sont écartés du flux. Trois tests de frontière/causalité/cache réussis. Cinq traces pilotes (3 train, 2 validation) reconstruites depuis les caches, respectivement 16/25/30/26/28 frames et 37/85/65/77/73 événements avec lieu ; aucune requête Riot.
- [x] Rejeu refondu sur la minimap officielle épinglée : dix portraits issus de l'atlas déjà présent, anneaux d'équipe, vie au dernier relevé, halo métrique autour de Faker, fosses statiques, icônes distinctes pour combat/objectif/vision/économie et flux cliquable. Les traces de Faker sont affichées par défaut ; un contrôle ouvre les dix joueurs, 2/4/8 frames et 15/60/180 secondes d'événements. Les traces restent uniquement entre relevés déjà passés.
- [x] Direction visuelle étendue : texture de Faille sous l'atlas pixel, sur le sol de la surface 3D et de l'écosystème, et dans la carte de pression ; portraits cohérents dans cette dernière ; cadres et palette des panneaux unifiés ; jauge 8×8/min à côté du repère 90 % sans changer les scores. `VISUAL_SYSTEM.md`, REPLAY, PRESSURE et README FR/EN documentent la source, les horloges et les limites.
- [x] Cinq parties pilotes (3 train, 2 validation) ouvertes dans le navigateur : 10 portraits et fond chargés pour chaque partie, traces v9 servies sans erreur. À 07:44.217, 4 lieux d'événement et 10 portraits sont affichés ; fenêtre 15 s : 1 lieu, 180 s : 4 ; masquer les traces retire tous les liens et masquer les adversaires ramène à 5 portraits. À 02:21.023 la mort de Faker reste absente, à 02:21.024 elle apparaît. Lecture mobile sans débordement horizontal et anglais vérifié. Reste la QA finale des autres onglets et la publication.
- [x] QA finale des autres vues : la carte officielle et les densités de l'atlas sont visibles ensemble ; le sol 3D et celui de l'écosystème reçoivent une texture projetée ; Pression montre la Faille et dix portraits ; la jauge des scores affiche l'archive 8×8/min à 17,49 % face au repère 90 %. Sur les cinq onglets atlas/3D/pression/scores/rejeu à 390 px, aucun débordement horizontal. Dans le rejeu final, profondeur 2 = 10 liens pour dix joueurs, 4 liens pour Faker seul ; les libellés FR/EN et le flux sont cohérents. Console navigateur : zéro erreur. Python : **64 tests réussis** ; JS valide, `git diff --check` valide, liens locaux des cinq documents contrôlés.
- [x] Publication du lot testé sur `main` via la connexion GitHub après l'échec du push HTTPS local sans identifiant (`Device not configured`). Les 14 blobs envoyés ont chacun le même SHA que le commit Git local ; l'arbre distant `ad314a1026b27c54a8ed3147804e05c460751ff5` est identique à l'arbre testé. Commit distant `33efeb595c4364749c189a72907182590ca9f87f` vérifié par fetch et diff, branche locale réalignée. Cette ligne de clôture est publiée séparément.

## M21 — rejeu analytique et scénarios (2026-10-11)

- [x] Audit initial de cinq ranked (3 train, 2 validation) : 130 frames, 6 106 événements bruts dont 20 à la première frame ; trois événements se trouvent exactement sur une frontière de frame dans le conteneur suivant. Aucun acteur sans coordonnées dans ce pilote. Le lecteur est corrigé pour attribuer les événements par leur propre timestamp et préserver les événements présents dès `t=0`.
- [x] Contrôles du rejeu renforcés : horloge à la milliseconde, synchronisation avec la minute commune, navigation précédent/suivant événement, filtres et visibilité des couches, état observé des dix joueurs. Le résultat final reste dans une fiche pliée ; les positions ne sont jamais interpolées.
- [x] Challenge synthétique : réponse adverse retardée également pour « cinq Faker », basée sur l'allocation passée ; schéma du fichier public porté à v2. Les sorties ne sont pas des probabilités de victoire.
- [x] Audit complet des 465 parties : 12 975 frames, 129 750 emplacements de joueurs avec coordonnées présentes, 563 198 événements bruts, 1 794 à la première frame, 30 frontières dans le conteneur suivant. Zéro frame à horodatage non croissant. Agrégat seul publié dans `docs/data/public_replay_audit.json` ; script relançable avec pilote `--limit 5`.
- [x] Cinq traces pilotes (3 train, 2 validation) générées en version 7 puis rappelées sans réécriture ; l'empreinte couvre checkpoint, NPZ, match et timeline, manifeste et méta du split. Tests Python complets : 64 réussites ; syntaxe JS/Python et `git diff --check` réussis.
- [x] Vérification dans le navigateur : à 02:21.023 la mort de Faker n'est pas visible, à 02:21.024 elle l'est ; raccourci d'événement, filtres, couches, roster, frise commune à 10 MIN, disposition mobile 390 px sans débordement. Routes privées inconnues retournent HTTP 404. README FR/EN, REPLAY et laboratoire des scénarios actualisés.
- [x] Le panneau d'audit apparaît en FR/EN avec les quatre volumes et leurs limites. Dans le Challenge v2, à 10 min « cinq Faker » affiche `TOP 1:0, MID 1:1, JUNGLE 2:1, BOT 1:3` quand l'adversaire réagit après 10 min à la formation bot précédente ; à 20 min la réaction suit la formation jungle de 10 min. La composition libre conserve cinq joueurs par camp. Changer de partie repart désormais à `t=0`, même si la frise était à 12 min ; vérifié dans le navigateur.
- [x] Validation finale locale : 64 tests Python, syntaxe JS/Python, `git diff --check`, liens locaux dans six documents, routes publiques/privées et sélecteur de partie vérifiés. Le navigateur affiche le rejeu en français sur une partie de démonstration ; le serveur reste sur `127.0.0.1:8008`.
- [x] Publication du lot vérifié sur `main` via la connexion GitHub après l'échec du push HTTPS local sans identifiant (`Device not configured`). Les 17 blobs envoyés ont chacun été comparés à leur SHA Git ; commit distant `d730d14fc3a129fdd8a85eef33ab48ca15fc516d`, arbre `620a14c7d5faef5e1df4fef2f7125d8a5921eab5`, identique à l'arbre local testé. Fetch et comparaison du diff réussis, puis branche locale alignée sur `origin/main`. Cette ligne de clôture est publiée dans un second commit documentaire.

## M20 — atlas de preuves et feuille de route 90 % (2026-10-11)

- [x] `PLAN.md` fixe le contrat de cette phase : graphiques issus d'agrégats, pilote de cinq parties, aucune ligne de match ou étiquette test publiée, et seuil de 90 % réservé à une cible exacte préspécifiée.
- [x] `scripts/render_roadmap_evidence.py` lit la base IoC en mode lecture seule. Le pilote original de trois matchs train et deux validation a **420 + 317 = 737 fenêtres** ; l'exécution complète a **58 974 train + 7 480 validation**. Comptes et split concordent avec le registre public ; aucune donnée test n'est parcourue par le calcul des nouvelles distributions.
- [x] Trois figures SVG et `public_roadmap90.json` générés : densité des sept labels, âge des positions dans chaque fenêtre, écart de la case unique 8×8 au seuil hypothétique de 90 %. Figures vérifiées visuellement ; unités, population et limites inscrites dans chaque visuel.
- [x] README FR/EN, `MODEL_90_ROADMAP.md`, registre IoC, résultats, inventaire et roadmap enrichis de trois graphiques, d'un tableau AP/prévalence par acte, de la séparation actes/issues, des deux horloges et d'une trajectoire M21–M24 avec portes d'arrêt. Le tableau cassé des finales dans `CORPUS.md` est réparé.
- [x] Génération reprise depuis la base privée, 62 tests Python passés, compilation `src`/`scripts`, `git diff --check`, neuf Markdown contrôlés sans lien local cassé ; comptes, âges et absence d'ID Riot dans l'agrégat vérifiés. Les trois SVG ont été rendus et inspectés ; `.env`, SQLite et JSONL restent ignorés par Git.
- [x] Publication sur `main` via la connexion GitHub après refus d'identifiants du push HTTPS local (`Device not configured`). Chacun des 16 blobs a été vérifié par son SHA Git ; commit distant `87c12d09510f1bb806e56dbc9819b3a49a0993e8`, arbre `9546973bebf8955961b5917ec846531b38217e7a`, identique à l'arbre local testé après fetch. Ce journal de clôture est publié dans un second commit documentaire.

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
- [x] Collecte cible `--limit 1000 --epochs 25` terminée avec tout l'historique disponible. Journaux locaux exclus de Git.

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
- [x] 470 IDs disponibles via l'API, 465 parties exploitables ; comparaison aux baselines effectuée. L'objectif de ~1 000 n'est pas atteignable depuis cet historique de compte au jour de la collecte.
- [x] Audit sur une partie Vi : `jungleMinionsKilled` était séparé de `minionsKilled` dans les frames. CS corrigé pour tous les joueurs, schéma passé à v3 ; collecte interrompue puis reprise à partir du cache (39 timelines déjà présentes, aucun JSON à retélécharger).
- [x] Pagination complète : l'API ne renvoie que 470 IDs ranked solo (page 400 = 70 IDs, puis fin). L'objectif « ~1 000 » est impossible avec l'historique actuellement disponible pour ce PUUID. La barre de progression a été corrigée pour refléter les IDs effectivement disponibles ; les 45 timelines déjà en cache sont conservées.
- [x] Trois PDF fournis par l'utilisateur lus et analysés dans `RESEARCH_NOTES.md`. Le papier Applied Sciences motive l'ajout de l'écart d'XP entre équipes et d'événements Baron/Herald ; le diagnostic par patch répond au risque de score agrégé masquant la dérive. Le schéma passe à v4. La sélection d'événements basée sur `t+1` est écartée des entrées pour éviter une fuite du futur. Les deux autres articles portent sur les LLM et ne sont pas présentés comme validation de ce modèle de jeu.
- [x] Pilote indépendant sur 90 matches (2 404 observations, schéma v4) : top-1 région 0,0610 contre 0,0854 pour la baseline région fréquente ; copie 0,0569. Diagnostic : la perte fortement pondérée semble sous-prédire les régions centrales fréquentes (région 119 = 198/1 923 observations train). La perte région devient 30 % pondérée + 70 % non pondérée pour conserver le traitement du déséquilibre sans sacrifier la top-1 ; nouvel essai lancé sur le même split.
- [x] Second pilote sur les mêmes 90 matches : top-1 région 0,0650, top-5 0,1748 ; légère amélioration mais encore sous la baseline 0,0854. Le corpus final disponible reste nécessaire.
- [x] Clarifications utilisateur intégrées : la cible est exclusivement l'action de Faker ; les rôles alliés sont identifiés et ordonnés (jungle, bot, support, mid, top), avec signaux de wards, kills et variations or/XP. Les dix positions sont conservées en vue macro complète, mais le modèle par défaut utilise un proxy de minimap qui masque les ennemis éloignés des alliés. Riot ne fournit pas visibilité exacte, coordonnées de wards, pings ni communication ; ils ne sont pas inventés.
- [x] Analyse descriptive des rotations par phase, rôle et issue ajoutée ; une tête auxiliaire estime l'issue finale sans l'utiliser en entrée. Cette estimation ne prouve aucun effet causal d'une action. Le schéma versionné passe à v6 ; tests synthétiques de bout en bout réussis.
- [x] Piste replay étudiée : aucun client LoL/`.rofl`/VOD LoL présent, Replay API locale indisponible. Support Riot : replays du patch courant, 20 dernières parties, sans chat. `REPLAY_FEASIBILITY.md` décrit l'export vidéo via l'API Replay officielle, l'alignement timeline et la validation des annotations de minimap/wards/pings ; aucune observation visuelle ou communication n'est prétendue disponible pour les 470 parties actuelles.
- [x] Pilote 200 matches, schéma v6 et vue minimap proxy : 5 274 observations, 20 matches test, top-1 région 0,0845 contre 0,0786 pour la meilleure baseline ; top-5 0,2927. L'achat reste sous la baseline « aucun achat » (0,4853 contre 0,5403) et la tête de victoire sous la prévalence constante (Brier 0,3090 contre 0,2607).
- [x] Diagnostic achats : `currentGold` est présent dans les timelines brutes, mais absent de la première représentation. Ajout de l'or non dépensé, de la proximité de la base, des morts récentes et des variations de niveau/or de Faker ; schéma v7. Nouveau pilote 200 matches lancé avant l'entraînement final.
- [x] Second pilote 200 matches, schéma v7 : top-1 région 0,0845, top-5 0,2986 ; achat 0,5187 contre baseline « aucun achat » 0,5403. L'issue auxiliaire reste non calibrée (Brier 0,3542 contre constante 0,2607) ; ne pas la présenter comme un estimateur causal.
- [x] Analyse enrichie : proximité Faker–jungler/bot/support et variation d'écart d'or/XP dans les deux minutes suivantes, comparées descriptivement aux minutes éloignées, agrégées par match, phase et issue. Les positions absentes sont exclues ; interprétation non causale explicite.
- [x] Sélection de la configuration déplacée vers le split validation ; le test final n'est exécuté qu'après ce choix. Les deux pilotes antérieurs ont servi au développement des features, donc leurs scores restent exploratoires.
- [x] Recherche complémentaire sur entraînements dans StarCraft II (AlphaStar et Unplugged), Dota 2 (OpenAI Five), Atari (Decision Transformer) et Minecraft (VPT/MineRL). Sources primaires et implications exploitables consignées dans `OTHER_GAMES_RESEARCH.md` ; self-play et RL hors ligne ne sont pas présentés comme réalisables depuis 470 timelines seules.
- [x] Travaux MOBA hiérarchiques et macro-goals lus : intégration expérimentale de distances rôle par rôle et Dragon/Baron dans les états, en cohérence avec les cibles « où aller »/« quelle ressource » ; schéma v8, pilote 200 matches relancé. Corpus TLoL de replays décodés identifié comme référence potentielle, sans transfert aveugle des anciens patches/ADC au style Faker.
- [x] Objectif utilisateur « Shadow Faker à 110 % » cadré dans `SHADOW_PLUS.md` : fidélité mesurable maintenant, supériorité de jeu exigeant valeur conditionnée à l'action, support hors ligne et parties jouées. IQL, CQL et AWR documentés comme voies expérimentales, sans confondre la tête actuelle de victoire avec une estimation causale d'action.
- [x] Revue multilingue initiale de sources publiques : VOD officielle Worlds 2024, vidéo T1 de communications en coréen, entretien direct Inven en coréen et traduction anglaise, commentaires Reddit. Provenance, statut « lu » vs « localisé », domaine pro vs solo queue et contrat d'annotation consignés dans `PUBLIC_GAME_ANALYSIS.md`. Recherche X peu concluante ; aucun commentaire non vérifié n'a été converti en label.
- [x] Collecte cible terminée : 470 IDs disponibles, 465 matches exploitables, cinq remakes exclus, zéro erreur de parse ; schéma v8, 12 510 observations, split 373/46/46 matches train/val/test. Pipeline complet lancé. L'évaluation ajoute un intervalle bootstrap apparié par match pour le gain top-1 contre la meilleure baseline.
- [x] Premier entraînement complet : validation top-1 0,0941 contre baseline 0,0808, mais test 0,0977 contre baseline 0,1128 (gain −1,50 point ; bootstrap 95 % de −3,33 à +0,43). Le critère final n'est pas satisfait. Diagnostic : répartition de rôle différente (65 % mid en validation, 82 % en test) et région 119 plus fréquente en test.
- [x] Prior spatial par rôle et phase ajouté depuis les matches train, l'interpolation et le lissage choisis sur validation. Sur le checkpoint initial, validation top-1 0,1059 contre la meilleure baseline enrichie à 0,0902, gain 1,57 point avec bootstrap apparié 95 % de +0,40 à +2,57. Test de cette variante : 0,1128 contre la baseline prior à 0,1161 ; le critère final n'est pas satisfait. Le test de la variante retenue reste exploratoire après la première consultation du test.
- [x] Ablation sans pondération de classe région : validation calibrée top-1 0,1028 ; moins forte que la variante mixte sur le split de sélection. Variante mixte restaurée. Essai de largeur 192, trois couches, LR 0,001 lancé sans fuite du test dans la sélection.
- [x] Variante large (1 424 292 paramètres, CPU plus rapide que MPS : 0,192 s contre 1,278 s au mini-benchmark) : arrêt anticipé à 15 époques, meilleure perte à l'époque 10 ; top-1 région calibrée en validation 0,1020, sous le modèle compact à 0,1059. Modèle compact retenu.
- [x] Calibrage de la classe « aucun achat » et « pas de compétence » sur validation : modèle compact 0,5969 achats contre baseline 0,5678 ; 0,5631 compétences contre baseline « aucune » 0,4776. Sur test : achats 0,5881 contre 0,5530 ; compétences 0,5530 contre 0,4703. Le score d'achat conditionnel à un achat réel reste faible (0,1009).
- [x] Test après cette sélection : top-1 région 0,1128, top-5 0,3358, région la plus fréquente 0,1128, prior rôle/phase 0,1161 ; gain contre la meilleure baseline −0,334 point, IC bootstrap 95 % [−1,513 ; +0,868]. L'issue auxiliaire obtient Brier 0,2242 contre 0,2505 pour la prévalence constante ; cela n'établit pas la valeur d'une action. Variante spatiale supplémentaire lancée ensuite sur le split validation.
- [x] Variante spatiale explicite (~538 790 paramètres) : direction de déplacement apprise depuis la position présente, arrêt anticipé à 20 époques ; top-1 validation calibré 0,1051 contre 0,1059 pour le modèle compact. Non évaluée sur test, modèle compact restauré.
- [x] Diagnostic additionnel : tableau de transitions spatiales conditionné par région actuelle/rôle/phase, ajusté sur train, 0,1075 sur validation seul. Une recherche large d'interpolation atteint 0,1082 (trois exemples de plus que le compact sur 1 275) ; gain minuscule et exploratoire, donc non promu ni évalué sur test.
- [x] Distance spatiale ajoutée à l'évaluation : sur test, erreur moyenne 4,37 cases pour le modèle compact contre 3,99 pour la région fréquente et 3,97 pour le prior rôle/phase. Cela confirme que le top-1 faible n'est pas simplement une erreur de case voisine.
- [x] Vérification finale locale : `pytest -q` = 4 tests passés ; relance de la commande complète depuis le cache, 465 matches repris, checkpoint réutilisé, métriques et GIF régénérés en quelques secondes. `RESULTS.md` documente le critère de performance non atteint sans masquer la première consultation du test.
- [x] Lecture descriptive des 465 matches : proximité support en milieu de partie 23,1 % des minutes dans les parties gagnées contre 21,0 % dans les perdues ; proximité Dragon 11,5 % contre 9,5 % ; proximité bot après 20 min 34,7 % contre 32,2 %. Jungle en début de partie 23,2 % contre 22,3 %. Les écarts sont petits, non corrigés des situations de jeu et ne démontrent aucun effet causal.
- [x] Phase 2 : fetch cinq parties, puis totalité des parties disponibles.
- [x] Phase 3 : parse et split par match.
- [x] Phase 4-5 : benchmark et entraînement.
- [x] Phase 6 : évaluation et baselines.
- [x] Phase 7 : GIF.
- [x] Phase 8 : README international, résultats honnêtes, validation finale et publication des changements sur `main`.
- [x] Publication initiale des analyses et du pipeline enrichi sur `main` : commit `884404abd5316eb0f508df9d178d94ae889ce1e0`, référence distante vérifiée identique et arbre de travail propre après synchronisation. Seuls les fichiers de code/documentation ont été publiés ; `.env`, `data/`, `models/`, `runs/` et `artifacts/` restent locaux et ignorés.
- [x] Suite au bilan, audit à résolution macro sans réentraînement : probabilités 16×16 regroupées en 8×8 et 4×4, baselines recalculées à chaque grille, bootstrap apparié par match. Sur le test déjà consulté, 8×8 : 0,1754 contre meilleure baseline 0,1537, gain +2,17 points [0,09 ; 4,22] ; 4×4 : 0,2364 contre 0,1980, gain +3,84 points [0,25 ; 6,13]. Intervalles validation contenant zéro et choix de métriques après examen du test : résultats exploratoires, pas une nouvelle preuve indépendante ni une réparation du critère 16×16. Prochaine étude : métriques macro préspécifiées sur de nouvelles parties non vues.
- [x] Après l'audit macro : `pytest -q` toujours 4/4 ; relance de la commande complète depuis le cache réussie, sans nouvel entraînement ni appel réseau pour les matches déjà cachés. `RESULTS.md` et README actualisés.

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

- [2026-10-09T20:53] Fetch 5: 39 usable ranked matches cached.

- [2026-10-09T20:53] Parse 5: 5 matches, 136 observations, 0 errors.

- [2026-10-09T20:53] Train 5: 3 epochs, device cpu, 516133 parameters.

- [2026-10-09T20:53] Evaluate 5: region top-1 0.0435, best baseline 0.0870.

- [2026-10-09T20:53] Demo 5: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T20:54] Fetch 5: 45 usable ranked matches cached.

- [2026-10-09T20:54] Parse 5: 5 matches, 136 observations, 0 errors.

- [2026-10-09T20:54] Train 5: 3 epochs, device cpu, 516133 parameters.

- [2026-10-09T20:54] Evaluate 5: region top-1 0.0435, best baseline 0.0870.

- [2026-10-09T20:54] Demo 5: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T20:56] Fetch 5: 94 usable ranked matches cached.

- [2026-10-09T20:56] Parse 5: 5 matches, 136 observations, 0 errors.

- [2026-10-09T20:56] Train 5: 3 epochs, device cpu, 516773 parameters.

- [2026-10-09T20:56] Evaluate 5: region top-1 0.0435, best baseline 0.0870.

- [2026-10-09T20:56] Demo 5: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T21:13] Fetch 5: 5 usable ranked matches available for this stage.

- [2026-10-09T21:13] Parse 5: 5 matches, 136 observations, 0 errors.

- [2026-10-09T21:13] Analyze 5: proximity by role/phase/outcome from 5 matches.

- [2026-10-09T21:13] Train 5: 3 epochs, device cpu, 522278 parameters.

- [2026-10-09T21:13] Validate 5: region top-1 0.0455, best baseline 0.0909.

- [2026-10-09T21:13] Demo 5: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T21:13] Fetch 1000: 465 usable ranked matches available for this stage.

- [2026-10-09T21:13] Parse 1000: 465 matches, 12510 observations, 0 errors.

- [2026-10-09T21:13] Analyze 1000: proximity by role/phase/outcome from 465 matches.

- [2026-10-09T21:17] Train 1000: 25 epochs, device cpu, 538532 parameters.

- [2026-10-09T21:17] Validate 1000: region top-1 0.0941, best baseline 0.0808.

- [2026-10-09T21:17] Demo 1000: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T21:17] Final test 1000: region top-1 0.0977, best baseline 0.1128.

- [2026-10-09T21:32] Fetch 1000: 465 usable ranked matches available for this stage.

- [2026-10-09T21:32] Parse 1000: 465 matches, 12510 observations, 0 errors.

- [2026-10-09T21:32] Analyze 1000: proximity by role/phase/outcome from 465 matches.

- [2026-10-09T21:32] Train 1000: 25 epochs, device cpu, 538532 parameters.

- [2026-10-09T21:32] Calibrate 1000: train-only role/phase spatial prior, alpha 0.75, validation accuracy 0.1059.

- [2026-10-09T21:32] Validate 1000: region top-1 0.1059, best baseline 0.0902.

- [2026-10-09T21:32] Demo 1000: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T21:32] Final test 1000: region top-1 0.1128, best baseline 0.1161.

- [2026-10-09T21:34] Fetch 1000: 465 usable ranked matches available for this stage.

- [2026-10-09T21:34] Parse 1000: 465 matches, 12510 observations, 0 errors.

- [2026-10-09T21:34] Analyze 1000: proximity by role/phase/outcome from 465 matches.

- [2026-10-09T21:34] Train 1000: 25 epochs, device cpu, 538532 parameters.

- [2026-10-09T21:34] Calibrate 1000: train-only role/phase spatial prior, alpha 0.75, validation accuracy 0.1059.

- [2026-10-09T21:34] Validate 1000: region top-1 0.1059, best baseline 0.0902.

- [2026-10-09T21:34] Demo 1000: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T21:34] Final test 1000: region top-1 0.1128, best baseline 0.1161.

- [2026-10-09T21:34] Performance gate unmet: test region gain is not clearly above the strongest baseline.

- [2026-10-09T21:45] Fetch 1000: 465 usable ranked matches available for this stage.

- [2026-10-09T21:46] Parse 1000: 465 matches, 12510 observations, 0 errors.

- [2026-10-09T21:46] Analyze 1000: proximity by role/phase/outcome from 465 matches.

- [2026-10-09T21:46] Train 1000: 25 epochs, device cpu, 538532 parameters.

- [2026-10-09T21:46] Calibrate 1000: train-only role/phase spatial prior, alpha 0.75, validation accuracy 0.1059.

- [2026-10-09T21:46] Validate 1000: region top-1 0.1059, best baseline 0.0902.

- [2026-10-09T21:46] Demo 1000: predicted_vs_actual.gif generated from held-out test match.

- [2026-10-09T21:46] Final test 1000: region top-1 0.1128, best baseline 0.1161.

- [2026-10-09T21:46] Performance gate unmet: test region gain is not clearly above the strongest baseline.

## Suite autonome — protocole prospectif et actions macro (2026-10-09)

- [x] `ROADMAP.md` fixe les étapes M0–M5 et les conditions de passage : fidélité macro avant toute prétention de « Shadow Plus » ; test 16×16 d'origine toujours reporté séparément.
- [x] Protocole local M0 gelé : 465 matches source, cutoff strict au 2026-10-01 13:22:43 UTC, checkpoint et méta copiés avec SHA-256, baseline train figée, seuil **100** nouveaux matches. Une évaluation prospective ne peut s'exécuter avant ce seuil et son résultat est ensuite caché pour ne pas multiplier les consultations.
- [x] Collecteur M1 : pages d'IDs dans un instantané nommé, réponses match/timeline conservées en cache ; parsing seulement des matches du même PUUID dont l'heure de début dépasse le cutoff. Reprise et déduplication vérifiées sur les tests synthétiques.
- [x] Premier instantané réel `20261009-freeze1` : cinq pages Riot reçues (470 IDs, toujours 465 parties utilisables), clé valide, **0/100 nouveau match**. Le score prospectif est `pending`, aucune accuracy n'a été calculée sur un pseudo-nouveau test.
- [x] M2 pilote cinq parties puis corpus complet : huit tags observables et masques de validité (approche jungle/bot/support/mid/top/Dragon/Baron, retour base). 465 matches et 12 510 observations traités, zéro erreur ; les tags dérivent du mouvement vers les positions **connues au temps t**, sans attribuer d'intention ni d'effet causal. Taux par phase disponibles dans `data/processed/macro_actions/meta.json` local.
- [x] Tests après M0–M2 : `pytest -q` passe (4 tests), y compris le gel, l'attente sous le seuil, le score une seule fois sur de nouvelles parties synthétiques, l'alignement des tags et leur reprise sans recalcul.
- [x] Visualisation : deux figures PNG calculées sur des agrégats publics (`docs/data/public_summary.json`) — scores 16×16/8×8/4×4 contre meilleures baselines, et rapprochement de Faker vers les rôles alliés par phase. Le générateur peut repartir des seuls agrégats publics ; aucune trace par match n'est publiée. Inspection visuelle des figures effectuée.
- [x] README anglais/français, résultats, plan, roadmap, protocole et notes de recherche reliés aux figures et à des diagrammes Mermaid. Les métriques choisies après consultation du test restent identifiées comme exploratoires.
- [x] M3 pilote : ajout d'une perte auxiliaire 8×8 calculée par regroupement probabiliste des 256 régions, sans changer les entrées ni le checkpoint figé. Test unitaire du regroupement et entraînement sur cinq parties synthétiques ; suite de tests complète : **5 passed**.
- [x] M3 corpus complet : variante avec perte auxiliaire 8×8 entraînée pendant 25 époques, 538 532 paramètres, seed 42, dans `models/macro8-v1/` (ignoré de Git). Le mini-benchmark était CPU 0,111 s contre MPS 0,736 s : CPU retenu. Sur validation, 8×8 **17,10 %** contre meilleure baseline **15,45 %**, écart +1,65 point et intervalle bootstrap 95 % **[−0,16 ; +3,42]** points. Le modèle déjà figé fait **17,33 %** sur cette validation : la nouvelle variante ne l'améliore pas et **n'est pas promue ni évaluée sur le test**. Aucun checkpoint figé n'a été remplacé.
- [x] Audit de formation : pilote cinq parties, puis 465 parties complètes sans erreur. Parmi 3 255 frames valides entre les minutes 3 et 10, cinq alliés se trouvent à moins de 2 500 unités du bot carry dans **une seule frame, sur une seule partie** ; le rapprochement n'établit pas une stratégie « cinq bot ». Agrégats publics, traces par match locales et ignorées.
- [x] Documentation visuelle : README anglais et français avec bannières générées, surface 3D observé/prédit, cartes, score, tempo, formation, diagrammes Mermaid et liens vers le tableau de bord. `DIAMOND.md` distingue espace, tempo, équipe, ressources, vision, exécution, risque, histoire et conséquences ; l'objectif sous la minute y reste explicitement futur.
- [x] Tableau de bord local FR/EN : cartes avec lecture de case, surface isométrique orientable, curseur de tempo, scores et échelle de preuve. Export d'un rejeu test de 26 minutes dans `artifacts/` (JSON et PNG locaux ignorés), avec heatmap de prédiction, positions alliées, destination observée, choix Shadow, or/XP et courbe rétrospective. Interface inspectée dans le navigateur : changement FR/EN, surface observée/prédite, angle et curseur de rejeu opérationnels. Le serveur ne sert que des chemins autorisés sur `127.0.0.1`.
- [x] Vérification finale locale : `pytest -q` **5 passed** ; `node --check dashboard/app.js`, compilation Python, `git diff --check` et rendu des figures depuis les agrégats publics passent. Bannière française SVG inspectée visuellement ; surface 3D PNG inspectée. Routes publiques et visuels répondent HTTP 200 ; accès direct à `data/raw/`, `.env` et traversée de chemin répond HTTP 404. Checkpoint figé et original : même SHA-256 `869c468880650a556ad4f31d1297daba410e842fb06ff38bc6b80e9e81c780f7`. Aucun résultat prospectif ni score sous la minute n'a été inventé.
- [x] Publication du code, des documents, du tableau de bord et des agrégats sur GitHub `main` via le connecteur authentifié : commit `31f5098ec2b8a76807824adec587c403b3d34f76`, arbre `39c9343f26e59545cf5bc4b53b5fff96bbf2dc9f`. `git ls-remote` et `git fetch` confirment le ref distant ; copie locale réconciliée et propre. Le refus d'authentification du `git push` HTTPS local n'a pas empêché la publication. Aucune donnée brute, clé, trace par partie ou poids du modèle n'est dans ce commit.
## Extension 64×64 et événements — 2026-10-09

- [x] Plan et risques écrits dans `PLAN.md` avant calcul. État initial : `main` propre, modèle historique 16×16 figé. Vérification Riot live : la première page ranked solo fraîche contient 100 IDs mais **aucun nouvel ID** par rapport au cache ; la première page toutes queues du même PUUID contient **19 IDs absents du corpus ranked**. Une exploration complète et une classification par queue sont nécessaires avant d'appeler cela « plus de games ».
- [x] Inspection d'une timeline locale : les kills portent `position` et un timestamp ; Dragon et Void Grubs apparaissent comme `ELITE_MONSTER_KILL`, ces derniers avec `monsterType=HORDE`. Certaines wards et autres événements n'ont pas de position. L'atlas n'inventera pas de coordonnées pour eux.
- [x] Exploration API étendue avec cache et quota persistant : **519 IDs** du même PUUID toutes queues, contre 470 en ranked solo. Les 49 autres matches sont 42 en queue 1750, 5 en 1740, 1 en 1700 (cartes 30) et 1 en 710 (carte 11, mode distinct). Match JSON et timeline des 49 conservés localement ; **49/49 timelines cachées**. Aucune nouvelle partie ranked solo queue 420, aucune partie supplémentaire comparable n'entre dans l'entraînement ou le test. Le modèle 64×64 se nourrit donc encore des 465 ranked validées ; la valeur documentaire des autres modes reste séparée.

- [2026-10-09T21:33:26+00:00] Five-game atlas, warehouse, pressure, interaction and text pilot passed.

- [2026-10-09T21:33:31+00:00] Next-level five-game pilot reused from checkpoint.

- [2026-10-09T21:33:34+00:00] 64x64 labels: 465 matches, 12510 pairs, 0 errors.

- [2026-10-09T21:33:37+00:00] Event atlas: 465 ranked matches, 0 errors.

- [2026-10-09T21:33:37+00:00] Warehouse: 12975 states, 12510 transitions, 353409 events.

- [2026-10-09T21:33:38+00:00] Enemy pressure: 12975 positional frames.

- [2026-10-09T21:34:19+00:00] Text: 930 EN/FR summaries, 0 errors.

- [2026-10-09T21:34:19+00:00] Vectors: 12510 states; kNN val exact64=0.0094.

- [2026-10-09T21:34:20+00:00] 64x64 historical test: 0.0109 exact, best baseline 0.0192; prospective claim pending.

- [2026-10-09T21:34:20+00:00] Interaction training states: 12510 pairs, 0 errors.

- [2026-10-09T21:34:21+00:00] Interaction candidate validation exact16=0.0871; test intentionally unscored.

- [2026-10-09T21:34:22+00:00] Dashboard aggregates, replay and public figures refreshed. Open http://127.0.0.1:8008/ with serve_dashboard.py.

## Écosystème et livraison Five Star Research Edition — 2026-10-09

- [x] Construction pilote cinq parties, puis corpus complet : `faker_states.sqlite` local contient **465 matches, 12 975 états, 12 510 transitions, 353 409 événements** ; matrice 4 096×4 096 sparse avec **11 450 cellules de transition occupées**. Aucune erreur de parsing. Les dix acteurs restent décrits autour de Faker ; aucun clic ou POV inventé.
- [x] Atlas 64×64 et événements : cinq parties d'abord, puis 465 ranked. Les 49 parties supplémentaires toutes queues ont leur match/timeline en cache mais appartiennent à d'autres modes ; **0 ranked solo supplémentaires**. Les agrégats distinguent positions réelles/prédites, ennemis, alliés, kills, morts, Dragon, Baron, Herald, Grubs, bâtiments, wards et événements sans coordonnées.
- [x] Entraînement 64×64 séparé et calibration sur validation. Test historique déjà consulté : **1,09 % case exacte** contre baseline forte **1,92 %** ; à quatre cases **22,89 %** contre copie de position **16,88 %**. Ensemble calibré pour 90 % : **91,90 % couverture** au prix de **43,72 % de la carte** (1 791 cases en moyenne). Aucune prétention de 90 % d'exactitude, ni confirmation prospective.
- [x] Pression et interactions : trajectoires adverses et proximités observées par phase ; 13 canaux causaux supplémentaires effectivement injectés dans une variante du transformer. Pilote cinq puis **465 parties / 12 510 paires / 0 erreur**. Entraînement 25 époques, 540 196 paramètres, seed 42 ; CPU choisi après mini-benchmark **0,108 s** contre MPS **0,631 s**. Validation 16×16 **8,71 %**, baseline fréquence **8,08 %**, modèle gelé **10,59 %** sur la même validation. Variante non promue, test non consulté.
- [x] Vecteurs : états 128-D de l'encodeur causal figé et matchs terminés 192-D rétrospectifs, tableaux mémoire-mappés pour les 12 510 paires et 465 parties. Le kNN k=25 obtient **0,94 % exact 64×64 en validation**, sous la baseline fréquence **1,25 %** ; résultat conservé comme diagnostic, pas victoire.
- [x] Index textuel local : **930 résumés déterministes EN/FR** pour les 465 ranked, plus deux notes sourcées de la partie professionnelle Nidalee–Kha'Zix de 2013. Les originaux UTF-8 d'autres langues peuvent être importés avec langue, provenance et statut. Aucun transcript externe non vérifié n'a été injecté. Correction historique : ce duel est un début professionnel de printemps, **pas un match Worlds**.
- [x] Interface fan-made rouge/noir/or, cinq étoiles sans affiliation T1/Riot : page d'accueil, atlas, métriques honnêtes, 3D des dix joueurs avec niveau en hauteur, champ local métrique, tableau des états t/t+1, timeline d'événements, recherche, partie choisie parmi 465 et scénarios synthétiques. Nouveau README EN/FR et documents `STATE_ECOSYSTEM.md`/`DESIGN.md` ; figures et schémas Mermaid liés.
- [x] Entrée reproductible `scripts/run_next_level.py` : relance le pipeline ranked de base si nécessaire, force un pilote cinq parties avant mise à l'échelle, exploite caches/checkpoints, renouvelle les agrégats et garde la variante d'interaction sur validation. Exécution pilote puis complète réussie sans erreur.
- [x] QA du tableau de bord via navigateur : **38** combinaisons atlas, **25** changements successifs du rejeu avec 25 états et images distincts, **45** combinaisons de scénarios, **8** tranches temporelles et **6** combinaisons surface/angle, soit **122 états interactifs vérifiés** avant recherche et ouverture d'une autre partie ; aucune erreur console. Recherche du cas Ambition : 2 langues trouvées. Autre partie ranked ouverte en **16 frames**. Les graphiques 64×64 ont été inspectés visuellement et leur contraste corrigé.
- [x] Contrôles de sécurité et de code : 38 **paires couche/phase uniques** confirmées par lecture DOM ; 12 tests pytest passent, vérification syntaxe JS, compilation Python et `git diff --check` passent. Routes publiques JSON/PNG et recherche répondent 200. Match non indexé, `.env`, `data/raw/` et accès traversant répondent 404. Reconstruction idempotente de la base : **0 match réécrit, 465 réutilisés du cache**.

## Frise commune, phase du modèle et code couleur — 2026-10-09

- [x] Reconstruction des prédictions/observations 64×64 **par phase** depuis le checkpoint local : **460 + 437 + 300 = 1 197** paires test. Chaque histogramme observé et prédit totalise ses exemples ; la somme des trois phases égale l'archive 64×64 initiale **dans chacune des 4 096 cases**. Le JSON agrégé public est passé au schéma 2 ; aucun détail de partie ajouté.
- [x] Frise persistante 0–39 min, utilisable au clavier et à la molette sur son curseur. Synchronisation dans les deux sens : atlas, surface 3D, tempo, pression, rejeu et repère du scénario synthétique. Légende globale et couche atlas colorée ; texte de provenance 46 parties test / 465 parties ranked / une seule partie rejouée. Les figures fixes et l'ancien modèle 16×16 sont signalés comme tels.
- [x] QA réelle dans le navigateur : **40 positions consécutives** avec vérification DOM de la phase, du total 460/437/300, de la surface, de la pression et du tempo ; changement de phase depuis l'atlas et changement de minute depuis le rejeu vérifiés ; légendes FR/EN vérifiées. **0 erreur console**. Le graphique de pression adapte maintenant son axe au maximum observé, de sorte que la phase tardive reste dans le cadre. Suite pytest : **12 passed** ; syntaxe JS et `git diff --check` passent.
- [x] Publication authentifiée sur `nabz0r/shadowfaker` **`main`** : commit de livraison `1497fc1385dfa20a6e9f8ddf0bb6ed3bb47bd346`, arbre `07c34d10a79a781985f387b461c7dd65839699e6`. Le ref distant a été vérifié par `git ls-remote`, puis récupéré localement ; contenu local et distant identique. Le dépôt ne contient ni clé Riot, ni JSON brut, ni trace de partie, ni poids du modèle.

## Vérification prospective — 2026-10-10

- [x] Nouvel instantané Riot `20261010` sur le même PUUID, queue 420 et région `asia` : cinq pages d'IDs retournent **100 + 100 + 100 + 100 + 70 = 470 IDs uniques** ; les 465 parties utilisables restent dans le cache. **0/100** partie strictement postérieure au cutoff gelé. Aucun score prospectif calculé et aucun nouveau label d'entraînement créé. La clé Riot a fonctionné pour cet appel ; prochain rafraîchissement selon disponibilité des parties et validité de la clé.

## M3 hiérarchique — 2026-10-10

- [x] Architecture, masques d'ablation et cibles macro spécifiés dans `PLAN.md` avant entraînement. Tête hiérarchique `8×8 → 16×16 → 64×64` à probabilités exactement cohérentes, cinq classes observables et huit tags masqués ; trois variantes de **même capacité, 732 782 paramètres** (Faker 24 canaux, +alliés 73, état complet 147). Pilote **cinq parties réelles** : 3 train/2 val, 71/54 paires, deux époques des trois variantes, alignement des labels sans erreur. Mini-benchmark CPU **0,0298 s** contre MPS **3,7706 s** sur le même sous-ensemble ; CPU retenu. Le score pilote est trop petit pour conclure. Trois tests ciblés passent : masques emboîtés, priorité/absence de position, normalisation et agrégation exacte des probabilités. Test ancien réservé ; aucune promotion M0 automatique.
- [x] Corpus M3 : 373 parties train (10 038 paires) et 46 validation (1 275), époques retenues 10/4/17 pour Faker seul/alliés/état complet. CPU choisi après mini-benchmark complet **0,0684 s** contre MPS **0,6053 s**. Lecture par lots groupés par partie : une époque environ 3 s au lieu de 10,6 s avec décompression aléatoire. Trois checkpoints locaux réutilisables ; aucune lecture du test ancien pour leur sélection.
- [x] Ablation brute 8×8 : **15,14 % / 14,98 % / 16,86 %** ; ajout des alliés seuls insuffisant, état complet supérieur à Faker seul de **+1,73 point**, IC bootstrap apparié par partie **[+0,16 ; +3,50]** sur la validation adaptative. Après prior rôle/phase entraîné sur train, poids choisi sur cette même validation : **17,10 % / 16,86 % / 17,49 %**. Meilleure baseline simple **15,29 %** ; gain du modèle complet +2,20 points, intervalle **[−0,16 ; +4,56]** contenant zéro. Ancien modèle gelé **17,33 %** 8×8 sur validation ; différence de point de 0,16 seulement, sans nouvelle preuve. Toutes les statistiques restent développement exploratoire.
- [x] Cinq classes de mouvement observables : F1 macro complet **44,9 %** contre règle majoritaire **16,5 %**, mais accuracy **68,6 %** contre **70,0 %** et retour base F1 **5,8 %** (50 exemples). Par phase, exact 8×8 **29,8 %** tôt / **13,1 %** milieu / **7,5 %** tard. Les entrées complètes incluent des informations globales possiblement invisibles à Faker ; aucune influence causale ni supériorité de jeu inférée.
- [x] Figure d'ablation rouge/noir/or vérifiée visuellement, résumé public strictement agrégé `docs/data/hierarchical_summary.json`, README EN/FR, résultats, roadmap et écosystème mis à jour. Le générateur régénère la figure depuis les seuls agrégats publics. Checkpoint M0 inchangé SHA-256 `869c468880650a556ad4f31d1297daba410e842fb06ff38bc6b80e9e81c780f7`; checkpoint M3 complet local `39abb02c5791531beff5b12bd6a0d82137575061a0e57c885af3b81bf93e9d05`. Le test prospectif reste **0/100** nouvelles parties.
- [x] Vérification M3 : **17 tests passent**, compilation Python, syntaxe JS, `git diff --check`, régénération depuis l'agrégat public et commande complète `scripts/run_next_level.py --epochs 25` réussissent. La commande réutilise les trois checkpoints M3, renouvelle la figure et termine sans erreur. Le protocole prospectif hors ligne répond `pending` **0/100** ; les deux copies du checkpoint M0 et le checkpoint M3 gardent leurs SHA-256 annoncés. Le code vérifie maintenant effectivement le hash M0 avant d'émettre son rapport M3.
- [x] Publication M3 sur GitHub `nabz0r/shadowfaker` **`main`** : commit de livraison `771bbc26c009d992da05778c270a6e471a026c24`, arbre `7f62a8693124975f172da7d8106ad0153247c019`. Les 13 blobs ont été comparés aux SHA Git locaux avant publication ; ref distant et arbre après récupération vérifiés identiques. Le JSON public est agrégé ; JSON Riot, .env, traces par partie et poids restent ignorés. Cette entrée est consignée dans un commit documentaire de suivi.

## M3b : diagnostic de prédictibilité et visibilité — 2026-10-10

- [x] Plan écrit avant les nouveaux calculs dans `PLAN.md` : audit d'alignement, référence de transition conditionnelle, masque de visibilité conservateur, comparaison par match sur validation de développement. Objectif 90 % maintenu comme question de recherche mesurable, sans changer silencieusement la cible 8×8 de la minute suivante.
- [x] Audit de géométrie : recalcul indépendant de la case 64×64 actuelle depuis `x`, comparé au label de case précédente ; **0 mismatch sur 10 038 paires train + 1 275 validation**, aucune position actuelle manquante. Aucune lecture du test pour sélectionner une règle. Référence de transition lissée choisie sur **75 matches internes au train** (298 fit/75 sélection), puis réajustée sur les 373 train : case actuelle + direction passée, lissage 64 ; **17,98 %** top-1 sur sélection interne, **15,69 %** top-1 et **39,76 %** top-5 sur validation historique. Copie de position : 10,98 % ; extrapolation 0,5× : 7,53 % ; 1× : 5,02 %. Pilote cinq parties (4 train/1 validation) vérifié. Pas d'amélioration sur M3.
- [x] Quatrième variante de même capacité 732 782 paramètres : **109 canaux** de visibilité approchée, contre 24 Faker seul, 73 Faker+alliés et 147 `x` proxy + champs globaux. Pilote cinq parties vérifié, puis entraînement complet et sélection uniquement sur validation. Le proxy atteint **16,71 % brut / 16,86 % calibré** en 8×8 et F1 macro décision **42,5 %** ; les 147 canaux atteignent **16,86 % / 17,49 %**, F1 macro **44,9 %**. Différence calibrée **+0,63 point**, IC bootstrap apparié **[−0,73 ; +1,90]** ; aucun gain fiable des champs globaux. Correction explicite du vocabulaire : toutes les variantes utilisent **`x`, jamais `x_oracle`** ; les positions ennemies demeurent des dernières vues heuristiques. Le modèle gelé M0 n'a pas changé.
- [x] Diagnostic « 90 % » sans artifice : modèle 147 canaux exact top-1 **17,49 %**, top-5 **42,98 %**, top-20 **71,22 %** ; top-41 atteint **90,12 % de couverture** en nommant **41/64 cases, soit 64,1 % de la carte**. Précision exacte tardive **7,5 %** après minute 20 ; le proxy 109 canaux est similaire. Figure rouge/noir/or `predictability_gap.png`, matrice publique des 147 champs et `VISIBILITY.md` créés ; les résumés publics n'exposent aucune trace de partie.

## M3c : tête spatiale par phase — 2026-10-10

- [x] Plan et risque de surapprentissage inscrits dans `PLAN.md` avant entraînement. Pilote cinq parties (3 train/2 validation) réussi, puis un unique modèle à encodeur partagé avec résidu 8×8 par phase ; sélection sur moyenne des trois phases en validation, sans ancien test. Capacité **751 406 paramètres**, contre 732 782 pour le modèle standard ; checkpoint séparé et local.
- [x] Époque 21 retenue sur validation : expert de phase **16,39 %** exact 8×8 global, **29,78 % / 11,29 % / 5,91 %** début/milieu/fin, contre **17,49 %** global et **29,78 % / 13,09 % / 7,53 %** pour le standard. Écart apparié −1,10 point, IC bootstrap 95 % **[−2,49 ; +0,38]**. L'expert n'améliore ni la fin de partie ni le global ; **non promu, test historique non consulté**. F1 macro des cinq types : 44,94 % contre 44,92 %, différence négligeable. Le modèle standard garde son rôle de meilleur candidat M3 de développement.
- [x] QA et reproduction : **22 tests pytest passent**, compilation Python, syntaxe JS, `git diff --check`, génération et relecture des figures à partir des seuls agrégats publics, vérification d'absence d'ID de match dans `public_predictability.json`. La commande unique `scripts/run_next_level.py --epochs 25` est relancée entièrement depuis les caches ; elle réutilise les checkpoints, régénère la matrice de visibilité et les deux figures, termine sans erreur. Protocole futur M0 toujours `pending` **0/100** ; SHA-256 M0 original/copie identiques `869c468880650a556ad4f31d1297daba410e842fb06ff38bc6b80e9e81c780f7`. Checkpoint M3 standard `39abb02c5791531beff5b12bd6a0d82137575061a0e57c885af3b81bf93e9d05`, expert de phase `a22a2e6282f4571b4bd5019fadbba0ab2bb8abb68764ad732e1604f957941c34`. Poids et traces restent ignorés.

- [2026-10-10T11:25:35+00:00] Next-level five-game pilot reused from checkpoint.

- [2026-10-10T11:25:38+00:00] 64x64 labels: 465 matches, 12510 pairs, 0 errors.

- [2026-10-10T11:25:41+00:00] Event atlas: 465 ranked matches, 0 errors.

- [2026-10-10T11:25:42+00:00] Warehouse: 12975 states, 12510 transitions, 353409 events.

- [2026-10-10T11:25:42+00:00] Enemy pressure: 12975 positional frames.

- [2026-10-10T11:26:24+00:00] Text: 930 EN/FR summaries, 0 errors.

- [2026-10-10T11:26:24+00:00] Vectors: 12510 states; kNN val exact64=0.0094.

- [2026-10-10T11:26:25+00:00] 64x64 historical test: 0.0109 exact, best baseline 0.0192; prospective claim pending.

- [2026-10-10T11:26:25+00:00] Interaction training states: 12510 pairs, 0 errors.

- [2026-10-10T11:26:25+00:00] Interaction candidate validation exact16=0.0871; test intentionally unscored.

- [2026-10-10T11:26:27+00:00] Hierarchical pilot: 3 train + 2 val games; validation only.

- [2026-10-10T11:26:29+00:00] Hierarchical ablations: selected full on validation 8x8=0.1749; historical test unscored.

- [2026-10-10T11:26:31+00:00] Dashboard aggregates, replay and public figures refreshed. Open http://127.0.0.1:8008/ with serve_dashboard.py.

- [2026-10-10T13:12:47+00:00] Next-level five-game pilot reused from checkpoint.

- [2026-10-10T13:12:50+00:00] 64x64 labels: 465 matches, 12510 pairs, 0 errors.

- [2026-10-10T13:12:53+00:00] Event atlas: 465 ranked matches, 0 errors.

- [2026-10-10T13:12:53+00:00] Warehouse: 12975 states, 12510 transitions, 353409 events.

- [2026-10-10T13:12:54+00:00] Enemy pressure: 12975 positional frames.

- [2026-10-10T13:13:34+00:00] Text: 930 EN/FR summaries, 0 errors.

- [2026-10-10T13:13:35+00:00] Vectors: 12510 states; kNN val exact64=0.0094.

- [2026-10-10T13:13:35+00:00] 64x64 historical test: 0.0109 exact, best baseline 0.0192; prospective claim pending.

- [2026-10-10T13:13:36+00:00] Interaction training states: 12510 pairs, 0 errors.

- [2026-10-10T13:13:36+00:00] Interaction candidate validation exact16=0.0871; test intentionally unscored.

- [2026-10-10T13:13:37+00:00] Hierarchical pilot: 3 train + 2 val games; validation only.

- [2026-10-10T13:13:40+00:00] Hierarchical ablations: selected full on validation 8x8=0.1749; historical test unscored.

- [2026-10-10T13:13:42+00:00] Transition geometry pilot: 4 train + 1 val games; alignment checked.

- [2026-10-10T13:13:42+00:00] Transition geometry: 0.1569 validation top-1; 0 alignment mismatches.

- [2026-10-10T13:13:44+00:00] Dashboard aggregates, replay and public figures refreshed. Open http://127.0.0.1:8008/ with serve_dashboard.py.

- [2026-10-10T13:19:39+00:00] Next-level five-game pilot reused from checkpoint.

- [2026-10-10T13:19:42+00:00] 64x64 labels: 465 matches, 12510 pairs, 0 errors.

- [2026-10-10T13:19:45+00:00] Event atlas: 465 ranked matches, 0 errors.

- [2026-10-10T13:19:45+00:00] Warehouse: 12975 states, 12510 transitions, 353409 events.

- [2026-10-10T13:19:46+00:00] Enemy pressure: 12975 positional frames.

- [2026-10-10T13:20:27+00:00] Text: 930 EN/FR summaries, 0 errors.

- [2026-10-10T13:20:27+00:00] Vectors: 12510 states; kNN val exact64=0.0094.

- [2026-10-10T13:20:28+00:00] 64x64 historical test: 0.0109 exact, best baseline 0.0192; prospective claim pending.

- [2026-10-10T13:20:28+00:00] Interaction training states: 12510 pairs, 0 errors.

- [2026-10-10T13:20:29+00:00] Interaction candidate validation exact16=0.0871; test intentionally unscored.

- [2026-10-10T13:20:30+00:00] Hierarchical pilot: 3 train + 2 val games; validation only.

- [2026-10-10T13:20:33+00:00] Hierarchical ablations: selected full on validation 8x8=0.1749; historical test unscored.

- [2026-10-10T13:20:33+00:00] Phase-expert pilot: 3 train + 2 val games; validation only.

- [2026-10-10T13:20:34+00:00] Phase-expert candidate: validation 8x8=0.1639; historical test unscored.

- [2026-10-10T13:20:35+00:00] Transition geometry pilot: 4 train + 1 val games; alignment checked.

- [2026-10-10T13:20:36+00:00] Transition geometry: 0.1569 validation top-1; 0 alignment mismatches.

- [2026-10-10T13:20:38+00:00] Dashboard aggregates, replay and public figures refreshed. Open http://127.0.0.1:8008/ with serve_dashboard.py.

## Publication M3b/M3c — 2026-10-10

- [2026-10-10T13:23:37+00:00] Published the 21-file predictability/visibility audit to GitHub `main` at `454a4775e0d00f0fc81fb0839300096161430d32`; remote tree `e3df92e96df1ebd16e5c372f6194fac2696f1b60` equals the locally tested tree. Synced local `main` to the remote commit with a clean worktree.
- [2026-10-10T13:23:37+00:00] Current best 8×8 validation top-1 remains 17.49%. Its top-41 set covers 90.12% of next cells but occupies 41/64 cells. The visible-proxy audit is inconclusive and the phase-expert and transition candidates did not improve top-1. No new candidate has been evaluated on the historical test; the prospective lockbox is still 0/100 games.
- [2026-10-10T13:23:37+00:00] Next evidence gate: collect independent future games and player-visible or replay-derived subminute observations before making a 90% exact-location claim. Preserve the frozen historical model and match-level isolation.

## Tableau de bord du diagnostic — 2026-10-10

- [2026-10-10T13:29:23+00:00] Re-ran the frozen prospective protocol offline: still `pending`, 0/100 new eligible matches. A named `20261010` ID snapshot was already cached, so no duplicate same-day Riot request was needed.
- [2026-10-10T13:29:23+00:00] Added the public 8×8 predictability JSON and figures to the dashboard allowlist, with a bilingual score panel showing 17.49% one-cell accuracy, 90.12% top-41 coverage and the 64.1% map area that entails. Its three validation-model bars follow the shared phase scrubber. Kept the 46 development-validation matches distinct from the 46 historical-test matches elsewhere on the page.
- [2026-10-10T13:29:23+00:00] Browser QA: saw early 29.8/29.6/29.8% bars change to late 7.5/7.0/5.9% at minute 25; checked the rendered chart. Local dashboard on port 8008 now serves both new public assets (HTTP 200); 22 tests passed, JS syntax and Python compilation passed, `git diff --check` clean.

## Extension 512×512 — livrée localement (2026-10-10)

- [2026-10-10] Plan 512×512 écrit avant implémentation dans `PLAN.md`. Résolution spatiale cible : 262 144 cases. Conserver les modèles/scores 16 et 64 comme archives ; entraîner un sous-modèle 64→8×8 pour avoir de vraies prédictions 512 sans tête dense. Les positions Riot restent à ~60 s ; l'objectif de 90 % de case exacte n'est pas établi.
- [2026-10-10] Pilote cinq ranked (4 train, 1 validation) : alignement 512→64 vérifié dans chaque batch ; adaptateur conditionnel de 25 280 paramètres entraîné deux époques. Benchmark d'un batch : CPU 0,0026 s contre MPS 0,5708 s, donc CPU choisi. Sur les 26 observations de l'unique partie de validation pilote, 0 case exacte pour le modèle et les baselines ; échantillon trop petit pour conclure. Passage au train complet autorisé.
- [2026-10-10] Entraînement complet : parent 64 gelé (SHA-256 `afe342ace77a2faf3de4cf9098b88e558641f80d500478a2c2a828f753f5b9c6`), 373 parties train et 46 validation, meilleur adaptateur choisi à l'époque 2 sur perte conditionnelle. La tête 512 a 25 280 paramètres ; top 16 parents à l'inférence. Le vieux test et le lockbox futur ne sont pas lus.
- [2026-10-10] Validation 512 : 1 275 transitions, **0/1 275 case exacte** pour Shadow, **8/1 275 = 0,63 %** pour copie de position, **4/1 275 = 0,31 %** pour case fréquente train. Rayon 16 cases fines : 8,94 % Shadow contre 7,29 % copie. Bootstrap apparié par match, gain exact contre meilleure baseline : [−1,04 ; −0,32] points à 95 %. Choix du parent 64 du modèle joint exact 0,94 % ; sous-case exacte avec parent oracle 2,12 % (diagnostic uniquement). Le modèle échoue au critère exact et reste un candidat de développement.
- [2026-10-10] Atlas local 512 : 465 ranked traitées, 0 erreur de parsing ; 46 parties de validation pour les destinations prédites/réelles, 465 ranked pour positions des joueurs et événements. Phases 460 / 443 / 372 = 1 275 destinations. JSON local `artifacts/grid512/atlas.json` ignoré par Git. Export public : métriques agrégées et deux figures. Les événements rares de la figure publique sont d'abord groupés en blocs 16×16 et les blocs à moins de trois événements sont masqués, puis lissés pour la lecture ; les cellules exactes ne sont pas publiées.
- [2026-10-10] Pipeline une commande mis à jour : pilote 512 puis train/validation/atlas/figures ; relance complète idempotente passée avec caches. README FR/EN, RESULTS, ROADMAP et PLAN alignés sur la nouvelle cohorte et la limite de précision. 25 tests Python passent ; syntaxe JS/Python et `git diff --check` passent.
- [2026-10-10] QA navigateur du tableau de bord local : **42 combinaisons** (14 couches × 3 phases) affichent badge 512 et total lisible, 0 erreur console ; la frise change bien les comptes 460→443→372 et la surface 3D, rotation 45→53°, bascule FR/EN et résultat 512 0,00 % / copie 0,63 %. Halo de présentation ajouté pour rendre les cellules isolées visibles ; le survol donne toujours le compte exact de la cellule.

- [2026-10-10T15:01:25+00:00] Next-level five-game pilot reused from checkpoint.

- [2026-10-10T15:01:28+00:00] 64x64 labels: 465 matches, 12510 pairs, 0 errors.

- [2026-10-10T15:01:31+00:00] Event atlas: 465 ranked matches, 0 errors.

- [2026-10-10T15:01:32+00:00] Warehouse: 12975 states, 12510 transitions, 353409 events.

- [2026-10-10T15:01:32+00:00] Enemy pressure: 12975 positional frames.

- [2026-10-10T15:02:14+00:00] Text: 930 EN/FR summaries, 0 errors.

- [2026-10-10T15:02:14+00:00] Vectors: 12510 states; kNN val exact64=0.0094.

- [2026-10-10T15:02:15+00:00] 64x64 historical test: 0.0109 exact, best baseline 0.0192; prospective claim pending.

- [2026-10-10T15:02:15+00:00] 512x512 five-game pilot: 4 train + 1 val games, 26 targets; parent-label alignment passed.

- [2026-10-10T15:02:15+00:00] 512x512 development validation: 46 games, 1275 targets; exact model=0.0000, copy=0.0063; test untouched.

- [2026-10-10T15:02:19+00:00] 512x512 sparse atlas: 465 ranked games, 0 errors; sparse cells stay local.

- [2026-10-10T15:02:22+00:00] Interaction training states: 12510 pairs, 0 errors.

- [2026-10-10T15:02:22+00:00] Interaction candidate validation exact16=0.0871; test intentionally unscored.

- [2026-10-10T15:02:23+00:00] Hierarchical pilot: 3 train + 2 val games; validation only.

- [2026-10-10T15:02:26+00:00] Hierarchical ablations: selected full on validation 8x8=0.1749; historical test unscored.

- [2026-10-10T15:02:27+00:00] Phase-expert pilot: 3 train + 2 val games; validation only.

- [2026-10-10T15:02:28+00:00] Phase-expert candidate: validation 8x8=0.1639; historical test unscored.

- [2026-10-10T15:02:29+00:00] Transition geometry pilot: 4 train + 1 val games; alignment checked.

- [2026-10-10T15:02:30+00:00] Transition geometry: 0.1569 validation top-1; 0 alignment mismatches.

- [2026-10-10T15:02:31+00:00] Dashboard aggregates, replay and public figures refreshed. Open http://127.0.0.1:8008/ with serve_dashboard.py.
# M4 — corpus supplémentaire et prédictions à 10 secondes (2026-10-10)

- [x] Plan préalable dans `PLAN.md` : domaines de données distincts, état causal au temps `t`, événements marqués, pilote cinq parties, métriques sans inflation par la classe « aucun ».
- [x] Rafraîchissement Riot nommé `20261010_expansion` : **470 IDs ranked**, **465 utilisables**, donc **0 nouvelle partie** du PUUID disponible à cette date. Cache des JSON conservé, aucun refetch des matches.
- [x] Audit local initial : 8 102 événements positionnés impliquent le PUUID dans 465 parties, mais leur point géographique peut être celui d'une cible ou d'un objectif. Ils ne sont pas des mesures de position de Faker.
- [x] Audit des alias : Sheep Esports attribue `Hide on bush#61151` à Faker pendant Worlds 2024 ; Riot résout cet ID EUW sur une PUUID distincte et rend **31/31 ranked queue 420 avec timeline** (pilote 5 puis 31). `silent silence#08022`, `wincg#84926` (EUW) et `Neo Hide on bush#NA1` (NA) se résolvent mais renvoient **0 ranked ID disponible**. Chaque source et route régionale figurent dans `data/raw/aliases/manifest.json`, privé. L'attribution historique n'est pas une preuve d'identité fournie par Riot.
- [x] Base pro locale `pro_catalog.sqlite` : cinq CSV de 2022–2026 dans `data/raw/pro/`, empreintes SHA-256 et provenance `unverified_public_mirror` enregistrées ; pilote cinq puis **671 parties Faker/T1/mid** (144/134/176/187/30). Le fichier 2026 se termine au 10 avril et n'est pas complet. Aucune donnée pro de fin de match ne sert de feature à t ou de label spatial.
- [x] Jeu supervisé 10 s : pilote cinq KR (803 fenêtres), puis **465 KR / 73 482 fenêtres**, zéro erreur ; **31 EUW / 5 383 fenêtres**, zéro erreur. Cache NPZ par partie versionné `schema_version=2`. Un test synthétique a révélé puis corrigé une double normalisation des positions ; tous les caches ont été reconstruits et deux tests de causalité/coordonnées manquantes passent. Targets : première marque d'événement dans `(t,t+10s]`, jamais position de Faker inférée.
- [x] Modèle MLP 22 537 paramètres, seed 42, split KR 373/46/46 par match et EUW uniquement en entraînement auxiliaire. Pilote 3 train/2 val distincts ; puis val KR **7 480 fenêtres** : phase-prior log loss 1,4472 / accuracy 52,59 % / macro F1 7,66 % ; KR seul 1,3923 / 53,98 % / 12,33 % ; KR+EUW 1,3847 / 54,44 % / 13,16 %. Gain log loss EUW 0,00765, IC bootstrap par match [0,00294 ; 0,01264] sur cette validation adaptative. Test historique non lu. Wards posées = 3 934/7 480 (52,59 %) des fenêtres de validation KR, donc l'accuracy brute ne résume pas la qualité.
- [x] Figure `corpus_event_clock.png` inspectée, JSON public strictement agrégé, tableau de bord FR/EN et README FR/EN enrichis ; `DATA_EXPANSION.md` relie mathématiques des processus ponctuels, voisinage biologique et protocole de challenge inspiré de `when-agents-rule`. Une commande `scripts/run_expansion.py` reprend les caches, teste cinq jeux puis reconstruit les artefacts.
- [x] Relance complète de l'extension depuis les checkpoints (`--skip-pro`) : 12/12 phases en 23 s ; aucun nouveau refetch des JSON de match. Réimport des cinq CSV pro inchangé : 671 parties ; le catalogue remplace désormais une ancienne version annuelle si le CSV change, vérifié par test ciblé.
- [x] Benchmark de cette petite tête (batch 512, 100 pas avec transfert depuis NumPy) : CPU 0,00146 s/batch, MPS 0,00243 s/batch ; CPU conservé pour ce modèle. La mesure dépend de la machine et ne remplace pas les benchmarks du transformer spatial.
- [x] 28 tests Python, compilation Python, syntaxe JavaScript et contrôle de diff passent. Le navigateur affiche les nombres FR, la figure et la nouvelle explication sur l'horloge de dix secondes ; zéro erreur console. La figure publique répond HTTP 200, une route vers les données brutes répond 404.
- [x] Extension publiée sur GitHub `main` au commit `b6bada66d8b926735924f63e91a0921d9acfa5ae`. Arbre distant `49d847938d6ce77d8923da9fb64f99b66fc9f28d` égal à l'arbre local testé ; `main` local synchronisé. Cette ligne de clôture sera publiée dans un second commit documentaire.

## M5 — recherche de la prochaine preuve (2026-10-10)

- [x] Vérification des sources primaires : API Replay Riot = contrôle d'un replay ouvert, pas un téléchargement d'archives ; ROFL annonce une seconde mais son dépôt est archivé et sa compatibilité moderne/macOS n'est pas démontrée ; TLoL couvre surtout des patches anciens ; Riot/GRID décrit actuellement les flux détaillés pro comme commerciaux, LCK pour média. Aucun `.rofl` trouvé dans Downloads/Documents.
- [x] Plan d'expérience et critères d'arrêt consignés dans `NEXT_RESEARCH.md` : un replay Faker assorti d'un match ID pour tester l'alignement, puis cinq jeux avant extension ; ablation à capacité égale des signaux jungle/bot/support/adversaires sur validation ; vue visible au joueur ; contrat de challenge et lockbox distinct. Aucun résultat 10 s spatial ou causal n'est revendiqué.
- [x] M5a : pilotes cinq jeux pour quatre variantes, puis entraînement KR 373/46 pour chacune à 22 537 paramètres et 7 480 fenêtres de validation. Perte log : complet 1,3923 ; sans alliés 1,3903 ; sans ennemis 1,3914 ; sans six distances jungle/bot/support 1,3919. Bootstrap apparié par match dans `docs/data/public_event_ablation.json`, figure inspectée. Les proxys de distance ne gagnent pas sur cette cible dominée par les wards ; aucune conclusion causale ni promotion sur le test. Pertes par match et identifiants restent locaux.
- [x] Diagnostic par classe publié : le modèle complet obtient F1 = 0 pour kill Faker (119 fenêtres), mort Faker (90) et objectif (135) sur la validation, malgré 53,98 % d'accuracy globale. Prochaine expérience : cible rare par type, calibration/précision-rappel et abstention ; preuve externe prioritaire : replay Faker aligné avec un match ID.
- [2026-10-10T15:56:23+00:00] M5a publiée sur GitHub `main` au commit `42655ef40594cf247d4ce3f9330491c0a4da0dce` ; l'arbre distant `b1e98c16d8bf71f16792d9e183dc2ce690b20ced` égale l'arbre local testé. 28 tests passent, syntaxe JavaScript et diff propres ; graphique HTTP 200, route brute HTTP 404. `main` local synchronisé sans modifications. Cette ligne de clôture fait l'objet d'un second commit documentaire.

## M5b — lecture des preuves sur le site (2026-10-10)

- [x] `dashboard/index.html` ouvert en `file://` affiche un lanceur local et essaie de rejoindre `127.0.0.1:8008` si le serveur est prêt. Le tableau interactif dépend des routes du serveur ; ce lanceur n'est pas un mode hors ligne. L'ouverture `file://` elle-même n'a pas pu être vérifiée en navigateur automatisé : la politique du navigateur de test bloque ce schéma. La version HTTP et le code statique ont été vérifiés.
- [x] Route `/event-ablation.json` ajoutée à la liste publique ; `/data/raw/` garde HTTP 404. Le panneau `#research` affiche les neuf classes depuis le JSON agrégé, les 3 934 wards posées / 7 480 fenêtres (52,6 %), F1 nul pour kill/mort Faker et objectif, et la distinction KR seul / appoint EUW. Aucun identifiant de partie ni perte par match n'est publié.
- [x] Parcours visuel « replay assorti 1 → 5 parties, événements rares, visibilité du joueur » ajouté en FR/EN ; README FR/EN avec schéma Mermaid, RESULTS, ROADMAP, PLAN et NEXT_RESEARCH synchronisés. Aucun nouveau score ou modèle revendiqué.
- [x] QA locale : 28 tests Python passent ; syntaxe JS et `git diff --check` passent ; 89 IDs HTML uniques ; agrégat de neuf classes somme à 7 480. Rendu du graphique inspecté en FR, EN et largeur mobile 390 px, zéro erreur console. Navigateur laissé sur `http://127.0.0.1:8008/#research` en français avec serveur local actif.
- [2026-10-10T16:01:45+00:00] Site, README FR/EN et documentation M5b publiés sur GitHub `main` au commit `fecb4c96c63392289cfbe802c0c8573c45192631` ; arbre distant `22f46d4ec4836f0351cc1a85e63549c824ac33a0` identique à l'arbre local vérifié. Branche locale synchronisée et propre. Cette ligne de publication est ajoutée dans un second commit documentaire.

## M6 — onglets, six étoiles et archive des finales (2026-10-10)

- [x] Le titre mondial 2025 de T1, sixième de l'organisation, a été vérifié auprès de son copropriétaire Comcast Spectacor. Les résultats des six finales gagnées (2013, 2015, 2016, 2023, 2024, 2025) sont sourcés dans `WORLD_FINALS.md`. Les **25 manches** et trois demi-finales marquantes forment des fiches factuelles, pas des replays ni de nouvelles trajectoires d'entraînement.
- [x] `scripts/build_world_finals.py` produit un JSON public versionné, avec source par manche ; `shadowfaker.text_index finals` ajoute **56 fiches FR/EN** au SQLite local sans doublons à la relance. Le catalogue reste isolé du modèle et de ses scores.
- [x] Refonte de navigation : une seule section active par URL `#`, retour/avance du navigateur, état accessible `aria-current`, barre horizontale visible sur mobile. L'onglet **Finales BO5** permet de choisir l'année, lire score, ordre des victoires/défaites, durée et source de chaque manche ; trois autres parties sont proposées comme pistes d'étude.
- [x] Affiche six étoiles en SVG, captures réelles du site, animation GIF de six écrans et README FR/EN structurés comme les chapitres de l'interface. `render_results.py` utilise désormais le générateur commun afin qu'une relance du pipeline conserve la nouvelle identité.
- [x] Documentation `DESIGN.md`, `WORLD_FINALS.md`, `RESULTS.md`, `ROADMAP.md`, `PLAN.md` et `NEXT_RESEARCH.md` alignée sur les données, leurs sources et les limites de la prédiction. Les captures n'incluent que l'interface et des agrégats publics.
- [x] Contrôle final : **30 tests Python**, syntaxe JS, diff propre ; 13 onglets parcourus en navigateur, toujours une seule section visible et un seul `aria-current` ; sélection mobile à 390 px et repositionnement de l'onglet actif après redimensionnement ; zéro erreur console. JSON public HTTP 200, données brutes HTTP 404 ; animation de six frames inspectée ; régénération des affiches conserve les six étoiles ; import local des 56 fiches confirmé.

## M7 — grilles lisibles et fiches de parties (2026-10-10)

- [x] Plan M7 écrit : clarifier les symboles et cohortes sur chaque carte, inventorier les données agrégées, enrichir les fiches privées de match avec résultats finaux, sans fuite vers les modèles temporels.
- [x] Pilote cinq puis 465 parties : `game_facts.sqlite` privé contient 465 fiches (UTC, patch, durée, champion, côté, résultat, K/D/A, CS, dégâts, vision, objets et compositions), zéro erreur. Hash du JSON source et reprise sans doublon ; clés absentes tolérées. Les données finales restent hors de l'état causal à `t`.
- [x] Index textuel FR/EN : pilote cinq puis 465 parties, 930 résumés ranked, zéro erreur ; 56 fiches de finales restent isolées. L'inventaire public donne 550 JSON match et 545 timelines en cache, 470 IDs KR ranked, 5 remakes, 465 exploitables, 12 975 frames, 12 510 transitions, 353 409 événements, dont 33 329 localisés. Aucun match ID/PUUID dans le JSON public.
- [x] Onglets Atlas, cartes 16×16, surface 3D et rejeu : légendes de symboles et cohorte, lecture exacte au survol. Onglets Corpus et Archives : inventaire agrégé, recherche locale par partie et cartes de statistiques finales. `scripts/refresh_catalog.py` refait pilote puis corpus depuis les caches ; exécution complète : 465 fiches, 930 documents, 56 fiches de finales, zéro erreur.

## M8 — zone de pression et sprites (2026-10-10)

- [x] Plan et risques M8 inscrits dans `PLAN.md`. Le calcul de pression version 2 a été piloté sur cinq jeux (139 frames avec position Faker), puis recalculé sur les **465 parties / 12 975 frames** pour rayons 1 000, 1 500, 2 500, 3 500, 5 000. Une entrée requiert une position ennemie connue aux deux frames ; zéro arrivée fictive due à une position manquante ou à la première frame. Les séries à 2 500 unités conservent 0,88 / 1,15 / 1,75 adversaires proches par frame sur 0–10 / 10–20 / 20+ minutes.
- [x] Sprites Data Dragon épinglés `16.20.1` : 169 champions et 160 IDs d'objets présents dans les 465 fiches, tous retrouvés. Deux atlas PNG et un manifest public ; les feuilles sources sont cachées localement, aucun match brut ni secret publié. Les noms EN/FR et icônes apparaissent dans les Archives et la fiche du rejeu. La version des icônes peut différer du patch d'une partie.
- [x] Vue Pression : cinq rayons sélectionnables, schéma de taille, barres par phase, cartes 0/1 et 0/2, unités et dénominateurs visibles. Test navigateur : 1 000 → 5 000 unités fait passer la moyenne précoce de 0,37 à 1,58 ; le curseur commun en phase tardive modifie la moyenne et le dénominateur. Aucune erreur console observée. Captures réelles dans `docs/figures/` et méthodes dans `PRESSURE.md`/`CORPUS.md`.
- [x] QA finale locale : **33 tests Python**, syntaxe JS, compilation Python et `git diff --check` passent ; routes sprites HTTP 200, chemin raw HTTP 404. 100 interactions navigateur rayon/chronologie vérifiées, zéro erreur console ; recherche EN sur « Hourglass » donne 68 parties et traduit les objets ; layout 390 px en une colonne, aucun débordement horizontal. Captures Pression desktop/mobile, Corpus et Archives sauvegardées. Liens locaux des README et guides visuels résolus.
- [x] M6–M8 publiés sur GitHub `main` via la connexion authentifiée au commit `ab8aeafc6dbef616ba39bbbeb7df0b47dcd197ba`. L'arbre distant `1627ada50ddca8745049fa538f5eb49c6f202ef1` est identique à l'arbre local testé ; les 19 blobs binaires ont été vérifiés par SHA Git avant l'assemblage. `git fetch` et la synchronisation de `main` local ont confirmé la publication. Cette ligne d'audit est un second commit documentaire.

## M11 — Mémoire de Faker et challenger (2026-10-10)

- [x] Architecture définie dans `PLAN.md` après la demande d'une base de décisions Faker et d'une boucle de challenge/apprentissage. Le transformer de comportement existant et un éventuel LLM textuel ont des rôles distincts ; aucun score futur ou 90 % exact n'est présumé.
- [x] Base locale causale train/validation, calibration par match, challenger de récupération et bilan honnête. Pilote 5+5 parties / 260 épisodes ; corpus 373 train / 10 038 épisodes et 46 validation / 1 275 épisodes, 125 attributs choisis (75 core + 50 IoC). Recherche sur 298 matches de mémoire et 75 matches de calibration, split par match. Sélection k=15, positions ×4, sans IoC, puis validation exacte 8×8 **11,53 %**, sous règle rôle/phase **15,29 %** et Shadow IoC **17,41 %**. Nearest 64×64 **0,63 %**, 512×512 **0 %** ; aucun test historique lu et aucune promotion. Base SQLite et exemples détaillés ignorés par Git ; JSON public agrégé.
- [x] Interface de challenge et documentation : tableau de scores dynamique, grille 8×8 interactive, choix/révélation/cas suivant, 24 exemples anonymes locaux, traduction FR/EN. `FAKER_MEMORY.md`, RESULTS, ROADMAP et README FR/EN à jour ; figure et capture navigateur réelles. L'API locale filtre les champs de cas et ne sert aucun match ID.
- [x] Relance intégrale de `run_ioc_challenge.py --epochs 25` depuis les caches : exit 0 après pilote 5 parties, audit 465 parties, trois checkpoints IoC repris, mémoire et figures reconstruites. **41 tests** Python, compilation, syntaxe JS, `git diff --check` et liens Markdown locaux passent. Navigateur : score, grille, révélation, cas suivant, traduction FR/EN, 390 px sans débordement, zéro erreur console ; route locale mémoire HTTP 200 et tentative `/data/raw/` HTTP 404.
- [x] M10–M11 publiés sur GitHub `main` au commit `127cedfa06b6a7e16c1088e4853d5214c355c070`. Les 29 blobs ont été vérifiés par SHA Git, l'arbre distant `a432972f263d91453eb97dcd49dc54d1aa84f7b0` égale l'arbre local testé ; `git fetch` et synchronisation de `main` local effectués. Cette ligne d'audit est publiée dans un second commit documentaire.

## M10 — Validation des événements (2026-10-10)

- [x] Plan ajouté à `PLAN.md`. Audit préliminaire des 465 timelines brutes : 62 `CHAMPION_KILL` sans tueur joueur (3 victimes Faker, 59 autres), 23 610 `TURRET_PLATE_DESTROYED` hors ancien index. Les événements gardent leur sens Riot : une position de kill ou d'objectif n'est pas la position de Faker.
- [x] Comparaison structurelle : pilote cinq parties, 4 190 lignes exactes ; corpus complet 465 parties, **353 409/353 409** lignes exactes sur 563 198 événements bruts, zéro erreur de lecture ou désaccord de classification. Audit de 1 288 achats/skills sans acteur, 62 morts sans tueur joueur dont 3 de Faker, 23 610 plaques hors ancien index. JSON agrégé et graphique publics ; aucun match ID exporté.
- [x] Corpus/README/docs actualisés ; `EVENT_VALIDATION.md`, JSON agrégé, figure et capture navigateur montrent les exclusions.

## M9 — Pression située et IoC d'itemisation (2026-10-10)

- [x] Plan M9 défini avant l'implémentation dans `PLAN.md` : position des dix joueurs à `t`, inventaires horodatés, masque de visibilité, ablation, 90 % avec surface et séparation des cohortes.
- [x] Pilote cinq parties : 125 décisions, 497 canaux par frame, aucun échec. `ITEM_PURCHASED/SOLD/DESTROYED/UNDO` sont appliqués dans l'ordre des timestamps, jamais après `t`.
- [x] Préparation complète depuis le cache : 465 parties, 12 510 décisions, zéro échec. Une timeline comporte deux frames exceptionnellement proches à 28 min ; l'alignement a été corrigé par timestamp le plus proche, après un premier passage 464/465. Les NPZ par partie restent privés et reprenables.
- [x] IoC statique officiel : Data Dragon, 12 patches joués, pilote 5 parties / 125 paires puis 465 parties / 12 510 paires, 617 canaux (147 état/interactions + 350 objets horodatés + 120 propriétés du patch), zéro erreur. Les catalogues et NPZ restent dans les caches ignorés de Git.
- [x] Entraînement sur 373/46 train/validation, même architecture 777 902 paramètres et trois variantes. Exact 8×8 validation : sans objets 16,94 %, objets horodatés 17,18 %, objets + Data Dragon 17,41 %, meilleure règle simple 15,29 %. Ancien candidat hiérarchique 17,49 % ; pas de promotion. Gain apparié complet contre sans objets +0,47 point, IC par match [−0,16 ; +1,13] ; propriétés statiques seules +0,24 [−0,15 ; +0,63]. Test historique et lockbox non lus. Couverture 90,75 % avec 40/64 cases, soit 62,5 % de la carte, non précision exacte.
- [x] Page Corpus : Riot IDs exacts avec statut d'attribution, compte de chaque type d'événement et présence de coordonnées ; ventes/destructions/annulations brutes clairement séparées de l'ancien total indexé. Panneau IoC avec 147→497→617, sources Riot/U.GG/Google et figure d'ablation. Atlas/3D/Pression : positions d'une partie au-dessus des agrégats, filtres acteur/rôle/objets/couloirs/rayon, lecture explicite de la dernière frame si la partie finit avant l'heure globale.
- [x] Challenge : composition libre de cinq rôles, allocation alliée/adverse à la minute, délai de réponse et partage des ressources ; unités arbitraires et absence de probabilité de victoire affichées. `IOC_VISION.md`, RESULTS, CORPUS, PRESSURE, GAME_THEORY_LAB, ROADMAP et README FR/EN mis à jour avec deux captures réelles et un graphique scientifique. `run_ioc_challenge.py` reprend les checkpoints ; `run_next_level.py` l'appelle pour l'exécution complète en une commande.
- [x] Relance intégrale de l'extension IoC depuis les caches : pilote cinq jeux, 465 jeux, entraînements repris, figure, inventaire et rejeu actualisés. **36 tests** Python, compilation, syntaxe JS, diff et liens Markdown locaux passent. Navigateur : 100 actions nouvelles vérifiées (40 minutes, cinq rayons, 12 filtres Pression, six rôles, 12 filtres Atlas, 12 filtres 3D, 13 paramètres Challenge), zéro erreur console ; cinq onglets sans débordement à 390 px. Figure HTTP 200, chemin `data/raw` HTTP 404.
- [x] Audit qualité d'inventaire ajouté après diagnostic d'un bruit de données : 1 351/4 650 sets d'IDs finaux exacts (29,05 %, Jaccard moyen 0,839), 3 132/129 750 frames d'acteurs avec >7 IDs distincts. Les objets initiaux/améliorations automatiques peuvent échapper aux événements. Le champ historique `item_slots` est un compte plafonné de quantités issues d'événements, pas les vrais emplacements. JSON d'audit agrégé publié, sans ID de partie ; objets finaux réservés à l'audit, jamais à l'état `t`.
- [x] Commande unique `run_next_level.py --limit 1000 --epochs 25` relancée jusqu'au bout (exit 0), y compris pilote cinq parties, corpus complet, ablations IoC et audit. Site redémarré : résultats IoC et audit chargés depuis les JSON publics, traduction FR/EN vérifiée, zéro erreur console, nouvelles routes HTTP 200 et `data/raw` HTTP 404. Capture IoC régénérée ; 36 tests, syntaxe JS, compilation, liens et diff sans erreur.
- [x] M9 publié sur GitHub `main` via la connexion authentifiée au commit `71f86c027e5b236f5a68ad1ba62a0a381d06ae82`. Les 31 blobs du changement ont été vérifiés par SHA Git avant assemblage ; l'arbre distant `f160e42c23b172532298a129dfaadbc76a4fae88` est identique à l'arbre local testé. `git fetch` puis synchronisation de `main` local ont confirmé la publication. Cette ligne d'audit est ajoutée dans un second commit documentaire.

- [2026-10-10T17:09:59+00:00] Item IoC pilot: five games, 125 observations, zero errors.

- [2026-10-10T17:09:59+00:00] Item IoC: 465 games, 12510 observations, 497 channels.

- [2026-10-10T17:09:59+00:00] Static item IoC pilot: five games, 125 observations, zero errors.

- [2026-10-10T17:10:02+00:00] Patch-matched Data Dragon IoC: 465 games, 617 channels, 12 patches.

- [2026-10-10T17:10:06+00:00] Static IoC validation: 46 games; selected full at 8x8=0.1741.

- [2026-10-10T17:10:08+00:00] Public IoC figure, corpus inventory and local game replay refreshed.

- [2026-10-10T17:12:22+00:00] Next-level five-game pilot reused from checkpoint.

- [2026-10-10T17:12:25+00:00] 64x64 labels: 465 matches, 12510 pairs, 0 errors.

- [2026-10-10T17:12:28+00:00] Event atlas: 465 ranked matches, 0 errors.

- [2026-10-10T17:12:28+00:00] Warehouse: 12975 states, 12510 transitions, 353409 events.

- [2026-10-10T17:12:28+00:00] Post-game facts: 465 private ranked cards; 0 errors. These are retrospective, not time-t model inputs.

- [2026-10-10T17:12:29+00:00] Data Dragon sprites: 169 champions, 160 items; pinned static version.

- [2026-10-10T17:12:31+00:00] Corpus inventory: 353409 events, 33329 positioned.

- [2026-10-10T17:12:31+00:00] Enemy pressure: 12975 positional frames.

- [2026-10-10T17:13:13+00:00] Text: 930 EN/FR summaries, 0 errors.

- [2026-10-10T17:13:13+00:00] Vectors: 12510 states; kNN val exact64=0.0094.

- [2026-10-10T17:13:14+00:00] 64x64 historical test: 0.0109 exact, best baseline 0.0192; prospective claim pending.

- [2026-10-10T17:13:14+00:00] 512x512 five-game pilot: 4 train + 1 val games, 26 targets; parent-label alignment passed.

- [2026-10-10T17:13:14+00:00] 512x512 development validation: 46 games, 1275 targets; exact model=0.0000, copy=0.0063; test untouched.

- [2026-10-10T17:13:19+00:00] 512x512 sparse atlas: 465 ranked games, 0 errors; sparse cells stay local.

- [2026-10-10T17:13:21+00:00] Interaction training states: 12510 pairs, 0 errors.

- [2026-10-10T17:13:21+00:00] Interaction candidate validation exact16=0.0871; test intentionally unscored.

- [2026-10-10T17:13:23+00:00] Hierarchical pilot: 3 train + 2 val games; validation only.

- [2026-10-10T17:16:56+00:00] Hierarchical ablations: selected full on validation 8x8=0.1749; historical test unscored.

- [2026-10-10T17:16:56+00:00] Phase-expert pilot: 3 train + 2 val games; validation only.

- [2026-10-10T17:18:14+00:00] Phase-expert candidate: validation 8x8=0.1639; historical test unscored.

- [2026-10-10T17:18:15+00:00] Transition geometry pilot: 4 train + 1 val games; alignment checked.

- [2026-10-10T17:18:16+00:00] Transition geometry: 0.1569 validation top-1; 0 alignment mismatches.

- [2026-10-10T17:18:18+00:00] Dashboard aggregates, replay and public figures refreshed. Open http://127.0.0.1:8008/ with serve_dashboard.py.

- [2026-10-10T17:18:19+00:00] Item IoC pilot: five games, 125 observations, zero errors.

- [2026-10-10T17:18:19+00:00] Static item IoC pilot: five games, 125 observations, zero errors.

- [2026-10-10T17:18:24+00:00] Item IoC: 465 games, 12510 observations, 497 channels.

- [2026-10-10T17:18:27+00:00] Patch-matched Data Dragon IoC: 465 games, 617 channels, 12 patches.

- [2026-10-10T17:18:30+00:00] Event-inventory audit: 1351/4650 exact final ID sets; proxy caveat documented.

- [2026-10-10T17:18:34+00:00] Static IoC validation: 46 games; selected full at 8x8=0.1741.

- [2026-10-10T17:18:37+00:00] Public IoC figure, corpus inventory and local game replay refreshed.

- [2026-10-10T17:18:37+00:00] Causal item IoC, played-patch catalogs, matched ablations and public IoC figure refreshed.

- [2026-10-10T17:55:39+00:00] Item IoC pilot: five games, 125 observations, zero errors.

- [2026-10-10T17:55:39+00:00] Static item IoC pilot: five games, 125 observations, zero errors.

- [2026-10-10T17:55:39+00:00] Event validation pilot: five games, 4190 exact indexed events.

- [2026-10-10T17:55:39+00:00] Faker memory pilot: 260 train/validation episodes across ten games.

- [2026-10-10T17:55:41+00:00] Item IoC: 465 games, 12510 observations, 497 channels.

- [2026-10-10T17:55:44+00:00] Patch-matched Data Dragon IoC: 465 games, 617 channels, 12 patches.

- [2026-10-10T17:55:47+00:00] Event-inventory audit: 1351/4650 exact final ID sets; proxy caveat documented.

- [2026-10-10T17:55:52+00:00] Event validation: 353409/353409 exact indexed rows across 465 games; exclusions documented.

- [2026-10-10T17:55:54+00:00] Static IoC validation: 46 games; selected full at 8x8=0.1741.

- [2026-10-10T17:56:02+00:00] Faker memory: 10038 train and 1275 validation decisions; retrieval 8x8=0.1153, no promotion over baseline.

- [2026-10-10T17:56:05+00:00] Public IoC figure, corpus inventory and local game replay refreshed.
## M12 — Matrices d'équipe autour de Faker (2026-10-11)

- [x] Plan M12 inscrit dans `PLAN.md` avant l'implémentation. LoL Esports affiche Doran, Oner, Faker et Keria sur la page T1 actuelle ; la source pro locale reste un miroir tiers non vérifié. Audit préalable : 671 manches Faker/T1 avec cinq lignes joueurs, 645 avec valeurs complètes à 10/15 minutes. Le champ `year` vaut 2026 dans 18 manches datées de décembre 2025 ; la chronologie sera fondée sur `date`, tout en conservant le tag saison.
- [x] Pilote cinq manches : 5 jeux, 25 lignes joueurs, 20 historiques de paires ; index complet : 671 jeux, 3 355 lignes, 2 684 paires, 645 photos complètes 10/15 min. Cache basé sur SHA-256 CSV, contenu sélectionné du catalogue et version de schéma ; seconde exécution sans reconstruction. Un nom bot absent en 2023 reste `UNKNOWN`, sans faire perdre la manche. Dates source triées, historique strictement antérieur.
- [x] Agrégat public par année, matrice de cojeu 4×4, exposition cumulée et demi-vie 90 jours, écarts or/XP des cinq rôles et corrélations 5×5 des variations d'or 10→15. En 2025 : 187 manches des quatre joueurs, r(Faker,bot)=+0,06, r(Faker,jungle)=+0,39 et r(bot,support)=+0,55 ; descriptif, sans interprétation causale.
- [x] Onglet FR/EN testé réellement : année 2022 donne 144 manches et zéro Doran ; 2025 donne 187 et la mémoire 90 jours change la courbe ; matrice 5×5 visible, aucun log console erreur. Largeur mobile 390 px sans débordement de la grille. Capture d'onglet et figure scientifique ajoutées au README FR/EN. `TEAM_MATRIX.md`, RESULTS, CORPUS, ROADMAP et entrée des commandes à jour.
- [x] Tests du code chronologique et des champs manquants ; 43 tests globaux passent, syntaxe JS, compilation Python, `git diff --check`, pilotage/reprise et audit JSON sans IDs de match. Sources pro privées ignorées par Git ; scores ranked inchangés.
- [x] Publication `main` : commit de livraison distant `0e6233be30d413a51fd03de5fcc98598b3f368b6`, arbre `4cec1591139709441759945850a49f236bc1e752` vérifié égal à l'arbre local après fetch. Ce journal est publié dans un commit de clôture séparé. Aucune donnée brute, clé, index détaillé ni poids ajouté à Git.

## M13 — Challenge rétrospectif chronologique de l'expérience commune (2026-10-11)

- [x] Protocole inscrit dans `PLAN.md` avant l'analyse : cible Faker mid à 15 min, entrée maximum 10 min, split par journée chronologique, comparaison ablatée et bootstrap groupé. Le résultat ne sera pas appelé prédiction de l'action de Faker.
- [x] Pilote cinq manches : 33 entrées de contexte et neuf historiques. Sur 645 états pro complets, matrice détaillée et identifiants gardés localement ; split par jours 534 train (201 jours), 39 validation (13 jours), 72 test (25 jours). Pénalité 100 choisie seulement sur le modèle sans historique en validation, puis appliquée aux deux variantes. Aucun champ à 15 minutes/final dans les entrées ; test automatique de mutation des cibles.
- [x] Test tenu à l'écart ouvert après ce choix : Faker mid MAE copie 412,64 or, contexte 442,17, contexte + historique 441,88. Différence appariée −0,29 or, bootstrap par jour [−2,89 ; +2,10]. Bot : contexte 460,08, historique 464,81, différence +4,73 [−16,75 ; +26,32]. Signal supplémentaire non confirmé, aucune promotion du modèle ranked.
- [x] Figure agrégée, panneau FR/EN et capture réelle ajoutés au site/README ; largeur mobile 390 px vérifiée sans débordement. `TEAM_PROBE.md`, RESULTS, ROADMAP, CORPUS, TEAM_MATRIX et commandes relançables mis à jour. `pytest -q` : 46 tests passés ; syntaxe JS, compilation Python et diff vérifiés. Route publique n'expose que l'agrégat.
- [x] Livraison M13 sur `main` : commit distant `4a714f4ecb6164a3513b1fc44de18768639aa3af`, arbre `65cdb1e56d6acd13c7a55214a1048fa782444cc2` identique au commit local testé ; fetch et référence distante vérifiés. Ce journal de clôture est publié dans un second commit. Les CSV/SQLite/NPZ détaillés et `.env` restent ignorés.

## M14 — Porte de précision exacte 90 % (2026-10-11)

- [x] Contrat d'évaluation inscrit dans `PLAN.md` avant les mesures : case unique 8×8, précision et couverture, split par match, borne Wilson, et aucune revendication de confirmation sur l'ancienne validation.
- [x] Snapshot Riot `20261011` tenté : HTTP 401 sur match-v5, message « Riot key invalid, expired or unauthorized ». Aucune nouvelle partie comptée ni score prospectif ouvert ; la clé de `.env` doit être renouvelée pour reprendre la collecte.
- [x] Pilote cinq parties : 143 transitions, exact 8×8 = 20,28 %. Audit complet : 46 parties / 1 275 transitions, exact = 17,49 % ; sur les 5 % de cas les plus confiants, 31/64 = 48,44 % et borne Wilson inférieure = 36,63 %. Les deux plis de 23 matchs ne sélectionnent aucun seuil satisfaisant le contrat 90 %. Figure et panneau FR/EN publiables, vérifiés visuellement sur navigateur desktop et mobile 390 px sans débordement ; capture réelle ajoutée aux README.
- [x] `NINETY_GATE.md`, README FR/EN, RESULTS, ROADMAP et commande générale mis à jour. 50 tests passent ; vérifications syntaxe JS, compilation Python, `git diff --check`, endpoint public et chemins privés ignorés par Git. L'endpoint ne contient ni identifiant de partie ni prédiction individuelle.
- [x] Livraison M14 sur `main` : commit distant `ab2a453470cc241e962defd09ddffd6889bc84f0`, arbre `2546582be7edf5da4077f9f570ec8566c434eb29` identique à l'arbre local testé après fetch. Ce journal de clôture est publié dans un second commit ; aucune donnée brute, clé, prédiction par match ni poids du modèle ne sont ajoutés à Git.

## M15 — Secondes et coordonnées continues (2026-10-11)

- [x] Correction de la cible inscrite dans `PLAN.md` : décision de Faker en secondes, temps de l'action et coordonnées continues ; les grilles deviennent des représentations ajustables. L'ancien 8×8 à une minute reste une archive, sans promesse à 90 %.
- [x] Pilote cinq parties sans erreur : 6 651 événements horodatés, médiane des positions Faker 60,02 s, aucune nouvelle position dans les horizons ≤30 s. Corpus complet 465/465 : 563 198 événements horodatés, 60 554 lieux valides, 55 122 événements impliquant Faker, 12 975 ancres de sa position et zéro nouvelle position dans les fenêtres 1/5/10/30 s. Agrégat seul dans Git ; aucun ID ni trajectoire publiée.
- [x] Contrat continu `action + délai + lieu éventuel` et métriques en unités de jeu avec provenance et perspective ; tests synthétiques de causalité, coordonnées manquantes et invariance à la grille. Le module n'attribue aucun score à la seconde en l'absence de labels haute fréquence.
- [x] Panneau Scores interactif 1/5/10/30 s et graphique vérifiés en FR/EN. Le curseur change les comptes (par ex. 1 s : 12 507 fenêtres / 770 avec Faker impliqué ; 30 s : 12 280 / 9 702) ; desktop et mobile 390 px sans débordement. Capture réelle et README FR/EN, RESULTS, ROADMAP, NINETY_GATE, SECOND_SCALE mis à jour.
- [x] 53 tests globaux passent ; syntaxe JS, compilation Python, `git diff --check` et route publique vérifiés. L'agrégat ne contient ni match ID, ni joueur individuel, ni trace.
- [x] Livraison M15 sur `main` : commit distant `5bd61221c463542bdc2e39264b0adafe69c56e00`, arbre `f925059a9330b7b637559b97abafa12517d0f028` vérifié identique à l'arbre local testé. Ce journal de clôture est publié dans un second commit. Les données brutes, `.env`, les poids et les traces par partie restent locaux.

## M16 — Prédire les événements attribués à Faker (2026-10-11)

- [x] Protocole inscrit dans `PLAN.md` avant la création du nouveau dataset : sept familles, fenêtre de 10 s, split par match, baselines train uniquement, validation exploratoire et test historique hors sélection.
- [x] Pilote cinq parties : 737 fenêtres, 420 train et 317 validation ; 252 contiennent au moins une famille Faker. Deux tests de causalité et d'attribution passent. Le cache NPZ est par match et versionné ; `ITEM_DESTROYED`/`LEVEL_UP` sont exclus.
- [x] Audit complet depuis le cache : 465/465 sans erreur, 73 482 fenêtres de 10 s ; 58 974 train, 7 480 validation, 7 028 test non lus pour la sélection. Chaque action/issue est reliée à un champ acteur Faker explicite ; les 24 986 fenêtres avec au moins une cible ne sont pas des positions.
- [x] Pilote d'entraînement trois matchs train/deux validation : perte log 0,6254 sur 317 fenêtres ; test de métrique AUPRC avec égalités.
- [x] Entraînement complet sur 373 matchs train, évaluation sur 46 validation / 7 480 fenêtres ; petit réseau de 13 575 paramètres, arrêt anticipé. Perte log 0,19427 contre 0,20481 pour la fréquence par phase ; gain 0,01054, IC bootstrap groupé par match [0,00906 ; 0,01211]. AUPRC macro 0,12110 contre 0,06600. Achats 0,24088 contre 0,08676 ; kill 0,07669 contre 0,05005. Résultats exploratoires : aucune position ni action gagnante prédite.
- [x] Figure agrégée par famille, documentation `FAKER_ACTIONS.md`, README FR/EN, RESULTS, ROADMAP, SECOND_SCALE et NEXT_RESEARCH mis à jour. L'onglet Scores affiche sept barres depuis le JSON public ; la chronologie commune commute les phases, et le sélecteur permet le total. Interface testée dans le navigateur en FR/EN, au début et à 25 min ; écran 390 px sans débordement (375 px de contenu pour 390 px de fenêtre).
- [x] Contrôle anti-métrique trompeuse : « toujours aucun événement » atteint 49 488/52 360 = 94,51 % d'accuracy binaire sur validation tout en ratant 2 872 positifs ; la page et les README l'expliquent. `pytest -q` : 56 tests passés ; syntaxe JS, compilation Python, `git diff --check`, endpoint public HTTP 200 et exclusions `.env`/NPZ/checkpoint confirmés.
- [x] Reprise vérifiée : deuxième construction des 465 matchs depuis NPZ en ~0,12 s, comptes inchangés et aucun nouvel appel Riot.
- [x] Livraison M16 sur `main` : commit distant `e45a447445a9af4f0735211e2ead5a0e5e895814`, arbre `2e2d2cc61988ce22a374b15e39eb47f01ac66fc3` vérifié égal à l'arbre local testé après fetch. Ce journal de clôture est publié dans un second commit. Les JSON Riot, NPZ individuels, pertes par match, poids et clé restent locaux.

## M17 — Rejeu analytique des parties indexées (2026-10-11)

- [x] Périmètre vérifié : le lecteur existant accepte déjà les 465 matchs locaux mais avance par frames d'environ 60 s et affiche la destination réelle à t+1. Planifié un lecteur à horloge en secondes avec événements horodatés et positions tenues au dernier échantillon, puis une analyse rétrospective distincte.
- [x] Trace locale v6 : temps exact de la frame et des événements en secondes, acteur des wards identifié par `creatorId` quand présent, dix joueurs avec coordonnées éventuellement absentes. Pilote trois parties train et deux validation, puis traces complètes : 16 à 30 transitions et 497 à 1 059 événements par partie ; timestamps strictement dans leur transition. Reprise vérifiée par mtime inchangé à la deuxième exportation. Une partie longue de 47 transitions / 1 161 événements s'exporte également.
- [x] Lecteur FR/EN : choix parmi 465 IDs, lecture/pause, curseur à la seconde, 1×/5×/20×/60×, sauts vers les événements majeurs, carte des dix positions au dernier échantillon et leur âge, lieux d'événements uniquement quand ils surviennent. Résultat final et comparatif avec la destination t+1 sont repliés pour éviter le spoiler.
- [x] Contrôles navigateur : passage à 05:00 après la nouvelle frame, horloge en lecture, pause, changement de partie, saut sur un kill à 05:38, traduction anglaise, et vue mobile 390 px sans débordement horizontal (document 375 px). Routes locales : 465 jeux, trace v6 HTTP 200, IDs absents et tentative de traversée rejetés par 404. `pytest -q` : 57 tests ; syntaxe JS et `git diff --check` passent.
- [x] README FR/EN et `REPLAY.md` mis à jour, diagramme de deux horloges ajouté. Les JSON et traces individuels restent locaux ; la page n'est ni une vidéo ni une trajectoire ou une vision à la seconde.
- [x] Livraison M17 sur `main` : commit `1d72f5d4ad26dc3c9b724083bcf2efc34ec48d30`, arbre `7308ac3f506d371f6c208ff618055a47bc5dfecd` égal à l'arbre local testé après fetch. Ce journal de clôture est publié dans un second commit. Clé, JSON Riot, traces de match et poids restent ignorés.

## M18 — Assainissement et challenger Faker à 10 s (2026-10-11)

- [x] Contrat et risques inscrits dans `PLAN.md` avant l'analyse. Les anciens 373/46/46 matchs et scores de validation M16 sont figés ; ancien test et futur lockbox hors sélection.
- [x] Pré-audit en lecture seule des 465 parties : identité PUUID, queue 420, dix IDs, correspondance match/timeline, horloge et durée cohérentes partout. 563 198 événements inspectés ; 11 196 enregistrements ciblables textuellement identiques dans une même partie, surtout des wards et achats. Leur multiplicité ne suffit pas à conclure à une corruption et ne change pas les labels binaires.
- [x] Pilote assaini trois matchs train/deux validation : 737 fenêtres, zéro quarantaine. Les 51 acteurs système `0` et 54 répétitions exactes sont comptés mais non attribués à Faker et non effacés ; aucun timestamp ciblable invalide. Les sources sont fingerprintées pour invalider le cache si le JSON ou les états changent.
- [x] Corpus complet assaini : 465/465 matchs, 73 482 fenêtres (58 974 train, 7 480 validation, 7 028 ancien test non utilisé), zéro quarantaine, mêmes nombres de labels par famille que M16. 7 578 acteurs système `0` et 11 196 répétitions textuelles de toutes les familles ciblables sont signalés ; dédupliquer à l'aveugle confondrait événements multiples légitimes et bruit.
- [x] Challenger causal 48 variables, même architecture MLP à sept têtes, 373 matchs train et 46 validation. Vérification exacte de `t`, `y` et des 37 anciennes variables sur chaque match de validation avant comparaison. Le pilote 5 matchs a tourné ; entraînement complet arrêté au meilleur checkpoint époque 30. Sur 7 480 fenêtres validation, les quatre actes observables passent de 0,22992 à 0,22309 en perte log et de 0,14929 à 0,17404 en AP macro ; gain de perte log 0,00683, IC bootstrap par match [0,00566 ; 0,00796]. Les issues de combat gagnent peu : AP macro 0,08352 → 0,08522. L'ancien test n'a pas été chargé.
- [x] Cache et reprise vérifiés : relance du corpus = 465 hits / 0 rebuild ; le checkpoint entraînement est réutilisé sur une seconde relance. Un NPZ pilote volontairement tronqué est reconstruit automatiquement (4 hits / 1 rebuild). Les features de base sont désormais recalculées depuis les JSON bruts lors d'une reconstruction, sans dépendre d'un ancien NPZ horloge éventuellement périmé.
- [x] Documentation `DATA_SANITATION.md` avec flux Mermaid, contrat de quarantaine, variables, métriques et limites ; nouveau graphique, README FR/EN, RESULTS, ROADMAP et onglet Scores mis à jour. UI vérifiée en français et en anglais, desktop et viewport mobile 390 px : panneau et valeurs visibles, largeur document 375 px, pas de débordement ; JSON et figure servis en HTTP 200. `pytest -q` : 60 tests ; syntaxe JS, compilation Python et diff vérifiés.
- [x] Livraison M18 sur `main` : commit distant `e4977a747ee8c35379d3e65585e2185728c95721`, arbre `62ebd513ff17322686c2eb2e2e9a1f20236085b6` vérifié égal à l'arbre local testé après fetch. Ce journal de clôture est publié dans un second commit. La clé, les JSON Riot, les NPZ individuels, les pertes par match et les poids restent locaux et ignorés.
- [x] Porte prospective revérifiée après livraison : un appel live à la page ranked KR la plus récente reçoit encore HTTP 401 le 11 octobre 2026. Aucune nouvelle partie n'a été comptée ; l'audit et le challenger M18 reposent seulement sur le cache. Statut documenté dans `DATA_SANITATION.md` ; une nouvelle clé Riot est nécessaire pour figer une cohorte future.

## M19 — Base IoC causale pour un futur modèle de langage (2026-10-11)

- [x] Audit des dépôts existants : entrepôt 465 matchs / 12 975 frames / 353 409 événements sélectionnés ; mémoire spatiale 11 313 épisodes train+val ; index de 988 textes ; corpus assaini de 73 482 fenêtres à 10 s. Ces pièces ne constituaient pas encore un registre commun des preuves à `t` et des labels futurs.
- [x] Plan et risques inscrits dans `PLAN.md` avant la construction. La nouvelle base privée `data/processed/faker_ioc.sqlite` version 2 relie par match, frame, participant, événement et fenêtre le JSON Riot et les NPZ assainis. SHA-256 des deux sources et du cache d'actions, split par match, remplacement transactionnel d'une partie modifiée et poursuite après erreur. L'ancien essai de schéma 1 a été archivé localement avant reconstruction ; aucune donnée utilisateur supprimée.
- [x] Pilote trois parties train/deux validation : 5 matchs, 130 frames, 1 300 états joueurs, 6 106 événements et 737 fenêtres, sans erreur. Construction complète : 465 matchs, 12 975 frames, 129 750 états joueurs, 563 198 événements et 73 482 fenêtres (58 974 train / 7 480 validation / 7 028 ancien test). Relance : 465 matchs trouvés en cache et zéro reconstruction.
- [x] Une entrée de fenêtre contient les dix acteurs et les objets déduits des événements jusqu'à `t`, l'âge du dernier relevé et les événements des 60 secondes précédentes. Les 48 champs historiques restent archivés ; l'export strict retire les dix distances par rôle dont le tag `teamPosition` vient des métadonnées de fin de match, et fournit 38 variables. Le label de sept familles sur `(t,t+10 s]` reste dans une clé distincte. Export JSONL privé train seulement vérifié sur cinq exemples ; validation et test exclus. Aucune phrase rétrospective ou statistique finale ne devient entrée.
- [x] `IOC_LEDGER.md`, figure SVG, README FR/EN, vision IoC, roadmap et panneau Corpus FR/EN actualisés ; seuls les agrégats sont servis. Interface vérifiée en navigateur sur ordinateur puis largeur 390 px sans débordement du panneau. Aucun nouveau score ni entraînement LLM revendiqué.
- [x] Export intégral privé : 58 974 lignes de 373 matchs train, 1 118 469 658 octets. Audit en streaming : zéro ligne val/test, zéro événement postérieur à `t`, zéro rôle rétrospectif dans l'entrée, 38 variables par exemple. Intégrité SQLite `ok`, clés étrangères valides, zéro snapshot futur. Relance du builder : 465 cache hits / 0 reconstruction.
- [x] Vérification : 62 tests passent, compilation Python, syntaxe JavaScript et `git diff --check`. Endpoint agrégé HTTP 200 après redémarrage du serveur ; panneau testé FR/EN et viewport 390 px ; journal console navigateur sans erreur. Les données Riot, l'export et les clés restent ignorés de Git.
- [x] Livraison de M19 sur `main` : commit distant `5803dfcc0a95864d0fcb74bd6b9173bd2642b6b0`, arbre `afcb643398ac22e38d3955324e692f3de7d4a840` vérifié égal à l'arbre local testé après fetch. Le push Git HTTPS local était sans identifiants (`Device not configured`) ; publication via connexion GitHub avec vérification de chacun des 20 blobs et de l'arbre. Ce journal de clôture est publié dans un second commit. Les 121 Mo de SQLite, 1,12 Go de JSONL, JSON Riot et secrets restent uniquement locaux.
# M23 — contexte LoL vérifié dans le rejeu (2026-10-12)

- [x] Recherche dans la documentation officielle Riot : Data Dragon fournit des données statiques et images versionnées pour objets/champions ; ses mises à jour peuvent suivre le patch avec retard. Le cache local contient les catalogues d'objets pour les 12 patchs déjà utilisés par les IoC.
- [x] Pilote de cinq timelines : 42 objectifs neutres, 59 destructions de bâtiments, 311 éliminations, 1 414 poses et 347 destructions de wards. Les sous-types des dragons, voies/tours et types de wards sont présents mais `UNDEFINED` est fréquent ; les achats de participant 0 doivent rester exclus.
- [x] Trace privée v10 : acteur, victime, assistants, camp bénéficiaire et base de son attribution, sous-types d'objectifs/wards, voie/tour, patch joué et catalogue officiel d'objets correspondant. Empreinte de cache étendue au catalogue ; aucune requête Riot de match nécessaire. Le bâtiment utilise le camp opposé au `teamId` détruit ; les coordonnées absentes restent nulles.
- [x] Lecture visuelle temporelle : score BLEU/ROUGE à l'instant choisi (kills, structures, dragons, Baron, Héraut, larves, wards), K/D/A de Faker, détails des événements, objets des dix joueurs au dernier relevé et coût/noms Data Dragon. Textes FR/EN, bandeau de provenance, source officielle et inconnu visible si le catalogue manque.
- [x] Pilote de cinq parties réelles : 4 176 événements affichables, cinq catalogues historiques disponibles, zéro erreur de trace. Audit complet ensuite : 465/465 parties lues, 352 121 événements affichables, 33 329 avec lieu Riot, 38 004 wards sans type précis, 114 315/114 315 achats attribués trouvés dans 12 versions Data Dragon. Fichier d'agrégats public d'environ 1 Ko, sans ID de match, PUUID ni clé.
- [x] Validation : 66 tests Python réussis ; syntaxe JS/Python et `git diff --check` réussis. Dans le navigateur, le dragon de terre à 08:07.352 est pris par le bleu, et le panneau se met à jour à cette seconde ; inventaires et version 16.8.1 visibles. Écran mobile 390 px sans débordement, anglais vérifié. README FR/EN, REPLAY et PLAN documentés.
- [x] Publication de M23 sur `main` par la connexion GitHub après l'échec du push HTTPS local sans identifiant (`Device not configured`). Les 13 blobs ont été vérifiés contre leurs SHA Git ; commit distant `b6cd5c87639559010bff48be30b12ec23d7f4007`, arbre `948358791d00e57ebffeb6be5d0cd34614d23f65`, identique à l'arbre local testé. Fetch, comparaison de diff et alignement de la branche locale réussis ; cette clôture est publiée dans un second commit documentaire.
