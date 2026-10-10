#!/usr/bin/env python3
"""Build a small, sourced public index of Faker's winning Worlds finals.

These are manually checked match facts, not Riot timelines or training labels.
Run after verifying the linked series pages if adding new records.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "data" / "world_finals.json"

# Outcomes are in T1/SKT order. Durations and series pages were checked against
# Games of Legends on 2026-10-10; 2025 title count is corroborated by T1 co-owner.
SERIES = [
    (2013, "SK Telecom T1", "Royal Club", "2013-10-04", 383,
     "WWW", ["30:07", "38:21", "20:41"], "Worlds 2013", "First world title"),
    (2015, "SK Telecom T1", "KOO Tigers", "2015-10-31", 2257,
     "WWLW", ["42:41", "38:15", "37:50", "34:34"], "Worlds 2015", "Faker's Ryze closes game 4"),
    (2016, "SK Telecom T1", "Samsung Galaxy", "2016-10-30", 4701,
     "WWLLW", ["54:41", "31:26", "71:20", "46:01", "49:11"], "Worlds 2016", "Five games; game 3 lasts 71 minutes"),
    (2023, "T1", "Weibo Gaming", "2023-11-19", 53622,
     "WWW", ["30:31", "29:57", "25:47"], "Worlds 2023", "Return to the title after seven years"),
    (2024, "T1", "Bilibili Gaming", "2024-11-02", 62816,
     "LWLWW", ["27:09", "27:25", "27:35", "31:42", "32:13"], "Worlds 2024", "Five-game final; Faker's Galio in game 5"),
    (2025, "T1", "KT Rolster", "2025-11-09", 72980,
     "WLLWW", ["36:10", "42:32", "36:52", "29:40", "36:47"], "Worlds 2025", "Sixth title; five-game Telecom War"),
]

EXTRA_GAMES = [
    {"id": "2016-rox-sf-g4", "year": 2016, "label": "ROX Tigers · semifinal G4", "result": "W",
     "duration": "42:57", "focus": "Bengi's Nidalee and a series rescue at 1–2",
     "source": "https://gol.gg/game/stats/4696/page-game/", "domain": "professional_public_summary"},
    {"id": "2017-rng-sf-g5", "year": 2017, "label": "Royal Never Give Up · semifinal G5", "result": "W",
     "duration": "41:03", "focus": "Faker's Galio in the deciding game of a five-game semifinal",
     "source": "https://gol.gg/game/stats/9070/page-game/", "domain": "professional_public_summary"},
    {"id": "2023-jdg-sf-g3", "year": 2023, "label": "JD Gaming · semifinal G3", "result": "W",
     "duration": None, "focus": "Faker on Azir; inspect the VOD before annotating the decisive engage",
     "source": "https://gol.gg/game/stats/53620/page-fullstats/", "domain": "professional_public_summary"},
]

NOTES_FR = {
    2013: "Premier titre mondial",
    2015: "Le Ryze de Faker conclut la manche 4",
    2016: "Cinq manches ; la troisième dure 71 minutes",
    2023: "Retour au sommet après sept ans",
    2024: "Cinq manches ; Faker joue Galio dans la dernière",
    2025: "Sixième titre ; Telecom War en cinq manches",
}
FOCUS_FR = {
    "2016-rox-sf-g4": "La Nidalee de Bengi permet de revenir à 2–2 dans la série",
    "2017-rng-sf-g5": "Le Galio de Faker dans la manche décisive d'une demi-finale en cinq actes",
    "2023-jdg-sf-g3": "Faker joue Azir ; annoter l'engagement décisif seulement après examen de la VOD",
}


def build():
    finals = []
    for year, team, opponent, date, base_id, outcomes, durations, tournament, note in SERIES:
        assert len(outcomes) == len(durations) and outcomes.count("W") == 3
        games = [{"number": i + 1, "result": result, "duration": duration,
                  "source": f"https://gol.gg/game/stats/{base_id+i}/page-game/"}
                 for i, (result, duration) in enumerate(zip(outcomes, durations))]
        finals.append({"year": year, "team": team, "opponent": opponent, "date": date,
                       "tournament": tournament, "score": f"3–{outcomes.count('L')}",
                       "note": note, "note_fr": NOTES_FR[year], "games": games,
                       "source": f"https://gol.gg/game/stats/{base_id}/page-summary/",
                       "domain": "professional_public_summary"})
    for game in EXTRA_GAMES:
        game["focus_fr"] = FOCUS_FR[game["id"]]
    payload = {"schema_version": 1, "status": "curated_public_match_facts",
               "verified_on": "2026-10-10", "finals": finals, "extra_games": EXTRA_GAMES,
               "title_source": "https://comcastspectacor.com/news/2025/12/t1-entertainment-sports-wins-2025-league-of-legends-world-championship/",
               "method": "Series result, T1 game result and duration transcribed from linked public match pages. No licensed VOD or timeline copied; no Faker click, POV, causal annotation, training label or Riot match ID is inferred."}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(finals)} finals, {sum(len(f['games']) for f in finals)} final games, {len(EXTRA_GAMES)} extra games -> {OUT}")


if __name__ == "__main__":
    build()
