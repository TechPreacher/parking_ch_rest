"""Main entry point for running the application."""

import uvicorn

from parkings_ch_api.config.settings import get_settings


def main() -> None:
    """Start the application server."""
    settings = get_settings()
    uvicorn.run(
        "parkings_ch_api:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.value.lower(),
    )


if __name__ == "__main__":
    main()
