from __future__ import annotations

import logging
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.config import INTERNAL_ERROR_MESSAGE, get_llm_chain
from core.github import GithubClient
from graph.graph import StaticAnalyzerWorkflow
from models.models import Any, ErrorResponse, GithubRequest, RunCreateStateless, RunCreateStatelessOutput, Union

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
def run_stateless_runs_post(body: RunCreateStateless, request: Request) -> Union[Any, ErrorResponse]:
    """
    Create Background Run
    """

    settings = request.app.state.settings

    try:
        # -----------------------------------------------
        # Extract the Github details from the input.
        # We expect the content to be located at: payload["input"]["github"]
        # -----------------------------------------------

        # Retrieve the 'input' field and ensure it is a dictionary.
        input_field = body.input
        if not isinstance(input_field, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid input format"
            )

        # Retrieve the 'github' field from the input dictionary.
        github_request = input_field.get("github")

        # Initialize the Github client and download the repository.
        github_client = GithubClient(github_request.github_token)
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
            detail=INTERNAL_ERROR_MESSAGE,
        )

    payload = {
        "agent_id": body.agent_id,
        "output": result,
        "model": settings.OPENAI_API_VERSION,
        "metadata": {},
    }
    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


@router.post(
    "/runs/stream",
    response_model=str,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    include_in_schema=False,
    tags=["Stateless Runs"],
)
def stream_run_stateless_runs_stream_post(
    body: RunCreateStateless,
) -> Union[str, ErrorResponse]:
    """
    Create Run, Stream Output
    """
    pass


@router.post(
    "/runs/wait",
    response_model=Any,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    include_in_schema=False,
    tags=["Stateless Runs"],
)
def wait_run_stateless_runs_wait_post(
    body: RunCreateStateless,
) -> Union[Any, ErrorResponse]:
    """
    Create Run, Wait for Output
    """
    pass
