const copy = {
  fr: {
    nav_atlas: "Atlas 512×512", nav_map: "16×16 historique", nav_replay: "Rejouer", nav_accuracy: "Scores", nav_research: "Recherche", nav_tempo: "Tempo", nav_pressure: "Pression", nav_strategy: "Stratégies", nav_challenge: "Challenge", nav_finals: "Finales BO5", nav_library: "Archives", nav_evidence: "Preuves",
    finals_title: "Six étoiles. Vingt-cinq manches de finale.", finals_intro: "Explore les six finales mondiales gagnées par Faker et T1/SKT. Chaque manche a son résultat, sa durée et une source vérifiable. Les parties professionnelles restent un corpus distinct : ici, pas de replay Riot, de clics ni de trajectoire inventée.", finals_epic: "Autres parties marquantes à étudier", finals_limit: "Fiches factuelles publiques indexées séparément des 465 timelines ranked KR. Les liens pointent vers les statistiques de Games of Legends ; le titre 2025 est confirmé par le copropriétaire de T1. Ce catalogue guide une future annotation de VOD, il n'entraîne pas Shadow.",
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
    replay_title: "Rejouer une partie, suivre chaque événement", replay_step: "Horloge en secondes · positions ~60 s",
    replay_intro: "Choisis une partie classée indexée. L'horloge suit les événements horodatés ; les dix points restent à leur dernière position réellement observée jusqu'à la frame suivante. C'est un rejeu analytique de la timeline Riot, pas une vidéo ni le point de vue de Faker.",
    live_kicker: "PARTIE LOCALE · CHRONOLOGIE OBSERVÉE", live_title: "Dix joueurs, une horloge", live_allies: "Alliés", live_enemies: "Adversaires", live_event: "Lieu d'événement", live_feed: "Événements déjà observés", live_speed: "Vitesse", live_limit: "Les événements ont leur temps propre. Les joueurs n'ont une nouvelle position qu'aux frames Riot (~60 s) ; aucun trajet ou clic entre frames n'est inventé. Les lieux des événements ne sont pas la position de Faker. Vision et communications inconnues.", replay_analysis: "Ouvrir l'analyse rétrospective : prévision Shadow et arrivée réelle à la minute suivante", game_spoiler: "Voir la fiche de fin de partie · résultat et objets finaux",
    replay_now: "Départ : compte à la minute affichée", replay_team: "Contexte : autres alliés au départ", replay_real: "Arrivée réelle une minute après", replay_guess: "Case prévue par Shadow", replay_minute: "Minute de départ",
    replay_gold: "Écart d'or équipe", replay_xp: "Écart d'XP", replay_level: "Niveau", replay_uncertainty: "Dispersion de prédiction",
    replay_play: "▶ Rejouer", replay_pause: "Ⅱ Pause", replay_trend_note: "Courbe rétrospective de l'écart d'or ; elle n'entre jamais dans l'état passé du modèle.",
    game_picker: "Ouvrir une des 465 parties indexées", game_open: "Ouvrir la partie", ecosystem_title: "Écosystème des dix joueurs · projection 3D", ecosystem_intro: "Le sol est la carte. La hauteur est le niveau observé. Les traits relient Faker aux joueurs proches ; les points montrent l'état à t, les contours leur position suivante. Le losange blanc est le choix du modèle. Proximité et réaction visible ne prouvent pas une influence causale.",
    geometry_title: "Champ local 64×64 · autour de Faker", geometry_intro: "Cette géométrie historique 64×64 colore les cases voisines à t selon un tenseur métrique positif, orienté par le mouvement passé de Faker et les alliés proches. L'arrivée réelle et les événements après t servent à lire la transition, jamais à calculer ce champ.",
    geometry_legend: "Turquoise : Faker à t · rose : arrivée à t+1 · bleu : alliés · rouge : adversaires et leurs déplacements. Le champ coloré est une hypothèse géométrique, pas la probabilité prédite par Shadow.", state_actor: "Acteur",
    accuracy_title: "Ce qu'on observe, ce que Shadow prédit", exploratory: "SECONDES · MODÈLES HISTORIQUES",
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
    nav_atlas: "512×512 atlas", nav_map: "Legacy 16×16", nav_replay: "Replay", nav_accuracy: "Scores", nav_research: "Research", nav_tempo: "Tempo", nav_pressure: "Pressure", nav_strategy: "Strategies", nav_challenge: "Challenge", nav_finals: "BO5 finals", nav_library: "Archive", nav_evidence: "Evidence",
    finals_title: "Six stars. Twenty-five final games.", finals_intro: "Explore Faker and T1/SKT's six winning Worlds finals. Every game has a result, duration and verifiable source. Professional games are a separate corpus: no Riot replay, clicks or invented trajectory appears here.", finals_epic: "Other landmark games to investigate", finals_limit: "Public match facts are indexed separately from the 465 KR ranked timelines. Links lead to Games of Legends statistics; T1's co-owner confirms the 2025 title. This catalogue guides future VOD annotation and does not train Shadow.",
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
    replay_title: "Replay a game, follow every event", replay_step: "Second clock · positions ~60 s",
    replay_intro: "Choose an indexed ranked game. The clock follows timestamped events; all ten player markers stay at their last observed positions until the next frame. This is an analytical Riot timeline replay, not a video or Faker's player view.",
    live_kicker: "LOCAL GAME · OBSERVED CHRONOLOGY", live_title: "Ten players, one clock", live_allies: "Allies", live_enemies: "Opponents", live_event: "Event location", live_feed: "Events observed so far", live_speed: "Speed", live_limit: "Events have their own timestamps. Player positions update only at Riot frames (~60 s); no path or clicks between frames are invented. Event locations are not Faker's position. Vision and communication are unknown.", replay_analysis: "Open retrospective analysis: Shadow forecast and actual arrival one minute later", game_spoiler: "Show end-of-game card · result and final items",
    replay_now: "Start: account at displayed minute", replay_team: "Context: other allies at the start", replay_real: "Observed arrival one minute later", replay_guess: "Cell predicted by Shadow", replay_minute: "Starting minute",
    replay_gold: "Team gold difference", replay_xp: "XP difference", replay_level: "Level", replay_uncertainty: "Forecast spread",
    replay_play: "▶ Play", replay_pause: "Ⅱ Pause", replay_trend_note: "Retrospective gold difference; future values never enter the model's past state.",
    game_picker: "Open one of 465 indexed games", game_open: "Open game", ecosystem_title: "Ten-player ecosystem · 3D projection", ecosystem_intro: "The floor is the map. Height is observed level. Links connect Faker to nearby players; dots show state at t and rings their next positions. The white diamond is the model's choice. Proximity and visible reactions do not prove causal influence.",
    geometry_title: "Legacy 64×64 local field · centred on Faker", geometry_intro: "This historical 64×64 geometry colours nearby cells at t with a positive metric tensor oriented by Faker's past movement and nearby allies. The observed arrival and later events explain the transition; they never construct the field.",
    geometry_legend: "Teal: Faker at t · pink: arrival at t+1 · blue: allies · red: opponents and their movements. The coloured field is a geometric hypothesis, not Shadow's predicted probability.", state_actor: "Actor",
    accuracy_title: "What we observe, what Shadow predicts", exploratory: "SECONDS · HISTORICAL MODELS",
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

Object.assign(copy.fr, {
  live_roster:"Dix joueurs · dernier état observé",live_filter:"Filtrer le flux",live_filter_all:"Tout",live_filter_faker:"Faker",live_filter_combat:"Combats",live_filter_objective:"Objectifs",live_filter_vision:"Vision",live_filter_economy:"Achats & compétences",live_prev:"← Événement",live_next:"Événement →",live_event:"Lieux d'événements",
  replay_audit_labels:["parties vérifiées","frames de positions","événements datés","frontières corrigées"],replay_audit_note:"Audit des 465 timelines : 1 794 événements existent dès la première frame ; 30 sont rangés dans le conteneur suivant. Le lecteur les place à leur timestamp propre. Aucune trajectoire entre frames n'est déduite.",
  nav_corpus:"Corpus", guide_choose:"Choisir une seule couche", guide_choose_copy:"La carte affiche le type sélectionné, pas dix joueurs superposés.", guide_point:"Un carré = une case", guide_point_copy:"Plus il est lumineux, plus cette case contient d'observations. Le halo aide seulement à voir une case isolée.", guide_hover:"Survoler pour compter", guide_hover_copy:"Le panneau donne le type, la phase, la coordonnée et le nombre exact.",
  map_key_real:"Gauche : arrivées observées", map_key_shadow:"Droite : choix du modèle", map_key_cell:"Une tuile = une région 16×16 ; même coordonnée sur les deux cartes.", surface_key_xy:"Plan X/Y : position sur la minimap", surface_key_z:"Hauteur Z : nombre de destinations dans la case", surface_key_one:"La vue montre une distribution agrégée, jamais dix joueurs à cet instant.",
  replay_key_now:"Point plein : position à t", replay_key_next:"Anneau : arrivée à t+1", replay_key_model:"Losange : case prédite", replay_key_limit:"Le fond est une probabilité du modèle 16×16 ; les autres joueurs sont des observations Riot à t.",
  corpus_title:"Qu'avons-nous vraiment en mémoire ?", corpus_intro:"Les fichiers bruts restent sur cette machine. Ici, seuls leurs volumes et leur sens sont publiés : une partie avec une timeline ranked, un résumé professionnel et une fiche de finale ne donnent pas la même résolution.", corpus_cached:"JSON de match en cache", corpus_cached_note:"toutes queues et régions du cache", corpus_timeline:"Timelines JSON", corpus_timeline_note:"les remakes peuvent manquer", corpus_usable:"Ranked KR exploitables", corpus_usable_note:"seules cibles du modèle spatial", corpus_facts:"Fiches de fin de match", corpus_facts_note:"pour explorer, jamais pour prédire à t", corpus_source:"Source", corpus_volume:"Volume", corpus_have:"Ce qu'on observe", corpus_use:"Usage correct", corpus_kr_have:"Positions des dix joueurs ~60 s, économie, niveaux, événements horodatés", corpus_kr_use:"États causaux et labels spatiaux ; split par partie", corpus_euw_have:"Timelines ranked, identité historique attribuée", corpus_euw_use:"Appoint au train d'événements, pas preuve d'identité", corpus_other:"Autres queues KR", corpus_other_have:"Matchs et timelines d'autres modes", corpus_other_use:"Archive locale, hors train ranked", corpus_pro:"Résumés pro 2022–2026", corpus_pro_have:"Score final, patch, champion, ligue ; miroir non vérifié", corpus_pro_use:"Découverte de cas, aucune trajectoire", corpus_finals:"Finales gagnées", corpus_finals_have:"Résultat, durée, lien par manche", corpus_finals_use:"Pistes de VOD, pas de labels de mouvement", corpus_states:"frames d'état", corpus_actors:"observations de joueurs", corpus_transitions:"transitions Faker", corpus_events:"événements indexés", corpus_position_kicker:"POURQUOI DES POINTS MANQUENT SUR LA CARTE", corpus_position_copy:"Achats, points de compétence et beaucoup de wards n'ont pas de coordonnées dans la timeline. Même quand un kill est positionné, le point peut être celui de la victime. Une position d'événement n'est donc jamais automatiquement celle de Faker.", corpus_next_title:"Ce que cet index change, et le prochain verrou", corpus_next_copy:"Date UTC, champion, côté bleu/rouge, score K/D/A, dégâts, vision, objets et compositions rendent les 465 parties retrouvables. Ce sont des données finales : les ajouter aux entrées à t tricherait. Pour viser une prédiction spatiale sous la minute, il faut un replay assorti au match ID, vérifier l'horloge et la vision, puis piloter cinq parties et tester sur des parties futures.", corpus_open_library:"Explorer les fiches de parties ↗",
  catalog_title:"465 parties, enfin lisibles", catalog_intro:"Recherche par champion, objet, date UTC, patch, ID ou composition. Ces cartes sont des statistiques finales du match et ne servent pas d'entrées au modèle à la minute t.", catalog_more:"Afficher plus", catalog_win:"VICTOIRE", catalog_loss:"DÉFAITE", catalog_unknown:"RÉSULTAT INCONNU", catalog_allies:"Alliés", catalog_enemies:"Adversaires", catalog_items:"Objets finaux", catalog_damage:"Dégâts champions", catalog_vision:"Vision", catalog_cs:"CS", catalog_duration:"Durée", catalog_side_blue:"CÔTÉ BLEU", catalog_side_red:"CÔTÉ ROUGE", catalog_filter_placeholder:"Azir, Sablier, 2026-09, KR_…", catalog_filter_label:"Filtrer les parties ranked", catalog_found:n=>`${n.toLocaleString("fr")} parties trouvées`,
  pressure_intro:"On compte les adversaires observés autour de Faker à chaque frame Riot (~60 s). Choisis une zone : les moyennes, les entrées et les états 0/1 ou 0/2 sont recalculés pour ce rayon.", pressure_zone:"Rayon autour de Faker", pressure_scheme:"Schéma d'échelle : le cercle suit le rayon choisi, pas une trajectoire ni des positions réelles.", pressure_near:"Adversaires proches", pressure_near_help:"Moyenne de joueurs ennemis avec position connue dans le cercle, sur une frame observée. Unité : joueurs par frame (0 à 5).", pressure_arrivals:"Entrées observées", pressure_arrival_help:"Ennemis positionnés hors du cercle à la frame précédente puis dedans à la suivante. Unité : entrées nettes par frame ; l'instant exact reste inconnu.", pressure_clock:"Tranche temporelle", pressure_clock_help:"Le curseur global choisit 0–10, 10–20 ou 20+ minutes. Les barres restent des moyennes sur toutes les parties.", pressure_live_kicker:"UNE PARTIE · DIX JOUEURS · MINUTE OBSERVÉE", pressure_live_title:"Qui est vraiment autour de Faker ?", pressure_live_intro:"La carte et la liste suivent la partie chargée et la frise commune. Les points sont des positions de timeline ; le cercle suit le rayon choisi.", pressure_game_label:"Partie indexée", pressure_game_open:"Charger", pressure_live_limit:"Positions et inventaires reconstruits depuis la timeline à t. La carte révèle aussi les adversaires cachés à Faker : ce n'est pas sa vision ni une mesure de sorts dépensés. Les icônes d'objets utilisent un atlas récent, parfois différent du patch joué.",
  atlas_point:(label,phase,x,y,count,grid,cohort)=>`${label} · ${phase} min · ${cohort} · case ${x},${y} sur ${grid}×${grid} : ${count.toLocaleString("fr")} observation${count>1?"s":""} exacte${count>1?"s":""}.`,
  atlas_empty:(label,phase,cohort)=>`${label} · ${phase} min · ${cohort}. Survole une case pour lire son compte exact ; la lueur autour n'ajoute aucun point.`,
  map_cell:(col,row,actual,shadow)=>`Case ${col},${row} sur 16×16 · Faker observé : ${actual} % des 1 197 arrivées · Shadow : ${shadow} % des 1 197 choix.`
});
Object.assign(copy.en, {
  live_roster:"Ten players · latest observed state",live_filter:"Filter feed",live_filter_all:"All",live_filter_faker:"Faker",live_filter_combat:"Fights",live_filter_objective:"Objectives",live_filter_vision:"Vision",live_filter_economy:"Purchases & skills",live_prev:"← Event",live_next:"Event →",live_event:"Event locations",
  replay_audit_labels:["audited games","position frames","timed events","fixed boundaries"],replay_audit_note:"Audit of 465 timelines: 1,794 events exist at the first frame; 30 are stored in the next container. The reader places them at their own timestamp. No path between frames is inferred.",
  nav_corpus:"Corpus", guide_choose:"Select one layer", guide_choose_copy:"The map shows the selected type, not ten players overlaid.", guide_point:"One square = one cell", guide_point_copy:"Brighter cells contain more observations. The halo only makes isolated cells visible.", guide_hover:"Hover to count", guide_hover_copy:"The panel identifies type, phase, coordinates and exact count.",
  map_key_real:"Left: observed arrivals", map_key_shadow:"Right: model choices", map_key_cell:"One tile = one 16×16 region; matching coordinates across the two maps.", surface_key_xy:"X/Y plane: minimap position", surface_key_z:"Z height: number of destinations in the cell", surface_key_one:"An aggregate distribution, never ten players in one instant.",
  replay_key_now:"Solid dot: position at t", replay_key_next:"Ring: observed arrival at t+1", replay_key_model:"Diamond: predicted cell", replay_key_limit:"The background is a 16×16 model probability; other players are Riot observations at t.",
  corpus_title:"What do we actually have in memory?", corpus_intro:"Raw files stay on this machine. Only aggregate counts and their meaning are published here: a ranked timeline, a professional summary and a final-game card have different resolution.", corpus_cached:"Cached match JSON", corpus_cached_note:"all queues and regions in the cache", corpus_timeline:"Timeline JSON", corpus_timeline_note:"short remakes can be absent", corpus_usable:"Usable KR ranked", corpus_usable_note:"the spatial model's target cohort", corpus_facts:"Post-game cards", corpus_facts_note:"for exploration, never prediction at t", corpus_source:"Source", corpus_volume:"Volume", corpus_have:"What we observe", corpus_use:"Valid use", corpus_kr_have:"Ten-player positions ~60 s, economy, levels, timestamped events", corpus_kr_use:"Causal states and spatial labels; split by match", corpus_euw_have:"Ranked timelines, historically attributed identity", corpus_euw_use:"Auxiliary event training, not identity proof", corpus_other:"Other KR queues", corpus_other_have:"Matches and timelines from other modes", corpus_other_use:"Local archive, outside ranked training", corpus_pro:"Pro summaries 2022–2026", corpus_pro_have:"Final score, patch, champion, league; unverified mirror", corpus_pro_use:"Case discovery, no trajectories", corpus_finals:"Winning finals", corpus_finals_have:"Result, duration and link per game", corpus_finals_use:"VOD leads, no movement labels", corpus_states:"sampled states", corpus_actors:"player observations", corpus_transitions:"Faker transitions", corpus_events:"indexed events", corpus_position_kicker:"WHY MAP POINTS ARE MISSING", corpus_position_copy:"Purchases, skill points and many wards have no coordinates in the timeline. A positioned kill can be located at the victim. An event position is never automatically Faker's position.", corpus_next_title:"What this index changes, and the next gate", corpus_next_copy:"UTC date, champion, blue/red side, K/D/A, damage, vision, items and compositions make 465 games discoverable. These are final statistics: using them as time-t inputs would leak the future. Spatial prediction below a minute needs a replay matched to a game ID, clock and vision checks, a five-game pilot and a future-game test.", corpus_open_library:"Explore the game cards ↗",
  catalog_title:"465 games, readable at last", catalog_intro:"Search by champion, item, UTC date, patch, ID or composition. These cards contain final-match statistics, never time-t model inputs.", catalog_more:"Show more", catalog_win:"WIN", catalog_loss:"LOSS", catalog_unknown:"RESULT UNKNOWN", catalog_allies:"Allies", catalog_enemies:"Opponents", catalog_items:"Final items", catalog_damage:"Champion damage", catalog_vision:"Vision", catalog_cs:"CS", catalog_duration:"Duration", catalog_side_blue:"BLUE SIDE", catalog_side_red:"RED SIDE", catalog_filter_placeholder:"Azir, Hourglass, 2026-09, KR_…", catalog_filter_label:"Filter ranked games", catalog_found:n=>`${n.toLocaleString("en")} games found`,
  pressure_intro:"We count observed opponents near Faker in each Riot frame (~60 s). Select a zone to recalculate averages, entries and 0/1 or 0/2 states for that radius.", pressure_zone:"Radius around Faker", pressure_scheme:"Scale diagram: the circle follows your chosen radius, not real player locations or paths.", pressure_near:"Nearby opponents", pressure_near_help:"Mean enemies with known positions inside the circle per observed frame. Unit: players per frame (0 to 5).", pressure_arrivals:"Observed entries", pressure_arrival_help:"Enemies with known positions outside the circle in one frame and inside it in the next. Unit: net entries per frame; exact timing is unknown.", pressure_clock:"Time slice", pressure_clock_help:"The shared slider selects 0–10, 10–20 or 20+ minutes. Bars remain averages across all games.", pressure_live_kicker:"ONE GAME · TEN PLAYERS · OBSERVED MINUTE", pressure_live_title:"Who is actually around Faker?", pressure_live_intro:"The map and roster follow the selected game and shared time slider. Points are timeline positions; the circle follows the selected radius.", pressure_game_label:"Indexed game", pressure_game_open:"Load", pressure_live_limit:"Positions and inventories are reconstructed from the timeline at t. The map also reveals opponents hidden from Faker: it is not his vision or a measure of spells spent. Item icons use a recent atlas that may differ from the played patch.",
  atlas_point:(label,phase,x,y,count,grid,cohort)=>`${label} · ${phase} min · ${cohort} · cell ${x},${y} of ${grid}×${grid}: ${count.toLocaleString("en")} exact observation${count===1?"":"s"}.`,
  atlas_empty:(label,phase,cohort)=>`${label} · ${phase} min · ${cohort}. Hover a cell for its exact count; the display halo adds no data points.`,
  map_cell:(col,row,actual,shadow)=>`Cell ${col},${row} of 16×16 · Faker observed: ${actual}% of 1,197 arrivals · Shadow: ${shadow}% of 1,197 choices.`
});
Object.assign(copy.fr, {
  corpus_ids_kicker:"RIOT IDS · RÉGION · PREUVE", corpus_ids_title:"Les pseudonymes exacts du corpus",
  corpus_ids_note:"Riot résout un Riot ID en PUUID, mais ne certifie pas l'identité de la personne. Les alias historiques sont attribués par des sources externes ; seuls les matches KR du compte principal forment la cible spatiale.",
  corpus_events_kicker:"TIMELINE · TYPE · POSITION", corpus_events_title:"Que veut dire un événement ?",
  corpus_events_note:"Volume indexé et fraction avec coordonnées par type. Les ventes, destructions et annulations d'objets sont comptées dans les JSON bruts pour reconstruire l'inventaire, mais hors de l'ancien total d'événements indexés."
});
Object.assign(copy.en, {
  corpus_ids_kicker:"RIOT IDS · REGION · EVIDENCE", corpus_ids_title:"Exact account names in the corpus",
  corpus_ids_note:"Riot resolves a Riot ID to a PUUID but does not certify the human player. Historical aliases rely on outside attribution; only the main KR account supplies spatial targets.",
  corpus_events_kicker:"TIMELINE · TYPE · LOCATION", corpus_events_title:"What does an event mean?",
  corpus_events_note:"Indexed volume and located fraction by type. Item sales, destruction and undo are counted in raw JSON to reconstruct inventories but sit outside the older indexed-event total."
});
Object.assign(copy.fr, {challenge_compose_title:"Compose cinq présences hypothétiques",
  challenge_allocation_title:"Qui occupe quelle zone à cette minute ?",
  challenge_allocation_note:"Bleu = nos cinq présences hypothétiques. Rouge = cinq réponses adverses prévues par la règle choisie. Chaque colonne est un nombre de joueurs, pas un avantage réel en jeu."});
Object.assign(copy.en, {challenge_compose_title:"Compose five hypothetical presences",
  challenge_allocation_title:"Who occupies each zone at this minute?",
  challenge_allocation_note:"Blue = our five hypothetical presences. Red = five opponent responses under the selected rule. Each column is a player count, not a real in-game advantage."});
copy.fr.challenge_names.custom="Composer 5 joueurs";
copy.en.challenge_names.custom="Compose 5 players";
copy.fr.pressure_live_limit="Positions Riot à t ; adversaires parfois cachés à Faker. Les objets sont une estimation par événements : trinkets initiaux et améliorations automatiques peuvent manquer. Audit final : 29 % des sets exacts. Les icônes utilisent un atlas récent distinct du patch joué.";
copy.en.pressure_live_limit="Riot positions at t may reveal enemies hidden from Faker. Items are estimated from events: starting trinkets and automatic upgrades can be missing. Final-set audit: 29% exact. Icons use a recent atlas distinct from the played patch.";
Object.assign(copy.fr, {guide_choose_copy:"Le fond montre une couche agrégée ; les points des dix joueurs viennent d'une seule partie et peuvent être masqués.",
  ioc_vision_title:"Une mémoire de la partie, centrée sur Faker",ioc_vision_intro:"À chaque minute observée, nous suivons les dix joueurs et estimons leurs objets depuis les événements déjà survenus. Le patch joué fournit les propriétés ; les événements futurs restent des cibles.",
  ioc_core:"état + interactions",ioc_items:"objets horodatés",ioc_patch:"catalogue du patch",ioc_vision_limit:"La visibilité ennemie est un proxy de dernière observation, pas la vraie minimap de Faker. Une page de builds actuelle ne révèle ni son inventaire passé ni sa décision.",
  ioc_vision_link:"Lire la matrice, les sources et les limites ↗",ioc_vision_result:"Validation réutilisée : 17,41 % en 8×8 ; gain d'ablation incertain. L'inventaire par événements n'est exact que pour 29 % des sets d'objets finaux. Couvrir 90 % des destinations requiert 40/64 cases.",
  ioc_source_riot:"12 patches de parties · propriétés statiques d'objets · utilisées à t",ioc_source_ugg:"Contexte de build public · pas de feature historique ; accès automatisé refusé",ioc_source_google:"Découverte de sources seulement · aucun snippet converti en vérité de match"});
Object.assign(copy.en, {guide_choose_copy:"The background is one aggregate layer; points for ten players come from one game and can be hidden.",
  ioc_vision_title:"A game memory centred on Faker",ioc_vision_intro:"At each observed minute we track ten players and estimate their items from events already seen. The played patch supplies properties; later events remain targets.",
  ioc_core:"state + interactions",ioc_items:"timestamped items",ioc_patch:"patch catalog",ioc_vision_limit:"Enemy visibility is a last-seen proxy, not Faker's real minimap. A current build page reveals neither a past inventory nor a decision.",
  ioc_vision_link:"Read the matrix, sources and limits ↗",ioc_vision_result:"Reused validation: 17.41% at 8×8; uncertain ablation lift. The event inventory matches only 29% of final item sets exactly. Covering 90% of destinations needs 40/64 cells.",
  ioc_source_riot:"12 played patches · static item properties · used at t",ioc_source_ugg:"Public build context · no historical feature; automated access denied",ioc_source_google:"Source discovery only · no snippet converted to match truth"});
Object.assign(copy.fr,{event_validation_kicker:"AUDIT · JSON RIOT ↔ INDEX LOCAL",event_validation_title:"Quels événements sont vraiment validés ?",
  event_validation_intro:"Nous comparons chaque ligne indexée à son événement d'origine. Le contrôle prouve une transcription fidèle des champs, pas la vision ni l'intention de Faker.",
  event_validation_doc:"Méthode et décisions ↗",event_validation_exact:"lignes indexées exactes",
  event_validation_actor:"achats / skills sans joueur attribuable",event_validation_neutral:"morts sans tueur joueur",
  event_validation_plates:"plaques hors index principal"});
Object.assign(copy.en,{event_validation_kicker:"AUDIT · RIOT JSON ↔ LOCAL INDEX",event_validation_title:"Which events are actually verified?",
  event_validation_intro:"Each indexed row is compared with its original event. This checks field transcription, not Faker's vision or intent.",
  event_validation_doc:"Method and decisions ↗",event_validation_exact:"exact indexed rows",
  event_validation_actor:"purchases / skills without player attribution",event_validation_neutral:"deaths without a player killer",
  event_validation_plates:"plates outside the main index"});
Object.assign(copy.fr,{nav_team:"Faker × équipe",team_title:"La mémoire d'une équipe autour de Faker",team_domain:"Corpus pro séparé",team_intro:"Doran, Oner et Keria ne sont pas trois variables fixes. Leur expérience commune avec Faker change à chaque manche. Ici, la matrice mesure les parties jouées ensemble et les ressources visibles à 10 puis 15 minutes ; elle ne lit ni la voix ni les déplacements.",team_year:"Période",team_total:"Parties passées",team_recent:"Mémoire 90 j",team_doc:"Méthode & provenance ↗",team_games:"manches avec Faker et cinq rôles",team_snapshots:"états complets à 10/15 min",team_latest:"dernier match du miroir",team_matrix_kicker:"QUI A JOUÉ AVEC QUI ?",team_matrix_title:"Matrice des manches communes",team_matrix_note:"Une case = nombre de manches professionnelles dans la période choisie où les deux noms figurent dans les cinq lignes T1.",team_curve_kicker:"AVANT LA MANCHE, PAS APRÈS",team_curve_title:"L'expérience commune s'accumule",team_curve_note:"Cumul avant le dernier match de chaque mois. La courbe décroissante donne moins de poids aux parties anciennes (demi-vie 90 jours).",team_resources_kicker:"PHOTO DU SCORE À 10 → 15 MINUTES",team_resources_title:"Où l'avantage se déplace",team_resources_note:"Moyenne des écarts or/XP de chaque rôle face à son opposant. La variation indique le déplacement du score entre 10 et 15 minutes, pas un transfert prouvé entre coéquipiers.",team_interpret_title:"Ce que cette expérience ne mesure pas",team_interpret:"Jouer ensemble crée des occasions de se connaître ; le nombre de manches ne mesure pas l'entente, la communication, le leadership ou une influence causale de Faker. Les chiffres viennent d'un miroir public tiers, arrêté à la date affichée ci-dessus, et restent hors de l'entraînement solo queue.",team_all:"Toute l'histoire",team_gold10:"Or vs lane · 10 min",team_gold15:"Or vs lane · 15 min",team_swing:"Δ or 10→15",team_xp_swing:"Δ XP 10→15",team_roles:{top:"TOP",jng:"JUNGLE",mid:"FAKER · MID",bot:"BOT",sup:"SUPPORT"},team_count:n=>`${n} manches avec les sept valeurs à 10/15 minutes pour chaque joueur · moyenne descriptive, sans positions ni voix.`});
Object.assign(copy.en,{nav_team:"Faker × team",team_title:"A team's memory around Faker",team_domain:"Separate pro corpus",team_intro:"Doran, Oner and Keria are not fixed variables. Their shared experience with Faker changes game by game. This matrix measures matches played together and resources visible at minutes 10 and 15; it sees neither voice nor movement.",team_year:"Period",team_total:"Prior games",team_recent:"90-day memory",team_doc:"Method & provenance ↗",team_games:"games with Faker and five roles",team_snapshots:"complete 10/15-minute states",team_latest:"last mirror game",team_matrix_kicker:"WHO PLAYED WITH WHOM?",team_matrix_title:"Shared-game matrix",team_matrix_note:"Each cell counts professional games in the selected period where both names appear among T1's five player rows.",team_curve_kicker:"BEFORE EACH GAME",team_curve_title:"Shared experience accumulates",team_curve_note:"History before the final game of each month. The decayed curve gives older games less weight (90-day half-life).",team_resources_kicker:"SCOREBOARD AT 10 → 15 MINUTES",team_resources_title:"Where the advantage shifts",team_resources_note:"Average gold/XP difference of each role versus its opponent. Change means scoreboard movement between minutes 10 and 15, not a proven transfer between teammates.",team_interpret_title:"What this experience cannot measure",team_interpret:"Playing together creates opportunities to know each other; game count does not measure trust, communication, leadership or Faker's causal influence. These figures come from a third-party public mirror ending on the date shown above and remain outside solo-queue training.",team_all:"All years",team_gold10:"Gold vs lane · 10 min",team_gold15:"Gold vs lane · 15 min",team_swing:"Δ gold 10→15",team_xp_swing:"Δ XP 10→15",team_roles:{top:"TOP",jng:"JUNGLE",mid:"FAKER · MID",bot:"BOT",sup:"SUPPORT"},team_count:n=>`${n} games with all seven 10/15-minute fields for each player · descriptive mean, no positions or voice.`});
Object.assign(copy.fr,{team_correlation_kicker:"MOUVEMENTS ENTRE RÔLES",team_correlation_title:"Qui varie avec qui ?",team_correlation_note:"Corrélation des variations d'écart d'or 10→15 min, manche par manche. +1 = évoluent ensemble ; 0 = pas de lien linéaire ; −1 = évoluent en sens contraire. Ni direction ni causalité ne sont déduites.",team_correlation_limit:"Échantillon limité aux mêmes manches complètes que la matrice ci-dessus ; un état global favorable peut faire progresser plusieurs rôles ensemble.",team_corr_roles:{top:"TOP",jng:"JNG",mid:"FAKER",bot:"BOT",sup:"SUP"}});
Object.assign(copy.en,{team_correlation_kicker:"HOW ROLES MOVE TOGETHER",team_correlation_title:"Which gaps move together?",team_correlation_note:"Correlation of the 10→15-minute gold-gap changes across games. +1 = move together; 0 = no linear association; −1 = move in opposite directions. Neither direction of influence nor causality follows.",team_correlation_limit:"Uses the same complete games as the scoreboard above; a favorable global game state may lift several roles together.",team_corr_roles:{top:"TOP",jng:"JNG",mid:"FAKER",bot:"BOT",sup:"SUP"}});
Object.assign(copy.fr,{probe_kicker:"CHALLENGE CHRONOLOGIQUE · 10 → 15 MIN",probe_title:"Est-ce que l'histoire commune aide vraiment ?",probe_intro:"On prédit l'écart d'or de Faker à 15 minutes à partir du score à 10 minutes. Trois méthodes affrontent les mêmes 72 manches test ; moins d'erreur est mieux.",probe_doc:"Protocole, chiffres et limites ↗",probe_methods:["Copier le score à 10 min","Contexte à 10 min","Contexte + parties communes"],probe_verdict:"Signal non confirmé : l'historique commun ne bat pas la simple copie du score à 10 minutes.",probe_detail:(d,lo,hi,n)=>`Gain de l'historique face au contexte : ${(-d).toLocaleString("fr-FR",{minimumFractionDigits:2,maximumFractionDigits:2})} or d'erreur en moins ; intervalle 95 % de ${lo.toLocaleString("fr-FR",{minimumFractionDigits:2})} à ${hi.toLocaleString("fr-FR",{minimumFractionDigits:2})} pour la différence historique − contexte (n = ${n} manches test). L'intervalle traverse zéro. Score pro omniscient, ni décision de Faker ni précision de Shadow.`});
Object.assign(copy.en,{probe_kicker:"CHRONOLOGICAL CHALLENGE · 10 → 15 MIN",probe_title:"Does shared history actually help?",probe_intro:"We predict Faker's 15-minute gold gap from the 10-minute scoreboard. Three methods face the same 72 test games; lower error is better.",probe_doc:"Protocol, numbers and limits ↗",probe_methods:["Copy 10-minute score","10-minute context","Context + shared games"],probe_verdict:"Signal not confirmed: shared history does not beat simply copying the 10-minute score.",probe_detail:(d,lo,hi,n)=>`History versus context: ${(-d).toFixed(2)} less gold error; 95% interval ${lo.toFixed(2)} to ${hi.toFixed(2)} for history − context (n = ${n} test games). The interval crosses zero. Omniscient pro scoreboard, neither Faker's decisions nor Shadow accuracy.`});
Object.assign(copy.fr,{ninety_kicker:"PORTE 90 % · UNE CASE EXACTE",ninety_title:"Et si Shadow ne répondait que lorsqu'il est sûr ?",ninety_intro:"On classe ses prédictions par confiance. L'axe horizontal mesure la part des transitions servies, pas la surface de carte proposée.",ninety_badge:"SEUIL NON ATTEINT",ninety_all_label:"Toutes les transitions · case 8×8 exacte",ninety_best_label:"Les 5 % les plus confiantes · 64 décisions",ninety_lockbox_label:"Nouvelles parties testées",ninety_limit:"Validation déjà utilisée pour choisir le modèle : exploratoire. Aucun seuil n'atteint 90 % avec une couverture utile. La collecte future est suspendue car la clé Riot a expiré ; aucun test prospectif ouvert.",ninety_doc:"Protocole exact et prochaines données ↗"});
Object.assign(copy.en,{ninety_kicker:"90% GATE · ONE EXACT CELL",ninety_title:"What if Shadow answers only when confident?",ninety_intro:"Predictions are ranked by confidence. The horizontal axis measures the share of transitions answered, not map area proposed.",ninety_badge:"GATE NOT MET",ninety_all_label:"All transitions · exact 8×8 cell",ninety_best_label:"Most confident 5% · 64 decisions",ninety_lockbox_label:"New games tested",ninety_limit:"The model was already selected using this validation cohort: exploratory. No threshold reaches 90% at useful coverage. Fresh collection is paused by an expired Riot key; no prospective test has been opened.",ninety_doc:"Exact protocol and next data ↗"});
Object.assign(copy.fr,{memory_title:"Un souvenir, une hypothèse, une réponse",memory_intro:"10 038 décisions de train alimentent une base locale de situations. Le challenger retrouve des cas proches, calibre ses choix sur des parties distinctes et prédit la prochaine région. Essayez vous-même sur des exemples de validation.",memory_doc:"Méthode et limites ↗",memory_retrieval:"mémoire · top-1 8×8",memory_baseline:"règle rôle/phase",memory_shadow:"Shadow IoC",memory_scores_limit:"Même validation réutilisée de 46 parties. La mémoire ne bat ni la règle ni Shadow ; aucune promotion du modèle. 512×512 désigne des cases de destination, pas une mesure à 512 Hz.",memory_you:"votre choix",memory_model:"mémoire",memory_actual:"observé",memory_instruction:"Cliquez une case : où Faker sera-t-il à la prochaine minute observée ?",memory_reveal:"Révéler",memory_next:"Cas suivant",memory_quiz_limit:"Ce quiz n'entraîne rien depuis le navigateur. La mémoire est calibrée sur le train ; les réponses de validation servent seulement à mesurer l'erreur.",memory_case:(n,total,row)=>`Cas ${n}/${total} · ${row.champion} · ${row.role} · minute ${row.minute}`,memory_feedback:(choice,pred,actual)=>`Votre case : ${choice ?? "—"} · Mémoire : ${pred} · Observé : ${actual}${choice===actual?" · juste !":""}`});
Object.assign(copy.en,{memory_title:"A memory, a guess, an answer",memory_intro:"10,038 training decisions form a local case memory. The challenger retrieves similar situations, tunes its choices on separate training matches, then predicts the next region. Try held-out validation cases yourself.",memory_doc:"Method and limits ↗",memory_retrieval:"memory · top-1 8×8",memory_baseline:"role/phase rule",memory_shadow:"Shadow IoC",memory_scores_limit:"Same reused validation set of 46 matches. Retrieval trails both the rule and Shadow; no model promotion. 512×512 means destination cells, not 512 Hz observations.",memory_you:"your choice",memory_model:"memory",memory_actual:"observed",memory_instruction:"Click a cell: where will Faker be at the next observed minute?",memory_reveal:"Reveal",memory_next:"Next case",memory_quiz_limit:"The browser quiz does not train a model. Retrieval is calibrated within training matches; validation answers measure error only.",memory_case:(n,total,row)=>`Case ${n}/${total} · ${row.champion} · ${row.role} · minute ${row.minute}`,memory_feedback:(choice,pred,actual)=>`Your cell: ${choice ?? "—"} · Memory: ${pred} · Observed: ${actual}${choice===actual?" · correct!":""}`});

Object.assign(copy.fr,{second_kicker:"CIBLE · SECONDES ET ESPACE CONTINU",second_title:"Que voit-on vraiment entre deux images ?",second_intro:"La grille n'est qu'un affichage ajustable. Ce curseur compte les événements réellement horodatés après une position connue de Faker ; il ne reconstitue pas ses déplacements entre les frames.",second_doc:"Source, cible et protocole ↗",second_horizon:"Fenêtre après la dernière position observée",second_windows:"fenêtres auditées",second_events:"avec un événement horodaté",second_faker:"avec Faker impliqué",second_position:"avec une nouvelle position de Faker",second_event_bar:"Événement API",second_faker_bar:"Faker impliqué",second_position_bar:"Position Faker observée",second_limit:"Un lieu d'événement n'est pas la position du joueur. La médiane entre positions observées vaut 60,02 s. Aucun score de déplacement de Faker à la seconde n'est encore établi."});
Object.assign(copy.en,{second_kicker:"TARGET · SECONDS AND CONTINUOUS SPACE",second_title:"What can we actually see between frames?",second_intro:"The grid is an adjustable display. This slider counts truly timestamped events after a known Faker position; it does not reconstruct his movement between frames.",second_doc:"Source, target and protocol ↗",second_horizon:"Window after the last observed position",second_windows:"audited windows",second_events:"with a timestamped event",second_faker:"with Faker involved",second_position:"with a new Faker position",second_event_bar:"API event",second_faker_bar:"Faker involved",second_position_bar:"Observed Faker position",second_limit:"An event locus is not the player's position. The median gap between observed positions is 60.02 s. There is no second-scale Faker movement score yet."});
Object.assign(copy.fr,{ninety_kicker:"ARCHIVE · CASE 8×8 À LA MINUTE",ninety_title:"L'ancien score de case, à sa juste place",ninety_intro:"Diagnostic d'un modèle à la minute : la confiance trie ses anciennes réponses. La cible actuelle porte sur des actions à la seconde et un espace continu.",ninety_badge:"ARCHIVE · 90 % NON ATTEINT",ninety_doc:"Audit historique de cette métrique ↗"});
Object.assign(copy.en,{ninety_kicker:"ARCHIVE · NEXT-MINUTE 8×8 CELL",ninety_title:"The old cell score in context",ninety_intro:"A minute-scale model diagnostic: confidence ranks its earlier answers. The current target is second-scale action and continuous space.",ninety_badge:"ARCHIVE · 90% NOT MET",ninety_doc:"Historical audit of this metric ↗"});

Object.assign(copy.fr,{faker_actions_kicker:"NOUVEAU MODÈLE · FAKER · 10 SECONDES",faker_actions_title:"Que fait Faker ensuite ?",faker_actions_intro:"Sept familles attribuées à Faker sur 46 parties de validation. Achats, compétences et wards sont des actes observables ; kill, mort et assistance sont des issues. La phase suit aussi le curseur de partie.",faker_actions_phase:"Phase évaluée",faker_actions_all:"Toutes",faker_actions_early:"Début <10 min",faker_actions_middle:"Milieu 10–20 min",faker_actions_late:"Fin ≥20 min",faker_actions_nll:"Perte log du modèle ↓",faker_actions_baseline:"Règle par phase ↓",faker_actions_ap:"AP moyenne · 7 familles ↑",faker_actions_empty:"Toujours « rien » · accuracy trompeuse",faker_actions_model:"Shadow",faker_actions_rule:"Règle par phase",faker_actions_unit:"Précision moyenne par famille · % ; plus haut = mieux",faker_actions_limit:"La règle « toujours rien » paraît forte car les événements sont rares, mais rate tous les cas positifs. Validation historique réutilisée ; ni lieu de Faker à la seconde ni action gagnante mesurée.",faker_actions_doc:"Protocole et résultats complets ↗",faker_actions_positive:"cas positifs",faker_actions_labels:{purchase:"Achat",skill_point:"Compétence",ward_placed:"Ward posée",ward_cleared:"Ward détruite",kill:"Kill · issue",death:"Mort · issue",assist:"Assistance · issue"}});
Object.assign(copy.en,{faker_actions_kicker:"NEW MODEL · FAKER · NEXT 10 SECONDS",faker_actions_title:"What does Faker do next?",faker_actions_intro:"Seven Faker-attributed families across 46 validation games. Purchases, skill points and wards are observable acts; kills, deaths and assists are outcomes. The shared game clock also selects the phase.",faker_actions_phase:"Evaluated phase",faker_actions_all:"All phases",faker_actions_early:"Early <10 min",faker_actions_middle:"Middle 10–20 min",faker_actions_late:"Late ≥20 min",faker_actions_nll:"Model log loss ↓",faker_actions_baseline:"Phase rule ↓",faker_actions_ap:"Mean AP · 7 families ↑",faker_actions_empty:"Always none · misleading accuracy",faker_actions_model:"Shadow",faker_actions_rule:"Phase rule",faker_actions_unit:"Average precision per family · %; higher is better",faker_actions_limit:"The always-none rule looks strong because events are rare, yet misses every positive case. Reused historical validation; neither Faker's second-scale position nor action value is measured.",faker_actions_doc:"Full protocol and scores ↗",faker_actions_positive:"positive cases",faker_actions_labels:{purchase:"Purchase",skill_point:"Skill point",ward_placed:"Ward placed",ward_cleared:"Ward cleared",kill:"Kill · outcome",death:"Death · outcome",assist:"Assist · outcome"}});
Object.assign(copy.fr,{sanitation_kicker:"CORPUS ASSAINI · MÊMES 46 PARTIES · 10 SECONDES",sanitation_title:"Plus de contexte, meilleure prédiction de Faker",sanitation_intro:"Un nouvel état causal ajoute l'or disponible, les CS, la santé et les changements depuis la frame précédente. Les 465 parties passent l'audit ; le graphique compare le modèle gelé et le challenger sur exactement les mêmes fenêtres de validation.",sanitation_new_ap:"Challenger · AP moyenne des quatre actes ↑",sanitation_old_ap:"Ancien modèle · mêmes actes ↑",sanitation_new_nll:"Challenger · perte log des actes ↓",sanitation_limit:"Validation historique déjà réutilisée : amélioration exploratoire, pas score prospectif ni preuve de vision réelle de la minimap. Les kills, morts et assists sont des issues séparées.",sanitation_doc:"Audit et protocole détaillés ↗"});
Object.assign(copy.en,{sanitation_kicker:"AUDITED CORPUS · SAME 46 GAMES · NEXT 10 SECONDS",sanitation_title:"More context, better Faker prediction",sanitation_intro:"A new causal state adds unspent gold, CS, health and changes since the previous frame. All 465 games pass the audit; this chart compares the frozen model and challenger on exactly the same validation windows.",sanitation_new_ap:"Challenger · mean AP for four acts ↑",sanitation_old_ap:"Previous model · same acts ↑",sanitation_new_nll:"Challenger · action log loss ↓",sanitation_limit:"Reused historical validation: exploratory improvement, not a prospective score or proof of Faker's actual minimap view. Kills, deaths and assists are separate outcomes.",sanitation_doc:"Audit and full protocol ↗"});

let language = "fr";
let summary = null;
let grid64 = null;
let atlas512 = null;
let atlasGrid = 64;
let grid512Score = null;
let events64 = null;
let challengeData = null;
let pressureData = null;
let spriteManifest = null;
let pressureRadius = 2500;
const iocFilters = {faker:true, allies:true, enemies:true, lanes:true, items:true, radius:true, role:"ALL"};
const lanePaths = {
  TOP:[[.06,.06],[.07,.90],[.10,.94],[.94,.94]],
  MID:[[.06,.06],[.94,.94]],
  BOT:[[.06,.06],[.90,.07],[.94,.10],[.94,.94]]
};
let predictabilityData = null;
let ninetyData = null;
let secondScaleData = null;
let fakerActionsData = null;
let sanitationData = null;
let eventAblation = null;
let challengeScenario = "five_faker";
let customAllocation = ["top","mid","jungle","bot","bot"];
let atlasValues = null;
let trace = null;
let surfaceMode = "actual";
let replayTimer = null;
let liveTimer = null;
let liveSeconds = 0;
let liveEvents = [];
let replayAudit = null;
let sharedMinute = 0;
let worldFinals = null;
let corpusData = null;
let iocLedger = null;
let eventValidation = null;
let memorySummary = null;
let memoryCases = [];
let memoryCaseIndex = 0;
let memoryChoice = null;
let memoryRevealed = false;
let teamData = null;
let teamProbe = null;
let teamYear = "2025";
let teamMode = "total";
let iocSummary = null;
let iocQuality = null;
let gameFacts = [];
let gameCardsShown = 12;
let selectedFinalYear = 2025;
const $ = (selector) => document.querySelector(selector);
const percent = (count, total) => (100 * count / total).toFixed(2);
const SVG_NS = "http://www.w3.org/2000/svg";
const phaseAt = (minute) => minute < 10 ? "early" : minute < 20 ? "middle" : "late";
const phaseLabel = (phase) => ({early:"0–10",middle:"10–20",late:"20+"})[phase];

function showSection() {
  const requested = decodeURIComponent(location.hash.slice(1));
  const ids = [...document.querySelectorAll("main > section[id]")].map(section => section.id);
  const active = ids.includes(requested) ? requested : "top";
  document.querySelector(".hero").hidden = active !== "top";
  document.querySelector(".stats").hidden = active !== "top";
  for (const section of document.querySelectorAll("main > section[id]")) section.hidden = section.id !== active;
  for (const link of document.querySelectorAll(".topbar nav a")) {
    const selected = link.getAttribute("href") === `#${active}`;
    link.classList.toggle("selected", selected);
    if (selected) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  positionActiveTab();
  requestAnimationFrame(() => window.scrollTo(0, 0));
}

function positionActiveTab() {
  const current = document.querySelector('.topbar nav a[aria-current="page"]');
  if (current) current.scrollIntoView({block: "nearest", inline: "center"});
}

function renderFinals() {
  if (!worldFinals) return;
  const fr = language === "fr";
  const tabs = $("#finals-tabs"); tabs.replaceChildren();
  for (const final of worldFinals.finals) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "final-year" + (final.year === selectedFinalYear ? " active" : "");
    button.textContent = `★ ${final.year}`;
    button.setAttribute("aria-pressed", String(final.year === selectedFinalYear));
    button.addEventListener("click", () => {selectedFinalYear = final.year; renderFinals();});
    tabs.append(button);
  }
  const final = worldFinals.finals.find(item => item.year === selectedFinalYear) || worldFinals.finals.at(-1);
  const detail = $("#finals-detail"); detail.replaceChildren();
  const heading = document.createElement("div"); heading.className = "final-heading";
  const title = document.createElement("div");
  const tag = document.createElement("span"); tag.className = "kicker"; tag.textContent = `${final.tournament.toUpperCase()} · ${final.date}`;
  const name = document.createElement("h3"); name.textContent = `${final.team}  ·  ${final.opponent}`;
  const note = document.createElement("p"); note.textContent = fr ? final.note_fr : final.note;
  title.append(tag, name, note);
  const score = document.createElement("strong"); score.className = "final-score"; score.textContent = final.score;
  heading.append(title, score); detail.append(heading);
  const games = document.createElement("div"); games.className = "final-games";
  for (const game of final.games) {
    const link = document.createElement("a");
    link.href = game.source; link.target = "_blank"; link.rel = "noopener noreferrer";
    link.className = `final-game ${game.result === "W" ? "win" : "loss"}`;
    const num = document.createElement("small"); num.textContent = `${fr ? "MANCHE" : "GAME"} ${game.number}`;
    const outcome = document.createElement("strong"); outcome.textContent = game.result === "W" ? (fr ? "VICTOIRE" : "WIN") : (fr ? "DÉFAITE" : "LOSS");
    const duration = document.createElement("span"); duration.textContent = `${game.duration} ↗`;
    link.append(num, outcome, duration); games.append(link);
  }
  detail.append(games);
  const source = document.createElement("a"); source.href = final.source; source.target = "_blank"; source.rel = "noopener noreferrer";
  source.className = "final-source"; source.textContent = fr ? "Statistiques de la série ↗" : "Series statistics ↗";
  detail.append(source);
  const extra = $("#finals-extra"); extra.replaceChildren();
  for (const game of worldFinals.extra_games) {
    const link = document.createElement("a"); link.href = game.source; link.target = "_blank"; link.rel = "noopener noreferrer";
    link.className = "extra-game";
    const year = document.createElement("strong"); year.textContent = `${game.year} · ${game.label}`;
    const focus = document.createElement("span"); focus.textContent = (fr ? game.focus_fr : game.focus) + " ↗";
    link.append(year, focus); extra.append(link);
  }
}

function renderCorpus() {
  if (!corpusData) return;
  const d = corpusData.domains, r = corpusData.raw_cache, w = corpusData.warehouse;
  const set = (id, value) => { $(id).textContent = Number(value).toLocaleString(language); };
  set("#corpus-cached", r.match_json); set("#corpus-timelines", r.timeline_json);
  set("#corpus-ranked", d.kr_ranked_usable); set("#corpus-facts", corpusData.postgame_facts);
  $("#corpus-kr").textContent = `${d.kr_ranked_usable.toLocaleString(language)} / ${d.kr_ranked_ids.toLocaleString(language)}`;
  set("#corpus-euw", d.euw_attributed_ranked); set("#corpus-other", d.kr_other_modes_cached);
  set("#corpus-pro", d.professional_mirror_summaries); set("#corpus-finals", d.curated_final_games);
  set("#corpus-states", w.frames); set("#corpus-actors", w.actor_rows);
  set("#corpus-transitions", w.transitions); set("#corpus-events", w.events);
  const rate = 100 * w.events_with_coordinates / w.events;
  $("#corpus-position-head").textContent = language === "fr" ?
    `${w.events_with_coordinates.toLocaleString(language)} événements localisés / ${w.events.toLocaleString(language)} indexés · ${rate.toFixed(1).replace('.',',')} %` :
    `${w.events_with_coordinates.toLocaleString(language)} of ${w.events.toLocaleString(language)} events have coordinates · ${rate.toFixed(1)}%`;
  $("#corpus-position-fill").style.width = `${rate}%`;
  const categories = $("#corpus-categories"); categories.replaceChildren();
  for (const [key, count] of Object.entries(w.event_categories).sort((a,b) => b[1]-a[1]).slice(0, 10)) {
    const label = key === "ITEM_PURCHASED" ? (language === "fr" ? "Achats" : "Purchases") :
      key === "SKILL_LEVEL_UP" ? (language === "fr" ? "Points de compétence" : "Skill points") :
      (copy[language].research_classes?.[key] || key.replaceAll("_", " "));
    const chip = document.createElement("span");
    const name = document.createTextNode(`${label} · `);
    const number = document.createElement("b"); number.textContent = count.toLocaleString(language);
    chip.append(name, number); categories.append(chip);
  }
  const accounts=$("#corpus-accounts");accounts.replaceChildren();
  for(const source of corpusData.source_accounts||[]){
    const card=document.createElement("article");card.className="corpus-account";
    const name=document.createElement("strong");name.textContent=source.riot_id;
    const badge=document.createElement("span");badge.textContent=source.region;
    const counts=document.createElement("p");counts.textContent=language==="fr"?
      `${source.ranked_ids} ID(s) ranked disponibles · ${source.usable_timelines??0} timeline(s) exploitables`:
      `${source.ranked_ids} available ranked ID(s) · ${source.usable_timelines??0} usable timeline(s)`;
    const claim=document.createElement("small");claim.textContent=source.region==="KR"?
      (language==="fr"?"Compte résolu par Riot ; identité de la personne non certifiée.":"Account resolved by Riot; human identity unverified."):
      (language==="fr"?`Attribution historique externe : ${source.claim}.`:`Outside historical attribution: ${source.claim}.`);
    card.append(name,badge,counts,claim);
    if(source.source_url){const link=document.createElement("a");link.href=source.source_url;link.target="_blank";
      link.rel="noopener noreferrer";link.textContent=language==="fr"?"Source de l'attribution ↗":"Attribution source ↗";card.append(link);}
    accounts.append(card);
  }
  const descriptions = language==="fr" ? {
    ITEM_PURCHASED:"Achat horodaté ; acteur parfois non attribué, lieu absent.",
    ITEM_SOLD:"Vente horodatée dans le JSON brut ; inventaire à t.",
    ITEM_DESTROYED:"Objet consommé ou transformé dans le JSON brut ; inventaire à t.",
    ITEM_UNDO:"Annulation d'achat dans le JSON brut ; avant/après item.",
    SKILL_LEVEL_UP:"Point de compétence ; pas une position.",
    ward_placed:"Ward posée ; aucune coordonnée dans cette cohorte.",ward_cleared:"Ward détruite ; aucune coordonnée dans cette cohorte.",
    faker_kill:"Kill attribué à Faker ; lieu de la victime éventuel.",
    faker_death:"Mort de Faker ; lieu de la victime éventuel.",
    ally_kill:"Kill allié ; lieu de la victime éventuel.",enemy_kill:"Kill adverse ; lieu de la victime éventuel.",
    dragon:"Dragon éliminé ; événement d'objectif.",baron:"Nashor éliminé ; événement d'objectif.",
    herald:"Herald éliminé ; événement d'objectif.",grubs:"Grubs éliminés ; événement d'objectif.",
    building:"Bâtiment détruit ; lieu du bâtiment éventuel."
  } : {
    ITEM_PURCHASED:"Timestamped purchase; actor sometimes unattributed, no location.",
    ITEM_SOLD:"Timestamped sale in raw JSON; updates inventory at t.",
    ITEM_DESTROYED:"Consumed or transformed item in raw JSON; updates inventory at t.",
    ITEM_UNDO:"Purchase undo in raw JSON; before/after item.",
    SKILL_LEVEL_UP:"Skill point; not a player position.",
    ward_placed:"Ward placed; no coordinates in this cohort.",ward_cleared:"Ward destroyed; no coordinates in this cohort.",
    faker_kill:"Kill credited to Faker; possible victim location.",
    faker_death:"Faker death; possible victim location.",
    ally_kill:"Ally kill; possible victim location.",enemy_kill:"Opponent kill; possible victim location.",
    dragon:"Dragon killed; objective event.",baron:"Baron killed; objective event.",
    herald:"Herald killed; objective event.",grubs:"Grubs killed; objective event.",
    building:"Building destroyed; possible building location."
  };
  const details=$("#corpus-event-detail");details.replaceChildren();
  for(const event of w.event_breakdown||[]){
    const row=document.createElement("article");row.className="corpus-event-row";
    const head=document.createElement("div");
    const label=document.createElement("strong");label.textContent=event.category.replaceAll("_"," ");
    const amount=document.createElement("b");amount.textContent=event.events.toLocaleString(language);
    head.append(label,amount);
    const note=document.createElement("p");note.textContent=descriptions[event.category]||event.category;
    const spatial=document.createElement("small");spatial.textContent=language==="fr"?
      `${event.positioned.toLocaleString(language)} lieux / ${event.events.toLocaleString(language)} événements${event.indexed?" indexés":" bruts · hors total indexé"}`:
      `${event.positioned.toLocaleString(language)} located / ${event.events.toLocaleString(language)} ${event.indexed?"indexed events":"raw events · outside indexed total"}`;
    const bar=document.createElement("span");bar.className="corpus-event-bar";
    const fill=document.createElement("i");fill.style.width=`${100*event.positioned/Math.max(1,event.events)}%`;
    const quality=eventValidation?.categories?.[event.category];
    const status=document.createElement("small");status.className="event-status";
    if(quality){
      const partial=quality.missing_required>0;status.classList.toggle("partial",partial);
      status.textContent=language==="fr"?
        `${quality.exact.toLocaleString(language)}/${quality.indexed.toLocaleString(language)} champs recopiés exactement${partial?` · ${quality.missing_required.toLocaleString(language)} acteur(s)/champ(s) non attribués`:""}`:
        `${quality.exact.toLocaleString(language)}/${quality.indexed.toLocaleString(language)} fields transcribed exactly${partial?` · ${quality.missing_required.toLocaleString(language)} unattributed actor(s)/field(s)`:""}`;
    }else{
      status.classList.add("partial");status.textContent=language==="fr"?"Hors ancien index ; compté dans le JSON brut":"Outside old index; counted in raw JSON";
    }
    bar.append(fill);row.append(head,note,spatial,status,bar);details.append(row);
  }
}

function renderEventValidation(){
  if(!eventValidation)return;
  const report=eventValidation, fr=language==="fr", fmt=n=>Number(n).toLocaleString(language);
  $("#event-validated").textContent=`${fmt(report.exact_index_rows)} / ${fmt(report.indexed_events)}`;
  const unattributed=(report.categories.ITEM_PURCHASED?.missing_required||0)+(report.categories.SKILL_LEVEL_UP?.missing_required||0);
  $("#event-unattributed").textContent=fmt(unattributed);
  $("#event-neutral").textContent=fmt(Object.values(report.neutral_champion_deaths).reduce((a,b)=>a+b,0));
  $("#event-plates").textContent=fmt(report.excluded_types.TURRET_PLATE_DESTROYED||0);
  $("#event-validation-note").textContent=fr?
    `${fmt(report.audited_matches)} parties contrôlées, ${fmt(report.failed_matches)} échec de lecture. Parmi les morts sans tueur, ${fmt(report.neutral_champion_deaths.faker_victim||0)} concernent Faker et restent des « morts de Faker ». Les ventes/destructions/annulations d'objets sont hors ancien index mais servent au proxy d'inventaire. Aucun événement exclu ne devient automatiquement une nouvelle cible du modèle.`:
    `${fmt(report.audited_matches)} games checked, ${fmt(report.failed_matches)} read failures. ${fmt(report.neutral_champion_deaths.faker_victim||0)} deaths without a player killer concern Faker and remain “Faker deaths”. Item sales/destruction/undo sit outside the old index but feed the inventory proxy. Excluded events do not automatically become new model targets.`;
}

function spriteIcon(kind, key, label) {
  const icon = document.createElement("span"); icon.className = `game-sprite ${kind}`;
  const spec = spriteManifest?.[kind]?.[String(key)];
  icon.setAttribute("role", "img"); icon.setAttribute("aria-label", label);
  if (spec) icon.style.backgroundPosition = `-${spec.x * 48}px -${spec.y * 48}px`;
  else { icon.classList.add("missing"); icon.textContent = "?"; }
  return icon;
}

function gameFactCard(game, interactive = false) {
  const t = copy[language];
  const card = document.createElement(interactive ? "button" : "article");
  if (interactive) card.type = "button";
  card.className = `game-fact ${game.won === 1 ? "win" : "loss"}`;
  const date = game.started_utc ? game.started_utc.slice(0,16).replace("T", " ") + " UTC" : "UTC ?";
  const duration = game.duration_seconds == null ? "—" : `${Math.floor(game.duration_seconds/60)}:${String(game.duration_seconds%60).padStart(2,"0")}`;
  const head = document.createElement("div"); head.className = "game-fact-head";
  const title = document.createElement("div"); title.className = "game-fact-title";
  title.append(spriteIcon("champions",game.champion,game.champion));
  const titleText = document.createElement("div");
  const champion = document.createElement("strong"); champion.textContent = game.champion;
  const side = game.side === "BLUE" ? t.catalog_side_blue : game.side === "RED" ? t.catalog_side_red : game.side;
  const meta = document.createElement("small"); meta.textContent = `${date} · ${side} · ${game.patch} · ${game.match_id}`;
  titleText.append(champion, meta); title.append(titleText);
  const outcome = document.createElement("span"); outcome.className = "game-fact-outcome";
  outcome.textContent = game.won === 1 ? t.catalog_win : game.won === 0 ? t.catalog_loss : t.catalog_unknown;
  head.append(title, outcome); card.append(head);
  const score = document.createElement("div"); score.className = "game-fact-score";
  for (const [label, value] of [["K / D / A",`${game.kills ?? "—"} / ${game.deaths ?? "—"} / ${game.assists ?? "—"}`],
    [t.catalog_damage,game.damage_champions?.toLocaleString(language) ?? "—"],
    [t.catalog_vision,game.vision_score ?? "—"],[t.catalog_cs,game.cs ?? "—"],[t.catalog_duration,duration]]) {
    const item = document.createElement("span");
    const valueNode = document.createElement("b"); valueNode.textContent = value;
    item.append(valueNode, document.createTextNode(label)); score.append(item);
  }
  card.append(score);
  const teams = document.createElement("div"); teams.className = "game-fact-teams";
  for (const [name, actors] of [[t.catalog_allies,game.allies],[t.catalog_enemies,game.enemies]]) {
    const item = document.createElement("div");
    const label = document.createElement("small"); label.textContent = name;
    const champions = document.createElement("span"); champions.className = "game-champion-row";
    for (const actor of actors) {
      const chip = document.createElement("span"); chip.className = `game-champion-chip ${name===t.catalog_allies && actor===game.champion ? "faker" : ""}`;
      chip.append(spriteIcon("champions",actor,actor),document.createTextNode(actor));
      champions.append(chip);
    }
    item.append(label,champions); teams.append(item);
  }
  card.append(teams);
  const items = document.createElement("div"); items.className = "game-fact-items";
  const itemLabel = document.createElement("b"); itemLabel.textContent = `${t.catalog_items} · `;
  items.append(itemLabel);
  const itemRow = document.createElement("span"); itemRow.className = "game-item-row";
  for (const id of game.items) {
    const spec = spriteManifest?.items?.[String(id)];
    const name = spec?.[language] || `#${id}`;
    const chip = document.createElement("span"); chip.className = "game-item-chip"; chip.title = `${name} · #${id}`;
    chip.append(spriteIcon("items",id,name),document.createTextNode(name));
    itemRow.append(chip);
  }
  if (!game.items.length) itemRow.textContent = "—";
  items.append(itemRow); card.append(items);
  return card;
}

function renderGamePreview(mid = $("#game-picker").value.trim()) {
  const preview = $("#game-fact-preview"); preview.replaceChildren();
  const game = gameFacts.find(item => item.match_id === mid);
  if (game) preview.append(gameFactCard(game));
}

function renderGameCards() {
  $("#game-filter").placeholder=copy[language].catalog_filter_placeholder;
  $("#game-filter").setAttribute("aria-label",copy[language].catalog_filter_label);
  const query = $("#game-filter").value.trim().toLocaleLowerCase();
  const matches = gameFacts.filter(game => [game.match_id,game.started_utc,game.patch,game.champion,
    ...game.allies,...game.enemies,...game.items.map(id => `${id} ${spriteManifest?.items?.[String(id)]?.[language] || ""}`)].join(" ").toLocaleLowerCase().includes(query));
  $("#game-filter-count").textContent = copy[language].catalog_found(matches.length);
  const list = $("#game-card-list"); list.replaceChildren();
  for (const game of matches.slice(0, gameCardsShown)) {
    const card = gameFactCard(game,true);
    card.addEventListener("click", () => { location.hash = "replay"; openGame(game.match_id); });
    list.append(card);
  }
  $("#game-more").hidden = matches.length <= gameCardsShown;
}

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

function setSharedMinute(minute, {preserveLive=false}={}) {
  sharedMinute = Math.max(0, Math.min(39, Math.round(Number(minute) || 0)));
  $("#faker-actions-phase-select").value = phaseAt(sharedMinute);
  $("#atlas-phase").value = phaseAt(sharedMinute);
  $("#minute-slider").value = Math.min(7, Math.floor(sharedMinute / 5));
  if (trace?.rows?.length) {
    const closest = trace.rows.reduce((best,row,index) =>
      Math.abs(row.minute - sharedMinute) < Math.abs(trace.rows[best].minute - sharedMinute) ? index : best, 0);
    $("#replay-slider").value = closest;
    updateReplay();
    if (!preserveLive && trace.schema_version >= 6) {
      stopLive();
      liveSeconds = trace.rows[closest].frame_seconds;
      renderLive();
    }
  }
  showSharedMinute();
  if (summary) updateTempo();
  if (atlas512 || events64) renderAtlas();
  if (atlas512 || grid64 || summary) renderSurface();
  if (pressureData) renderPressure();
  if (challengeData) renderChallenge();
  if (predictabilityData) renderPredictability();
  if (ninetyData) renderNinety();
  if (secondScaleData) renderSecondScale();
  if (fakerActionsData) renderFakerActions();
  if (sanitationData) renderSanitation();
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
  $("#second-horizon").setAttribute("aria-label",language === "fr" ?
    "Horizon en secondes : 1, 5, 10 ou 30" : "Horizon in seconds: 1, 5, 10 or 30");
  renderIocResult();
  renderIocLedger();
  renderIocControls();
  if (summary) {
    updateTempo();
    updateReadout(7, 7);
    renderSurface();
  }
  if (atlas512 || events64) renderAtlas();
  if (challengeData) renderChallenge();
  if (pressureData) renderPressure();
  if (predictabilityData) renderPredictability();
  if (ninetyData) renderNinety();
  if (secondScaleData) renderSecondScale();
  if (fakerActionsData) renderFakerActions();
  if (sanitationData) renderSanitation();
  if (grid512Score) renderGrid512Score();
  if (eventAblation) renderResearchEvents();
  if (worldFinals) renderFinals();
  if (corpusData) renderCorpus();
  if (eventValidation) renderEventValidation();
  if (teamData) renderTeam();
  if (teamProbe) renderTeamProbe();
  if (memorySummary) renderMemory();
  if (gameFacts.length) { renderGameCards(); renderGamePreview(); }
  if (trace) { updateReplay(); renderLive(); renderMoments(); }
  renderReplayAudit();
  showSharedMinute();
}

function renderReplayAudit() {
  const root=$("#replay-audit");root.replaceChildren();
  if(!replayAudit?.counts)return;
  const counts=replayAudit.counts;
  const metrics=[counts.games,counts.frames,counts.events,counts.events_exactly_on_previous_boundary];
  metrics.forEach((value,index)=>{
    const card=document.createElement("div");card.className="replay-audit-stat";
    const strong=document.createElement("strong");strong.textContent=value.toLocaleString(language);
    const label=document.createElement("span");label.textContent=copy[language].replay_audit_labels[index];
    card.append(strong,label);root.append(card);
  });
  const note=document.createElement("p");note.textContent=copy[language].replay_audit_note;root.append(note);
}

function renderIocLedger() {
  const root = $("#ioc-ledger");
  if (!root) return;
  const fr = language === "fr";
  root.querySelector(".ioc-ledger-heading h3").textContent = fr ?
    "Où est la base qui relie le jeu autour de Faker ?" : "Where is the database of Faker's game context?";
  root.querySelector(".ioc-ledger-heading p").textContent = fr ?
    "L'or n'est qu'une colonne. Le registre relie le dernier état connu des dix joueurs, les événements passés et la prochaine action observée de Faker. Chaque preuve garde son horloge et sa source." :
    "Gold is one column. The ledger joins the last observed state of all ten players, past events and Faker's next observed action. Every piece of evidence keeps its time and source.";
  const labels = fr ? ["parties", "états de joueurs", "événements horodatés", "fenêtres train · 10 s"] :
    ["games", "player states", "timestamped events", "train windows · 10 s"];
  root.querySelectorAll(".ioc-ledger-stats span").forEach((span, i) => { span.textContent = labels[i]; });
  const flow = fr ? [
    "Jungle · bot · support · ennemis<br><small>positions, vie, XP, CS, niveaux, objets</small>",
    "Wards · combats · objectifs<br><small>événements passés ≤ t</small>",
    "Faker à t<br><small>38 champs export · 48 archivés</small>",
    "Action à t+10 s<br><small>7 labels séparés</small>"] : [
    "Jungle · bot · support · enemies<br><small>positions, health, XP, CS, levels, items</small>",
    "Wards · fights · objectives<br><small>past events ≤ t</small>",
    "Faker at t<br><small>38 export fields · 48 archived</small>",
    "Action at t+10 s<br><small>7 separate labels</small>"];
  root.querySelectorAll(".ioc-ledger-flow span").forEach((span, i) => { span.innerHTML = flow[i]; });
  root.querySelector(".ioc-ledger-foot").textContent = fr ?
    "Positions ≈ 60 s ; événements horodatés. La timeline voit toute la carte. Le JSONL d'entraînement est privé et limité aux parties train ; aucun LLM n'est encore entraîné sur cette base." :
    "Positions ≈ 60 s; events have timestamps. The timeline sees the whole map. Training JSONL stays private and train-only; no LLM has been trained on this database.";
  root.querySelector(".text-link").textContent = fr ? "Schéma, export et limites ↗" : "Schema, export and limits ↗";
  if (iocLedger) {
    const fmt = n => Number(n).toLocaleString(fr ? "fr-FR" : "en-US");
    $("#ioc-ledger-games").textContent = fmt(iocLedger.tables.games);
    $("#ioc-ledger-actors").textContent = fmt(iocLedger.tables.actors);
    $("#ioc-ledger-events").textContent = fmt(iocLedger.tables.events);
    $("#ioc-ledger-train").textContent = fmt(iocLedger.windows_by_split.train);
  }
}

function renderIocResult() {
  if (!iocSummary || !iocQuality) return;
  const score = 100 * iocSummary.variants.full.top1_8;
  const inventory = 100 * iocQuality.exact_final_id_set_fraction;
  const coverage = Object.entries(iocSummary.variants.full.topk8)
    .map(([k, value]) => [Number(k), value]).sort((a, b) => a[0] - b[0])
    .find(([, value]) => value >= .9)?.[0];
  const locale = language === "fr" ? "fr-FR" : "en-US";
  const fmt = (number, digits) => number.toLocaleString(locale, {minimumFractionDigits: digits, maximumFractionDigits: digits});
  $("#ioc-vision-result").textContent = language === "fr"
    ? `Validation réutilisée : ${fmt(score, 2)} % en 8×8 ; gain d'ablation incertain. L'inventaire par événements n'est exact que pour ${fmt(inventory, 1)} % des sets d'objets finaux. Couvrir 90 % des destinations requiert ${coverage}/64 cases.`
    : `Reused validation: ${fmt(score, 2)}% at 8×8; uncertain ablation lift. The event inventory matches only ${fmt(inventory, 1)}% of final item sets exactly. Covering 90% of destinations needs ${coverage}/64 cells.`;
}

function updateReadout(col, row) {
  const density = summary.test_map_density;
  const index = row * 16 + col;
  $("#map-readout").textContent = copy[language].map_cell(
    col, row, percent(density.actual[index], density.samples),
    percent(density.predicted[index], density.samples)
  );
}

function renderNinety() {
  if (!ninetyData) return;
  const percentage = value => `${(100 * value).toLocaleString(language === "fr" ? "fr-FR" : "en-US",{minimumFractionDigits:2,maximumFractionDigits:2})} %`;
  $("#ninety-all").textContent = percentage(ninetyData.all_transitions_accuracy);
  $("#ninety-top").textContent = percentage(ninetyData.accuracy_at_fixed_served_coverage[0].exact_accuracy);
  $("#ninety-lockbox").textContent = `${ninetyData.prospective.new_games_scored} / ${ninetyData.prospective.required_new_games}`;
}

function renderSecondScale() {
  if (!secondScaleData) return;
  const horizons = [1, 5, 10, 30];
  const seconds = horizons[Number($("#second-horizon").value)];
  const row = secondScaleData.horizons_seconds[String(seconds)];
  const locale = language === "fr" ? "fr-FR" : "en-US";
  const percentage = n => `${(100 * n / row.windows).toLocaleString(locale,{maximumFractionDigits:1})} %`;
  $("#second-horizon-value").textContent = `${seconds} s`;
  for (const [key,value] of [["windows",row.windows],["events",row.with_event],["faker",row.with_faker_involvement],["position",row.with_new_faker_position]]) {
    $("#second-"+key).textContent = value.toLocaleString(locale);
  }
  for (const [key,value] of [["event",row.with_event],["faker",row.with_faker_involvement],["position",row.with_new_faker_position]]) {
    $("#second-"+key+"-pct").textContent = percentage(value);
    $("#second-"+key+"-fill").style.width = `${100 * value / row.windows}%`;
  }
}

function renderFakerActions() {
  if (!fakerActionsData) return;
  const phase = $("#faker-actions-phase-select").value;
  const scores = phase === "all" ? fakerActionsData.scores : fakerActionsData.by_phase[phase];
  if (!scores) return;
  const locale = language === "fr" ? "fr-FR" : "en-US";
  const number = x => Number(x).toLocaleString(locale,{minimumFractionDigits:3,maximumFractionDigits:3});
  const percent = x => Number(100*x).toLocaleString(locale,{minimumFractionDigits:1,maximumFractionDigits:1}) + " %";
  $("#faker-actions-nll").textContent = number(scores.model.nll);
  $("#faker-actions-baseline").textContent = number(scores.phase_train_frequency.nll);
  $("#faker-actions-ap").textContent = percent(scores.model.macro_average_precision);
  const positives = Object.values(scores.model.per_class).reduce((sum,row) => sum + row.positives,0);
  $("#faker-actions-empty").textContent = percent(1 - positives / (scores.model.windows * 7));
  const rows = Object.entries(scores.model.per_class).map(([key,row]) => {
    const base = scores.phase_train_frequency.per_class[key];
    const modelAP = row.average_precision || 0;
    const baseAP = base.average_precision || 0;
    return `<div class="faker-actions-row"><span class="label">${copy[language].faker_actions_labels[key]}<small>${row.positives.toLocaleString(locale)} ${copy[language].faker_actions_positive}</small></span><span class="tracks"><span class="track"><i style="width:${Math.min(100,modelAP*250)}%"></i></span><span class="track"><i style="width:${Math.min(100,baseAP*250)}%"></i></span></span><strong>${percent(modelAP)}<small>${percent(baseAP)}</small></strong></div>`;
  });
  $("#faker-actions-rows").innerHTML = rows.join("");
}

function renderSanitation() {
  if (!sanitationData) return;
  const locale = language === "fr" ? "fr-FR" : "en-US";
  const percent = value => (100 * value).toLocaleString(locale,{minimumFractionDigits:1,maximumFractionDigits:1}) + " %";
  $("#sanitation-new-ap").textContent = percent(sanitationData.action_summary.candidate.macro_ap);
  $("#sanitation-old-ap").textContent = percent(sanitationData.action_summary.incumbent.macro_ap);
  $("#sanitation-new-nll").textContent = sanitationData.action_summary.candidate.nll.toLocaleString(locale,{minimumFractionDigits:3,maximumFractionDigits:3});
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
  const cohort = modelPositions ? (local ? (language === "fr" ? "46 parties de validation" : "46 validation games") : (language === "fr" ? "test historique" : "historical test")) :
    (language === "fr" ? "465 ranked KR" : "465 KR ranked games");
  $("#atlas-canvas").dataset.cohort = cohort;
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
  drawCanvasIoc(ctx);
  renderIocReadout("#atlas-ioc-readout");
  $("#atlas-total").previousElementSibling.textContent = modelPositions ?
    (local ? (language === "fr" ? "Destinations de validation" : "Validation destinations") :
             (language === "fr" ? "Destinations du test historique" : "Historical test destinations")) :
    teamPositions ? (language === "fr" ? "Positions des 465 parties" : "Positions across 465 games") : copy[language].atlas_total;
  const oldRecord = events64?.phases?.[phase]?.[layer];
  const total = local ? local.total : modelPositions ? modelPhase.samples : teamPositions ? entries.reduce((n, row) => n + row[1], 0) : oldRecord.total;
  $("#atlas-total").textContent = total.toLocaleString(language);
  $("#atlas-unplaced").textContent = positions ? "—" : (local?.without_position ?? oldRecord?.without_position ?? 0).toLocaleString(language);
  $("#atlas-readout").textContent = copy[language].atlas_empty($("#atlas-layer").selectedOptions[0].textContent,phaseLabel(phase),cohort);
}

function renderTeam() {
  if (!teamData) return;
  if (teamYear !== "all" && !teamData.by_year[teamYear]) teamYear = teamData.years.at(-1);
  const t = copy[language];
  const locale = language === "fr" ? "fr-FR" : "en-US";
  const yearSelect = $("#team-year");
  yearSelect.replaceChildren();
  for (const year of ["all", ...teamData.years]) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year === "all" ? t.team_all : year;
    yearSelect.append(option);
  }
  yearSelect.value = teamYear;
  $("#team-mode-total").classList.toggle("active", teamMode === "total");
  $("#team-mode-recent").classList.toggle("active", teamMode === "recent");
  const data = teamYear === "all" ? teamData.all : teamData.by_year[teamYear];
  $("#team-games").textContent = data.games.toLocaleString(locale);
  $("#team-complete").textContent = data.complete_10_15.toLocaleString(locale);
  $("#team-last").textContent = teamData.last_date;
  const names = teamData.focus;
  const matrix = $("#team-pair-matrix");
  matrix.replaceChildren();
  const empty = document.createElement("span"); empty.className = "team-matrix-corner"; matrix.append(empty);
  for (const name of names) {
    const header = document.createElement("strong"); header.textContent = name; matrix.append(header);
  }
  const high = Math.max(1, data.games);
  data.pair_matrix.forEach((row, i) => {
    const label = document.createElement("strong"); label.textContent = names[i]; matrix.append(label);
    row.forEach((value, j) => {
      const cell = document.createElement("div");
      cell.className = "team-matrix-cell";
      cell.style.backgroundColor = value ? `rgba(255,85,119,${(.13 + .67 * value / high).toFixed(3)})` : "#18202b";
      cell.textContent = value.toLocaleString(locale);
      cell.title = `${names[i]} × ${names[j]} · ${value} ${language === "fr" ? "manches communes" : "shared games"}`;
      matrix.append(cell);
    });
  });
  const curve = $("#team-curve"); curve.replaceChildren();
  const monthly = teamData.monthly_prior.filter(row => teamYear === "all" || row.month.startsWith(teamYear));
  const roster = [{name:"Doran",color:"#ffd188"},{name:"Oner",color:"#76dce5"},{name:"Keria",color:"#ff79a3"}];
  const field = teamMode === "total" ? "prior_games" : "effective90";
  const values = roster.flatMap(person => monthly.map(row => row[person.name]?.[field] || 0));
  const ceiling = Math.max(1, ...values);
  const xAt = index => 55 + index / Math.max(1, monthly.length - 1) * 490;
  const yAt = value => 274 - value / ceiling * 224;
  for (let i = 0; i <= 4; i++) {
    const yy = 274 - i * 56;
    curve.append(svgNode("line", {x1:55,x2:545,y1:yy,y2:yy,stroke:"#694b59","stroke-width":1}));
    const label = svgNode("text", {x:5,y:yy+4,fill:"#d5b8c2","font-size":12});
    label.textContent = Math.round(ceiling * i / 4).toLocaleString(locale); curve.append(label);
  }
  for (const person of roster) {
    const points = monthly.map((row,i)=>`${xAt(i)},${yAt(row[person.name]?.[field] || 0)}`).join(" ");
    if (points) curve.append(svgNode("polyline",{points,fill:"none",stroke:person.color,"stroke-width":4,"stroke-linecap":"round","stroke-linejoin":"round"}));
    const last = monthly.at(-1);
    if (last) curve.append(svgNode("circle",{cx:xAt(monthly.length-1),cy:yAt(last[person.name]?.[field] || 0),r:6,fill:person.color,stroke:"#fff","stroke-width":2}));
  }
  for (const index of [...new Set([0,Math.floor((monthly.length-1)/2),monthly.length-1])]) {
    if (monthly[index]) {
      const label = svgNode("text",{x:xAt(index),y:305,fill:"#d5b8c2","font-size":11,"text-anchor":index===0?"start":index===monthly.length-1?"end":"middle"});
      label.textContent = monthly[index].month; curve.append(label);
    }
  }
  const legend = $("#team-curve-legend"); legend.replaceChildren();
  for (const person of roster) {
    const item = document.createElement("span"); item.style.color = person.color;
    const last = monthly.at(-1)?.[person.name]?.[field] || 0;
    item.textContent = `${person.name} · ${teamMode === "recent" ? last.toFixed(1) : last.toLocaleString(locale)}`;
    legend.append(item);
  }
  const grid = $("#team-resource-grid"); grid.replaceChildren();
  for (const label of ["",t.team_gold10,t.team_gold15,t.team_swing,t.team_xp_swing]) {
    const head = document.createElement("strong"); head.className = "team-resource-head"; head.textContent = label; grid.append(head);
  }
  for (const role of teamData.roles) {
    const head = document.createElement("strong"); head.className = role === "mid" ? "team-role faker" : "team-role"; head.textContent = t.team_roles[role]; grid.append(head);
    for (const field of ["gold_diff10","gold_diff15","gold_swing10_15","xp_swing10_15"]) {
      const value = data.roles[role][field];
      const cell = document.createElement("span"); cell.className = "team-resource-value";
      cell.textContent = value == null ? "—" : `${value > 0 ? "+" : ""}${Math.round(value).toLocaleString(locale)}`;
      const alpha = value == null ? 0 : Math.min(.7, .12 + Math.abs(value) / 450);
      cell.style.backgroundColor = value == null ? "#25212b" : value >= 0 ? `rgba(99,223,211,${alpha})` : `rgba(255,91,127,${alpha})`;
      cell.title = `${t.team_roles[role]} · ${Math.round(value || 0)} · n=${data.roles[role].n}`;
      grid.append(cell);
    }
  }
  $("#team-resource-count").textContent = t.team_count(data.complete_10_15);
  const corrGrid = $("#team-correlation-grid"); corrGrid.replaceChildren();
  const corrNames = teamData.roles.map(role => t.team_corr_roles[role]);
  const blank = document.createElement("span"); corrGrid.append(blank);
  for (const name of corrNames) { const head = document.createElement("strong"); head.textContent = name; corrGrid.append(head); }
  data.gold_swing_correlations.forEach((row, i) => {
    const head = document.createElement("strong"); head.textContent = corrNames[i]; corrGrid.append(head);
    row.forEach((value, j) => {
      const cell = document.createElement("span"); cell.className = "team-matrix-cell";
      cell.textContent = value == null ? "—" : `${value > 0 ? "+" : ""}${value.toFixed(2)}`;
      const alpha = value == null ? 0 : .10 + Math.abs(value) * .67;
      cell.style.backgroundColor = value == null ? "#25212b" : value >= 0 ? `rgba(93,220,212,${alpha.toFixed(3)})` : `rgba(255,91,127,${alpha.toFixed(3)})`;
      cell.title = `${corrNames[i]} × ${corrNames[j]} · r=${value == null ? "—" : value.toFixed(3)} · n=${data.complete_10_15}`;
      corrGrid.append(cell);
    });
  });
}

function renderTeamProbe() {
  if (!teamProbe) return;
  const t = copy[language];
  const endpoint = teamProbe.endpoints.faker_mid;
  const items = ["persistence", "ten_minute_context", "context_plus_history"];
  const colors = ["#8f92a5", "#71dae2", "#ff789d"];
  const scores = items.map(key => endpoint.test[key].mae_gold);
  const max = Math.max(...scores) * 1.06;
  const bars = $("#team-probe-bars"); bars.replaceChildren();
  items.forEach((key, index) => {
    const row = document.createElement("div"); row.className = "team-probe-row";
    const label = document.createElement("span"); label.textContent = t.probe_methods[index];
    const track = document.createElement("div"); track.className = "team-probe-track";
    const fill = document.createElement("i"); fill.style.width = `${100 * scores[index] / max}%`; fill.style.background = colors[index]; track.append(fill);
    const value = document.createElement("strong"); value.textContent = `${scores[index].toLocaleString(language === "fr" ? "fr-FR" : "en-US",{minimumFractionDigits:2})} g`;
    row.append(label, track, value); bars.append(row);
  });
  $("#team-probe-result").textContent = t.probe_verdict;
  const [low, high] = endpoint.paired_test_delta_ci95_day_bootstrap_gold;
  $("#team-probe-detail").textContent = t.probe_detail(endpoint.paired_test_delta_history_minus_context_mae_gold, low, high, teamProbe.split.games.test);
}

function renderMemory() {
  if (!memorySummary) return;
  const percent = value => `${(100 * value).toFixed(2).replace(".", language === "fr" ? "," : ".")} %`;
  $("#memory-retrieval").textContent = percent(memorySummary.validation_top1_8);
  $("#memory-baseline").textContent = percent(memorySummary.validation_baselines.role_phase_prior);
  $("#memory-shadow").textContent = iocSummary?.variants?.full?.top1_8 == null ? "—" : percent(iocSummary.variants.full.top1_8);
  const grid = $("#memory-grid");
  grid.replaceChildren();
  if (!memoryCases.length) {
    $("#memory-case-title").textContent = language === "fr" ? "Cas locaux indisponibles" : "Local cases unavailable";
    return;
  }
  const row = memoryCases[memoryCaseIndex];
  $("#memory-case-index").textContent = `${String(memoryCaseIndex + 1).padStart(2, "0")} / ${memoryCases.length}`;
  $("#memory-case-title").textContent = copy[language].memory_case(memoryCaseIndex + 1, memoryCases.length, row);
  for (let y = 7; y >= 0; y--) for (let x = 0; x < 8; x++) {
    const cell = y * 8 + x;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "memory-cell";
    button.setAttribute("role", "gridcell");
    button.setAttribute("aria-label", `${language === "fr" ? "Case" : "Cell"} ${x + 1}, ${y + 1}`);
    if (memoryChoice === cell) button.classList.add("choice");
    if (memoryRevealed && row.predicted_cell8 === cell) button.classList.add("model");
    if (memoryRevealed && row.observed_cell8 === cell) button.classList.add("actual");
    button.addEventListener("click", () => { if (!memoryRevealed) { memoryChoice = cell; renderMemory(); } });
    grid.append(button);
  }
  $("#memory-feedback").textContent = memoryRevealed
    ? copy[language].memory_feedback(memoryChoice, row.predicted_cell8, row.observed_cell8)
    : memoryChoice === null ? "" : `${language === "fr" ? "Votre choix" : "Your choice"} : ${memoryChoice}`;
}

function renderChallenge() {
  const tabs = $("#challenge-scenarios"); tabs.replaceChildren();
  for (const key of [...Object.keys(challengeData.scenarios),"custom"]) {
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
  const compose=$("#challenge-compose");compose.hidden=challengeScenario!=="custom";
  const players=$("#challenge-players");players.replaceChildren();
  if(challengeScenario==="custom")customAllocation.forEach((zone,index)=>{
    const label=document.createElement("label"),select=document.createElement("select");
    label.append(document.createTextNode(`${language==="fr"?"Joueur":"Player"} ${index+1}`));
    for(const key of ["top","mid","jungle","bot"]){
      const option=document.createElement("option");option.value=key;option.textContent=key.toUpperCase();select.append(option);
    }
    select.value=zone;select.addEventListener("change",()=>{customAllocation[index]=select.value;renderChallenge();});
    label.append(select);players.append(label);
  });
  const customRows=()=>Array.from({length:8},(_,tick)=>{
    const ours=Object.fromEntries(["top","mid","jungle","bot"].map(zone=>[zone,customAllocation.filter(value=>value===zone).length]));
    const enemy={top:1,mid:1,jungle:1,bot:2};
    const focus=Object.keys(ours).reduce((a,b)=>ours[b]>ours[a]?b:a,"top");
    if(tick>=delay){const donor=focus==="bot"?"top":"bot";enemy[donor]--;enemy[focus]++;}
    const resource=Object.values(ours).reduce((sum,n)=>sum+(n?Math.min(1,n)+Number(sharing)*Math.max(0,Math.min(n-1,1)):0),0)/5;
    const coverage=Object.values(ours).filter(n=>n>0).length/4;
    const local=Math.max(0,ours[focus]-enemy[focus])/5;
    return {minute:tick*5,allocation:ours,opponent_allocation:enemy,resource_access:resource,
      map_coverage:coverage,local_pressure:local};
  });
  const rows=challengeScenario==="custom"?customRows():challengeData.scenarios[challengeScenario][String(delay)][sharing];
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
  const lanes=$("#challenge-lanes");lanes.replaceChildren();
  for(const zone of ["top","mid","jungle","bot"]){
    const row=document.createElement("div");row.className="challenge-lane";
    const name=document.createElement("strong");name.textContent=zone.toUpperCase();
    const team=document.createElement("span");team.className="team";team.style.width=`${selected.allocation[zone]*10}%`;
    const opponent=document.createElement("span");opponent.className="opponent";opponent.style.width=`${selected.opponent_allocation[zone]*10}%`;
    const counts=document.createElement("small");counts.textContent=`${selected.allocation[zone]} : ${selected.opponent_allocation[zone]}`;
    row.append(name,team,opponent,counts);lanes.append(row);
  }
}

function renderIocControls() {
  const labels = language === "fr" ?
    {faker:"Faker",allies:"Alliés",enemies:"Adversaires",lanes:"Couloirs",items:"Objets",radius:"Zone",role:"Rôle"} :
    {faker:"Faker",allies:"Allies",enemies:"Opponents",lanes:"Lanes",items:"Items",radius:"Radius",role:"Role"};
  for (const container of document.querySelectorAll(".ioc-controls")) {
    container.replaceChildren();
    for (const key of ["faker","allies","enemies","lanes","items","radius"]) {
      const label=document.createElement("label"),input=document.createElement("input");
      input.type="checkbox";input.checked=iocFilters[key];input.dataset.iocFilter=key;
      label.append(input,document.createTextNode(labels[key]));container.append(label);
      input.addEventListener("change",()=>{
        iocFilters[key]=input.checked;renderIocControls();refreshIocViews();
      });
    }
    const roleLabel=document.createElement("label"),select=document.createElement("select");
    roleLabel.append(document.createTextNode(`${labels.role} `));
    const names=language==="fr"?{ALL:"Tous",TOP:"Top",JUNGLE:"Jungle",MIDDLE:"Mid",BOTTOM:"Bot",UTILITY:"Support"}:
      {ALL:"All",TOP:"Top",JUNGLE:"Jungle",MIDDLE:"Mid",BOTTOM:"Bot",UTILITY:"Support"};
    for(const [value,name] of Object.entries(names)){
      const option=document.createElement("option");option.value=value;option.textContent=name;select.append(option);
    }
    select.value=iocFilters.role;select.dataset.iocRole="1";
    select.addEventListener("change",()=>{iocFilters.role=select.value;renderIocControls();refreshIocViews();});
    roleLabel.append(select);container.append(roleLabel);
  }
}

function refreshIocViews() {
  if(atlas512||events64)renderAtlas();
  if(summary)renderSurface();
  if(pressureData)renderPressure();
}

function showIocActor(actor) {
  if(actor.side==="faker")return iocFilters.faker;
  return iocFilters[actor.side==="ally"?"allies":"enemies"] &&
    (iocFilters.role==="ALL" || actor.role===iocFilters.role);
}

function currentIocRow() {return trace?.rows?.[Number($("#replay-slider").value)];}

function renderIocReadout(selector) {
  const row=currentIocRow();
  const own=row?.actors_t?.find(a=>a.side==="faker");
  if(!own){$(selector).textContent=language==="fr"?"Superpose une partie observée en la chargeant dans Pression ou Évolution.":
    "Overlay an observed game by loading it in Pressure or Evolution.";return;}
  const actors=row.actors_t.filter(a=>a.xy&&showIocActor(a));
  const itemText=iocFilters.items ? (language==="fr"?`${own.items?.length||0} objets de Faker suivis à t`:
    `${own.items?.length||0} Faker items tracked at t`) : "";
  const ended=sharedMinute>row.minute+.5 ? (language==="fr"?" · dernière frame disponible":" · last available frame"):"";
  $(selector).textContent=language==="fr"?
    `Surimpression : ${row.minute.toFixed(0)} min d'une partie${ended} · ${actors.length} positions affichées${itemText?` · ${itemText}`:""}. Le fond agrège plusieurs parties ; les points décrivent cette partie seulement.`:
    `Overlay: ${row.minute.toFixed(0)} min of one game${ended} · ${actors.length} positions shown${itemText?` · ${itemText}`:""}. The background aggregates many games; the points describe this one game.`;
}

function drawCanvasIoc(ctx) {
  const row=currentIocRow();
  if(!row)return;
  const project=xy=>[xy[0]*512,(1-xy[1])*512];
  if(iocFilters.lanes){
    ctx.save();ctx.lineWidth=2;ctx.setLineDash([8,7]);ctx.strokeStyle="rgba(255,220,165,.72)";
    for(const path of Object.values(lanePaths)){
      ctx.beginPath();path.forEach((xy,i)=>{const p=project(xy);i?ctx.lineTo(...p):ctx.moveTo(...p);});ctx.stroke();
    }
    ctx.restore();
  }
  const own=row.actors_t.find(a=>a.side==="faker");
  if(iocFilters.radius&&own?.xy){
    const [x,y]=project(own.xy);ctx.save();ctx.beginPath();ctx.arc(x,y,pressureRadius/15000*512,0,Math.PI*2);
    ctx.fillStyle="rgba(255,83,107,.11)";ctx.strokeStyle="#ffd895";ctx.lineWidth=2;ctx.fill();ctx.stroke();ctx.restore();
  }
  for(const actor of row.actors_t.filter(a=>a.xy&&showIocActor(a))){
    const [x,y]=project(actor.xy),color=actor.side==="faker"?"#ffd895":actor.side==="ally"?"#70a8ff":"#ff637d";
    ctx.beginPath();ctx.arc(x,y,actor.side==="faker"?8:6,0,Math.PI*2);
    ctx.fillStyle=color;ctx.fill();ctx.strokeStyle="#fff";ctx.lineWidth=1.7;ctx.stroke();
    if(iocFilters.items&&actor.side==="faker"){
      ctx.font="bold 13px sans-serif";ctx.fillStyle="#fff4db";
      ctx.fillText(`F · ${actor.items?.length||0}`,Math.min(462,x+11),Math.max(18,y-10));
    }
  }
}

function renderPressureLive() {
  const svg = $("#pressure-live-map"), roster = $("#pressure-live-roster");
  svg.replaceChildren(); roster.replaceChildren();
  const row = trace?.rows?.[Number($("#replay-slider").value)];
  const own = row?.actors_t?.find(actor => actor.side === "faker");
  if (!own?.xy) {
    $("#pressure-live-readout").textContent = language === "fr" ?
      "Charge une partie indexée pour afficher les positions à la minute choisie." :
      "Load an indexed game to show player positions at the selected minute.";
    return;
  }
  const project = xy => [30 + xy[0] * 500, 530 - xy[1] * 500];
  svg.append(svgNode("rect", {x:30,y:30,width:500,height:500,fill:"#190f1a",stroke:"#94556b","stroke-width":2}));
  if(iocFilters.lanes)for(const [lane,path] of Object.entries(lanePaths)){
    svg.append(svgNode("polyline",{points:path.map(xy=>project(xy).join(",")).join(" "),
      fill:"none",stroke:"#ffcf98",opacity:.55,"stroke-width":4,"stroke-dasharray":"8 8"}));
    const mid=project(path[Math.floor(path.length/2)]);
    const label=svgNode("text",{x:mid[0]+5,y:mid[1]-6,fill:"#ffd895","font-size":10});label.textContent=lane;svg.append(label);
  }
  for (let i=1;i<8;i++) {
    const v=30+i*62.5;
    svg.append(svgNode("line",{x1:v,y1:30,x2:v,y2:530,stroke:"#5e354a",opacity:.55}));
    svg.append(svgNode("line",{x1:30,y1:v,x2:530,y2:v,stroke:"#5e354a",opacity:.55}));
  }
  const [fx,fy] = project(own.xy);
  if(iocFilters.radius)svg.append(svgNode("circle",{cx:fx,cy:fy,r:pressureRadius/15000*500,
    fill:"#ff536b",opacity:.11,stroke:"#ff9eae","stroke-width":5}));
  const known = row.actors_t.filter(actor => actor.xy);
  const nearby = side => known.filter(actor => actor.side === side &&
    Math.hypot(actor.xy[0]-own.xy[0],actor.xy[1]-own.xy[1]) <= pressureRadius/15000);
  const nearEnemy = nearby("enemy"), nearAlly = nearby("ally");
  for (const actor of known.filter(showIocActor)) {
    const [px,py] = project(actor.xy);
    const inside = actor.side !== "faker" && Math.hypot(actor.xy[0]-own.xy[0],actor.xy[1]-own.xy[1]) <= pressureRadius/15000;
    const color = actor.side === "faker" ? "#ffd895" : actor.side === "ally" ? "#70a8ff" : "#ff637d";
    if (inside) svg.append(svgNode("line",{x1:fx,y1:fy,x2:px,y2:py,stroke:color,opacity:.7,
      "stroke-width":2,"stroke-dasharray":"5 5"}));
    svg.append(svgNode("circle",{cx:px,cy:py,r:actor.side==="faker"?10:inside?8:6,
      fill:color,stroke:"#fff7ee","stroke-width":inside?2.5:1.5}));
    const label=svgNode("text",{x:Math.min(490,px+10),y:Math.max(25,py-7),fill:color,
      "font-size":11,"font-weight":800});
    label.textContent=actor.side==="faker"?"FAKER":actor.role.slice(0,3);svg.append(label);
  }
  const missing = 10-known.length;
  const ended=sharedMinute>row.minute+.5 ? (language==="fr"?" · dernière frame disponible":" · last available frame"):"";
  $("#pressure-live-readout").textContent = language === "fr" ?
    `${row.minute.toFixed(0)} min${ended} · ${nearEnemy.length}/5 adversaires et ${nearAlly.length}/4 alliés dans ${pressureRadius.toLocaleString("fr")} unités · ${missing} position(s) absente(s).` :
    `${row.minute.toFixed(0)} min${ended} · ${nearEnemy.length}/5 opponents and ${nearAlly.length}/4 allies within ${pressureRadius.toLocaleString("en")} units · ${missing} missing position(s).`;
  for (const actor of row.actors_t.filter(showIocActor)) {
    const card=document.createElement("div");card.className=`pressure-actor ${actor.side}`;
    const distance = actor.xy ? Math.round(Math.hypot(actor.xy[0]-own.xy[0],actor.xy[1]-own.xy[1])*15000) : null;
    card.classList.toggle("inside",actor.side!=="faker" && distance!==null && distance<=pressureRadius);
    const heading=document.createElement("div");heading.className="pressure-actor-heading";
    heading.append(spriteIcon("champions",actor.champion,actor.champion));
    const title=document.createElement("strong");title.textContent=`${actor.side==="faker"?"FAKER":actor.role} · ${actor.champion}`;
    const range=document.createElement("span");range.textContent=actor.side==="faker"?`Niv. ${actor.level}`:
      distance===null?"position ?":`${distance.toLocaleString(language)} u`;
    heading.append(title,range);card.append(heading);
    const items=document.createElement("div");items.className="pressure-actor-items";
    for(const item of (iocFilters.items ? actor.items||[] : []).slice(0,7)) {
      const name=spriteManifest?.items?.[String(item)]?.[language] || `#${item}`;
      const icon=spriteIcon("items",item,name);icon.title=name;items.append(icon);
    }
    if(iocFilters.items&&!actor.items?.length) {
      const empty=document.createElement("small");empty.textContent=language==="fr"?"Aucun objet suivi à t":"No tracked item at t";items.append(empty);
    }
    if(iocFilters.items)card.append(items);
    roster.append(card);
  }
}

function renderPressure() {
  const svg=$("#pressure-chart");svg.replaceChildren();
  const phases=[["early","0–10"],["middle","10–20"],["late","20+"]];
  const selectedPhase = phaseAt(sharedMinute);
  const profile=pressureData.radius_profiles?.[String(pressureRadius)] || pressureData;
  const selectedRow = profile.phases[selectedPhase];
  $("#pressure-radius-label").textContent = `${pressureRadius.toLocaleString(language)} ${language==="fr"?"unités":"units"}`;
  $("#pressure-radius-scale").textContent = language==="fr" ?
    `1 000 ─────────── 5 000 unités · côté de la carte ≈ 15 000 unités` :
    `1,000 ─────────── 5,000 units · map width ≈ 15,000 units`;
  $("#pressure-phase-readout").textContent = language === "fr" ?
    `${phaseLabel(selectedPhase)} min · rayon ${pressureRadius.toLocaleString("fr")} unités · ${(selectedRow.mean_near_enemies??0).toFixed(2)} adversaire(s) par frame · ${(selectedRow.arrival_rate_per_frame??0).toFixed(2)} entrée(s) par frame · ${selectedRow.frames.toLocaleString("fr")} frames / ${pressureData.source_matches} parties.` :
    `${phaseLabel(selectedPhase)} min · ${pressureRadius.toLocaleString("en")} unit radius · ${(selectedRow.mean_near_enemies??0).toFixed(2)} opponents per frame · ${(selectedRow.arrival_rate_per_frame??0).toFixed(2)} entries per frame · ${selectedRow.frames.toLocaleString("en")} frames / ${pressureData.source_matches} games.`;
  const zone=$("#pressure-zone");zone.replaceChildren();
  zone.append(svgNode("rect",{x:20,y:20,width:200,height:200,fill:"#271a24",stroke:"#8a5b6a","stroke-width":2}));
  for(const xy of [60,100,140,180]) {
    zone.append(svgNode("line",{x1:xy,y1:20,x2:xy,y2:220,stroke:"#654556","stroke-width":.7}));
    zone.append(svgNode("line",{x1:20,y1:xy,x2:220,y2:xy,stroke:"#654556","stroke-width":.7}));
  }
  zone.append(svgNode("circle",{cx:120,cy:120,r:pressureRadius/15000*200,fill:"#ff536b",opacity:.22,stroke:"#ff8ca1","stroke-width":5}));
  zone.append(svgNode("circle",{cx:120,cy:120,r:6,fill:"#ffd895",stroke:"#fff"}));
  const fakerLabel=svgNode("text",{x:131,y:116,fill:"#ffd895","font-size":12,"font-weight":800});fakerLabel.textContent="FAKER";zone.append(fakerLabel);
  const widthLabel=svgNode("text",{x:230,y:37,fill:"#e8d4db","font-size":11});widthLabel.textContent="≈15 000";zone.append(widthLabel);
  const radiusLabel=svgNode("text",{x:230,y:61,fill:"#ff91a2","font-size":13,"font-weight":800});radiusLabel.textContent=`R ${pressureRadius.toLocaleString(language)}`;zone.append(radiusLabel);
  const maximum=Math.max(1,...Object.values(profile.phases).flatMap(row=>[row.mean_near_enemies??0,row.arrival_rate_per_frame??0]));
  const scale=Math.ceil(maximum*2)/2;
  const yAt=v=>260-v/scale*180;
  for(let index=0;index<=4;index++) {
    const mark=scale*index/4;
    const y=yAt(mark);
    svg.append(svgNode("line",{x1:64,x2:760,y1:y,y2:y,stroke:"#34516a"}));
    const label=svgNode("text",{x:17,y:y+4,fill:"#a2bbcd","font-size":12});label.textContent=mark.toFixed(2);svg.append(label);
  }
  for(const [index,[phase,label]] of phases.entries()) {
    const row=profile.phases[phase],x=140+index*240;
    if (phase === selectedPhase) svg.append(svgNode("rect",{x:x-24,y:52,width:155,height:245,rx:9,fill:"#724158",opacity:.42,stroke:"#ffd895"}));
    for(const [j,key,color] of [[0,"mean_near_enemies","#ff637d"],[1,"arrival_rate_per_frame","#ffca77"]]) {
      const value=row[key]??0,height=180*value/scale;
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
  for(const [key,row] of Object.entries(profile.score_slices)) {
    const card=document.createElement("div");card.className="pressure-slice";
    const title=document.createElement("strong");title.textContent=key==="other" ? (language==="fr"?"Autres scores":"Other scores") : `Faker ${key}`;
    const value=document.createElement("span");value.textContent=row.mean_near_enemies==null?"—":row.mean_near_enemies.toFixed(2);
    const detail=document.createElement("small");detail.textContent=`${row.frames.toLocaleString(language)} ${language==="fr"?"états · adversaires proches en moyenne":"states · nearby opponents on average"}`;
    card.append(title,value,detail);cards.append(card);
  }
  renderPressureLive();
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
  const live=currentIocRow();
  if(live){
    const locate=xy=>project(xy[0]*grid,xy[1]*grid,0);
    if(iocFilters.lanes)for(const path of Object.values(lanePaths)){
      svg.append(svgNode("polyline",{points:path.map(xy=>locate(xy).join(",")).join(" "),
        fill:"none",stroke:"#ffd895",opacity:.78,"stroke-width":2,"stroke-dasharray":"6 5"}));
    }
    const own=live.actors_t.find(actor=>actor.side==="faker");
    if(iocFilters.radius&&own?.xy){
      const points=Array.from({length:49},(_,i)=>{
        const angle=i/48*Math.PI*2;
        return locate([own.xy[0]+Math.cos(angle)*pressureRadius/15000,
                       own.xy[1]+Math.sin(angle)*pressureRadius/15000]);
      });
      svg.append(svgNode("polyline",{points:points.map(p=>p.join(",")).join(" "),
        fill:"none",stroke:"#ffadbd",opacity:.9,"stroke-width":1.6}));
    }
    for(const actor of live.actors_t.filter(a=>a.xy&&showIocActor(a))){
      const [x,y]=locate(actor.xy);
      const color=actor.side==="faker"?"#ffd895":actor.side==="ally"?"#70a8ff":"#ff637d";
      svg.append(svgNode("circle",{cx:x,cy:y,r:actor.side==="faker"?7:5,fill:color,
        stroke:"#fff","stroke-width":1.7}));
      if(iocFilters.items&&actor.side==="faker"){
        const badge=svgNode("text",{x:Math.min(558,x+10),y:y-9,fill:"#fff4db","font-size":12,
          "font-weight":800,stroke:"#261622","stroke-width":2,"paint-order":"stroke"});
        badge.textContent=`F · ${actor.items?.length||0}`;svg.append(badge);
      }
    }
  }
  renderIocReadout("#surface-ioc-readout");
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
    for(const event of row.events_next||[])if(important.has(event.category))
      moments.push({index,event,minute:(event.time_seconds??row.minute*60)/60});
  });
  for(const moment of moments.slice(0,32)) {
    const button=document.createElement("button");button.type="button";
    button.textContent=`${formatPreciseTime(moment.event.time_seconds ?? moment.minute*60)} · ${liveEventLabel(moment.event,null).replace(" · ⊙","")}`;
    button.addEventListener("click",()=>{
      stopLive();stopReplay();
      if (trace.schema_version >= 6) liveSeconds=moment.event.time_seconds;
      setSharedMinute(Math.floor(moment.minute),{preserveLive:true});
      renderLive();
    });
    container.append(button);
  }
}

function formatGameTime(seconds) {
  const whole=Math.max(0,Math.floor(Number(seconds)||0));
  return `${String(Math.floor(whole/60)).padStart(2,"0")}:${String(whole%60).padStart(2,"0")}`;
}

function formatPreciseTime(seconds) {
  const millis=Math.max(0,Math.round((Number(seconds)||0)*1000));
  return `${String(Math.floor(millis/60000)).padStart(2,"0")}:${String(Math.floor(millis/1000)%60).padStart(2,"0")}.${String(millis%1000).padStart(3,"0")}`;
}

function syncSharedFromLive() {
  const minute=Math.max(0,Math.min(39,Math.floor(liveSeconds/60)));
  if (minute!==sharedMinute) setSharedMinute(minute,{preserveLive:true});
}

function stopLive() {
  if (liveTimer) clearInterval(liveTimer);
  liveTimer=null;
  $("#live-play").textContent=copy[language].replay_play;
}

function liveEventLabel(event, actor) {
  const fr=language==="fr";
  const name=actor?.side==="faker"?"Faker":actor?.champion;
  const category={
    faker_kill:fr?"Faker élimine un adversaire":"Faker kills an opponent",
    faker_death:fr?"Faker meurt":"Faker dies",
    ally_kill:fr?"Élimination alliée":"Ally kill",
    enemy_kill:fr?"Élimination adverse":"Opponent kill",
    dragon:fr?"Dragon":"Dragon",baron:fr?"Baron Nashor":"Baron Nashor",
    herald:fr?"Héraut":"Herald",grubs:fr?"Larves du Néant":"Void grubs",
    building:fr?"Bâtiment détruit":"Structure destroyed",
    ward_placed:fr?"Balise posée":"Ward placed",
    ward_cleared:fr?"Balise détruite":"Ward cleared",
    ITEM_PURCHASED:fr?"Achat":"Purchase",
    SKILL_LEVEL_UP:fr?"Point de compétence":"Skill point",
  }[event.category]||event.category.replaceAll("_"," ");
  const item=event.item_id?` · ${spriteManifest?.items?.[String(event.item_id)]?.[language]||`#${event.item_id}`}`:"";
  const skill=event.skill_slot?` · ${["","Q","W","E","R"][event.skill_slot]||event.skill_slot}`:"";
  const owner=event.category==="faker_kill"?"":event.category==="faker_death"&&name?
    ` · ${fr?"par":"by"} ${name}`:name?` · ${name}`:"";
  return `${category}${owner}${item}${skill}${event.cell64==null?"":" · ⊙"}`;
}

function filteredLiveEvents() {
  const filter=$("#live-event-filter").value;
  if(filter==="all")return liveEvents;
  const own=trace?.rows?.[0]?.actors_t?.find(actor=>actor.side==="faker")?.participant;
  return liveEvents.filter(event=>{
    if(filter==="faker")return event.category.startsWith("faker_") || event.actor_id===own;
    if(filter==="combat")return event.category.endsWith("_kill") || event.category==="faker_death";
    if(filter==="objective")return ["dragon","baron","herald","grubs","building"].includes(event.category);
    if(filter==="vision")return ["ward_placed","ward_cleared"].includes(event.category);
    return ["ITEM_PURCHASED","SKILL_LEVEL_UP"].includes(event.category);
  });
}

function jumpLiveEvent(direction) {
  const candidates=filteredLiveEvents();
  const event=direction<0?[...candidates].reverse().find(e=>e.time_seconds<liveSeconds-.0005):
    candidates.find(e=>e.time_seconds>liveSeconds+.0005);
  if(!event)return;
  stopLive();liveSeconds=event.time_seconds;syncSharedFromLive();renderLive();
}

function renderLive() {
  if (!trace || trace.schema_version < 6) return;
  const rows=trace.rows;
  const end=rows.at(-1).next_frame_seconds;
  liveSeconds=Math.max(0,Math.min(end,liveSeconds));
  $("#live-slider").value=liveSeconds.toFixed(3);
  $("#live-clock").textContent=`${formatPreciseTime(liveSeconds)} / ${formatPreciseTime(end)}`;
  let index=0;
  while(index+1<rows.length && rows[index+1].frame_seconds<=liveSeconds) index++;
  const row=rows[index];
  const finalSample=index===rows.length-1 && liveSeconds>=row.next_frame_seconds;
  const sampleTime=finalSample?row.next_frame_seconds:row.frame_seconds;
  const actors=finalSample?row.actors_next:row.actors_t;
  const missing=actors.filter(actor=>!actor.xy).length;
  const age=Math.max(0,liveSeconds-sampleTime).toFixed(1);
  $("#live-sample").textContent=language==="fr"?
    `Positions Riot à ${formatPreciseTime(sampleTime)} · âge ${age} s · ${10-missing}/10 disponibles (vue omnisciente)`:
    `Riot positions at ${formatPreciseTime(sampleTime)} · ${age} s old · ${10-missing}/10 available (omniscient view)`;
  const target=formatGameTime(row.next_frame_seconds);
  $("#live-forecast").textContent=finalSample?(language==="fr"?"Fin des positions observées ; aucune prévision suivante disponible.":"End of sampled positions; no next forecast available."):(language==="fr"?
    `Shadow historique : case 16×16 ${row.predicted_region%16},${Math.floor(row.predicted_region/16)} pour la prochaine frame vers ${target}. Prévision, pas position réelle.`:
    `Historical Shadow: 16×16 cell ${row.predicted_region%16},${Math.floor(row.predicted_region/16)} for the next frame around ${target}. Forecast, not an observed position.`);
  const svg=$("#live-map");svg.replaceChildren();
  svg.append(svgNode("rect",{x:0,y:0,width:600,height:600,fill:"#100d18"}));
  svg.append(svgNode("rect",{x:60,y:60,width:480,height:480,fill:"#221923",stroke:"#a85d73","stroke-width":2}));
  for(const points of ["60,540 60,60 540,60","60,540 540,60","60,540 540,540 540,60"])
    svg.append(svgNode("polyline",{points,fill:"none",stroke:"#684251","stroke-width":14,"stroke-linejoin":"round"}));
  svg.append(svgNode("line",{x1:75,y1:300,x2:525,y2:300,stroke:"#497789","stroke-width":20,opacity:.28}));
  const visibleEvents=filteredLiveEvents();
  for(const e of visibleEvents) {
    if(!$("#live-show-places").checked || e.time_seconds>liveSeconds || e.time_seconds<liveSeconds-8 || e.cell64==null) continue;
    const x=60+((e.cell64%64+.5)/64)*480,y=540-((Math.floor(e.cell64/64)+.5)/64)*480;
    const marker=svgNode("circle",{cx:x,cy:y,r:11,fill:"none",stroke:"#ffe09c","stroke-width":3,opacity:.9});
    const title=svgNode("title");title.textContent=`${formatPreciseTime(e.time_seconds)} · ${e.category}`;marker.append(title);svg.append(marker);
  }
  const labels=[];
  for(const actor of actors) {
    if(actor.side==="ally"&&!$("#live-show-allies").checked || actor.side==="enemy"&&!$("#live-show-enemies").checked)continue;
    if(!actor.xy)continue;
    const x=60+actor.xy[0]*480,y=540-actor.xy[1]*480;
    const colour=actor.side==="faker"?"#ffdf9c":actor.side==="ally"?"#67b8f3":"#ff667e";
    const dot=svgNode("circle",{cx:x,cy:y,r:actor.side==="faker"?10:7,fill:colour,stroke:"#100d18","stroke-width":2});
    const title=svgNode("title");title.textContent=`${actor.side==="faker"?"Faker":actor.role} · ${actor.champion} · niveau ${actor.level}`;dot.append(title);svg.append(dot);
    const name=actor.side==="faker"?"FAKER":actor.champion;
    const width=name.length*(actor.side==="faker"?8:6.5)+4;
    let labelX=x+13,labelY=y-10,placed=false;
    for(let step=0;step<40;step++) {
      const side=step%2===0?1:-1;
      const level=Math.floor(step/2);
      const tier=Math.ceil(level/2);
      const direction=level%2===0?1:-1;
      const candidateX=side>0?x+13:x-13-width;
      const candidateY=y-10+direction*tier*15;
      const box={x:candidateX,y:candidateY-12,w:width,h:15};
      if(box.x<62||box.x+box.w>538||box.y<62||box.y+box.h>538)continue;
      if(labels.some(other=>box.x<other.x+other.w+4&&box.x+box.w+4>other.x&&box.y<other.y+other.h+3&&box.y+box.h+3>other.y))continue;
      labelX=candidateX;labelY=candidateY;labels.push(box);placed=true;break;
    }
    if(!placed)continue;
    if(Math.hypot(labelX-x,labelY-y)>26)
      svg.append(svgNode("line",{x1:x,y1:y,x2:labelX,y2:labelY-4,stroke:colour,"stroke-width":.8,opacity:.55}));
    const label=svgNode("text",{x:labelX,y:labelY,fill:colour,"font-size":actor.side==="faker"?13:10,"font-weight":700,stroke:"#100d18","stroke-width":3,"paint-order":"stroke"});
    label.textContent=name;svg.append(label);
  }
  const own=actors.find(actor=>actor.side==="faker");
  const roster=$("#live-roster");roster.replaceChildren();
  for(const actor of actors){
    if(actor.side==="ally"&&!$("#live-show-allies").checked || actor.side==="enemy"&&!$("#live-show-enemies").checked)continue;
    const card=document.createElement("div");card.className=`live-player ${actor.side}`;
    const who=document.createElement("strong");who.textContent=`${actor.side==="faker"?"FAKER · ":""}${actor.champion} · ${actor.role}`;
    const detail=document.createElement("span");
    const distance=own?.xy&&actor.xy?Math.round(Math.hypot(actor.xy[0]-own.xy[0],actor.xy[1]-own.xy[1])*15000):null;
    detail.textContent=`Lv ${actor.level} · ${actor.health_fraction==null?"HP ?":`HP ${Math.round(actor.health_fraction*100)}%`} · ${actor.side==="faker"?"—":distance==null?"?":`${distance.toLocaleString(language)} u`}`;
    card.append(who,detail);roster.append(card);
  }
  const feed=$("#live-events");feed.replaceChildren();
  const past=visibleEvents.filter(e=>e.time_seconds<=liveSeconds).slice(-8).reverse();
  if(!past.length)feed.textContent=language==="fr"?"Aucun événement encore.":"No events yet.";
  for(const event of past) {
    const item=document.createElement("div");item.className="live-event";
    const actor=actors.find(a=>a.participant===event.actor_id);
    item.textContent=`${formatPreciseTime(event.time_seconds)}  ${liveEventLabel(event,actor)}`;
    feed.append(item);
  }
  $("#live-prev-event").disabled=!visibleEvents.some(e=>e.time_seconds<liveSeconds-.0005);
  $("#live-next-event").disabled=!visibleEvents.some(e=>e.time_seconds>liveSeconds+.0005);
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
    if (data.schema_version < 6) await openGame(data.match_id);
  } catch (_) { /* Per-match trace is local and optional. */ }
}

function setTrace(data) {
  if (!data.rows?.length || data.source_step_seconds !== 60 || data.schema_version < 3) return;
  stopLive();stopReplay();trace=data;
  liveEvents=[];
  if(data.schema_version>=6){
    const seen=new Set();
    for(const row of trace.rows){
      if(seen.has(row.source_frame_index))continue;
      seen.add(row.source_frame_index);
      liveEvents.push(...(row.events_initial||[]),...(row.events_next||[]));
    }
    liveEvents.sort((a,b)=>a.time_seconds-b.time_seconds);
    liveSeconds=trace.rows[0].frame_seconds;
    $("#live-slider").max=trace.rows.at(-1).next_frame_seconds;
    $("#live-replay").hidden=false;
    renderLive();
  }else $("#live-replay").hidden=true;
  $("#replay-slider").max=trace.rows.length-1;$("#replay-slider").value=0;
  $("#replay-nav").hidden=false;
  $("#game-picker").value=trace.match_id;
  $("#pressure-game-picker").value=trace.match_id;
  $("#game-status").textContent=`${trace.match_id} · ${trace.split} · ${trace.rows.length} frames · ${liveEvents.length} events`;
  renderGamePreview(trace.match_id);
  renderMoments();setSharedMinute(0);
}

async function loadGameList() {
  try {
    const response=await fetch("/api/games");if(!response.ok)return;
    gameFacts=await response.json();
    const list=$("#game-options");list.replaceChildren();
    for(const game of gameFacts){const option=document.createElement("option");option.value=game.match_id;
      option.label=`${game.started_utc?.slice(0,10) || "?"} · ${game.champion} · ${game.kills}/${game.deaths}/${game.assists} · ${game.won ? "W" : "L"}`;
      list.append(option);}
    renderGameCards();renderGamePreview();
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
  const optional = await Promise.allSettled([fetch("/grid64.json"), fetch("/events64.json"), fetch("/challenge.json"), fetch("/pressure.json"), fetch("/predictability.json"), fetch("/atlas512.json"), fetch("/grid512.json"), fetch("/event-ablation.json"), fetch("/world-finals.json"), fetch("/corpus.json"), fetch("/sprites.json"), fetch("/ioc-summary.json"), fetch("/ioc-quality.json"), fetch("/event-validation.json"), fetch("/faker-memory.json"), fetch("/api/memory/cases"), fetch("/team-matrix.json"), fetch("/team-probe.json"), fetch("/ninety-gate.json"), fetch("/second-scale.json"), fetch("/faker-actions.json"), fetch("/faker-actions-sanitized.json"), fetch("/replay-audit.json")]);
  const payloads = await Promise.all(optional.map(async (item) =>
    item.status === "fulfilled" && item.value.ok ? item.value.json() : null));
  let memoryPayload;
  [grid64, events64, challengeData, pressureData, predictabilityData, atlas512, grid512Score, eventAblation, worldFinals, corpusData, spriteManifest, iocSummary, iocQuality, eventValidation, memorySummary, memoryPayload, teamData, teamProbe, ninetyData, secondScaleData, fakerActionsData, sanitationData, replayAudit] = payloads;
  renderReplayAudit();
  try { const response = await fetch("/ioc-ledger.json"); if (response.ok) iocLedger = await response.json(); }
  catch (error) { console.warn("IoC ledger aggregate unavailable", error); }
  memoryCases = memoryPayload?.examples || [];
  renderIocResult();
  renderIocLedger();
  if (summary && (atlas512 || grid64)) renderSurface();
  if (atlas512 || events64) renderAtlas();
  if (challengeData) renderChallenge();
  if (pressureData) renderPressure();
  if (predictabilityData) renderPredictability();
  if (ninetyData) renderNinety();
  if (secondScaleData) renderSecondScale();
  if (fakerActionsData) renderFakerActions();
  if (sanitationData) renderSanitation();
  if (grid512Score) renderGrid512Score();
  if (eventAblation) renderResearchEvents();
  if (worldFinals) renderFinals();
  if (corpusData) renderCorpus();
  if (eventValidation) renderEventValidation();
  if (teamData) renderTeam();
  if (teamProbe) renderTeamProbe();
  if (memorySummary) renderMemory();
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
window.addEventListener("hashchange", showSection);
window.addEventListener("resize", positionActiveTab);
for (const link of document.querySelectorAll('a[href^="#"]')) link.addEventListener("click", event => {
  event.preventDefault();
  const target = link.getAttribute("href");
  if (location.hash === target) showSection();
  else history.pushState(null, "", target), showSection();
});
window.addEventListener("popstate", showSection);
$("#library-search").addEventListener("click",searchLibrary);
$("#library-query").addEventListener("keydown",event=>{if(event.key==="Enter")searchLibrary();});
$("#game-open").addEventListener("click",()=>openGame());
$("#game-picker").addEventListener("keydown",event=>{if(event.key==="Enter")openGame();});
$("#game-picker").addEventListener("input",()=>renderGamePreview());
$("#pressure-game-open").addEventListener("click",()=>openGame($("#pressure-game-picker").value.trim()));
$("#pressure-game-picker").addEventListener("keydown",event=>{
  if(event.key==="Enter")openGame($("#pressure-game-picker").value.trim());
});
$("#game-filter").addEventListener("input",()=>{gameCardsShown=12;renderGameCards();});
$("#game-more").addEventListener("click",()=>{gameCardsShown+=12;renderGameCards();});
$("#pressure-radius").addEventListener("input",event=>{
  pressureRadius=(pressureData?.available_radii_units || [1000,1500,2500,3500,5000])[Number(event.target.value)] || 2500;
  if (pressureData) renderPressure();
});
$("#time-scrubber").addEventListener("input",event=>setSharedMinute(event.target.value));
$("#second-horizon").addEventListener("input",renderSecondScale);
$("#faker-actions-phase-select").addEventListener("change",renderFakerActions);
$("#time-scrubber").addEventListener("wheel",event=>{event.preventDefault();setSharedMinute(sharedMinute+(event.deltaY>0?1:-1));},{passive:false});
$("#minute-slider").addEventListener("input", () => setSharedMinute(Number($("#minute-slider").value)*5));
$("#atlas-layer").addEventListener("change", () => { if (atlas512 || events64) renderAtlas(); });
$("#atlas-phase").addEventListener("change", () => setSharedMinute(({early:0,middle:10,late:20})[$("#atlas-phase").value]));
$("#atlas-canvas").addEventListener("mousemove", (event) => {
  if (!atlasValues) return;
  const bounds = event.target.getBoundingClientRect();
  const x = Math.min(atlasGrid - 1, Math.max(0, Math.floor((event.clientX - bounds.left) / bounds.width * atlasGrid)));
  const y = Math.min(atlasGrid - 1, Math.max(0, atlasGrid - 1 - Math.floor((event.clientY - bounds.top) / bounds.height * atlasGrid)));
  $("#atlas-readout").textContent = copy[language].atlas_point($("#atlas-layer").selectedOptions[0].textContent,
    phaseLabel($("#atlas-phase").value),x,y,atlasValues.get(y*atlasGrid+x) || 0,atlasGrid,$("#atlas-canvas").dataset.cohort);
});
$("#atlas-canvas").addEventListener("mouseleave", () => { if (atlas512 || events64) $("#atlas-readout").textContent = copy[language].atlas_hover; });
$("#challenge-response").addEventListener("input", () => { if (challengeData) renderChallenge(); });
$("#challenge-sharing").addEventListener("input", () => { if (challengeData) renderChallenge(); });
$("#team-year").addEventListener("change", event => { teamYear = event.target.value; renderTeam(); });
$("#team-mode-total").addEventListener("click", () => { teamMode = "total"; renderTeam(); });
$("#team-mode-recent").addEventListener("click", () => { teamMode = "recent"; renderTeam(); });
$("#memory-reveal").addEventListener("click", () => { if (memoryCases.length) { memoryRevealed = true; renderMemory(); } });
$("#memory-next").addEventListener("click", () => { if (memoryCases.length) { memoryCaseIndex = (memoryCaseIndex + 1) % memoryCases.length; memoryChoice = null; memoryRevealed = false; renderMemory(); } });
$("#surface-actual").addEventListener("click", () => { surfaceMode = "actual"; if (summary) renderSurface(); });
$("#surface-shadow").addEventListener("click", () => { surfaceMode = "predicted"; if (summary) renderSurface(); });
$("#angle-slider").addEventListener("input", () => { if (summary) renderSurface(); });
$("#replay-slider").addEventListener("input", () => { stopReplay(); if (trace) setSharedMinute(trace.rows[Number($("#replay-slider").value)].minute); });
$("#live-slider").addEventListener("input",()=>{stopLive();liveSeconds=Number($("#live-slider").value);syncSharedFromLive();renderLive();});
for(const id of ["live-show-allies","live-show-enemies","live-show-places","live-event-filter"])
  $("#"+id).addEventListener("change",()=>{if(trace)renderLive();});
$("#live-prev-event").addEventListener("click",()=>jumpLiveEvent(-1));
$("#live-next-event").addEventListener("click",()=>jumpLiveEvent(1));
$("#live-play").addEventListener("click",()=>{
  if(!trace || trace.schema_version<6)return;
  if(liveTimer){stopLive();return;}
  if(liveSeconds>=trace.rows.at(-1).next_frame_seconds)liveSeconds=0;
  syncSharedFromLive();
  $("#live-play").textContent=copy[language].replay_pause;
  liveTimer=setInterval(()=>{
    liveSeconds+=Number($("#live-speed").value)*.2;
    syncSharedFromLive();
    renderLive();
    if(liveSeconds>=trace.rows.at(-1).next_frame_seconds)stopLive();
  },200);
});
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
showSection();
start();
