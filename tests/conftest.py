import os
import pytest
from typing import Dict

from dotenv import load_dotenv

def pytest_configure(config):
    """Called before test collection, configure global test environment."""
    load_dotenv()  # Load environment variables once for all tests

@pytest.fixture(scope="session")
def test_environment() -> Dict[str, str]:
    """Fixture to provide test environment variables."""
    return {
        "TF_CODE_ANALYZER_HOST": os.getenv("TF_CODE_ANALYZER_HOST", "127.0.0.1"),
        "TF_CODE_ANALYZER_PORT": os.getenv("TF_CODE_ANALYZER_PORT", "8133"),
        "GH_REPO_URL": os.getenv("GH_REPO_URL", "https://github.com/test/repo"),
        "GH_TOKEN": os.getenv("GH_TOKEN", "test_token"),
        "GH_BRANCH": os.getenv("GH_BRANCH", "main"),
        'AGP_GATEWAY_ENDPOINT': os.getenv("AGP_GATEWAY_ENDPOINT", "http://127.0.0.1:46357")
    }

@pytest.fixture(scope="session")
def base_url(test_environment: Dict[str, str]) -> str:
    """Fixture to provide the base URL for API requests."""
    return f"http://{test_environment['TF_CODE_ANALYZER_HOST']}:{test_environment['TF_CODE_ANALYZER_PORT']}/api/v1"

@pytest.fixture(scope="session")
def github_details(test_environment: Dict[str, str]) -> Dict[str, str]:
    """Fixture to provide GitHub details for testing."""
    return {
        "repo_url": test_environment["GH_REPO_URL"],
        "github_token": test_environment["GH_TOKEN"],
        "branch": test_environment["GH_BRANCH"]
    }

@pytest.fixture(scope="session")
def api_headers() -> Dict[str, str]:
    """Fixture to provide common API headers."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    } 