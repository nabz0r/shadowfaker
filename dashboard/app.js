const copy = {
  fr: {
    nav_atlas: "Atlas 512×512", nav_map: "16×16 historique", nav_replay: "Évolution", nav_research: "Recherche", nav_tempo: "Tempo", nav_strategy: "Stratégies", nav_challenge: "Challenge", nav_library: "Archives", nav_evidence: "Preuves",
    time_title: "CHRONOLOGIE · FAIRE DÉFILER", key_faker: "Faker à t", key_real: "arrivée réelle", key_shadow: "choix Shadow", key_ally: "alliés", key_enemy: "adversaires", key_objective: "objectifs",
    fixed_16: "Archive fixe : ancien modèle 16×16, toutes phases réunies. Sa prédiction par phase n'a pas été conservée ; la frise anime les vues 512×512 de validation ci-dessus.",
    hero_eyebrow: "Laboratoire de décisions macro · KR ranked solo",
    hero_title: "Observer Faker.<br>Tester Shadow.",
    hero_copy: "Nous suivons les décisions du compte « Hide on bush#KR1 » dans le contexte des dix joueurs, des objectifs et d'une vision approximée. Ses positions sont observées environ chaque minute ; une seconde horloge prédit le type du prochain événement à dix secondes, sans prétendre connaître sa position à cette cadence.",
    explore: "Explorer les cartes", evidence: "Voir les preuves", stat_games: "parties utilisables",
    stat_observations: "paires de minutes", stat_exact: "précision 16×16", stat_future: "nouvelles parties pour confirmer",
    map_title: "Où Faker va. Où Shadow pense qu'il va.",
    map_intro: "Déplace la souris sur une case : les deux minimaps utilisent les mêmes 1 197 observations. La couleur montre la fréquence de chaque prochaine position, pas une trajectoire ou la vision du joueur.",
    observed: "FAKER · OBSERVÉ", predicted: "SHADOW · PRÉDIT", less: "rare", more: "fréquent",
    map_insight: "Shadow sur-prédit une case centrale : 39,43 % de ses choix, contre 11,28 % des destinations réelles. La carte révèle une faiblesse concrète du modèle actuel.",
    atlas_title: "Le jeu, case par case et événement par événement", atlas_intro: "Choisis une couche et une phase. La couleur indique où se concentrent les positions ou les événements observés dans les ranked : kills, morts, Dragon, Nashor, Herald, Grubs, bâtiments et wards. Les wards sans coordonnées sont comptées mais pas placées sur la carte.",
    atlas_layer: "Couche", atlas_phase: "Phase", atlas_positions_real: "Destinations observées", atlas_positions_model: "Destinations prédites", atlas_positions_enemy: "Positions adverses", atlas_positions_allies: "Positions alliées", atlas_faker_kill: "Kills du compte", atlas_faker_death: "Morts du compte", atlas_ally_kill: "Kills alliés", atlas_enemy_kill: "Kills adverses", atlas_building: "Bâtiments", atlas_ward: "Wards posées", atlas_early: "0–10 min", atlas_middle: "10–20 min", atlas_late: "20+ min", atlas_total: "Événements dans la phase", atlas_unplaced: "Sans position connue", atlas_note: "Positions échantillonnées ~60 s ; événements horodatés plus finement. Les destinations 512×512 viennent de 46 parties de validation ; joueurs et événements de 465 ranked. Le halo rend les points visibles à l'écran, sans créer de mesures : le survol lit la case exacte. Cette carte agrège des parties, sans reconstituer la vision du joueur.", atlas_hover: "Survole une case", atlas_cell: (x,y,n) => `Case ${x},${y} : ${n.toLocaleString("fr")} ${n === 1 ? "événement ou position" : "événements ou positions"}`,
    surface_title: "La minimap devient une surface de choix", surface_intro: "Les axes au sol sont les coordonnées de la carte ; la hauteur est la fréquence d'une prochaine position. Tourne la surface et compare la distribution réelle à Shadow. La troisième dimension est une fréquence agrégée, pas le relief réel de LoL ni une preuve de stratégie gagnante.",
    surface_actual: "Observé", surface_shadow: "Shadow", surface_rotate: "Angle de vue",
    replay_title: "Une décision change le prochain état", replay_step: "Rejeu historique 16×16 · ~60 s",
    replay_intro: "Cette vue par partie utilise encore le modèle historique 16×16. À chaque frame : depuis la position actuelle, où sera le compte environ une minute plus tard ? Le fond coloré est sa probabilité prédite ; les anneaux montrent la réponse et son choix le plus probable. L'atlas 512×512 ci-dessus est un agrégat distinct de validation.",
    replay_now: "Départ : compte à la minute affichée", replay_team: "Contexte : autres alliés au départ", replay_real: "Arrivée réelle une minute après", replay_guess: "Case prévue par Shadow", replay_minute: "Minute de départ",
    replay_gold: "Écart d'or équipe", replay_xp: "Écart d'XP", replay_level: "Niveau", replay_uncertainty: "Dispersion de prédiction",
    replay_play: "▶ Rejouer", replay_pause: "Ⅱ Pause", replay_trend_note: "Courbe rétrospective de l'écart d'or ; elle n'entre jamais dans l'état passé du modèle.",
    game_picker: "Ouvrir une des 465 parties indexées", game_open: "Ouvrir la partie", ecosystem_title: "Écosystème des dix joueurs · projection 3D", ecosystem_intro: "Le sol est la carte. La hauteur est le niveau observé. Les traits relient Faker aux joueurs proches ; les points montrent l'état à t, les contours leur position suivante. Le losange blanc est le choix du modèle. Proximité et réaction visible ne prouvent pas une influence causale.",
    geometry_title: "Champ local 64×64 · autour de Faker", geometry_intro: "Cette géométrie historique 64×64 colore les cases voisines à t selon un tenseur métrique positif, orienté par le mouvement passé de Faker et les alliés proches. L'arrivée réelle et les événements après t servent à lire la transition, jamais à calculer ce champ.",
    geometry_legend: "Turquoise : Faker à t · rose : arrivée à t+1 · bleu : alliés · rouge : adversaires et leurs déplacements. Le champ coloré est une hypothèse géométrique, pas la probabilité prédite par Shadow.", state_actor: "Acteur",
    accuracy_title: "Ce qu'on sait vraiment prédire", exploratory: "8×8 / 4×4 exploratoires",
    exact_explain: "<strong>16×16 :</strong> Shadow 11,28 %, baseline 11,61 %. Le critère initial n'est pas atteint.",
    metric_exact: "64×64 · CASE EXACTE", metric_exact_note: "Shadow sur 1 197 décisions test", metric_baseline: "BASELINE · CASE FRÉQUENTE", metric_baseline_note: "Meilleure règle simple sur les mêmes décisions", metric_radius: "À 4 CASES PRÈS", metric_radius_note: "Shadow · copie de la position précédente : 16,88 %", metric_coverage: "ZONE QUI COUVRE 91,9 %", metric_coverage_note: "Part moyenne de la carte proposée · seuil ajusté en validation", metric_context: "Ces chiffres viennent d'un test historique déjà inspecté. « 91,9 % » n'est pas une prédiction exacte : la zone couvre en moyenne 1 791 cases sur 4 096. Aucune amélioration prospective ni capacité de jeu supérieure n'est démontrée.",
    predictability_kicker: "LABORATOIRE · 46 PARTIES DE VALIDATION", predictability_title: "Une case exacte, ou presque toute la carte ?", predictability_intro: "Sur la même grille 8×8, agrandir la liste des cases candidates augmente la couverture. Le seuil de 90 % n'est franchi qu'avec 41 cases sur 64.", predictability_badge: "PAS UN TEST FUTUR", predictability_exact: "1 case · précision exacte", predictability_coverage: "41 cases · couverture", predictability_area: "surface de carte proposée", predictability_phase: "Prédire une seule case dans la phase choisie par la chronologie", predictability_limit: "Ces chiffres viennent de la validation de développement, pas du test futur. La visibilité ennemie est une approximation. La chronologie change les barres par tranche de temps ; elle n'invente pas une précision à la seconde.", predictability_full: "Proxy + stats globales", predictability_visible: "Vision approximée", predictability_expert: "Expert par phase", predictability_samples: n => `${n} décisions de validation · même grille 8×8 pour les trois candidats. Aucun ne démontre 90 % de précision exacte.`,
    coarse_explain: "<strong>8×8 et 4×4 :</strong> un signal de rotations plus larges apparaît, mais il a été examiné après lecture du test. Il faut des parties futures.",
    grid512_kicker: "512×512 · 46 PARTIES DE VALIDATION · 1 275 TRANSITIONS", grid512_title: "Plus de pixels. Pas plus de certitude.", grid512_intro: "L'adaptateur 512 choisit une sous-case dans les prédictions 64×64 gelées. Sur validation, il ne trouve aucune case exacte. Copier la position précédente reste meilleur ; la grille plus fine révèle surtout la limite des données à une minute.", grid512_model: "Shadow · case 512 exacte", grid512_copy: "Copier la position précédente", grid512_near: "Shadow · rayon de 16 cases 512", grid512_limit: "Candidat de développement, test historique non consulté et aucune preuve prospective. Les cases 512 font environ 29 unités de carte de côté ; les positions restent observées toutes les ~60 s.", grid64_archive: "Archive séparée ci-dessous : ancien candidat 64×64 sur test historique déjà inspecté. Ses scores ne sont pas les scores du modèle 512×512.",
    event_clock_kicker: "NOUVELLE HORLOGE · 10 SECONDES · 7 480 FENÊTRES DE VALIDATION", event_clock_title: "Quel événement macro vient ensuite ?", event_clock_intro: "Un second modèle combine le dernier état disponible et les événements déjà passés pour prédire le premier événement des dix secondes suivantes. 31 parties EUW attribuées à Faker enrichissent uniquement l'entraînement ; 671 parties professionnelles ajoutent des résumés, sans trajectoires.", event_clock_model: "Perte log · KR + EUW, plus bas est meilleur", event_clock_baseline: "Perte log · règle par phase", event_clock_windows: "Fenêtres KR de 10 s, pas des positions", event_clock_limit: "Résultat exploratoire sur les mêmes 46 parties de validation utilisées pour choisir le modèle. Les positions de Faker restent à ~60 s ; les points d'événement ne sont pas sa localisation ni une preuve de meilleure stratégie.",
    ablation_kicker: "TEST DU CONTEXTE · MÊME MODÈLE · 46 PARTIES KR", ablation_title: "Jungle, bot et support : signal mesuré ?", ablation_intro: "Nous avons réentraîné quatre fois le même modèle en masquant certaines positions alliées ou adverses. Sur cette validation, retirer les distances des alliés améliore très légèrement la perte log (1,390 contre 1,392) ; retirer les seuls rôles jungle/bot/support change presque rien. Cela teste la valeur prédictive de ces six distances, pas l'importance de ces joueurs dans la vraie partie.", ablation_limit: "Écart exploratoire sur une validation déjà utilisée pour le développement ; aucun candidat promu ni test futur consulté. Les wards représentent 52,6 % des cibles ; F1 = 0 pour les kills de Faker, ses morts et les objectifs.",
    research_title: "Ce qu'il faut observer ensuite", research_badge: "Pas de promesse à 90 %", research_intro: "Le score global d'événements masque ce que le modèle manque : les wards sont majoritaires, et les événements décisifs restent mal reconnus. Les trois étapes suivantes partent d'un test falsifiable, pas d'une grille plus fine.",
    research_replay_metric: "1 → 5 parties", research_replay_title: "Aligner avant d'entraîner", research_replay_copy: "Une partie de Faker avec replay et match ID vérifiés, puis cinq. Comparer positions, horloges et wards aux ancres Riot ; jamais inventer ses clics ou sa vision.",
    research_events_title: "Mesurer les événements rares", research_events_copy: "Kills de Faker, morts et objectifs : précision/rappel par classe, calibration et abstention. La validation actuelle est exploratoire.",
    research_vision_metric: "t → t+1", research_vision_title: "Revenir au point de vue du joueur", research_vision_copy: "Comparer la carte visible pour l'équipe, notre proxy et la vue spectateur sur les mêmes parties. Les communications restent inconnues sans source dédiée.",
    research_chart_kicker: "46 PARTIES KR · 7 480 FENÊTRES · MODÈLE KR SEUL", research_chart_title: "Ce que l'accuracy globale cache", research_chart_intro: "Chaque ligne montre le nombre de cibles observées et le F1 du modèle complet pour ce type d'événement. Les barres sont des scores F1, pas des probabilités de victoire.", research_chart_limit: "Même validation réutilisée pendant le développement ; aucun score prospectif. Un F1 nul signifie qu'aucune prédiction top-1 correcte de cette classe n'a été récupérée.", research_ward_label: "Cibles « ward posée »", research_ward_copy: "3 934 fenêtres sur 7 480. L'accuracy d'environ 54 % ne signifie pas que Shadow anticipe les décisions qui font gagner.", research_doc: "Lire le protocole de recherche ↗",
    research_classes: {none:"Aucun événement",faker_kill:"Kill de Faker",faker_death:"Mort de Faker",ally_kill:"Kill allié",enemy_kill:"Kill adverse",objective:"Objectif",structure:"Bâtiment",ward_placed:"Ward posée",ward_cleared:"Ward détruite"},
    tempo_title: "Une équipe qui chauffe et se refroidit", tempo_interactive: "Explorer une tranche de temps", tempo_overview: "Vue d'ensemble fixe des 40 premières minutes. Le graphique coloré ci-dessous réagit au curseur.",
    tempo_interactive_help: "Pourcentage de minutes où Faker se rapproche d'un allié déjà positionné.", minute: "Minute",
    tempo_explain: "Ce sont des rapprochements géométriques, pas des preuves d'aide ou de communication. Le top évolue aussi : aucun rôle n'a un poids constant de 20 %.",
    pressure_title: "La pression autour de Faker", pressure_intro: "On suit les cinq adversaires : leurs positions par phase, combien sont à moins de 2 500 unités de Faker, et combien entrent dans ce rayon entre deux frames. Leurs déplacements sont visibles dans le rejeu. Ce n'est pas une mesure de sorts dépensés ni d'attention mentale.", pressure_limit: "Les états 0/1 et 0/2 sont rares, situés à des moments différents des autres états. Comparer directement leurs moyennes ne démontre ni que Faker attire la pression ni qu'il la réduit.",
    strategy_title: "Et si cinq joueurs allaient bot ?", hypothesis: "Hypothèse, pas résultat",
    strategy_explain: "Dans ces 465 parties, une seule frame précoce montre les cinq alliés dans un rayon de 2 500 unités du bot carry. Cette proximité ne prouve pas une stratégie cinq bot. La question exige de mesurer ce qui est gagné, perdu ailleurs et comment l'adversaire réagit.",
    challenge_title: "Et si les cinq changeaient les règles ?", challenge_badge: "Simulation synthétique", challenge_intro: "Compare cinq hypothèses : tous top, tous mid, tous jungle, tous bot, ou cinq copies imaginaires d'un style macro adaptatif. Le modèle répartit une ressource abstraite et une réponse adverse ; il ne simule ni les combats ni les chances de gagner.", challenge_response: "Réponse adverse après", challenge_sharing: "Partage des ressources", challenge_limit: "Scores en unités arbitraires, hypothèses explicites et non calibrées sur les parties. « Cinq Faker » désigne une allocation fictive : nous n'avons pas cinq agents capables de jouer. Ce visuel sert à trouver des questions à tester en jeu.", challenge_names: {five_top:"5 top",five_mid:"5 mid",five_jungle:"5 jungle",five_bot:"5 bot",five_faker:"5 Faker · hypothèse"}, challenge_readout: (minute,a,b,c) => `À ${minute} min : pression locale ${a} · couverture ${b} · accès aux ressources ${c} (échelles 0–100 arbitraires)`,
    library_title: "Explorer les traces et les récits", library_intro: "La recherche locale relie 930 résumés factuels français/anglais des 465 ranked à des études de cas sourcées, dans leur langue d'origine. Les textes professionnels sont un autre domaine et ne deviennent jamais des labels ranked par simple ressemblance.", library_search: "Rechercher", library_note: "Recherche en texte local avec langue et provenance. Un résultat décrit une partie ou une source ; il ne prouve pas une décision ni sa cause.", library_empty: "Aucun résultat local pour cette recherche.",
    lab_link: "Lire le laboratoire d'hypothèses ↗", evidence_title: "Où nous en sommes",
    step1: "Décrire le compte", step1copy: "465 matches ; timeline et actions à une minute.",
    step2: "Tester le clone", step2copy: "16×16 sous la meilleure baseline ; signaux 8×8 à confirmer.",
    step3: "Attendre du neuf", step3copy: "0/100 nouvelles parties éligibles au premier rafraîchissement.",
    step4: "Jouer et comparer", step4copy: "Une stratégie meilleure exige des parties comparables.",
    demo_title: "Démo locale · une partie de test", demo_copy: "Prédiction et position observée sur une timeline. Fichier local, jamais publié dans Git.",
    footer_note: "Compte Riot vérifié par PUUID ; l'API n'établit pas à elle seule l'identité de la personne. Données brutes et GIF de partie conservés localement. Cet outil raconte les preuves disponibles, pas une victoire sur Faker.",
    map_cell: (col, row, actual, shadow) => `Case ${col},${row} · position réelle ${actual} % · prédiction Shadow ${shadow} %`,
    role_jungle: "Jungle", role_bot: "Bot carry", role_support: "Support", eligible: "minutes éligibles",
    load_error: "Les chiffres agrégés sont indisponibles. Lance le serveur du dashboard depuis le dépôt."
  },
  en: {
    nav_atlas: "512×512 atlas", nav_map: "Legacy 16×16", nav_replay: "Evolution", nav_research: "Research", nav_tempo: "Tempo", nav_strategy: "Strategies", nav_challenge: "Challenge", nav_library: "Archive", nav_evidence: "Evidence",
    time_title: "TIMELINE · SCRUB TO EXPLORE", key_faker: "Faker at t", key_real: "observed arrival", key_shadow: "Shadow choice", key_ally: "allies", key_enemy: "opponents", key_objective: "objectives",
    fixed_16: "Fixed archive: the earlier 16×16 model across all phases. Its per-phase predictions were not retained; the timeline animates the 512×512 validation views above.",
    hero_eyebrow: "Macro decision lab · KR ranked solo", hero_title: "Observe Faker.<br>Test Shadow.",
    hero_copy: "We follow decisions by the account “Hide on bush#KR1” in the context of ten players, objectives and approximate vision. Its positions are observed about every minute; a separate clock predicts the next event type at ten seconds without claiming to know the player's position at that cadence.",
    explore: "Explore the maps", evidence: "See the evidence", stat_games: "usable matches",
    stat_observations: "minute pairs", stat_exact: "16×16 accuracy", stat_future: "new matches needed to confirm",
    map_title: "Where Faker goes. Where Shadow thinks he goes.",
    map_intro: "Hover over a cell: both minimaps use the same 1,197 observations. Colour shows the frequency of next positions, not a path or the player's own view.",
    observed: "FAKER · OBSERVED", predicted: "SHADOW · PREDICTED", less: "rare", more: "frequent",
    map_insight: "Shadow overpredicts one central cell: 39.43% of its choices versus 11.28% of real destinations. The map exposes a concrete weakness of the current model.",
    atlas_title: "The game, cell by cell and event by event", atlas_intro: "Choose a layer and phase. Colour shows where observed positions or ranked events concentrate: kills, deaths, Dragon, Baron, Herald, Grubs, buildings and wards. Wards without coordinates are counted but not placed on the map.",
    atlas_layer: "Layer", atlas_phase: "Phase", atlas_positions_real: "Observed destinations", atlas_positions_model: "Predicted destinations", atlas_positions_enemy: "Enemy positions", atlas_positions_allies: "Ally positions", atlas_faker_kill: "Account kills", atlas_faker_death: "Account deaths", atlas_ally_kill: "Ally kills", atlas_enemy_kill: "Enemy kills", atlas_building: "Buildings", atlas_ward: "Wards placed", atlas_early: "0–10 min", atlas_middle: "10–20 min", atlas_late: "20+ min", atlas_total: "Events in this phase", atlas_unplaced: "Without known position", atlas_note: "Positions are sampled about every 60 s; event timestamps are finer. The 512×512 destinations use 46 validation games; players/events use 465 ranked. A display halo makes points visible without inventing measurements: hover reads the exact cell. This aggregate map is not player vision.", atlas_hover: "Hover over a cell", atlas_cell: (x,y,n) => `Cell ${x},${y}: ${n.toLocaleString("en")} ${n === 1 ? "event or position" : "events or positions"}`,
    surface_title: "The minimap becomes a surface of choices", surface_intro: "The ground axes are map coordinates; height is how often a next position occurs. Rotate the surface and compare reality with Shadow. The third dimension is aggregate frequency, not LoL terrain or proof of a winning strategy.",
    surface_actual: "Observed", surface_shadow: "Shadow", surface_rotate: "View angle",
    replay_title: "A decision changes the next state", replay_step: "Legacy 16×16 replay · ~60 s",
    replay_intro: "This individual-game replay still uses the historical 16×16 model. At each frame, it asks where the account will be about one minute later. The background is its predicted probability; rings mark the observed arrival and model choice. The 512×512 atlas above is a separate validation aggregate.",
    replay_now: "Start: account at displayed minute", replay_team: "Context: other allies at the start", replay_real: "Observed arrival one minute later", replay_guess: "Cell predicted by Shadow", replay_minute: "Starting minute",
    replay_gold: "Team gold difference", replay_xp: "XP difference", replay_level: "Level", replay_uncertainty: "Forecast spread",
    replay_play: "▶ Play", replay_pause: "Ⅱ Pause", replay_trend_note: "Retrospective gold difference; future values never enter the model's past state.",
    game_picker: "Open one of 465 indexed games", game_open: "Open game", ecosystem_title: "Ten-player ecosystem · 3D projection", ecosystem_intro: "The floor is the map. Height is observed level. Links connect Faker to nearby players; dots show state at t and rings their next positions. The white diamond is the model's choice. Proximity and visible reactions do not prove causal influence.",
    geometry_title: "Legacy 64×64 local field · centred on Faker", geometry_intro: "This historical 64×64 geometry colours nearby cells at t with a positive metric tensor oriented by Faker's past movement and nearby allies. The observed arrival and later events explain the transition; they never construct the field.",
    geometry_legend: "Teal: Faker at t · pink: arrival at t+1 · blue: allies · red: opponents and their movements. The coloured field is a geometric hypothesis, not Shadow's predicted probability.", state_actor: "Actor",
    accuracy_title: "What we can really predict", exploratory: "8×8 / 4×4 exploratory",
    exact_explain: "<strong>16×16:</strong> Shadow 11.28%, baseline 11.61%. The original gate is not met.",
    metric_exact: "64×64 · EXACT CELL", metric_exact_note: "Shadow across 1,197 test decisions", metric_baseline: "BASELINE · MOST FREQUENT CELL", metric_baseline_note: "Best simple rule on the same decisions", metric_radius: "WITHIN 4 CELLS", metric_radius_note: "Shadow · copy previous location: 16.88%", metric_coverage: "SET COVERING 91.9%", metric_coverage_note: "Mean share of the proposed map · threshold fitted on validation", metric_context: "These figures come from a previously inspected historical test. ‘91.9%’ is not an exact prediction: the set spans 1,791 of 4,096 cells on average. No prospective improvement or superior playing ability has been shown.",
    predictability_kicker: "LAB · 46 VALIDATION MATCHES", predictability_title: "One exact cell, or almost the whole map?", predictability_intro: "On the same 8×8 grid, a longer shortlist covers more destinations. Reaching 90% coverage takes 41 of 64 cells.", predictability_badge: "NOT A FUTURE TEST", predictability_exact: "1 cell · exact accuracy", predictability_coverage: "41 cells · coverage", predictability_area: "proposed share of map", predictability_phase: "One-cell prediction in the phase selected on the timeline", predictability_limit: "These are development validation figures, not a future test. Enemy visibility is approximated. The timeline switches phase bins; it does not invent second-by-second accuracy.", predictability_full: "Proxy + global stats", predictability_visible: "Vision proxy", predictability_expert: "Phase expert", predictability_samples: n => `${n} validation decisions · same 8×8 grid for all three candidates. None shows 90% exact accuracy.`,
    coarse_explain: "<strong>8×8 and 4×4:</strong> a broader rotation signal appears, but it was explored after seeing the test. Future games are needed.",
    grid512_kicker: "512×512 · 46 VALIDATION GAMES · 1,275 TRANSITIONS", grid512_title: "More pixels. No extra certainty.", grid512_intro: "The 512 adapter selects a subcell within frozen 64×64 predictions. On validation, it finds no exact cells. Copying the previous position remains stronger; the finer grid mainly exposes the limit of one-minute observations.", grid512_model: "Shadow · exact 512 cell", grid512_copy: "Copy previous position", grid512_near: "Shadow · within 16 cells", grid512_limit: "Development candidate; historical test untouched and no prospective evidence. A 512 cell is about 29 map units wide; positions are still observed only about every 60 seconds.", grid64_archive: "Separate archive below: the older 64×64 candidate on an already inspected historical test. Those are not 512×512 model scores.",
    event_clock_kicker: "NEW CLOCK · 10 SECONDS · 7,480 VALIDATION WINDOWS", event_clock_title: "Which macro event comes next?", event_clock_intro: "A second model combines the latest available state with past events to predict the first event in the next ten seconds. Thirty-one EUW games historically attributed to Faker enrich training only; 671 professional games add summaries without trajectories.", event_clock_model: "Log loss · KR + EUW, lower is better", event_clock_baseline: "Log loss · phase rule", event_clock_windows: "KR ten-second windows, not positions", event_clock_limit: "Exploratory result on the same 46 validation matches used to select the model. Faker positions remain sampled at about 60 seconds; event locations are not his position or proof of stronger strategy.",
    ablation_kicker: "CONTEXT TEST · SAME MODEL · 46 KR GAMES", ablation_title: "Do jungle, bot and support add signal?", ablation_intro: "We retrained the same model four times, masking allied or opponent positions. On this validation set, removing allied distances slightly improves log loss (1.390 versus 1.392); removing only the jungle/bot/support role channels changes almost nothing. This tests the predictive value of those six distances, not the importance of those players in the actual game.", ablation_limit: "Exploratory difference on development validation; no candidate was promoted and no future test was opened. Wards make up 52.6% of targets; F1 = 0 for Faker kills, Faker deaths and objectives.",
    research_title: "What we need to observe next", research_badge: "No 90% claim", research_intro: "The global event score hides what the model misses: wards dominate, while decisive events remain poorly detected. Each next step begins with a falsifiable measurement, not a finer grid.",
    research_replay_metric: "1 → 5 games", research_replay_title: "Align before training", research_replay_copy: "Start with one verified Faker replay and match ID, then five. Align positions, clocks and wards with Riot anchors; never infer clicks or player vision from spectator data.",
    research_events_title: "Measure rare events", research_events_copy: "Faker kills, deaths and objectives: class-specific precision/recall, calibration and abstention. Current validation is exploratory.",
    research_vision_metric: "t → t+1", research_vision_title: "Return to the player view", research_vision_copy: "Compare team-visible map, our proxy and spectator view on the same matches. Communication stays unknown without a dedicated source.",
    research_chart_kicker: "46 KR GAMES · 7,480 WINDOWS · KR-ONLY MODEL", research_chart_title: "What global accuracy hides", research_chart_intro: "Each row shows the number of observed targets and the full model's F1 for that event type. Bars are F1 scores, not win probabilities.", research_chart_limit: "Development validation was reused; no prospective score. Zero F1 means no correct top-1 prediction of that class was recovered here.", research_ward_label: "Ward-placement targets", research_ward_copy: "3,934 of 7,480 windows. About 54% accuracy does not mean Shadow anticipates winning decisions.", research_doc: "Read the research protocol ↗",
    research_classes: {none:"No event",faker_kill:"Faker kill",faker_death:"Faker death",ally_kill:"Ally kill",enemy_kill:"Opponent kill",objective:"Objective",structure:"Structure",ward_placed:"Ward placed",ward_cleared:"Ward cleared"},
    tempo_title: "A team that heats up and cools down", tempo_interactive: "Explore a time slice", tempo_overview: "Fixed overview of the first 40 minutes. The coloured chart below responds to the slider.",
    tempo_interactive_help: "Share of minutes when the account moves closer to an ally already positioned at time t.", minute: "Minute",
    tempo_explain: "These are geometric approaches, not proof of help or communication. Top changes too: no role has a fixed 20% weight.",
    pressure_title: "Pressure around Faker", pressure_intro: "We follow all five opponents: their positions by phase, how many are within 2,500 units of Faker, and how many enter that radius between frames. Their paths are visible in the replay. This does not measure spells spent or mental attention.", pressure_limit: "States at 0/1 and 0/2 are rare and occur at different times than the other states. Comparing their means does not show that Faker attracts or reduces pressure.",
    strategy_title: "What if all five went bot?", hypothesis: "Hypothesis, not result",
    strategy_explain: "In these 465 matches, only one early frame has all five allies within 2,500 units of the bot carry. Proximity does not prove a five-bot strategy. The question requires measuring gains, losses elsewhere, and opponent response.",
    challenge_title: "What if all five changed the rules?", challenge_badge: "Synthetic simulation", challenge_intro: "Compare five hypotheses: all top, all mid, all jungle, all bot, or five imaginary copies of an adaptive macro style. The model allocates abstract resources and an opponent response; it does not simulate fights or win chances.", challenge_response: "Opponent reacts after", challenge_sharing: "Resource sharing", challenge_limit: "Arbitrary units, explicit assumptions, and no calibration to played matches. 'Five Faker' is a fictional allocation: we do not have five playable Faker agents. This view helps identify questions for real games.", challenge_names: {five_top:"5 top",five_mid:"5 mid",five_jungle:"5 jungle",five_bot:"5 bot",five_faker:"5 Faker · hypothesis"}, challenge_readout: (minute,a,b,c) => `At ${minute} min: local pressure ${a} · coverage ${b} · resource access ${c} (arbitrary 0–100 scales)`,
    library_title: "Explore traces and stories", library_intro: "Local search connects 930 factual French/English summaries of 465 ranked games to sourced case studies in their original languages. Professional material belongs to another domain and never becomes a ranked label through similarity alone.", library_search: "Search", library_note: "Local text search with language and provenance. A result describes a game or source; it does not prove a decision or its cause.", library_empty: "No local result for this query.",
    lab_link: "Read the strategy hypothesis lab ↗", evidence_title: "Where we stand",
    step1: "Describe the account", step1copy: "465 matches; one-minute timeline and actions.",
    step2: "Test the clone", step2copy: "16×16 below strongest baseline; 8×8 signals need confirmation.",
    step3: "Wait for new games", step3copy: "0/100 eligible new matches on the first refresh.",
    step4: "Play and compare", step4copy: "A stronger strategy requires comparable played games.",
    demo_title: "Local demo · one test match", demo_copy: "Prediction and observed position along a timeline. Local file, never committed to Git.",
    footer_note: "Riot account verified by PUUID; the API alone cannot establish a person's identity. Raw data and per-game GIF stay local. This tool presents available evidence, not a victory over Faker.",
    map_cell: (col, row, actual, shadow) => `Cell ${col},${row} · observed ${actual}% · Shadow predicted ${shadow}%`,
    role_jungle: "Jungle", role_bot: "Bot carry", role_support: "Support", eligible: "eligible minutes",
    load_error: "Aggregate metrics unavailable. Start the dashboard server from the repository."
  }
};

