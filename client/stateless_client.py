# Description: This file contains a sample graph client that makes a stateless request to the Remote Graph Server.
# Usage: python client/stateless_client.py

import os
import traceback

from dotenv import load_dotenv, find_dotenv
from fastapi import requests
import json
from langgraph.graph import END, START, StateGraph
import logging
import requests
from requests.exceptions import RequestException, Timeout, HTTPError, ConnectionError
from typing import Dict, TypedDict, Any

from app.core.logging_config import configure_logging
from app.core.utils import *

logger = configure_logging()
logger = logging.getLogger(__name__)

load_environment_variables()

# configure remote server
port = int(os.getenv("PORT", "8123"))
host = os.getenv("HOST", "127.0.0.1")
REMOTE_SERVER_URL = f"http://{host}:{port}/api/v1/runs"
logging.info(f"Remote server URL: {REMOTE_SERVER_URL}")

# Define the graph state
class GraphState(TypedDict):
    """Represents the state of the graph, containing the file_path."""
    file_path: str
    output: Dict[str, str]


def node_remote_request_stateless(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles a stateless request to the Remote Graph Server.
    
    Args:
        state (Dict[str, Any]): The current state of the graph.
    
    Returns:
        Dict[str, Any]: The updated state of the graph after processing the request.
    """
    if "file_path" not in state or not state["file_path"]:
        error_msg = "GraphState is missing file_path"
        logger.error(json.dumps({"error": error_msg}))
        return {"error": error_msg}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "input": {"file_path": state["file_path"]}
    }
    logger.info(f"Sending request to remote server with payload: {payload}")

    # Use a session for efficiency
    with requests.Session() as session:
        try:
            response = session.post(REMOTE_SERVER_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raises HTTPError for 4xx and 5xx

            try:
                response_data = response.json()  # Validate JSON response
            except json.JSONDecodeError as json_err:
                error_msg = "Invalid JSON response from server"
                logger.error(json.dumps({"error": error_msg, "exception": str(json_err)}))
                return {"error": error_msg}
            
            logger.info(f"Received response from remote server: {response_data}")
            return {"output": response_data}
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
            logger.error(json.dumps({
                "error": error_msg,
                "exception": str(e),
                "stack_trace": traceback.format_exc()
            }))
            return {"error": error_msg}

def build_graph() -> any:
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

if __name__ == "__main__":
    graph = build_graph()
    # get current file path as string
    test_files_path = f"{os.path.dirname(os.path.abspath(__file__))}/test_files"
    input = {"file_path": test_files_path}
    logger.info({"event": "invoking_graph", "input": input})
    result = graph.invoke(input)
    if "output" in result:
        logger.info({"event": "final_result", "result": result["output"]})
    else:
        logger.error({"event": "final_result", "result": result})