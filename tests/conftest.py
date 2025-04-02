import os
import pytest
from typing import Dict, Any

# Test environment configuration
os.environ["TF_CODE_ANALYZER_HOST"] = "127.0.0.1"
os.environ["TF_CODE_ANALYZER_PORT"] = "8133"
os.environ["GITHUB_REPO_URL"] = "https://github.com/test/repo"
os.environ["GITHUB_TOKEN"] = "test_token"
os.environ["GITHUB_BRANCH"] = "main"

@pytest.fixture(scope="session")
def test_environment() -> Dict[str, str]:
    """Fixture to provide test environment variables."""
    return {
        "TF_CODE_ANALYZER_HOST": os.getenv("TF_CODE_ANALYZER_HOST", "127.0.0.1"),
        "TF_CODE_ANALYZER_PORT": os.getenv("TF_CODE_ANALYZER_PORT", "8133"),
        "GITHUB_REPO_URL": os.getenv("GITHUB_REPO_URL", "https://github.com/test/repo"),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "test_token"),
        "GITHUB_BRANCH": os.getenv("GITHUB_BRANCH", "main")
    }

@pytest.fixture(scope="session")
def base_url(test_environment: Dict[str, str]) -> str:
    """Fixture to provide the base URL for API requests."""
    return f"http://{test_environment['TF_CODE_ANALYZER_HOST']}:{test_environment['TF_CODE_ANALYZER_PORT']}/api/v1"

@pytest.fixture(scope="session")
def github_details(test_environment: Dict[str, str]) -> Dict[str, str]:
    """Fixture to provide GitHub details for testing."""
    return {
        "repo_url": test_environment["GITHUB_REPO_URL"],
        "github_token": test_environment["GITHUB_TOKEN"],
        "branch": test_environment["GITHUB_BRANCH"]
    }

@pytest.fixture(scope="session")
def api_headers() -> Dict[str, str]:
    """Fixture to provide common API headers."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    } 