let language = "fr";
let summary = null;
let grid64 = null;
let atlas512 = null;
let atlasGrid = 64;
let grid512Score = null;
let events64 = null;
let challengeData = null;
let pressureData = null;
let predictabilityData = null;
let eventAblation = null;
let challengeScenario = "five_faker";
let atlasValues = null;
let trace = null;
let surfaceMode = "actual";
let replayTimer = null;
let sharedMinute = 0;
const $ = (selector) => document.querySelector(selector);
const percent = (count, total) => (100 * count / total).toFixed(2);
const SVG_NS = "http://www.w3.org/2000/svg";
const phaseAt = (minute) => minute < 10 ? "early" : minute < 20 ? "middle" : "late";
const phaseLabel = (phase) => ({early:"0–10",middle:"10–20",late:"20+"})[phase];

function showSharedMinute() {
  const phase = phaseAt(sharedMinute);
  $("#time-scrubber").value = sharedMinute;
  $("#time-current").textContent = `${sharedMinute} MIN`;
  $("#time-phase").textContent = `${phaseLabel(phase)} MIN`;
  const cohort = atlas512 ? (language === "fr" ? "46 parties de validation pour Faker/Shadow en 512×512" :
    "46 validation games for Faker/Shadow at 512×512") :
    (language === "fr" ? "46 parties test pour Faker/Shadow en 64×64" : "46 test games for Faker/Shadow at 64×64");
  $("#time-interpretation").textContent = language === "fr" ?
    `Cartes : phase ${phaseLabel(phase)} min (${cohort}, 465 ranked pour joueurs/événements) · rejeu : une partie, minute ${trace?.rows?.[Number($("#replay-slider").value)]?.minute.toFixed(0) ?? "—"} · simulation : hypothèse.` :
    `Maps: ${phaseLabel(phase)} min phase (${cohort}, 465 ranked games for players/events) · replay: one game, minute ${trace?.rows?.[Number($("#replay-slider").value)]?.minute.toFixed(0) ?? "—"} · simulation: hypothetical.`;
}

