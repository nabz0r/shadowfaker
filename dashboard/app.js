const copy = {
  fr: {
    nav_map: "Minimap", nav_replay: "Évolution", nav_tempo: "Tempo", nav_strategy: "Stratégies", nav_evidence: "Preuves",
    hero_eyebrow: "Laboratoire de décisions macro · KR ranked solo",
    hero_title: "Observer Faker.<br>Tester Shadow.",
    hero_copy: "Un modèle local prédit la prochaine décision du compte « Hide on bush#KR1 » à partir de l'état de la partie. Les autres joueurs, la vision approximée et les objectifs façonnent le contexte. L'objectif infra-minute reste une étape de recherche : les données actuelles sont espacées d'environ 60 secondes.",
    explore: "Explorer les cartes", evidence: "Voir les preuves", stat_games: "parties utilisables",
    stat_observations: "paires de minutes", stat_exact: "précision 16×16", stat_future: "nouvelles parties pour confirmer",
    map_title: "Où Faker va. Où Shadow pense qu'il va.",
    map_intro: "Déplace la souris sur une case : les deux minimaps utilisent les mêmes 1 197 observations. La couleur montre la fréquence de chaque prochaine position, pas une trajectoire ou la vision du joueur.",
    observed: "FAKER · OBSERVÉ", predicted: "SHADOW · PRÉDIT", less: "rare", more: "fréquent",
    map_insight: "Shadow sur-prédit une case centrale : 39,43 % de ses choix, contre 11,28 % des destinations réelles. La carte révèle une faiblesse concrète du modèle actuel.",
    surface_title: "La minimap devient une surface de choix", surface_intro: "Les axes au sol sont les coordonnées de la carte ; la hauteur est la fréquence d'une prochaine position. Tourne la surface et compare la distribution réelle à Shadow. La troisième dimension est une probabilité, pas le relief réel de LoL ni une preuve de stratégie gagnante.",
    surface_actual: "Observé", surface_shadow: "Shadow", surface_rotate: "Angle de vue",
    replay_title: "Une décision change le prochain état", replay_step: "Échantillonné chaque ~60 s",
    replay_intro: "Rejoue une partie de test locale, minute après minute. La carte montre la distribution du modèle à l'instant t, les alliés visibles dans l'état, la destination réelle à t+1 et le choix prédit. Entre deux frames, les actions et réactions restent inconnues.",
    replay_team: "alliés à t", replay_real: "Faker à t+1", replay_guess: "choix Shadow", replay_minute: "Minute",
    replay_gold: "Écart d'or équipe", replay_xp: "Écart d'XP", replay_level: "Niveau", replay_uncertainty: "Dispersion de prédiction",
    replay_play: "▶ Rejouer", replay_pause: "Ⅱ Pause", replay_trend_note: "Courbe rétrospective de l'écart d'or ; elle n'entre jamais dans l'état passé du modèle.",
    accuracy_title: "Ce qu'on sait vraiment prédire", exploratory: "8×8 / 4×4 exploratoires",
    exact_explain: "<strong>16×16 :</strong> Shadow 11,28 %, baseline 11,61 %. Le critère initial n'est pas atteint.",
    coarse_explain: "<strong>8×8 et 4×4 :</strong> un signal de rotations plus larges apparaît, mais il a été examiné après lecture du test. Il faut des parties futures.",
    tempo_title: "Une équipe qui chauffe et se refroidit", tempo_interactive: "Explorer une tranche de temps",
    tempo_interactive_help: "Pourcentage de minutes où Faker se rapproche d'un allié déjà positionné.", minute: "Minute",
    tempo_explain: "Ce sont des rapprochements géométriques, pas des preuves d'aide ou de communication. Le top évolue aussi : aucun rôle n'a un poids constant de 20 %.",
    strategy_title: "Et si cinq joueurs allaient bot ?", hypothesis: "Hypothèse, pas résultat",
    strategy_explain: "Dans ces 465 parties, une seule frame précoce montre les cinq alliés dans un rayon de 2 500 unités du bot carry. Cette proximité ne prouve pas une stratégie cinq bot. La question exige de mesurer ce qui est gagné, perdu ailleurs et comment l'adversaire réagit.",
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
    nav_map: "Minimap", nav_replay: "Evolution", nav_tempo: "Tempo", nav_strategy: "Strategies", nav_evidence: "Evidence",
    hero_eyebrow: "Macro decision lab · KR ranked solo", hero_title: "Observe Faker.<br>Test Shadow.",
    hero_copy: "A local model predicts the next decision of the account “Hide on bush#KR1” from the evolving game state. Other players, an approximate view of vision and objectives provide context. Sub-minute prediction is the next research target: current timelines are roughly 60 seconds apart.",
    explore: "Explore the maps", evidence: "See the evidence", stat_games: "usable matches",
    stat_observations: "minute pairs", stat_exact: "16×16 accuracy", stat_future: "new matches needed to confirm",
    map_title: "Where Faker goes. Where Shadow thinks he goes.",
    map_intro: "Hover over a cell: both minimaps use the same 1,197 observations. Colour shows the frequency of next positions, not a path or the player's own view.",
    observed: "FAKER · OBSERVED", predicted: "SHADOW · PREDICTED", less: "rare", more: "frequent",
    map_insight: "Shadow overpredicts one central cell: 39.43% of its choices versus 11.28% of real destinations. The map exposes a concrete weakness of the current model.",
    surface_title: "The minimap becomes a surface of choices", surface_intro: "The ground axes are map coordinates; height is how often a next position occurs. Rotate the surface and compare reality with Shadow. The third dimension is probability, not LoL terrain or proof of a winning strategy.",
    surface_actual: "Observed", surface_shadow: "Shadow", surface_rotate: "View angle",
    replay_title: "A decision changes the next state", replay_step: "Sampled every ~60 s",
    replay_intro: "Replay one local test match minute by minute. The map shows the model distribution at time t, allies present in the state, the real destination at t+1 and the predicted choice. Actions and reactions between frames remain unknown.",
    replay_team: "allies at t", replay_real: "Faker at t+1", replay_guess: "Shadow choice", replay_minute: "Minute",
    replay_gold: "Team gold difference", replay_xp: "XP difference", replay_level: "Level", replay_uncertainty: "Forecast spread",
    replay_play: "▶ Play", replay_pause: "Ⅱ Pause", replay_trend_note: "Retrospective gold difference; future values never enter the model's past state.",
    accuracy_title: "What we can really predict", exploratory: "8×8 / 4×4 exploratory",
    exact_explain: "<strong>16×16:</strong> Shadow 11.28%, baseline 11.61%. The original gate is not met.",
    coarse_explain: "<strong>8×8 and 4×4:</strong> a broader rotation signal appears, but it was explored after seeing the test. Future games are needed.",
    tempo_title: "A team that heats up and cools down", tempo_interactive: "Explore a time slice",
    tempo_interactive_help: "Share of minutes when the account moves closer to an ally already positioned at time t.", minute: "Minute",
    tempo_explain: "These are geometric approaches, not proof of help or communication. Top changes too: no role has a fixed 20% weight.",
    strategy_title: "What if all five went bot?", hypothesis: "Hypothesis, not result",
    strategy_explain: "In these 465 matches, only one early frame has all five allies within 2,500 units of the bot carry. Proximity does not prove a five-bot strategy. The question requires measuring gains, losses elsewhere, and opponent response.",
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
let trace = null;
let surfaceMode = "actual";
let replayTimer = null;
const $ = (selector) => document.querySelector(selector);
const percent = (count, total) => (100 * count / total).toFixed(2);
const SVG_NS = "http://www.w3.org/2000/svg";

function translate() {
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const value = copy[language][element.dataset.i18n];
    if (value !== undefined) element.innerHTML = value;
  });
  $("#language").textContent = language === "fr" ? "EN" : "FR";
  if (summary) {
    updateTempo();
    updateReadout(7, 7);
    renderSurface();
  }
  if (trace) updateReplay();
}

