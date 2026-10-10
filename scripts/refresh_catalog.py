#!/usr/bin/env python3
"""One command: rebuild private game cards/search and public aggregate inventory."""
import json

from shadowfaker.config import CONFIG
from shadowfaker.game_facts import build as build_facts
from shadowfaker.text_index import generate as generate_text, import_world_finals

from build_world_finals import build as build_finals
from build_corpus_inventory import build as build_inventory
from build_sprites import build as build_sprites


def main() -> None:
    meta = json.loads((CONFIG.processed / "meta.json").read_text())
    ids = sorted(meta["counts"])
    puuid = json.loads((CONFIG.raw / "resolved_account.json").read_text())["puuid"]
    raw = CONFIG.raw / "matches"
    pilot = build_facts(ids[:5], puuid, raw)
    if pilot["errors"] or pilot["total"] < 5:
        raise RuntimeError(f"Five-game post-game index pilot failed: {pilot['errors']}")
    print("Five-game facts pilot passed.", flush=True)
    full = build_facts(ids, puuid, raw)
    print(f"Post-game facts: {full['total']} indexed, {len(full['errors'])} errors.", flush=True)
    sprites = build_sprites()
    print(f"Sprite atlas: {sprites['champions']} champions, {sprites['items']} items.", flush=True)
    preview = generate_text(limit=5)
    if preview["errors"]:
        raise RuntimeError(f"Five-game text pilot failed: {preview['errors']}")
    full_text = generate_text()
    print(f"Ranked text: {full_text['generated_documents']} documents, {len(full_text['errors'])} errors.", flush=True)
    build_finals()
    finals = import_world_finals()
    print(f"Finals text: {finals['indexed_documents']} documents.", flush=True)
    inventory = build_inventory()
    print(f"Public inventory: {inventory['warehouse']['events']} events, "
          f"{inventory['warehouse']['events_with_coordinates']} positioned.", flush=True)


if __name__ == "__main__":
    main()