function setSharedMinute(minute) {
  sharedMinute = Math.max(0, Math.min(39, Math.round(Number(minute) || 0)));
  $("#atlas-phase").value = phaseAt(sharedMinute);
  $("#minute-slider").value = Math.min(7, Math.floor(sharedMinute / 5));
  if (trace?.rows?.length) {
    const closest = trace.rows.reduce((best,row,index) =>
      Math.abs(row.minute - sharedMinute) < Math.abs(trace.rows[best].minute - sharedMinute) ? index : best, 0);
    $("#replay-slider").value = closest;
    updateReplay();
  }
  showSharedMinute();
  if (summary) updateTempo();
  if (atlas512 || events64) renderAtlas();
  if (atlas512 || grid64 || summary) renderSurface();
  if (pressureData) renderPressure();
  if (challengeData) renderChallenge();
  if (predictabilityData) renderPredictability();
  if (grid512Score) renderGrid512Score();
  if (eventAblation) renderResearchEvents();
}

function translate() {
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const value = copy[language][element.dataset.i18n];
    if (value !== undefined) element.innerHTML = value;
  });
  document.querySelectorAll("[data-number]").forEach((element) => {
    const value = Number(element.dataset.number);
    element.textContent = value.toLocaleString(language === "fr" ? "fr-FR" : "en-US", {
      minimumFractionDigits: Number.isInteger(value) ? 0 : 3,
      maximumFractionDigits: Number.isInteger(value) ? 0 : 3
    });
  });
  $("#language").textContent = language === "fr" ? "EN" : "FR";
  if (summary) {
    updateTempo();
    updateReadout(7, 7);
    renderSurface();
  }
  if (atlas512 || events64) renderAtlas();
  if (challengeData) renderChallenge();
  if (pressureData) renderPressure();
  if (predictabilityData) renderPredictability();
  if (grid512Score) renderGrid512Score();
  if (eventAblation) renderResearchEvents();
  if (trace) updateReplay();
  showSharedMinute();
}

