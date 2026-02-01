import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env.test"
load_dotenv(env_path, override=True)
