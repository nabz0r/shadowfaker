#!/usr/bin/env python3
"""Serve the aggregate-only dashboard and optional local GIF, never raw Riot files."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit, parse_qs

from shadowfaker.text_index import search
from shadowfaker.demo import export_trace
from shadowfaker.state_matrix import DB
from shadowfaker.util import read_json
from shadowfaker.config import CONFIG

ROOT = Path(__file__).resolve().parents[1]
FIGURES = frozenset({"faker_vs_shadow_minimap.png", "benchmark_scales.png",
                     "team_tempo.png", "role_approach_by_phase.png", "team_clustering.png",
                     "actual_minimap.png", "predicted_minimap.png",
                     "probability_surface_3d.png", "readme_hero_en.svg", "readme_hero_fr.svg"})
FIGURES = FIGURES | frozenset({"grid64_observed_vs_predicted.png", "event_atlas64.png",
                               "enemy_pressure.png", "challenge_scenarios.png",
                               "predictability_gap.png", "hierarchical_ablation.png",
                               "atlas512_validation.png", "atlas512_events.png"})
ROUTES = {"/": ROOT / "dashboard" / "index.html",
          "/app.js": ROOT / "dashboard" / "app.js",
          "/style.css": ROOT / "dashboard" / "style.css",
          "/summary.json": ROOT / "docs" / "data" / "public_summary.json",
          "/grid64.json": ROOT / "docs" / "data" / "public_grid64.json",
          "/events64.json": ROOT / "docs" / "data" / "public_events64.json",
          "/challenge.json": ROOT / "docs" / "data" / "challenge_scenarios.json",
          "/pressure.json": ROOT / "docs" / "data" / "public_pressure.json",
          "/predictability.json": ROOT / "docs" / "data" / "public_predictability.json",
          "/atlas512.json": ROOT / "artifacts" / "grid512" / "atlas.json",
          "/grid512.json": ROOT / "docs" / "data" / "public_grid512.json",
          "/replay.json": ROOT / "artifacts" / "replay_trace.json",
          "/demo.gif": ROOT / "artifacts" / "predicted_vs_actual.gif"}


class DashboardHandler(BaseHTTPRequestHandler):
    def _file(self) -> Path | None:
        route = urlsplit(self.path).path
        if route.startswith("/figures/"):
            filename = route.removeprefix("/figures/")
            return ROOT / "docs" / "figures" / filename if filename in FIGURES else None
        if route.startswith("/replay-frames/"):
            filename = route.removeprefix("/replay-frames/")
            return ROOT / "artifacts" / "replay_frames" / filename if re.fullmatch(r"(?:KR_\d+/)?\d\d\.png", filename) else None
        return ROUTES.get(route)

    def _serve(self, head: bool = False) -> None:
        path = self._file()
        if path is None or not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if not head:
            self.wfile.write(data)

    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/api/games":
            with sqlite3.connect(DB) as database:
                rows = database.execute("SELECT match_id,champion_id,state_count FROM matches ORDER BY match_id").fetchall()
            self._json([{"match_id": mid,"champion_id": champ,"states": states} for mid,champ,states in rows])
            return
        if urlsplit(self.path).path == "/api/replay":
            mid = (parse_qs(urlsplit(self.path).query).get("match") or [""])[0]
            meta = read_json(CONFIG.processed / "meta.json") or {}
            if not re.fullmatch(r"KR_\d+",mid) or mid not in meta.get("counts",{}):
                self.send_error(404,"Unknown indexed ranked match")
                return
            try:
                path = export_trace(match_id=mid,max_frames=80,allow_any=True)
                self._json(json.loads(path.read_text()))
            except Exception as exc:
                self.send_error(500,str(exc))
            return
        if urlsplit(self.path).path == "/api/search":
            params = parse_qs(urlsplit(self.path).query)
            query = (params.get("q") or [""])[0][:120]
            language = (params.get("language") or [""])[0][:10] or None
            self._json(search(query, language, 10))
            return
        self._serve()

    def _json(self, payload) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_HEAD(self) -> None:
        self._serve(head=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="Localhost by default; do not expose private demo media")
    parser.add_argument("--port", type=int, default=8008)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Shadow Faker dashboard: http://{args.host}:{args.port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