function updateReadout(col, row) {
  const density = summary.test_map_density;
  const index = row * 16 + col;
  $("#map-readout").textContent = copy[language].map_cell(
    col, row, percent(density.actual[index], density.samples),
    percent(density.predicted[index], density.samples)
  );
}

function renderPredictability() {
  const phase = phaseAt(sharedMinute);
  const data = predictabilityData.by_phase;
  const k = predictabilityData.first_listed_k_at_90_coverage;
  const formatPercent = (value, digits) => `${(100 * value).toLocaleString(language, {minimumFractionDigits: digits, maximumFractionDigits: digits})} %`;
  $("#predictability-exact").textContent = formatPercent(predictabilityData.location_topk8["1"], 2);
  $("#predictability-coverage").textContent = formatPercent(predictabilityData.location_topk8[String(k)], 2);
  $("#predictability-area").textContent = formatPercent(k / 64, 1);
  $("#predictability-coverage-label").textContent = language === "fr" ? `${k} cases · couverture` : `${k} cells · coverage`;
  const rows = [
    ["full", "predictability_full", "#ff536b"],
    ["visible_proxy", "predictability_visible", "#ffd895"],
    ["phase_expert", "predictability_expert", "#90a9ff"]
  ];
  const bars = $("#predictability-phase-bars");
  bars.replaceChildren();
  $("#predictability-phase-label").textContent = `${phaseLabel(phase)} MIN`;
  for (const [key, title, color] of rows) {
    const rate = 100 * data[key][phase].top1_8;
    const bar = document.createElement("div"); bar.className = "predictability-bar";
    const name = document.createElement("span"); name.textContent = copy[language][title];
    const track = document.createElement("div"); track.className = "predictability-bar-track";
    const fill = document.createElement("span"); fill.className = "predictability-bar-fill";
    fill.style.width = `${Math.min(100, rate / 35 * 100)}%`; fill.style.background = color;
    track.append(fill);
    const value = document.createElement("b"); value.textContent = `${rate.toLocaleString(language, {minimumFractionDigits: 1, maximumFractionDigits: 1})} %`;
    bar.append(name, track, value); bars.append(bar);
  }
  $("#predictability-phase-note").textContent = copy[language].predictability_samples(data.full[phase].samples);
}

function renderGrid512Score() {
  const fmt = (value) => `${(100 * value).toLocaleString(language, {minimumFractionDigits: 2, maximumFractionDigits: 2})} %`;
  $("#grid512-model").textContent = fmt(grid512Score.model_top1);
  $("#grid512-copy").textContent = fmt(grid512Score.copy_previous_top1);
  $("#grid512-near").textContent = fmt(grid512Score.within_radius_cells["16"].model);
}

function renderResearchEvents() {
  const counts = eventAblation.class_counts_validation;
  const f1 = eventAblation.variants.find(row => row.name === "full")?.by_class_f1;
  if (!counts || !f1) return;
  const rows = $("#research-event-chart");
  rows.replaceChildren();
  for (const key of Object.keys(counts)) {
    const row = document.createElement("div"); row.className = "research-event-row";
    const label = document.createElement("span"); label.textContent = copy[language].research_classes[key] || key;
    const count = document.createElement("small"); count.textContent = `n=${counts[key].toLocaleString(language)}`;
    const track = document.createElement("div"); track.className = "research-event-track";
    const fill = document.createElement("i"); fill.style.width = `${Math.max(0, Math.min(100, f1[key] * 100))}%`;
    fill.style.background = key === "ward_placed" ? "#ffd895" : f1[key] ? "#ff627b" : "#a26b7c";
    track.append(fill);
    const value = document.createElement("b"); value.textContent = f1[key].toLocaleString(language, {style:"percent", maximumFractionDigits:1});
    row.append(label, count, track, value); rows.append(row);
  }
  const share = counts.ward_placed / eventAblation.validation_windows;
  $("#research-ward-share").textContent = share.toLocaleString(language, {style:"percent", maximumFractionDigits:1});
}

