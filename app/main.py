import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from api.routes import stateless_runs
from core.config import APISettings, load_and_validate_app_settings
from core.logging_config import configure_logging
from core.utils import load_environment_variables, check_required_binaries


logger = configure_logging()  # Apply global logging settings


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

    # Load and validate application settings
    try:
        app.state.settings = load_and_validate_app_settings()
    except ValueError as e:
        logger.error(f"Startup failed: {e}")
        raise SystemExit(1)

    return app


def main() -> None:
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
    # Load environment variables before starting the application
    load_environment_variables()
    settings = APISettings()

    # Validate that required binaries are installed
    check_required_binaries()

    logger = logging.getLogger("app")  # Default logger for main script
    logger.info("Starting FastAPI application...")

    # Start the FastAPI application using Uvicorn
    uvicorn.run(
        create_app(settings),
        host=settings.TF_CODE_ANALYZER_HOST,
        port=settings.TF_CODE_ANALYZER_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
