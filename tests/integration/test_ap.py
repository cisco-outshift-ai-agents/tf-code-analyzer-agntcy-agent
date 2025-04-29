import logging
import pytest

from client.ap.stateless_client import build_graph


def test_ap_client(github_details):
    """
    Integration test for the AP client that verifies:
        1. Successful graph execution for a local AP node
        2. Correct output from static analyzer
    This test requires:
    - Running Static Analyzer agent
    - Valid environment variables for this test
    """
    logger = logging.getLogger()

    graph = build_graph()
    github_input = {"github_details": github_details}
    result = graph.invoke(github_input)

    assert result is not None, "Graph invocation should return a result"
    assert isinstance(result, dict), "Result should be a dictionary"
    assert (
        "static_analyzer_output" in result
    ), "Result should contain 'static_analyzer_output'"
    assert (
        "Duplicate output definition" in result["static_analyzer_output"]
    ), "Expected error message not found in output"
