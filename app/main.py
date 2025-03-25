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

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from agp.agp import AGPConfig
from api.routes import stateless_runs
from core.config import APISettings, load_and_validate_app_settings
from core.logging_config import configure_logging
from core.utils import load_environment_variables, check_required_binaries
from starlette.requests import Request

logger = configure_logging()  # Apply global logging settings

class Log422Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 422:
            try:
                body = await request.json()
            except Exception:
                body = "Unable to parse body"

            log_data = {
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
                "body": body,
            }
            logger.error(f"422 Validation Error: {log_data}")
        return response

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Defines startup and shutdown logic for the FastAPI application.

    This function follows the `lifespan` approach, allowing resource initialization
    before the server starts and cleanup after it shuts down.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: The application runs while `yield` is active.

    Behavior:
    - On startup: Logs a startup message.
    - On shutdown: Logs a shutdown message.
    - Can be extended to initialize resources (e.g., database connections).
    """
    logging.info("Starting Terraform Code Analyzer Agent")

    # Example: Attach database connection to app state (if needed)
    # app.state.db = await init_db_connection()

    yield  # Application runs while 'yield' is in effect.

    logging.info("Application shutdown")

    # Example: Close database connection (if needed)
    # await app.state.db.close()


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generates a unique identifier for API routes.

    Args:
        route (APIRoute): The FastAPI route object.

    Returns:
        str: A unique string identifier for the route.

    Behavior:
    - If the route has tags, the ID is formatted as `{tag}-{route_name}`.
    - If no tags exist, the route name is used as the ID.
    """
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


def add_handlers(app: FastAPI) -> None:
    """
    Adds global route handlers to the FastAPI application.

    This function registers common endpoints, such as the root message
    and the favicon.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        None
    """

    @app.get(
        "/",
        summary="Root endpoint",
        description="Returns a welcome message for the API.",
        tags=["General"],
    )
    async def root() -> dict:
        """
        Root endpoint that provides a welcome message.

        Returns:
            dict: A JSON response with a greeting message.
        """
        return {"message": "Gateway of the App"}


def create_app(settings: APISettings) -> FastAPI:
    """
    Creates and configures the FastAPI application instance.

    This function sets up:
    - The API metadata (title, version, OpenAPI URL).
    - CORS middleware to allow cross-origin requests.
    - Route handlers for API endpoints.
    - A custom unique ID generator for API routes.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
        version="0.1.0",
        description=settings.DESCRIPTION,
        lifespan=lifespan,  # Use the new lifespan approach for startup/shutdown
    )
    add_handlers(app)
    app.include_router(stateless_runs.router, prefix=settings.API_V1_STR)

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    app.add_middleware(Log422Middleware)

    # Load and validate application settings
    try:
        app.state.settings = load_and_validate_app_settings()
    except ValueError as e:
        logger.error(f"Startup failed: {e}")
        raise SystemExit(1)

    return app

async def agp_connect(app: FastAPI, settings: APISettings):
    """
    Attempts to connect to the AGP Gateway, logs errors but does not raise.
    This ensures the REST server remains available even if AGP fails.
    """
    try:
        AGPConfig.gateway_container.set_config(
            endpoint=settings.AGP_GATEWAY_ENDPOINT, insecure=True
        )
        AGPConfig.gateway_container.set_fastapi_app(app)

        _ = await AGPConfig.gateway_container.connect_with_retry(
            agent_container=AGPConfig.agent_container, max_duration=10, initial_delay=1
        )

        await AGPConfig.gateway_container.start_server(
            agent_container=AGPConfig.agent_container
        )
        logger.info("AGP client connected and running.")
    except RuntimeError as e:
        logger.error("AGP RuntimeError: %s", e)
    except Exception as e:
        logger.error("AGP client connection failed: %s. Continuing without AGP.", e)



async def serve_rest(app: FastAPI, settings: APISettings):
    """
    Starts the Uvicorn server to serve the FastAPI application.
    """
    config = uvicorn.Config(app, host=settings.TF_CODE_ANALYZER_HOST, port=settings.TF_CODE_ANALYZER_PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main() -> None:
    """
    Entry point for running the FastAPI application.

    This function performs the following:
    - Configures logging globally.
    - Loads environment variables from a `.env` file.
    - Retrieves the port from environment variables (default: 8123).
    - Starts the Uvicorn server.

    Returns:
        None
    """
    load_environment_variables()
    settings = APISettings()

    check_required_binaries()

    logger.info("Starting REST server and initializing AGP client (if available).")

    app = create_app(settings)

    # Launch REST server and AGP client in parallel
    await asyncio.gather(
        serve_rest(app, settings),
        agp_connect(app, settings)
    )

if __name__ == "__main__":
    asyncio.run(main())
