import os
import pytest
import asyncio
from typing import Dict, Any
import json
from unittest.mock import Mock, patch, AsyncMock

from agp_api.gateway.gateway_container import GatewayContainer
from agp_api.agent.agent_container import AgentContainer
from client.agp.agp_client import Config, send_and_recv, init_client_gateway_conn

# Test configuration
TEST_ENDPOINT = "http://127.0.0.1:46357"
TEST_REMOTE_AGENT = "test_server"

@pytest.fixture
def mock_gateway_container():
    """Fixture to provide a mocked gateway container."""
    with patch('client.agp.agp_client.Config.gateway_container') as mock:
        mock.gateway = AsyncMock()
        mock.gateway.receive.return_value = (None, json.dumps({
            "status": "success",
            "data": {"message": "Analysis completed"}
        }).encode('utf8'))
        mock.publish_messsage = AsyncMock()
        mock.connect_with_retry = AsyncMock()
        yield mock

@pytest.fixture
def mock_agent_container():
    """Fixture to provide a mocked agent container."""
    with patch('client.agp.agp_client.Config.agent_container') as mock:
        yield mock

@pytest.fixture
def test_payload() -> Dict[str, Any]:
    """Fixture to provide test payload for gateway messages."""
    return {
        "agent_id": "remote_agent",
        "input": {
            "github_details": {
                "repo_url": "https://github.com/test/repo",
                "github_token": "test_token",
                "branch": "main"
            }
        },
        "route": "/api/v1/runs"
    }

@pytest.mark.asyncio
async def test_init_client_gateway_conn(mock_gateway_container):
    """Test gateway connection initialization."""
    mock_gateway_container.set_config = Mock()
    mock_gateway_container.connect_with_retry.return_value = True
    
    await init_client_gateway_conn(TEST_REMOTE_AGENT)
    
    mock_gateway_container.set_config.assert_called_once_with(
        endpoint=TEST_ENDPOINT,
        insecure=True
    )
    mock_gateway_container.connect_with_retry.assert_called_once_with(
        agent_container=Config.agent_container,
        max_duration=10,
        initial_delay=1,
        remote_agent=TEST_REMOTE_AGENT
    )

@pytest.mark.asyncio
async def test_send_and_recv(mock_gateway_container, test_payload):
    """Test sending and receiving messages through the gateway."""
    mock_gateway_container.publish_messsage.return_value = None
    mock_gateway_container.gateway.receive.return_value = (
        None,
        json.dumps({
            "status": "success",
            "data": {"message": "Analysis completed"}
        }).encode('utf8')
    )
    
    result = await send_and_recv(test_payload, TEST_REMOTE_AGENT)
    
    assert result["status"] == "success"
    assert result["data"]["message"] == "Analysis completed"
    mock_gateway_container.publish_messsage.assert_called_once_with(
        test_payload,
        agent_container=Config.agent_container,
        remote_agent=TEST_REMOTE_AGENT
    )

@pytest.mark.asyncio
async def test_send_and_recv_error_handling(mock_gateway_container, test_payload):
    """Test error handling in send_and_recv."""
    mock_gateway_container.publish_messsage.side_effect = Exception("Connection error")
    
    result = await send_and_recv(test_payload, TEST_REMOTE_AGENT)
    
    assert "error" in result
    assert result["error"] == "Connection error"

@pytest.mark.asyncio
async def test_send_and_recv_invalid_response(mock_gateway_container, test_payload):
    """Test handling of invalid response from gateway."""
    mock_gateway_container.publish_messsage.return_value = None
    mock_gateway_container.gateway.receive.return_value = (
        None,
        b"invalid json"
    )
    
    result = await send_and_recv(test_payload, TEST_REMOTE_AGENT)
    
    assert "error" in result
    assert "Failed to decode response" in result["error"]

@pytest.mark.asyncio
async def test_gateway_connection_timeout(mock_gateway_container):
    """Test gateway connection timeout."""
    mock_gateway_container.set_config = Mock()
    mock_gateway_container.connect_with_retry.side_effect = asyncio.TimeoutError()
    
    with pytest.raises(asyncio.TimeoutError):
        await init_client_gateway_conn(TEST_REMOTE_AGENT)

@pytest.mark.asyncio
async def test_gateway_connection_retry(mock_gateway_container):
    """Test gateway connection retry mechanism."""
    mock_gateway_container.set_config = Mock()
    mock_gateway_container.connect_with_retry = AsyncMock()
    mock_gateway_container.connect_with_retry.side_effect = [
        Exception("First attempt failed"),
        True
    ]
    
    with pytest.raises(Exception) as exc_info:
        await init_client_gateway_conn(TEST_REMOTE_AGENT)
    
    assert str(exc_info.value) == "First attempt failed"
    assert mock_gateway_container.connect_with_retry.call_count == 1 