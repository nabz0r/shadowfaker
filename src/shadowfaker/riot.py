"""Riot client with conservative persistent pacing and atomic response cache."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import time
from urllib.parse import quote

import requests

from .config import CONFIG
from .util import atomic_json


class RiotError(RuntimeError):
    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(message)


class RiotClient:
    BASE = "https://asia.api.riotgames.com"

    def __init__(self, key: str | None = None, raw: Path | None = None, spacing: float = 1.3):
        self.key = key or os.getenv("RIOT_API_KEY", "")
        if not self.key:
            raise RiotError(0, f"RIOT_API_KEY absent. Add it to {CONFIG.root / '.env'} and rerun.")
        self.raw = raw or CONFIG.raw
        self.raw.mkdir(parents=True, exist_ok=True)
        self.spacing = spacing
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": self.key, "User-Agent": "shadowfaker-personal-research/0.1"})

    def _pace(self) -> None:
        """One request per 1.3 s, shared by processes via a locked timestamp file."""
        path = self.raw / ".rate_limit"
        with path.open("a+") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            stream.seek(0)
            try:
                last = float(stream.read().strip() or "0")
            except ValueError:
                last = 0
            delay = max(0.0, last + self.spacing - time.time())
            if delay:
                time.sleep(delay)
            now = time.time()
            stream.seek(0)
            stream.truncate()
            stream.write(str(now))
            stream.flush()
            os.fsync(stream.fileno())
            fcntl.flock(stream, fcntl.LOCK_UN)

    def get(self, path: str, cache: Path, params: dict | None = None, missing_ok: bool = False):
        if cache.exists():
            return json.loads(cache.read_text())
        for attempt in range(7):
            self._pace()
            try:
                response = self.session.get(self.BASE + path, params=params, timeout=(8, 30))
            except requests.RequestException as exc:
                if attempt == 6:
                    raise RiotError(0, f"Network failure after retries: {exc}") from exc
                time.sleep(min(30, 2**attempt + random.random()))
                continue
            if response.status_code == 200:
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise RiotError(200, "Riot returned malformed JSON") from exc
                atomic_json(cache, payload)
                return payload
            if response.status_code in (401, 403):
                raise RiotError(response.status_code, "Riot key invalid, expired or unauthorized. Refresh RIOT_API_KEY in .env, then rerun.")
            if response.status_code == 404:
                if missing_ok:
                    return None
                raise RiotError(404, f"Riot resource not found: {path}")
            if response.status_code == 429:
                try:
                    wait = float(response.headers.get("Retry-After", "5"))
                except ValueError:
                    wait = 5.0
                time.sleep(max(wait, 1.0) + 0.25)
                continue
            if response.status_code in (500, 502, 503, 504):
                if attempt < 6:
                    time.sleep(min(60, 2**attempt + random.random()))
                    continue
            raise RiotError(response.status_code, f"Riot HTTP {response.status_code} for {path}")
        raise RiotError(429, "Riot rate limit persisted after retries; rerun later from cache.")

    def account(self, game_name: str, tag_line: str):
        name, tag = quote(game_name, safe=""), quote(tag_line, safe="")
        return self.get(f"/riot/account/v1/accounts/by-riot-id/{name}/{tag}", self.raw / "account" / f"{name}_{tag}.json", missing_ok=True)

    def ids(self, puuid: str, start: int, count: int = 100):
        identity = hashlib.sha256(puuid.encode()).hexdigest()[:16]
        return self.get(f"/lol/match/v5/matches/by-puuid/{quote(puuid, safe='')}/ids", self.raw / "ids" / identity / f"{start}_{count}.json", params={"queue": 420, "start": start, "count": count})

    def match(self, match_id: str):
        return self.get(f"/lol/match/v5/matches/{quote(match_id, safe='')}", self.raw / "matches" / f"{match_id}.json", missing_ok=True)

    def timeline(self, match_id: str):
        return self.get(f"/lol/match/v5/matches/{quote(match_id, safe='')}/timeline", self.raw / "timelines" / f"{match_id}.json", missing_ok=True)
