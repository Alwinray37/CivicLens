from dataclasses import dataclass
from pathlib import Path

@dataclass
class PipelineConfig:
    meeting_year: int = 2026
    council_meetings_id: int = 1
    api_timeout: int = 30
    output_dir: Path = Path("output")
    temp_dir: Path = Path(".temp")