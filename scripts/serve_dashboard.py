#!/usr/bin/env python3
"""Serve the aggregate-only dashboard and optional local GIF, never raw Riot files."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIGURES = frozenset({"faker_vs_shadow_minimap.png", "benchmark_scales.png",
                     "team_tempo.png", "role_approach_by_phase.png", "team_clustering.png",
                     "actual_minimap.png", "predicted_minimap.png",
                     "probability_surface_3d.png", "readme_hero_en.svg", "readme_hero_fr.svg"})
ROUTES = {"/": ROOT / "dashboard" / "index.html",
          "/app.js": ROOT / "dashboard" / "app.js",
          "/style.css": ROOT / "dashboard" / "style.css",
          "/summary.json": ROOT / "docs" / "data" / "public_summary.json",
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
            return ROOT / "artifacts" / "replay_frames" / filename if len(filename) == 6 and filename[:2].isdigit() and filename[2:] == ".png" else None
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
        self._serve()

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
