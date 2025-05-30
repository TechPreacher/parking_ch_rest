"""Error handling for data sources."""

from typing import Any

from ..utils.logging import setup_logging

logger = setup_logging(__name__)


class DataSourceError(Exception):
    """Base class for data source exceptions."""

    def __init__(
        self,
        message: str,
        source_name: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Error message
            source_name: Name of the data source
            details: Additional error details
        """
        self.source_name = source_name
        self.details = details or {}
        super().__init__(f"{source_name}: {message}")


class DataFetchError(DataSourceError):
    """Error raised when fetching data from a source fails."""


class DataParseError(DataSourceError):
    """Error raised when parsing data from a source fails."""


class NoDataAvailableError(DataSourceError):
    """Error raised when no data is available from a source."""


def handle_data_source_error(error: Exception, source_name: str) -> DataSourceError:
    """Convert a generic exception to a DataSourceError.

    Args:
        error: Original exception
        source_name: Name of the data source

    Returns:
        DataSourceError: Wrapped error
    """
    logger.error(f"Error in data source {source_name}: {error!s}")

    # Map common errors to specific data source errors
    if isinstance(error, ValueError):
        return DataParseError(str(error), source_name)
    if isinstance(error, ConnectionError | TimeoutError):
        return DataFetchError(str(error), source_name)
    return DataSourceError(str(error), source_name)
