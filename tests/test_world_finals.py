"""The public professional catalogue stays internally consistent and isolated."""
import json
from pathlib import Path

from shadowfaker.text_index import import_world_finals, search


ROOT = Path(__file__).resolve().parents[1]


def test_world_finals_series_and_sources():
    data = json.loads((ROOT / "docs/data/world_finals.json").read_text())
    assert [f["year"] for f in data["finals"]] == [2013, 2015, 2016, 2023, 2024, 2025]
    assert sum(len(f["games"]) for f in data["finals"]) == 25
    assert len(data["extra_games"]) == 3
    for final in data["finals"]:
        assert final["score"] == f"3–{sum(g['result'] == 'L' for g in final['games'])}"
        assert sum(g["result"] == "W" for g in final["games"]) == 3
        assert final["source"].startswith("https://gol.gg/game/stats/")
        for number, game in enumerate(final["games"], 1):
            assert game["number"] == number
            assert game["source"].startswith("https://gol.gg/game/stats/")
            assert len(game["duration"].split(":")) == 2


def test_world_finals_index_idempotent_and_searchable(tmp_path):
    index = tmp_path / "worlds.sqlite"
    first = import_world_finals(index)
    second = import_world_finals(index)
    assert first["indexed_documents"] == second["indexed_documents"] == 56
    hits = search("KT Rolster", "en", index=index)
    assert hits and all(hit["source_kind"] == "professional_public_summary" for hit in hits)
