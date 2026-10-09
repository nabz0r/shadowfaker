from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Config:
    root: Path = ROOT
    raw: Path = ROOT / "data" / "raw"
    processed: Path = ROOT / "data" / "processed"
    models: Path = ROOT / "models"
    runs: Path = ROOT / "runs"
    artifacts: Path = ROOT / "artifacts"
    game_name: str = os.getenv("RIOT_GAME_NAME", "hide on bush")
    tag_line: str = os.getenv("RIOT_TAG_LINE", "KR1")
    seed: int = 42
    window: int = 8
    grid: int = 16
    schema_version: int = 2

    def make_dirs(self) -> None:
        for path in (self.raw, self.processed, self.models, self.runs, self.artifacts):
            path.mkdir(parents=True, exist_ok=True)


CONFIG = Config()
