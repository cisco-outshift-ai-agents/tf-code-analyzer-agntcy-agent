import os
import pytest
from typing import Dict, Any
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import APISettings, AppSettings
from app.core.github import GithubClient
from app.graph.graph import StaticAnalyzerWorkflow
from github import Github
from fastapi import HTTPException
from http import HTTPStatus

# Configure test environment
TEST_HOST = os.getenv("TF_CODE_ANALYZER_HOST", "127.0.0.1")
TEST_PORT = os.getenv("TF_CODE_ANALYZER_PORT", "8133")
BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}/api/v1"

@pytest.fixture
def test_client():
    """Fixture to provide a FastAPI TestClient with OpenAI settings."""
    settings = APISettings()
    with patch('app.main.load_and_validate_app_settings') as mock_settings:
        app_settings = AppSettings(
            OPENAI_API_KEY="test-key",
            OPENAI_API_VERSION="gpt-4o",
            OPENAI_API_TYPE="openai"
        )
        mock_settings.return_value = app_settings
        app = create_app(settings)
        return TestClient(app)

@pytest.fixture
def mock_github(mocker):
    """Mock GitHub client."""
    mock = mocker.patch('app.core.github.Github')
    mock_instance = mock.return_value
    mock_instance.get_rate_limit.return_value = None  # Mock successful authentication
    return mock_instance

@pytest.fixture
def mock_github_client(mocker):
    """Mock GithubClient authentication and requests."""
    mocker.patch('app.core.github.GithubClient._authenticate', return_value=None)
    mock_response = mocker.Mock()
    mock_response.iter_content.return_value = [b'test data']
    mock_response.raise_for_status.return_value = None
    mock_get = mocker.patch('requests.get')
    mock_get.return_value = mock_response
    return mocker.patch('app.core.github.GithubClient')

@pytest.fixture
def mock_github_client_error(mocker):
    """Mock GithubClient authentication with error."""
    mocker.patch('app.core.github.GithubClient._authenticate', side_effect=HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid GitHub token"
    ))
    return mocker.patch('app.core.github.GithubClient')

@pytest.fixture
def mock_zipfile(mocker):
    """Mock zipfile operations."""
    mock_zip = mocker.Mock()
    mock_zip.namelist.return_value = ['test-repo-main/']
    mock_zip_context = mocker.patch('zipfile.ZipFile')
    mock_zip_context.return_value.__enter__.return_value = mock_zip
    return mock_zip

@pytest.fixture
def test_github_details() -> Dict[str, str]:
    """Fixture to provide test GitHub details."""
    return {
        "repo_url": "https://github.com/test/repo",
        "github_token": "test_token",
        "branch": "main"
    }

@pytest.fixture
def test_payload(test_github_details: Dict[str, str]) -> Dict[str, Any]:
    """Fixture to provide test payload for API requests."""
    return {
        "agent_id": "remote_agent",
        "model": "gpt-4o",
        "metadata": {"id": "test-id"},
        "input": {"github_details": test_github_details}
    }

@pytest.fixture
def test_client_azure():
    """Fixture to provide a FastAPI TestClient with Azure OpenAI settings."""
    settings = APISettings()
    with patch('app.main.load_and_validate_app_settings') as mock_settings:
        app_settings = AppSettings(
            AZURE_OPENAI_API_KEY="test-azure-key",
            AZURE_OPENAI_ENDPOINT="https://test.openai.azure.com/",
            AZURE_OPENAI_DEPLOYMENT_NAME="test-deployment",
            AZURE_OPENAI_API_VERSION="2024-02-15-preview",
            OPENAI_TEMPERATURE=0.7
        )
        mock_settings.return_value = app_settings
        app = create_app(settings)
        return TestClient(app)

@pytest.fixture
def test_client_openai():
    """Fixture to provide a FastAPI TestClient with OpenAI settings."""
    settings = APISettings()
    with patch('app.main.load_and_validate_app_settings') as mock_settings:
        app_settings = AppSettings(
            OPENAI_API_KEY="test-key",
            OPENAI_API_VERSION="gpt-4o",
        )
        mock_settings.return_value = app_settings
        app = create_app(settings)
        return TestClient(app)

def test_root_endpoint(test_client_openai):
    """Test the root endpoint returns the correct welcome message."""
    response = test_client_openai.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Gateway of the App"}