function bindMap(mapImage) {
  mapImage.addEventListener("mousemove", (event) => {
    const bounds = mapImage.getBoundingClientRect();
    const col = Math.max(0, Math.min(15, Math.floor((event.clientX - bounds.left) / bounds.width * 16)));
    const row = Math.max(0, Math.min(15, 15 - Math.floor((event.clientY - bounds.top) / bounds.height * 16)));
    updateReadout(col, row);
  });
  mapImage.addEventListener("mouseleave", () => updateReadout(7, 7));
}

function renderAtlas() {
  const layer = $("#atlas-layer").value;
  const phase = $("#atlas-phase").value;
  const modelPositions = layer === "positions_real" || layer === "positions_model";
  const teamPositions = layer === "positions_enemy" || layer === "positions_allies";
  const positions = modelPositions || teamPositions;
  const canvas = $("#atlas-canvas"), ctx = canvas.getContext("2d");
  ctx.fillStyle = "#091526"; ctx.fillRect(0, 0, 512, 512);
  const modelPhase = grid64?.phases?.[phase] || grid64;
  const fallback = modelPositions ? modelPhase?.[layer === "positions_real" ? "observed_density" : "predicted_density"] :
    teamPositions ? pressureData?.phases[phase][layer === "positions_enemy" ? "enemy_density" : "ally_density"] : events64?.phases?.[phase]?.[layer]?.cells;
  const local = atlas512?.phases?.[phase]?.[layer];
  if (!local && !fallback) {
    $("#atlas-readout").textContent = language === "fr" ? "L'atlas est en cours de calcul." : "The atlas is being computed.";
    return;
  }
  atlasGrid = local ? 512 : 64;
  const entries = local ? local.cells : fallback.flatMap((count, index) => count ? [[index, count]] : []);
  atlasValues = new Map(entries);
  $("#atlas-resolution").textContent = `${atlasGrid} × ${atlasGrid} · ${(atlasGrid ** 2).toLocaleString(language)} ${language === "fr" ? "CASES" : "CELLS"}`;
  const colors = {positions_real:[72,228,210],positions_model:[255,145,193],positions_enemy:[255,79,112],positions_allies:[106,165,255],faker_kill:[255,186,111],
    faker_death:[255,92,122],ally_kill:[105,169,255],enemy_kill:[221,93,162],dragon:[247,170,74],
    baron:[182,121,255],herald:[114,213,225],grubs:[174,246,112],building:[243,239,172],ward_placed:[87,225,225]};
  const rgb = colors[layer] || [130,170,220];
  $("#atlas-layer-swatch").style.background = `rgb(${rgb.join(",")})`;
  $("#atlas-layer-meaning").textContent = `${$("#atlas-layer").selectedOptions[0].textContent} · ${phaseLabel(phase)} min`;
  const max = entries.reduce((value, row) => Math.max(value, row[1]), 1);
  const scale = 512 / atlasGrid;
  if (atlasGrid === 512 && entries.length < 5000) {
    ctx.globalAlpha = .20;
    ctx.fillStyle = `rgb(${rgb.join(",")})`;
    for (const [index] of entries) {
      const x = index % atlasGrid, y = atlasGrid - 1 - Math.floor(index / atlasGrid);
      ctx.fillRect(x - 3, y - 3, 7, 7);
    }
    ctx.globalAlpha = 1;
  }
  for (const [index, count] of entries) {
    const x = index % atlasGrid, y = Math.floor(index / atlasGrid);
    const strength = Math.pow(count / max, .42);
    const channel = (n) => Math.round(8 + (n - 8) * (.18 + .82 * strength));
    ctx.fillStyle = `rgb(${channel(rgb[0])},${channel(rgb[1])},${channel(rgb[2])})`;
    ctx.fillRect(x * scale, (atlasGrid - 1 - y) * scale, scale, scale);
  }
  ctx.strokeStyle = "rgba(190,218,240,.13)"; ctx.lineWidth = 1;
  for (let i = 0; i <= 8; i++) {
    const pixel = i * 64 + .5;
    ctx.beginPath(); ctx.moveTo(pixel, 0); ctx.lineTo(pixel, 512); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, pixel); ctx.lineTo(512, pixel); ctx.stroke();
  }
  $("#atlas-total").previousElementSibling.textContent = modelPositions ?
    (local ? (language === "fr" ? "Destinations de validation" : "Validation destinations") :
             (language === "fr" ? "Destinations du test historique" : "Historical test destinations")) :
    teamPositions ? (language === "fr" ? "Positions des 465 parties" : "Positions across 465 games") : copy[language].atlas_total;
  const oldRecord = events64?.phases?.[phase]?.[layer];
  const total = local ? local.total : modelPositions ? modelPhase.samples : teamPositions ? entries.reduce((n, row) => n + row[1], 0) : oldRecord.total;
  $("#atlas-total").textContent = total.toLocaleString(language);
  $("#atlas-unplaced").textContent = positions ? "—" : (local?.without_position ?? oldRecord?.without_position ?? 0).toLocaleString(language);
  $("#atlas-readout").textContent = copy[language].atlas_hover;
}

function renderChallenge() {
  const tabs = $("#challenge-scenarios"); tabs.replaceChildren();
  for (const key of Object.keys(challengeData.scenarios)) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = copy[language].challenge_names[key];
    button.classList.toggle("active", key === challengeScenario);
    button.addEventListener("click", () => { challengeScenario = key; renderChallenge(); });
    tabs.append(button);
  }
  const delays = [1,2,4], shares = ["0.4","0.7","1.0"];
  const delay = delays[Number($("#challenge-response").value) - 1];
  const sharing = shares[Number($("#challenge-sharing").value)];
  $("#challenge-response-label").textContent = `${delay * 5} min`;
  $("#challenge-sharing-label").textContent = `${Math.round(Number(sharing) * 100)} %`;
  const rows = challengeData.scenarios[challengeScenario][String(delay)][sharing];
  const chart = $("#challenge-chart"); chart.replaceChildren();
  const xAt = (i) => 55 + i * 100, yAt = (v) => 240 - v * 190;
  for (const value of [0,.25,.5,.75,1]) {
    const y = yAt(value);
    chart.append(svgNode("line", {x1: 42,x2: 760,y1:y,y2:y,stroke:"#2c4960"}));
    const label = svgNode("text", {x:8,y:y+4,fill:"#8fa9be","font-size":11});
    label.textContent = `${Math.round(value*100)}`; chart.append(label);
  }
  const series = [["local_pressure","#ff91c1",language === "fr" ? "Pression locale" : "Local pressure"],
                  ["map_coverage","#62e4d8",language === "fr" ? "Couverture" : "Coverage"],
                  ["resource_access","#ffbc77",language === "fr" ? "Ressources" : "Resources"]];
  series.forEach(([key,color,label],j) => {
    chart.append(svgNode("polyline", {points:rows.map((r,i)=>`${xAt(i)},${yAt(r[key])}`).join(" "),
                                     fill:"none",stroke:color,"stroke-width":3}));
    const name = svgNode("text", {x:75+j*210,y:28,fill:color,"font-size":13,"font-weight":700});
    name.textContent = label; chart.append(name);
  });
  rows.forEach((row,i) => {
    const tick = svgNode("text", {x:xAt(i),y:274,fill:"#9cb5c9","font-size":11,"text-anchor":"middle"});
    tick.textContent = `${row.minute}m`; chart.append(tick);
  });
  const selected = rows.reduce((best,row) => Math.abs(row.minute-sharedMinute)<Math.abs(best.minute-sharedMinute)?row:best,rows[0]);
  const cursor = xAt(rows.indexOf(selected));
  chart.append(svgNode("line", {x1:cursor,x2:cursor,y1:40,y2:240,stroke:"#fff8f5","stroke-width":2,"stroke-dasharray":"5 5"}));
  for(const [key,color] of [["local_pressure","#ff91c1"],["map_coverage","#62e4d8"],["resource_access","#ffbc77"]])
    chart.append(svgNode("circle",{cx:cursor,cy:yAt(selected[key]),r:6,fill:color,stroke:"#fff","stroke-width":2}));
  const pct = (x) => `${Math.round(x * 100)}/100`;
  $("#challenge-readout").textContent = copy[language].challenge_readout(
    selected.minute,pct(selected.local_pressure),pct(selected.map_coverage),pct(selected.resource_access));
}

