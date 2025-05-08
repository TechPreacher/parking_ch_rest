"""Frontend API client for Docker environment.

This module contains a simplified API client for use in the Docker environment.
"""

import os
from typing import Any

import httpx

# Get API host and port from environment variables
API_HOST = os.environ.get("APP_HOST", "api")
API_PORT = int(os.environ.get("APP_PORT", "8000"))
REQUEST_TIMEOUT = int(os.environ.get("APP_REQUEST_TIMEOUT", "10"))


class DockerApiClient:
    """Client for interacting with the Parking API in Docker environment."""

    def __init__(self) -> None:
        """Initialize the API client."""
        self.base_url = f"http://{API_HOST}:{API_PORT}/api/v1"
        self.timeout = httpx.Timeout(REQUEST_TIMEOUT)

    async def get_cities(self) -> list[dict[str, Any]]:
        """Get list of supported cities.

        Returns:
            list[dict[str, Any]]: List of city information
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/cities")
            response.raise_for_status()
            return response.json()

    async def get_parkings(self, city_id: str) -> list[dict[str, Any]]:
        """Get parking information for a specific city.

        Args:
            city_id: City identifier

        Returns:
            list[dict[str, Any]]: List of parking information
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/cities/{city_id}/parkings")
            response.raise_for_status()
            return response.json()

    async def get_parking(self, city_id: str, parking_id: str) -> dict[str, Any]:
        """Get detailed information for a specific parking.

        Args:
            city_id: City identifier
            parking_id: Parking identifier

        Returns:
            dict[str, Any]: Detailed parking information
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/cities/{city_id}/parkings/{parking_id}")
            response.raise_for_status()
            return response.json()