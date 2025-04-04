import io
import json
import logging
import pytest

from client.agp.agp_client import build_graph, fetch_github_environment_variables

@pytest.mark.asyncio
async def test_agp_client(github_details):
    """
    Integration test for the AGP client that verifies:
        1. Successful graph execution for a remote AGP node
        2. Correct output from static analyzer
    This test requires:
    - Running AGP gateway
    - Running Static Analyzer agent
    - Valid environment variables for this test
    - Network connectivity to remote services
    """
    try:
        graph = await build_graph()
        input = {"github_details": github_details}
        result = await graph.ainvoke(input)

        assert result is not None, "Graph invocation should return a result"
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "static_analyzer_output" in result, "Result should contain 'static_analyzer_output'"
        assert "Duplicate output definition" in result['static_analyzer_output'], "Expected error message not found in output"     
    except Exception as e:
        pytest.fail(str(e))
