"""Fetch historically attributed alternate accounts into isolated domains."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from .config import CONFIG
from .fetch import duration_seconds
from .riot import RiotClient, RiotError
from .util import atomic_json, read_json

ALIASES = (
    ("Hide on bush", "61151", "europe", "EUW1", "2024 EUW Worlds bootcamp",
     "https://www.sheepesports.com/de/all/articles/lol-2024-worlds-players-accounts-on-euw-server/en"),
    ("silent silence", "08022", "europe", "EUW1", "community attributed, historical",
     "https://www.leagueofgraphs.com/fr/summoner/euw/Hide%2Bon%2Bbush-61151"),
    ("wincg", "84926", "europe", "EUW1", "community attributed, historical",
     "https://www.leagueofgraphs.com/fr/summoner/euw/Hide%2Bon%2Bbush-61151"),
    ("Neo Hide on bush", "NA1", "americas", "NA1", "community attributed, historical",
     "https://www.leagueofgraphs.com/fr/summoner/euw/Hide%2Bon%2Bbush-61151"),
)


def audit(snapshot: str, pilot: int | None = None, raw: Path = CONFIG.raw) -> dict:
    main = read_json(raw / "manifest.json")
    if not main:
        raise FileNotFoundError("Main account manifest missing")
    output = raw / "aliases" / "manifest.json"
    report = read_json(output, {"schema_version": 1, "accounts": {}, "games": {}})
    report["snapshot"] = snapshot
    for name, tag, route, prefix, claim, source_url in ALIASES:
        client = RiotClient(raw=raw, routing=route)
        alias = f"{name}#{tag}"
        account = client.account(name, tag)
        if not account:
            report["accounts"][alias] = {"status": "not_found", "claim": claim, "source_url": source_url}
            atomic_json(output, report)
            continue
        puuid = account["puuid"]
        if puuid == main["account"]["puuid"]:
            report["accounts"][alias] = {"status": "same_puuid_main", "claim": claim, "source_url": source_url}
            atomic_json(output, report)
            continue
        ids, seen = [], set()
        for start in range(0, 5000, 100):
            page = client.ids(puuid, start, 100, snapshot=snapshot, queue=420)
            for mid in page:
                if mid not in seen:
                    ids.append(mid)
                    seen.add(mid)
            if len(page) < 100:
                break
        report["accounts"][alias] = {"status": "resolved_by_riot", "claim": claim,
                                      "source_url": source_url, "route": route,
                                      "puuid": puuid,
                                      "ranked_ids": len(ids), "identity": "historical_attribution_not_player_proof"}
        selected = ids[:pilot] if pilot is not None else ids
        for mid in tqdm(selected, desc=f"{alias} ranked", unit="game"):
            if report["games"].get(mid, {}).get("status") == "ok":
                continue
            try:
                m = None
                if not mid.startswith(prefix+"_"):
                    status = "wrong_region"
                else:
                    m = client.match(mid)
                    info = (m or {}).get("info") or {}
                    members = info.get("participants") or []
                    if not m:
                        status = "missing_match"
                    elif info.get("queueId") != 420 or not any(p.get("puuid") == puuid for p in members):
                        status = "wrong_queue_or_account"
                    elif duration_seconds(info) < 300:
                        status = "remake"
                    else:
                        timeline = client.timeline(mid)
                        status = "ok" if timeline and len((timeline.get("info") or {}).get("frames") or []) >= 2 else "no_timeline"
                row = {"status": status, "alias": alias, "domain": "attributed_euw_soloq" if route == "europe" else "attributed_na_soloq"}
                if m:
                    row["game_date_utc"] = datetime.fromtimestamp(info.get("gameCreation", 0)/1000, timezone.utc).date().isoformat()
                report["games"][mid] = row
            except RiotError as exc:
                if exc.status in (401, 403, 429):
                    atomic_json(output, report)
                    raise
                report["games"][mid] = {"status": "error", "alias": alias, "reason": str(exc)}
            atomic_json(output, report)
    report["summary"] = {"accounts_resolved": sum(v["status"] == "resolved_by_riot" for v in report["accounts"].values()),
                         "ranked_ids": sum(v.get("ranked_ids", 0) for v in report["accounts"].values()),
                         "games_by_status": dict(Counter(v["status"] for v in report["games"].values())),
                         "pilot": pilot is not None}
    atomic_json(output, report)
    return report["summary"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", required=True)
    p.add_argument("--pilot", type=int)
    a = p.parse_args()
    print(audit(a.snapshot, a.pilot))


if __name__ == "__main__":
    main()