def test_runs_endpoint_invalid_payload(test_client_openai):
    """Test the runs endpoint with invalid payload."""
    response = test_client_openai.post(
        "/api/v1/runs",
        json={"invalid": "payload"}
    )
    assert response.status_code == 422  # FastAPI validation error
    assert response.json()["detail"] == "Invalid input format"

def test_runs_endpoint_invalid_github_details(test_client_openai, mock_github_client_error):
    """Test the runs endpoint with invalid GitHub details."""
    invalid_payload = {
        "agent_id": "remote_agent",
        "model": "gpt-4o",
        "metadata": {"id": "test-id"},
        "input": {
            "github_details": {
                "repo_url": "https://github.com/test/repo",
                "github_token": "invalid_token",
                "branch": "main"
            }
        }
    }

    response = test_client_openai.post(
        "/api/v1/runs",
        json=invalid_payload
    )
    assert response.status_code == 401  # Unauthorized
    assert response.json()["detail"] == "Invalid GitHub token"

@patch('app.core.github.GithubClient.download_repo_zip')
def test_runs_endpoint_github_error(mock_download_repo, test_client_openai, test_payload, mock_github_client):
    """Test the runs endpoint when GitHub operations fail."""
    mock_download_repo.side_effect = Exception("GitHub error")
    
    response = test_client_openai.post(
        "/api/v1/runs",
        json=test_payload
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred. Please try again later."

@patch('app.core.github.GithubClient.download_repo_zip')
@patch('app.graph.graph.StaticAnalyzerWorkflow.analyze')
def test_runs_endpoint_analysis_error(mock_analyze, mock_download_repo, test_client_openai, test_payload, mock_github_client):
    """Test the runs endpoint when analysis fails."""
    mock_download_repo.return_value = "/path/to/repo"
    mock_analyze.side_effect = Exception("Analysis error")
    
    response = test_client_openai.post(
        "/api/v1/runs",
        json=test_payload
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred. Please try again later."

def test_runs_endpoint_missing_github_details(test_client_openai):
    """Test the runs endpoint when GitHub details are missing."""
    invalid_payload = {
        "agent_id": "remote_agent",
        "model": "gpt-4o",
        "metadata": {"id": "test-id"},
        "input": {}  # Missing github_details
    }
    
    response = test_client_openai.post(
        "/api/v1/runs",
        json=invalid_payload
    )
    assert response.status_code == 422
    assert "github details not provided" in response.json()["detail"].lower()

@patch('app.core.github.GithubClient.download_repo_zip')
@patch('app.graph.graph.StaticAnalyzerWorkflow.analyze')
def test_runs_endpoint_azure_configuration(mock_analyze, mock_download_repo, test_client_azure, test_payload, mock_github_client, mock_zipfile):
    """Test the runs endpoint with Azure OpenAI configuration."""
    with patch('app.core.github.GithubClient.download_repo_zip') as mock_download_repo, \
         patch('app.graph.graph.StaticAnalyzerWorkflow.analyze') as mock_analyze:
        
        # Setup mocks
        mock_download_repo.return_value = "/path/to/repo"
        mock_analyze.return_value = {"analysis": "success"}
        
        response = test_client_azure.post(
            "/api/v1/runs",
            json=test_payload
        )
        
        assert response.status_code == 200
        assert response.json()["output"] == {"analysis": "success"}
        assert response.json()["agent_id"] == "remote_agent"
        assert response.json()["model"] == "gpt-4o"

@patch('app.core.github.GithubClient.download_repo_zip')
@patch('app.graph.graph.StaticAnalyzerWorkflow.analyze')
def test_runs_endpoint_openai_configuration(mock_analyze, mock_download_repo, test_client_openai, test_payload, mock_github_client, mock_zipfile):
    """Test the runs endpoint with OpenAI configuration."""
    with patch('app.core.github.GithubClient.download_repo_zip') as mock_download_repo, \
         patch('app.graph.graph.StaticAnalyzerWorkflow.analyze') as mock_analyze:
        
        # Setup mocks
        mock_download_repo.return_value = "/path/to/repo"
        mock_analyze.return_value = {"analysis": "success"}
        
        response = test_client_openai.post(
            "/api/v1/runs",
            json=test_payload
        )
        
        assert response.status_code == 200
        assert response.json()["output"] == {"analysis": "success"}
        assert response.json()["agent_id"] == "remote_agent"
        assert response.json()["model"] == "gpt-4o"

    