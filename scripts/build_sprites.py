#!/usr/bin/env python3
"""Build small local sprite atlases for champions and final items in the private index.

The committed atlases contain only Riot Data Dragon static art, never match data.
The version is pinned so a rebuild produces the same art and labels.
"""
import argparse
import io
import json
from pathlib import Path
import sqlite3
import time

from PIL import Image
import requests

from shadowfaker.config import CONFIG
from shadowfaker.game_facts import DB
from shadowfaker.util import atomic_json


VERSION = "16.20.1"
CDN = "https://ddragon.leagueoflegends.com/cdn"
RAW = CONFIG.raw / "ddragon"
ASSETS = CONFIG.root / "dashboard" / "assets"
MANIFEST = CONFIG.root / "docs" / "data" / "sprites.json"


def cached(url: str, path: Path) -> bytes:
    if path.is_file():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=25)
            response.raise_for_status()
            data = response.content
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(path)
            return data
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def build(version: str = VERSION, database: Path = DB) -> dict:
    with sqlite3.connect(database) as db:
        rows = db.execute("SELECT champion,allies_json,enemies_json,items_json FROM games").fetchall()
    champions: set[str] = set()
    items: set[int] = set()
    for champion, allies, enemies, item_ids in rows:
        champions.update([champion, *json.loads(allies), *json.loads(enemies)])
        items.update(json.loads(item_ids))
    # Consumables and trinkets rarely survive into end-of-game inventories,
    # but their timestamped events are prominent in the replay.
    items.update({2003, 2031, 2033, 2055, 3340, 3363, 3364, 2138, 2139, 2140})
    if not rows:
        raise ValueError("Build the local post-game index before the sprite atlas")

    base = f"{CDN}/{version}"
    def data(locale: str, kind: str) -> dict:
        path = RAW / version / f"{locale}_{kind}.json"
        return json.loads(cached(f"{base}/data/{locale}/{kind}.json", path))["data"]

    champ_data = data("en_US", "champion")
    item_en = data("en_US", "item")
    item_fr = data("fr_FR", "item")
    # Cover items that disappear before the final scoreboard (components,
    # potions, wards and trinkets), without publishing any match inventory.
    items.update(int(key) for key, entry in item_en.items()
                 if key.isdigit() and (entry.get("maps") or {}).get("11"))
    by_name = {key.casefold(): value for key, value in champ_data.items()}
    by_name.update({value["name"].casefold(): value for value in champ_data.values()})
    metadata = {"schema_version": 1, "data_dragon_version": version,
                "source": "https://developer.riotgames.com/docs/lol#data-dragon",
                "champions": {}, "items": {}, "unmatched_champions": [], "unmatched_items": []}
    ASSETS.mkdir(parents=True, exist_ok=True)

    for kind, selected, source in (("champions", sorted(champions), champ_data),
                                   ("items", sorted(items), item_en)):
        found = []
        for value in selected:
            entry = by_name.get(value.casefold()) if kind == "champions" else source.get(str(value))
            if entry is None:
                metadata[f"unmatched_{kind}"].append(value)
            else:
                found.append((value, entry))
        atlas = Image.new("RGBA", (16 * 48, ((len(found) + 15) // 16) * 48))
        sheets = {}
        for index, (value, entry) in enumerate(found):
            spec = entry["image"]
            sheet = spec["sprite"]
            if sheet not in sheets:
                path = RAW / version / "sprite" / sheet
                sheets[sheet] = Image.open(io.BytesIO(cached(f"{base}/img/sprite/{sheet}", path))).convert("RGBA")
            icon = sheets[sheet].crop((spec["x"], spec["y"], spec["x"] + spec["w"], spec["y"] + spec["h"]))
            atlas.paste(icon, ((index % 16) * 48, (index // 16) * 48))
            coords = {"x": index % 16, "y": index // 16}
            if kind == "items":
                coords.update({"en": entry["name"],
                               "fr": item_fr.get(str(value), {}).get("name", entry["name"])})
            metadata[kind][str(value)] = coords
        atlas.save(ASSETS / f"{kind}.png", optimize=True)
    atomic_json(MANIFEST, metadata)
    return {"champions": len(metadata["champions"]), "items": len(metadata["items"]),
            "unmatched_champions": metadata["unmatched_champions"],
            "unmatched_items": metadata["unmatched_items"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=VERSION)
    args = parser.parse_args()
    print(build(args.version))


if __name__ == "__main__":
    main()