function renderPressure() {
  const svg=$("#pressure-chart");svg.replaceChildren();
  const phases=[["early","0–10"],["middle","10–20"],["late","20+"]];
  const selectedPhase = phaseAt(sharedMinute);
  const selectedRow = pressureData.phases[selectedPhase];
  $("#pressure-phase-readout").textContent = language === "fr" ?
    `${phaseLabel(selectedPhase)} min · ${selectedRow.mean_near_enemies.toFixed(2)} adversaire(s) proches en moyenne · ${selectedRow.arrival_rate_per_frame.toFixed(2)} entrée(s) par frame. Statistiques de 465 parties.` :
    `${phaseLabel(selectedPhase)} min · ${selectedRow.mean_near_enemies.toFixed(2)} nearby opponents on average · ${selectedRow.arrival_rate_per_frame.toFixed(2)} arrivals per frame. Statistics from 465 games.`;
  const yAt=v=>260-v*104;
  for(const mark of [0,.5,1,1.5,2]) {
    const y=yAt(mark);
    svg.append(svgNode("line",{x1:64,x2:760,y1:y,y2:y,stroke:"#34516a"}));
    const label=svgNode("text",{x:17,y:y+4,fill:"#a2bbcd","font-size":12});label.textContent=mark.toFixed(1);svg.append(label);
  }
  for(const [index,[phase,label]] of phases.entries()) {
    const row=pressureData.phases[phase],x=140+index*240;
    if (phase === selectedPhase) svg.append(svgNode("rect",{x:x-24,y:52,width:155,height:245,rx:9,fill:"#724158",opacity:.42,stroke:"#ffd895"}));
    for(const [j,key,color] of [[0,"mean_near_enemies","#ff637d"],[1,"arrival_rate_per_frame","#ffca77"]]) {
      const value=row[key],height=104*value;
      svg.append(svgNode("rect",{x:x+j*54,y:260-height,width:42,height,rx:5,fill:color}));
      const n=svgNode("text",{x:x+j*54+21,y:251-height,fill:color,"font-size":12,"font-weight":700,"text-anchor":"middle"});
      n.textContent=value.toFixed(2);svg.append(n);
    }
    const title=svgNode("text",{x:x+50,y:294,fill:"#dbe9f1","font-size":13,"text-anchor":"middle"});title.textContent=`${label} min`;svg.append(title);
  }
  for(const [i,[label,color]] of [[language==="fr"?"Adversaires proches":"Nearby opponents","#ff637d"],[language==="fr"?"Entrées dans le rayon":"Entries into radius","#ffca77"]].entries()) {
    svg.append(svgNode("rect",{x:80+i*320,y:20,width:12,height:12,fill:color}));
    const t=svgNode("text",{x:100+i*320,y:31,fill:"#dcecf3","font-size":12});t.textContent=label;svg.append(t);
  }
  const cards=$("#pressure-slices");cards.replaceChildren();
  for(const [key,row] of Object.entries(pressureData.score_slices)) {
    const card=document.createElement("div");card.className="pressure-slice";
    const title=document.createElement("strong");title.textContent=key==="other" ? (language==="fr"?"Autres scores":"Other scores") : `Faker ${key}`;
    const value=document.createElement("span");value.textContent=row.mean_near_enemies==null?"—":row.mean_near_enemies.toFixed(2);
    const detail=document.createElement("small");detail.textContent=`${row.frames.toLocaleString(language)} ${language==="fr"?"états · adversaires proches en moyenne":"states · nearby opponents on average"}`;
    card.append(title,value,detail);cards.append(card);
  }
}

function svgNode(name, attributes = {}) {
  const node = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
  return node;
}

function renderSurface() {
  const svg = $("#surface-svg");
  svg.replaceChildren();
  const phase = phaseAt(sharedMinute);
  const modelPhase = grid64?.phases?.[phase] || grid64;
  const local = atlas512?.phases?.[phase];
  const density = local ? {actual: local.positions_real.cells, predicted: local.positions_model.cells,
                           samples: local.positions_real.total} : grid64 ?
    {actual: modelPhase.observed_density, predicted: modelPhase.predicted_density, samples: modelPhase.samples} : summary.test_map_density;
  const grid = local ? 512 : grid64 ? 64 : 16;
  $("#surface-resolution").textContent = `${grid} × ${grid} × P · ${phaseLabel(phase)} MIN`;
  $("#surface-time").textContent = language === "fr" ?
    `${phaseLabel(phase)} min · ${density.samples.toLocaleString(language)} destinations de 46 parties ${local ? "de validation" : "test"} · turquoise = observé, rose = Shadow` :
    `${phaseLabel(phase)} min · ${density.samples.toLocaleString(language)} destinations from 46 ${local ? "validation" : "test"} games · teal = observed, pink = Shadow`;
  const values = density[surfaceMode];
  const maximum = local ? Math.max(1, ...density.actual.map(row => row[1]), ...density.predicted.map(row => row[1])) :
    Math.max(1, ...density.actual, ...density.predicted);
  const radians = Number($("#angle-slider").value) * Math.PI / 180;
  $("#angle-label").textContent = `${$("#angle-slider").value}°`;
  const project = (x, y, z) => {
    const rx = (x - grid / 2) * Math.cos(radians) - (y - grid / 2) * Math.sin(radians);
    const ry = (x - grid / 2) * Math.sin(radians) + (y - grid / 2) * Math.cos(radians);
    return [320 + rx * 336 / grid, 256 + ry * 144 / grid - z];
  };
  const points = (...vertices) => vertices.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const base = [project(0, 0, 0), project(grid, 0, 0), project(grid, grid, 0), project(0, grid, 0)];
  svg.append(svgNode("polygon", {points: points(...base), fill: "#132c42", stroke: "#3a667b", "stroke-width": 1.5}));
  const cells = [];
  if (local) {
    for (const [index, count] of values) {
      const x = index % grid, y = Math.floor(index / grid);
      cells.push({x, y, count, depth: x * Math.sin(radians) + y * Math.cos(radians)});
    }
  } else for (let y = 0; y < grid; y++) for (let x = 0; x < grid; x++) {
    const count = values[y * grid + x];
    if (count) cells.push({x, y, count, depth: x * Math.sin(radians) + y * Math.cos(radians)});
  }
  cells.sort((a, b) => a.depth - b.depth);
  const actual = surfaceMode === "actual";
  for (const {x, y, count} of cells) {
    const height = 116 * Math.sqrt(count / maximum);
    const a = project(x, y, height), b = project(x + 1, y, height);
    const c = project(x + 1, y + 1, height), d = project(x, y + 1, height);
    const b0 = project(x + 1, y, 0), c0 = project(x + 1, y + 1, 0), d0 = project(x, y + 1, 0);
    svg.append(svgNode("polygon", {points: points(b, c, c0, b0), fill: actual ? "#115c68" : "#73305f", stroke: "#264760", "stroke-width": .3}));
    svg.append(svgNode("polygon", {points: points(d, c, c0, d0), fill: actual ? "#1c8690" : "#9b3d76", stroke: "#264760", "stroke-width": .3}));
    const top = svgNode("polygon", {points: points(a, b, c, d), fill: actual ? "#58e1d2" : "#ff91c1",
                                    "fill-opacity": (.25 + .7 * Math.sqrt(count / maximum)).toFixed(2),
                                    stroke: actual ? "#74ebe1" : "#ffc4dd", "stroke-width": .55});
    const title = svgNode("title");
    title.textContent = `${x},${y}: ${percent(count, density.samples)}%`;
    top.append(title); svg.append(top);
  }
  const title = svgNode("text", {x: 28, y: 40, fill: actual ? "#62e4d8" : "#ffa1c9",
                                 "font-size": 16, "font-weight": 700, "letter-spacing": 2});
  title.textContent = actual ? copy[language].surface_actual.toUpperCase() : copy[language].surface_shadow.toUpperCase();
  svg.append(title);
  $("#surface-actual").classList.toggle("active", actual);
  $("#surface-shadow").classList.toggle("active", !actual);
}

function renderTrend(index) {
  const svg = $("#replay-trend");
  svg.replaceChildren();
  const values = trace.rows.map((row) => row.gold_diff);
  const low = Math.min(0, ...values), high = Math.max(0, ...values);
  const span = Math.max(1, high - low);
  const at = (i) => [26 + i * 748 / Math.max(1, values.length - 1), 108 - (values[i] - low) * 85 / span];
  const zeroY = 108 - (0 - low) * 85 / span;
  svg.append(svgNode("line", {x1: 20, x2: 780, y1: zeroY, y2: zeroY, stroke: "#426078", "stroke-dasharray": "5 6"}));
  svg.append(svgNode("polyline", {points: values.map((_, i) => at(i).join(",")).join(" "),
                                  fill: "none", stroke: "#62e4d8", "stroke-width": 3, "stroke-linejoin": "round"}));
  const [x, y] = at(index);
  svg.append(svgNode("line", {x1: x, x2: x, y1: 15, y2: 112, stroke: "#ffbc77", "stroke-width": 2}));
  svg.append(svgNode("circle", {cx: x, cy: y, r: 6, fill: "#ffbc77", stroke: "white", "stroke-width": 1}));
}

function renderLocalField(row) {
  const canvas = $("#replay-field"), ctx = canvas.getContext("2d");
  ctx.fillStyle = "#0b1b2e"; ctx.fillRect(0, 0, 512, 512);
  const own = row.actors_t?.find(a => a.side === "faker");
  const arrived = row.actors_next?.find(a => a.side === "faker");
  if (!own?.xy || !row.metric_t) return;
  const [cx, cy] = own.xy.map(v => v * 64), g = row.metric_t;
  for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
    const dx = x + .5 - cx, dy = y + .5 - cy;
    const d2 = Math.max(0, g[0][0]*dx*dx + 2*g[0][1]*dx*dy + g[1][1]*dy*dy);
    const intensity = Math.exp(-d2 / 2);
    ctx.fillStyle = `rgb(${Math.round(10+34*intensity)},${Math.round(28+181*intensity)},${Math.round(47+170*intensity)})`;
    ctx.fillRect(x*8,(63-y)*8,8,8);
  }
  ctx.strokeStyle = "rgba(210,235,245,.15)";
  for (let k=0;k<=64;k+=8) {
    ctx.beginPath();ctx.moveTo(k*8+.5,0);ctx.lineTo(k*8+.5,512);ctx.stroke();
    ctx.beginPath();ctx.moveTo(0,k*8+.5);ctx.lineTo(512,k*8+.5);ctx.stroke();
  }
  const dot = (xy,color,r,ring=false) => {
    if (!xy) return;
    ctx.beginPath();ctx.arc(xy[0]*512,(1-xy[1])*512,r,0,2*Math.PI);
    ctx.lineWidth=3;ctx.strokeStyle="#f6f8fc";
    if (ring) { ctx.strokeStyle=color;ctx.stroke(); }
    else { ctx.fillStyle=color;ctx.fill();ctx.stroke(); }
  };
  for (const enemy of row.actors_t) if (enemy.side === "enemy") {
    const later=row.actors_next?.find(a=>a.participant===enemy.participant);
    if (enemy.xy && later?.xy) {
      ctx.setLineDash([3,5]);ctx.beginPath();ctx.moveTo(enemy.xy[0]*512,(1-enemy.xy[1])*512);
      ctx.lineTo(later.xy[0]*512,(1-later.xy[1])*512);
      ctx.strokeStyle="#ff607e";ctx.lineWidth=1.6;ctx.stroke();ctx.setLineDash([]);
      dot(later.xy,"#ff607e",6,true);
    }
    dot(enemy.xy,"#ff607e",4);
  }
  for (const actor of row.actors_t) if (actor.side === "ally") dot(actor.xy,"#73aaff",4);
  if (arrived?.xy) {
    ctx.setLineDash([5,7]);ctx.beginPath();ctx.moveTo(own.xy[0]*512,(1-own.xy[1])*512);
    ctx.lineTo(arrived.xy[0]*512,(1-arrived.xy[1])*512);
    ctx.strokeStyle="#ff9ac3";ctx.lineWidth=2;ctx.stroke();ctx.setLineDash([]);
  }
  dot(own.xy,"#62e4d8",8);
  dot(arrived?.xy,"#ff91c1",12,true);
}

