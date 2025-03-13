# Description: This file contains a sample graph client that makes a stateless request to the Remote Graph Server.
# Usage: python client/stateless_client.py

import json
import logging
import os
import sys
import traceback
import uuid
from typing import Any, Dict, TypedDict

import requests
from langgraph.graph import END, START, StateGraph
from requests.exceptions import (ConnectionError, HTTPError, RequestException,
                                 Timeout)

# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

from app.core.logging_config import configure_logging
from app.core.utils import load_environment_variables

logger = configure_logging()


# configure remote server
port = int(os.getenv("TF_CODE_ANALYZER_PORT", "8123"))
host = os.getenv("TF_CODE_ANALYZER_HOST", "127.0.0.1")
REMOTE_SERVER_URL = f"http://{host}:{port}/api/v1/runs"
logging.info(f"Remote server URL: {REMOTE_SERVER_URL}")


def fetch_github_environment_variables() -> Dict[str, str | None]:
    """
    Fetches the GitHub environment variables from the system.

    Returns:
        Dict[str, str]: A dictionary containing the GitHub environment variables.
    """
    github = {
        "repo_url": os.getenv("GITHUB_REPO_URL"),
        "github_token": os.getenv("GITHUB_TOKEN"),
        "branch": os.getenv("GITHUB_BRANCH"),
    }
    return github


# Define the graph state


class GraphState(TypedDict):
    """Represents the state of the graph, containing the file_path."""

    github: Dict[str, str]
    static_analyzer_output: str


def node_remote_request_stateless(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles a stateless request to the Remote Graph Server.

    Args:
        state (Dict[str, Any]): The current state of the graph.

    Returns:
        Dict[str, Any]: The updated state of the graph after processing the request.
    """
    if "github" not in state or not state["github"]:
        error_msg = "GraphState is missing 'github' key"
        logger.error(json.dumps({"error": error_msg}))
        return {"error": error_msg}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "agent_id": "remote_agent",
        "model": "gpt-4o",
        "metadata": {"id": str(uuid.uuid4())},
        "input": {"github": state["github"]},
    }
    logger.info(f"Sending request to remote server with payload: {payload}")

    # Use a session for efficiency
    with requests.Session() as session:
        try:
            response = session.post(REMOTE_SERVER_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raises HTTPError for 4xx and 5xx

            try:
                # Parse response as JSON
                response_data = response.json()
                # Decode JSON response
                decoded_response = decode_response(response_data)
                logger.info(decoded_response)

                return {
                    "static_analyzer_output": decoded_response.get(
                        "static_analyzer_output", ""
                    )
                }
            except json.JSONDecodeError as json_err:
                error_msg = "Invalid JSON response from server"
                logger.error(
                    json.dumps({"error": error_msg, "exception": str(json_err)})
                )
                return {"error": error_msg}
        except (Timeout, ConnectionError) as conn_err:
            error_msg = "Connection timeout or failure"
            logger.error(json.dumps({"error": error_msg, "exception": str(conn_err)}))
            return {"error": error_msg}

        except HTTPError as http_err:
            error_msg = f"HTTP request failed with status {response.status_code}"
            logger.error(json.dumps({"error": error_msg, "exception": str(http_err)}))
            return {"error": error_msg}

        except RequestException as req_err:
            error_msg = "Request failed"
            logger.error(json.dumps({"error": error_msg, "exception": str(req_err)}))
            return {"error": error_msg}

        except Exception as e:
            error_msg = "Unexpected failure"
            logger.error(
                json.dumps(
                    {
                        "error": error_msg,
                        "exception": str(e),
                        "stack_trace": traceback.format_exc(),
                    }
                )
            )
            return {"error": error_msg}


def decode_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decodes the JSON response from the remote server and extracts relevant information.

    Args:
        response_data (Dict[str, Any]): The JSON response from the server.

    Returns:
        Dict[str, Any]: A structured dictionary containing extracted response fields.
    """
    try:
        agent_id = response_data.get("agent_id", "Unknown")
        output = response_data.get("output", {})
        model = response_data.get("model", "Unknown")
        metadata = response_data.get("metadata", {})

        # Extract messages if present
        static_analyzer_output = output.get("static_analyzer_output", [])

        return {
            "agent_id": agent_id,
            "static_analyzer_output": static_analyzer_output,
            "model": model,
            "metadata": metadata,
        }
    except Exception as e:
        return {"error": f"Failed to decode response: {str(e)}"}


def build_graph() -> Any:
    """
    Constructs the state graph for handling request with the Remote Graph Server.

    Returns:
        StateGraph: A compiled LangGraph state graph.
    """
    builder = StateGraph(GraphState)
    builder.add_node("node_remote_request_stateless", node_remote_request_stateless)
    builder.add_edge(START, "node_remote_request_stateless")
    builder.add_edge("node_remote_request_stateless", END)
    return builder.compile()


def main():
    load_environment_variables()
    graph = build_graph()
    github_details = fetch_github_environment_variables()
    input = {"github": github_details}
    logger.info({"event": "invoking_graph", "input": input})
    result = graph.invoke(input)
    if "output" in result:
        logger.info({"event": "final_result", "result": result["output"]})
    else:
        logger.error({"event": "final_result", "result": result})


if __name__ == "__main__":
    main()
