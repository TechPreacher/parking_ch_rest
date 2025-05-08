"""Application entry point."""

import uvicorn
from fastapi import FastAPI

from .api.routes import router
from .config.settings import get_settings
from .utils.logging import setup_logging

logger = setup_logging(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured application
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        root_path=settings.api_root_path,
    )

    # Register API routes
    app.include_router(router)

    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event() -> None:
        """Execute code when the application starts."""
        logger.info("Application starting up")

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Execute code when the application shuts down."""
        logger.info("Application shutting down")

    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "parkings_ch_api:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.value.lower(),
    )