function renderStateMatrix(row) {
  renderLocalField(row);
  const coords = (a) => a?.xy ? `${Math.floor(a.xy[0]*64)},${Math.floor(a.xy[1]*64)}` : "?";
  const name = (a) => a.side === "faker" ? `Faker · ${a.champion}` :
    `${a.side === "ally" ? (language === "fr" ? "Allié" : "Ally") : (language === "fr" ? "Adversaire" : "Opponent")} ${a.role.toLowerCase()} · ${a.champion}`;
  const body = $("#state-table tbody"); body.replaceChildren();
  for (const actor of row.actors_t || []) {
    const next = row.actors_next?.find(a => a.participant === actor.participant);
    const tr = document.createElement("tr");
    const cells = [name(actor),coords(actor),coords(next),
      actor.xy && next?.xy ? `${Math.round(Math.hypot(next.xy[0]-actor.xy[0],next.xy[1]-actor.xy[1])*64)} cases` : "?"];
    for (const value of cells) { const td=document.createElement("td");td.textContent=value;tr.append(td); }
    if (actor.side === "faker") tr.className="focus-row";
    body.append(tr);
  }
  const item = row.first_item_next == null ? "—" : row.first_item_next;
  const skill = row.first_skill_next == null ? "—" : row.first_skill_next;
  $("#state-action").textContent = language === "fr" ?
    `Faker : ${coords(row.actors_t?.find(a=>a.side==="faker"))} → ${coords(row.actors_next?.find(a=>a.side==="faker"))} · achat ${item} · compétence ${skill} · clic inconnu` :
    `Faker: ${coords(row.actors_t?.find(a=>a.side==="faker"))} → ${coords(row.actors_next?.find(a=>a.side==="faker"))} · purchase ${item} · skill ${skill} · click unknown`;
  const events = $("#state-events"); events.replaceChildren();
  const title = document.createElement("strong");
  title.textContent = language === "fr" ? "Événements entre t et t+1" : "Events between t and t+1";
  events.append(title);
  for (const event of (row.events_next || []).slice(0,12)) {
    const pill=document.createElement("span");pill.className=`event-pill ${event.category}`;
    pill.textContent=`+${event.seconds_after_t}s · ${event.category.replaceAll("_"," ")}${event.cell64 == null ? " · ?" : ` · ${event.cell64%64},${Math.floor(event.cell64/64)}`}`;
    events.append(pill);
  }
  if ((row.events_next || []).length>12) {
    const more=document.createElement("small");more.textContent=`+${row.events_next.length-12}`;events.append(more);
  }
}

function renderEcosystem(row) {
  const svg=$("#ecosystem-svg");svg.replaceChildren();
  const project=(xy,level=0)=>[410+(xy[0]-xy[1])*310,135+(xy[0]+xy[1])*155-level*8];
  const ground=[[0,0],[1,0],[1,1],[0,1]].map(x=>project(x));
  svg.append(svgNode("polygon",{points:ground.map(p=>p.join(",")).join(" "),fill:"#291621",stroke:"#a05368","stroke-width":2}));
  for(let value=0;value<=1.001;value+=.125) {
    for(const pair of [[[value,0],[value,1]],[[0,value],[1,value]]]) {
      const a=project(pair[0]),b=project(pair[1]);
      svg.append(svgNode("line",{x1:a[0],y1:a[1],x2:b[0],y2:b[1],stroke:"#69404f","stroke-width":.7}));
    }
  }
  const own=row.actors_t?.find(a=>a.side==="faker");
  if(!own?.xy)return;
  const point=(actor)=>project(actor.xy,actor.level);
  const ownPoint=point(own);
  const actors=[...row.actors_t].filter(a=>a.xy).sort((a,b)=>(a.xy[0]+a.xy[1])-(b.xy[0]+b.xy[1]));
  for(const actor of actors) {
    const color=actor.side==="faker"?"#ffd895":actor.side==="ally"?"#70a8ff":"#ff536b";
    const floor=project(actor.xy),upper=point(actor);
    svg.append(svgNode("line",{x1:floor[0],y1:floor[1],x2:upper[0],y2:upper[1],stroke:color,"stroke-width":1.5,opacity:.65}));
    const proximity=Math.hypot(actor.xy[0]-own.xy[0],actor.xy[1]-own.xy[1]);
    if(actor.side!=="faker"&&proximity<2500/15000) {
      svg.append(svgNode("line",{x1:ownPoint[0],y1:ownPoint[1],x2:upper[0],y2:upper[1],stroke:color,
                              "stroke-width":2.2,opacity:.7,"stroke-dasharray":"5 4"}));
    }
    const later=row.actors_next?.find(a=>a.participant===actor.participant);
    if(later?.xy){
      const future=project(later.xy,later.level);
      svg.append(svgNode("line",{x1:upper[0],y1:upper[1],x2:future[0],y2:future[1],stroke:color,
                             "stroke-width":1.2,opacity:.6,"stroke-dasharray":"3 5"}));
      svg.append(svgNode("circle",{cx:future[0],cy:future[1],r:actor.side==="faker"?8:5,
                                   fill:"none",stroke:color,"stroke-width":1.7,opacity:.9}));
    }
    svg.append(svgNode("circle",{cx:upper[0],cy:upper[1],r:actor.side==="faker"?11:7,
                                 fill:color,stroke:"#fff6ec","stroke-width":1.7}));
    const label=svgNode("text",{x:upper[0]+10,y:upper[1]-9,fill:color,"font-size":11,"font-weight":750});
    label.textContent=`${actor.side==="faker"?"FAKER":actor.role.slice(0,3)} · ${actor.level}`;svg.append(label);
  }
  const pred=[(row.predicted_region%16+.5)/16,(Math.floor(row.predicted_region/16)+.5)/16];
  const [px,py]=project(pred);
  svg.append(svgNode("polygon",{points:`${px},${py-9} ${px+8},${py} ${px},${py+9} ${px-8},${py}`,
                                 fill:"#fff",stroke:"#ff536b","stroke-width":2}));
  const enemies=actors.filter(a=>a.side==="enemy"&&Math.hypot(a.xy[0]-own.xy[0],a.xy[1]-own.xy[1])<2500/15000).length;
  const allies=actors.filter(a=>a.side==="ally"&&Math.hypot(a.xy[0]-own.xy[0],a.xy[1]-own.xy[1])<2500/15000).length;
  $("#ecosystem-readout").textContent=language==="fr"?
    `À ${row.minute.toFixed(0)} min : ${enemies} adversaire(s), ${allies} allié(s) dans 2 500 unités de Faker. Hauteur = niveau, anneaux = état suivant.`:
    `At ${row.minute.toFixed(0)} min: ${enemies} opponents, ${allies} allies within 2,500 units of Faker. Height = level, rings = next state.`;
}

function renderMoments() {
  const container=$("#notable-moments");container.replaceChildren();
  if(!trace)return;
  const important=new Set(["faker_kill","faker_death","dragon","baron","herald","grubs","building"]);
  const moments=[];
  trace.rows.forEach((row,index)=>{
    const event=row.events_next?.find(e=>important.has(e.category));
    if(event)moments.push({index,event,minute:row.minute});
  });
  for(const moment of moments.slice(0,20)) {
    const button=document.createElement("button");button.type="button";
    button.textContent=`${moment.minute.toFixed(0)}m · ${moment.event.category.replaceAll("_"," ")}`;
    button.addEventListener("click",()=>{stopReplay();setSharedMinute(moment.minute);});
    container.append(button);
  }
}

function updateReplay() {
  const index = Number($("#replay-slider").value);
  const row = trace.rows[index];
  $("#replay-image").src = `/replay-frames/${row.image}`;
  $("#replay-minute").textContent = row.minute.toFixed(0);
  $("#replay-gold").textContent = `${row.gold_diff >= 0 ? "+" : ""}${row.gold_diff.toLocaleString(language)}`;
  $("#replay-xp").textContent = `${row.xp_diff >= 0 ? "+" : ""}${row.xp_diff.toLocaleString(language)}`;
  $("#replay-level").textContent = row.level;
  $("#replay-entropy").textContent = `${(100 * row.forecast_entropy_0_1).toFixed(0)} %`;
  $("#replay-play").textContent = copy[language][replayTimer ? "replay_pause" : "replay_play"];
  renderTrend(index);
  if (trace.schema_version >= 3) { renderStateMatrix(row);renderEcosystem(row); }
}

function stopReplay() {
  if (replayTimer) clearInterval(replayTimer);
  replayTimer = null;
  if (trace) updateReplay();
}

async function loadReplay() {
  try {
    const response = await fetch("/replay.json", {cache: "no-store"});
    if (!response.ok) return;
    const data = await response.json();
    setTrace(data);
  } catch (_) { /* Per-match trace is local and optional. */ }
}

function setTrace(data) {
  if (!data.rows?.length || data.source_step_seconds !== 60 || data.schema_version < 3) return;
  stopReplay();trace=data;
  $("#replay-slider").max=trace.rows.length-1;$("#replay-slider").value=0;
  $("#replay").hidden=false;$("#replay-nav").hidden=false;
  $("#game-picker").value=trace.match_id;
  $("#game-status").textContent=`${trace.match_id} · ${trace.split} · ${trace.rows.length} frames`;
  renderMoments();setSharedMinute(sharedMinute);
}

