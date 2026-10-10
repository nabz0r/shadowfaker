"""Checkpointed one-command expansion: Riot aliases, pro catalog and 10s events."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import logging
from pathlib import Path
import time

import requests
from tqdm import tqdm

from shadowfaker.config import CONFIG
from shadowfaker.fetch import fetch
from shadowfaker.alias_fetch import audit
from shadowfaker.event_clock import build as build_events, build_alias
from shadowfaker.event_model import run as train_events
from shadowfaker.pro_catalog import import_csv
from render_expansion import build as render

LOG = logging.getLogger("expansion")
MIRROR = "https://raw.githubusercontent.com/twodotone/finalLOL/main/data/csv/"


def mirror_csv(year: int) -> Path:
    path = CONFIG.raw / "pro" / f"oracle_mirror_{year}.csv"
    if path.exists() and path.stat().st_size > 1_000_000:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    url = MIRROR + f"{year}_LoL_esports_match_data_from_OraclesElixir.csv"
    pending = path.with_suffix(".csv.part")
    for attempt in range(5):
        try:
            with requests.get(url, stream=True, timeout=(8,60)) as response:
                response.raise_for_status()
                with pending.open("wb") as stream:
                    for block in response.iter_content(1024*1024):
                        if block:
                            stream.write(block)
            if pending.stat().st_size < 1_000_000:
                raise ValueError(f"Suspiciously short CSV from {url}")
            pending.replace(path)
            return path
        except (requests.RequestException,ValueError) as exc:
            LOG.warning("Mirror %s attempt %s/5 failed: %s",year,attempt+1,exc)
            if attempt == 4:
                raise
            time.sleep(min(30,2**attempt))
    raise RuntimeError("unreachable")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", default=datetime.now(timezone.utc).strftime("%Y%m%d"))
    p.add_argument("--skip-pro", action="store_true", help="Use an existing pro catalog; do not download mirror CSVs")
    a = p.parse_args()
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
    steps = ["Riot KR refresh", "EUW/NA alias pilot", "EUW/NA alias full",
             "10s KR pilot", "10s KR full", "10s EUW pilot", "10s EUW full",
             "Pro catalog", "Event model pilot", "KR model", "KR+EUW model", "Public aggregate figure"]
    with tqdm(total=len(steps),desc="Shadow Faker expansion",unit="phase") as progress:
        def step(name, function):
            progress.set_postfix_str(name)
            LOG.info("Starting %s",name)
            result=function()
            LOG.info("Finished %s",name)
            progress.update()
            return result
        step(steps[0],lambda: fetch(1000,id_snapshot=a.snapshot+"_ranked"))
        step(steps[1],lambda: audit(a.snapshot+"_aliases",pilot=5))
        step(steps[2],lambda: audit(a.snapshot+"_aliases"))
        step(steps[3],lambda: build_events(limit=5))
        step(steps[4],build_events)
        step(steps[5],lambda: build_alias(limit=5))
        step(steps[6],build_alias)
        if a.skip_pro:
            if not (CONFIG.processed/"pro_catalog.meta.json").exists():
                raise FileNotFoundError("--skip-pro needs an existing local pro catalog")
            step(steps[7],lambda: None)
        else:
            def pro():
                paths=[mirror_csv(year) for year in range(2022,2027)]
                import_csv(paths[:1],CONFIG.processed/"pro_catalog_pilot.sqlite",limit=5)
                return import_csv(paths)
            step(steps[7],pro)
        step(steps[8],lambda: train_events(pilot=True,epochs=4))
        step(steps[9],train_events)
        step(steps[10],lambda: train_events(with_euw=True))
        step(steps[11],render)


if __name__ == "__main__":
    main()
