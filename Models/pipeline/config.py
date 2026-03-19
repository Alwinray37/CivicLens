import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PipelineConfig:
    meeting_year: int = 2026
    council_meetings_id: int = 1
    api_timeout: int = 30
    compute_type: str = "float16"
    batch_size: str = "16"
    enable_cleanup: bool = True
    pyannote_token: str = os.getenv("PYANNOTE_TOKEN")
    output_dir: Path = Path("output")
    temp_dir: Path = Path(".temp")

    def __post_init__(self):
        """Create directories if they don't exist."""
        self.output_dir = Path(self.output_dir).resolve()
        self.temp_dir = Path(self.temp_dir).resolve()
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)