function updateReadout(col, row) {
  const density = summary.test_map_density;
  const index = row * 16 + col;
  $("#map-readout").textContent = copy[language].map_cell(
    col, row, percent(density.actual[index], density.samples),
    percent(density.predicted[index], density.samples)
  );
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

function svgNode(name, attributes = {}) {
  const node = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
  return node;
}

function renderSurface() {
  const svg = $("#surface-svg");
  svg.replaceChildren();
  const density = summary.test_map_density;
  const maximum = Math.max(...density.actual, ...density.predicted);
  const values = density[surfaceMode];
  const radians = Number($("#angle-slider").value) * Math.PI / 180;
  $("#angle-label").textContent = `${$("#angle-slider").value}°`;
  const project = (x, y, z) => {
    const rx = (x - 8) * Math.cos(radians) - (y - 8) * Math.sin(radians);
    const ry = (x - 8) * Math.sin(radians) + (y - 8) * Math.cos(radians);
    return [320 + rx * 21, 256 + ry * 9 - z];
  };
  const points = (...vertices) => vertices.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const base = [project(0, 0, 0), project(16, 0, 0), project(16, 16, 0), project(0, 16, 0)];
  svg.append(svgNode("polygon", {points: points(...base), fill: "#132c42", stroke: "#3a667b", "stroke-width": 1.5}));
  const cells = [];
  for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) {
    const count = values[y * 16 + x];
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
    trace = await response.json();
    if (!trace.rows?.length || trace.source_step_seconds !== 60) return;
    $("#replay-slider").max = trace.rows.length - 1;
    $("#replay").hidden = false;
    $("#replay-nav").hidden = false;
    updateReplay();
  } catch (_) { /* Per-match trace is local and optional. */ }
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
}

async function start() {
  translate();
  try {
    const response = await fetch("/summary.json", {cache: "no-store"});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    summary = await response.json();
    bindMap($("#actual-map")); bindMap($("#predicted-map"));
    updateReadout(7, 7); updateTempo();
    renderSurface();
  } catch (error) {
    $("#map-readout").textContent = copy[language].load_error;
    console.error(error);
  }
  try {
    const response = await fetch("/demo.gif", {method: "HEAD"});
    if (response.ok) $("#demo").hidden = false;
  } catch (_) { /* Demo is optional and local only. */ }
  await loadReplay();
}

$("#language").addEventListener("click", () => { language = language === "fr" ? "en" : "fr"; translate(); });
$("#minute-slider").addEventListener("input", () => { if (summary) updateTempo(); });
$("#surface-actual").addEventListener("click", () => { surfaceMode = "actual"; if (summary) renderSurface(); });
$("#surface-shadow").addEventListener("click", () => { surfaceMode = "predicted"; if (summary) renderSurface(); });
$("#angle-slider").addEventListener("input", () => { if (summary) renderSurface(); });
$("#replay-slider").addEventListener("input", () => { stopReplay(); if (trace) updateReplay(); });
$("#replay-play").addEventListener("click", () => {
  if (!trace) return;
  if (replayTimer) { stopReplay(); return; }
  if (Number($("#replay-slider").value) >= trace.rows.length - 1) $("#replay-slider").value = 0;
  replayTimer = setInterval(() => {
    const next = Number($("#replay-slider").value) + 1;
    if (next >= trace.rows.length) { stopReplay(); return; }
    $("#replay-slider").value = next; updateReplay();
  }, 750);
  updateReplay();
});
start();
