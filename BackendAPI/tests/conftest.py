import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    env_path = Path(__file__).parent.parent / ".env.test"
    load_dotenv(env_path)

    yield