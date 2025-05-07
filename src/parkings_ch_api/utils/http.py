"""HTTP client utilities."""

from typing import Any

import aiohttp

from ..config.settings import get_settings
from ..utils.logging import setup_logging

logger = setup_logging(__name__)


class HttpClient:
    """HTTP client for making requests to external services."""

    def __init__(self, timeout: int | None = None) -> None:
        """Initialize the HTTP client.

        Args:
            timeout: Request timeout in seconds
        """
        settings = get_settings()
        self.timeout = timeout or settings.request_timeout

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a GET request.

        Args:
            url: URL to request
            params: Query parameters
            headers: HTTP headers

        Returns:
            Any: Response data

        Raises:
            aiohttp.ClientError: If request fails
        """
        logger.debug(f"Making GET request to {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as response:
                response.raise_for_status()
                logger.debug(f"Response status: {response.status}")

                content_type = response.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    return await response.json()
                if "application/xml" in content_type or "text/xml" in content_type:
                    return await response.text()
                if "text" in content_type:
                    return await response.text()
                return await response.read()


async def fetch_url(url: str, timeout: int | None = None) -> Any:
    """Convenience function for making an HTTP GET request.

    Args:
        url: URL to request
        timeout: Request timeout in seconds

    Returns:
        Any: Response data

    Raises:
        aiohttp.ClientError: If request fails
    """
    client = HttpClient(timeout=timeout)
    return await client.get(url)
