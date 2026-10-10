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
