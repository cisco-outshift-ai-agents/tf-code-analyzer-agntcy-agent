# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import SecretStr

from agent_workflow_server.generated.models.content import Content as SrvContent
from agent_workflow_server.generated.models.message import Message as SrvMessage
from agent_workflow_server.generated.models.run_output import RunOutput as SrvRunOutput
from agent_workflow_server.generated.models.run_result import RunResult as SrvRunResult
from agent_workflow_server.generated.models.run_stateless import (
    RunStateless as SrvRunStateless,
)
from agent_workflow_server.generated.models.run_status import RunStatus as SrvRunStatus
from agent_workflow_server.generated.models.run_create_stateless import (
    RunCreateStateless as SrvRunCreateStateless,
)
from agent_workflow_server.generated.models.run_wait_response_stateless import (
    RunWaitResponseStateless as SrvRunWaitResponseStateless,
)
from app.core.config import INTERNAL_ERROR_MESSAGE, get_llm_chain
from app.core.github import GithubClient
from app.graph.graph import StaticAnalyzerWorkflow
from app.models.ap.models import (
    Any,
    ErrorResponse,
    GithubRequest,
    RunCreateStateless,
    RunCreateStatelessOutput,
    Union,
)

router = APIRouter(tags=["Stateless Runs"])
logger = logging.getLogger(__name__)


@router.post(
    "/runs",
    response_model=RunCreateStatelessOutput,
    responses={
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
        "500": {"model": ErrorResponse},
    },
    tags=["Stateless Runs"],
)
def run_stateless_runs_post(
    body: RunCreateStateless, request: Request
) -> Union[Any, ErrorResponse]:
    """
    Create Background Run
    """
    logger.info("Received request to run the static analyzer workflow")
    settings = request.app.state.settings

    try:
        # -----------------------------------------------
        # Extract the Github details from the input.
        # We expect the content to be located at: payload["input"]["github"]
        # -----------------------------------------------

        # Retrieve the 'input' field and ensure it is a dictionary.
        input_field = body.input
        if not isinstance(input_field, dict):
            logger.info("Invalid input format")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid input format",
            )

        # Retrieve the 'github' field from the input dictionary.
        github_details = input_field.get("github_details")
        if not isinstance(github_details, GithubRequest):
            logger.info(f"Invalid Github details format: {type(github_details)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid Github details format: {type(github_details)}",
            )
        github_request = github_details
        logger.info("Github request: %s", github_request)

        # Initialize the Github client and download the repository.
        github_client = GithubClient(
            SecretStr(github_request.github_token)
            if github_request.github_token
            else None
        )
        try:
            file_path = github_client.download_repo_zip(
                repo_url=github_request.repo_url,
                branch=github_request.branch,
                destination_folder=settings.DESTINATION_FOLDER,
            )
        except Exception as e:
            logger.error("Internal error occurred: %s", e, exc_info=True)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=INTERNAL_ERROR_MESSAGE,
            ) from e

        # Run the static analyzer workflow on the downloaded repository.
        workflow = StaticAnalyzerWorkflow(chain=get_llm_chain(settings))
        result = workflow.analyze(file_path)
        logger.info(result)
    except HTTPException as http_exc:
        logger.error(
            "HTTP error during run processing: %s", http_exc.detail, exc_info=True
        )
        raise http_exc
    except Exception as exc:
        logger.error("Internal error during run processing: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            # detail=INTERNAL_ERROR_MESSAGE,
            detail=exc
        ) from exc

    payload = {
        "agent_id": body.agent_id,
        "output": result,
        "model": settings.OPENAI_API_VERSION,
        "metadata": {},
    }
    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


# ACP Endpoint
@router.post(
    "/runs/wait",
    responses={
        200: {"model": SrvRunWaitResponseStateless, "description": "Success"},
        404: {"model": str, "description": "Not Found"},
        409: {"model": str, "description": "Conflict"},
        422: {"model": str, "description": "Validation Error"},
    },
    tags=["Stateless Runs"],
    summary="Create a stateless run and wait for its output",
    response_model_by_alias=True,
)
async def create_and_wait_for_stateless_run_output(
    body: SrvRunCreateStateless, request: Request
) -> SrvRunWaitResponseStateless:
    """
    Create Run, Wait for Output
    """
    logger.info("Received request to run the static analyzer workflow")
    settings = request.app.state.settings

    try:
        # -----------------------------------------------
        # Extract the Github details from the input.
        # We expect the content to be located at: payload["input"]["github"]
        # -----------------------------------------------

        # Retrieve the 'input' field and ensure it is a dictionary.
        input_field = body.input
        if not isinstance(input_field, dict):
            logger.info("Invalid input format")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid input format",
            )

        # Retrieve the 'github' field from the input dictionary.
        github_details = input_field.get("github_details")
        if not isinstance(github_details, GithubRequest):
            logger.info(f"Invalid Github details format: {type(github_details)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid Github details format: {type(github_details)}",
            )
        github_request = github_details
        logger.info("Github request: %s", github_request)

        # Initialize the Github client and download the repository.
        github_client = GithubClient(
            SecretStr(github_request.github_token)
            if github_request.github_token
            else None
        )
        try:
            file_path = github_client.download_repo_zip(
                repo_url=github_request.repo_url,
                branch=github_request.branch,
                destination_folder=settings.DESTINATION_FOLDER,
            )
        except Exception as e:
            logger.error("Internal error occurred: %s", e, exc_info=True)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=INTERNAL_ERROR_MESSAGE,
            ) from e

        # Run the static analyzer workflow on the downloaded repository.
        workflow = StaticAnalyzerWorkflow(chain=get_llm_chain(settings))
        result = workflow.analyze(file_path)
        # Build WrkFlow Srv Run Output
        message = SrvMessage(role="ai", content=SrvContent(json.dumps(result)))
        run_result = SrvRunResult(type="result", values=result, messages=[message])
        run_output = SrvRunOutput(run_result)
        logger.info(result)
    except HTTPException as http_exc:
        logger.error(
            "HTTP error during run processing: %s", http_exc.detail, exc_info=True
        )
        raise http_exc
    except Exception as exc:
        logger.error("Internal error during run processing: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_ERROR_MESSAGE,
        ) from exc
    current_datetime = datetime.now(tz=timezone.utc)
    run_stateless = SrvRunStateless(
        run_id=str(body.metadata.get("id", "")) if body.metadata else "",
        agent_id=body.agent_id or "",
        created_at=current_datetime,
        updated_at=current_datetime,
        status=SrvRunStatus.SUCCESS,
        creation=body,
    )
    return SrvRunWaitResponseStateless(run=run_stateless, output=run_output)