async function loadGameList() {
  try {
    const response=await fetch("/api/games");if(!response.ok)return;
    const games=await response.json(),list=$("#game-options");list.replaceChildren();
    for(const game of games){const option=document.createElement("option");option.value=game.match_id;
      option.label=`champion ${game.champion_id} · ${game.states} states`;list.append(option);}
  }catch(_) { /* Local warehouse is optional when viewing published aggregate UI. */ }
}

async function openGame(mid=$("#game-picker").value.trim()) {
  if(!/^KR_\d+$/.test(mid)) {$("#game-status").textContent="Invalid ranked game ID";return;}
  $("#game-status").textContent=language==="fr"?"Chargement de la partie…":"Loading game…";
  try {
    const response=await fetch(`/api/replay?match=${encodeURIComponent(mid)}`);
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    setTrace(await response.json());
  }catch(error){$("#game-status").textContent=String(error);}
}

function updateTempo() {
  const index = Number($("#minute-slider").value);
  const start = index * 5;
  $("#minute-label").textContent = `${start}–${start + 5}`;
  const rows = summary.tempo_5min[`${start}_${start + 5}`];
  const elements = [
    ["approach_jungle", "role_jungle", "#4dd7c9"],
    ["approach_bot", "role_bot", "#78a8ff"],
    ["approach_support", "role_support", "#ffb36c"]
  ];
  const container = $("#tempo-bars");
  container.replaceChildren();
  for (const [key, label, color] of elements) {
    const row = rows[key];
    const rate = row.valid ? 100 * row.positive / row.valid : 0;
    const item = document.createElement("div"); item.className = "tempo-row";
    const heading = document.createElement("div"); heading.className = "tempo-row-heading";
    const role = document.createElement("span"); role.textContent = copy[language][label];
    const number = document.createElement("strong"); number.textContent = `${rate.toFixed(1)} %`;
    heading.append(role, number);
    const track = document.createElement("div"); track.className = "tempo-track";
    const fill = document.createElement("span"); fill.style.width = `${Math.min(100, rate * 4)}%`; fill.style.background = color;
    track.append(fill);
    const eligible = document.createElement("small"); eligible.textContent = `${row.valid.toLocaleString(language)} ${copy[language].eligible}`;
    item.append(heading, track, eligible); container.append(item);
  }
  const graph = $("#tempo-focus");
  graph.replaceChildren();
  const xAt = (i) => 66 + i * 94;
  const yAt = (rate) => 210 - Math.min(20, rate) * 8;
  graph.append(svgNode("rect", {x: xAt(index) - 36, y: 28, width: 72, height: 186,
                                 rx: 9, fill: "#1d4656", opacity: .7}));
  for (const mark of [0, 5, 10, 15, 20]) {
    const y = yAt(mark);
    graph.append(svgNode("line", {x1: 42, x2: 760, y1: y, y2: y, stroke: "#2f4b63", "stroke-width": 1}));
    const label = svgNode("text", {x: 8, y: y + 4, fill: "#9bb3c9", "font-size": 11});
    label.textContent = `${mark}%`; graph.append(label);
  }
  for (const [j, [key, label, color]] of elements.entries()) {
    const rates = Array.from({length: 8}, (_, i) => {
      const r = summary.tempo_5min[`${i * 5}_${i * 5 + 5}`][key];
      return r.valid ? 100 * r.positive / r.valid : 0;
    });
    graph.append(svgNode("polyline", {points: rates.map((v, i) => `${xAt(i)},${yAt(v)}`).join(" "),
                                      fill: "none", stroke: color, "stroke-width": 3, "stroke-linejoin": "round"}));
    graph.append(svgNode("circle", {cx: xAt(index), cy: yAt(rates[index]), r: 7,
                                    fill: color, stroke: "#f5f8fc", "stroke-width": 2}));
    const name = svgNode("text", {x: 68 + j * 230, y: 24,
                                  fill: color, "font-size": 12, "font-weight": 700});
    name.textContent = `${copy[language][label]} ${rates[index].toFixed(1)}%`;
    graph.append(name);
  }
  for (let i = 0; i < 8; i++) {
    const label = svgNode("text", {x: xAt(i), y: 242, fill: i === index ? "#f5f8fc" : "#8da3bb",
                                   "font-size": 11, "text-anchor": "middle", "font-weight": i === index ? 700 : 400});
    label.textContent = `${i * 5}–${i * 5 + 5}`; graph.append(label);
  }
}

async function start() {
  translate();
  try {
    const response = await fetch("/summary.json", {cache: "no-store"});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    summary = await response.json();
    bindMap($("#actual-map")); bindMap($("#predicted-map"));
    updateReadout(7, 7); setSharedMinute(sharedMinute);
    renderSurface();
  } catch (error) {
    $("#map-readout").textContent = copy[language].load_error;
    console.error(error);
  }
  const optional = await Promise.allSettled([fetch("/grid64.json"), fetch("/events64.json"), fetch("/challenge.json"), fetch("/pressure.json"), fetch("/predictability.json"), fetch("/atlas512.json"), fetch("/grid512.json"), fetch("/event-ablation.json")]);
  const payloads = await Promise.all(optional.map(async (item) =>
    item.status === "fulfilled" && item.value.ok ? item.value.json() : null));
  [grid64, events64, challengeData, pressureData, predictabilityData, atlas512, grid512Score, eventAblation] = payloads;
  if (summary && (atlas512 || grid64)) renderSurface();
  if (atlas512 || events64) renderAtlas();
  if (challengeData) renderChallenge();
  if (pressureData) renderPressure();
  if (predictabilityData) renderPredictability();
  if (grid512Score) renderGrid512Score();
  if (eventAblation) renderResearchEvents();
  showSharedMinute();
  await loadGameList();
  try {
    const response = await fetch("/demo.gif", {method: "HEAD"});
    if (response.ok) $("#demo").hidden = false;
  } catch (_) { /* Demo is optional and local only. */ }
  await loadReplay();
}

async function searchLibrary() {
  const query = $("#library-query").value.trim();
  const results = $("#library-results"); results.replaceChildren();
  if (!query) return;
  try {
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const rows = await response.json();
    if (!rows.length) { results.textContent = copy[language].library_empty; return; }
    for (const row of rows) {
      const card=document.createElement("article");card.className="library-result";
      const meta=document.createElement("strong");
      meta.textContent=`${row.language.toUpperCase()} · ${row.source_kind.replaceAll("_"," ")} · ${row.status.replaceAll("_"," ")}`;
      const body=document.createElement("p");body.textContent=row.content;
      const source=document.createElement("small");source.textContent=row.provenance;
      card.append(meta,body,source);results.append(card);
      if(row.source_key.startsWith("generated:")) {
        const mid=row.source_key.split(":")[1];
        const open=document.createElement("button");open.className="library-open";open.type="button";
        open.textContent=language==="fr"?"Ouvrir cette partie ↗":"Open this game ↗";
        open.addEventListener("click",async()=>{await openGame(mid);location.hash="replay";});
        card.append(open);
      }
    }
  } catch (error) { results.textContent=String(error); }
}

$("#language").addEventListener("click", () => { language = language === "fr" ? "en" : "fr"; translate(); });
$("#library-search").addEventListener("click",searchLibrary);
$("#library-query").addEventListener("keydown",event=>{if(event.key==="Enter")searchLibrary();});
$("#game-open").addEventListener("click",()=>openGame());
$("#game-picker").addEventListener("keydown",event=>{if(event.key==="Enter")openGame();});
$("#time-scrubber").addEventListener("input",event=>setSharedMinute(event.target.value));
$("#time-scrubber").addEventListener("wheel",event=>{event.preventDefault();setSharedMinute(sharedMinute+(event.deltaY>0?1:-1));},{passive:false});
$("#minute-slider").addEventListener("input", () => setSharedMinute(Number($("#minute-slider").value)*5));
$("#atlas-layer").addEventListener("change", () => { if (atlas512 || events64) renderAtlas(); });
$("#atlas-phase").addEventListener("change", () => setSharedMinute(({early:0,middle:10,late:20})[$("#atlas-phase").value]));
$("#atlas-canvas").addEventListener("mousemove", (event) => {
  if (!atlasValues) return;
  const bounds = event.target.getBoundingClientRect();
  const x = Math.min(atlasGrid - 1, Math.max(0, Math.floor((event.clientX - bounds.left) / bounds.width * atlasGrid)));
  const y = Math.min(atlasGrid - 1, Math.max(0, atlasGrid - 1 - Math.floor((event.clientY - bounds.top) / bounds.height * atlasGrid)));
  $("#atlas-readout").textContent = copy[language].atlas_cell(x,y,atlasValues.get(y*atlasGrid+x) || 0);
});
$("#atlas-canvas").addEventListener("mouseleave", () => { if (atlas512 || events64) $("#atlas-readout").textContent = copy[language].atlas_hover; });
$("#challenge-response").addEventListener("input", () => { if (challengeData) renderChallenge(); });
$("#challenge-sharing").addEventListener("input", () => { if (challengeData) renderChallenge(); });
$("#surface-actual").addEventListener("click", () => { surfaceMode = "actual"; if (summary) renderSurface(); });
$("#surface-shadow").addEventListener("click", () => { surfaceMode = "predicted"; if (summary) renderSurface(); });
$("#angle-slider").addEventListener("input", () => { if (summary) renderSurface(); });
$("#replay-slider").addEventListener("input", () => { stopReplay(); if (trace) setSharedMinute(trace.rows[Number($("#replay-slider").value)].minute); });
$("#replay-play").addEventListener("click", () => {
  if (!trace) return;
  if (replayTimer) { stopReplay(); return; }
  if (Number($("#replay-slider").value) >= trace.rows.length - 1) setSharedMinute(trace.rows[0].minute);
  replayTimer = setInterval(() => {
    const next = Number($("#replay-slider").value) + 1;
    if (next >= trace.rows.length) { stopReplay(); return; }
    setSharedMinute(trace.rows[next].minute);
  }, 750);
  updateReplay();
});
start();
