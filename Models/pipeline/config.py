import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


def load_config(config_path: Optional[str] = None) -> "PipelineConfig":
    """
    Load PipelineConfig from a YAML file.

    Searches for config.yaml in the current working directory if no path is given.
    Missing fields fall back to PipelineConfig defaults.
    """
    search_path = Path(config_path) if config_path else Path("config.yaml")

    if not search_path.exists():
        if config_path:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        # No config.yaml in CWD — use all defaults
        return PipelineConfig()

    with search_path.open("r") as f:
        data = yaml.safe_load(f) or {}

    return PipelineConfig(
        output_dir=Path(data.get("output_dir", "output")),
        temp_dir=Path(data.get("temp_dir", ".temp")),
        meeting_year=int(data.get("meeting_year", 2026)),
    )


@dataclass
class PipelineConfig:
    meeting_year: int = 2026
    council_meetings_id: int = 1
    api_timeout: int = 30
    compute_type: str = "float16"
    batch_size: str = "16"
    enable_cleanup: bool = True
    pyannote_token: str = field(default_factory=lambda: os.getenv("PYANNOTE_TOKEN", ""))
    output_dir: Path = field(default_factory=lambda: Path("output"))
    temp_dir: Path = field(default_factory=lambda: Path(".temp"))
    target_date: Optional[str] = None  # YYYY-MM-DD; None means use latest

    def __post_init__(self):
        """Create directories if they don't exist."""
        self.output_dir = Path(self.output_dir).resolve()
        self.temp_dir = Path(self.temp_dir).resolve()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
