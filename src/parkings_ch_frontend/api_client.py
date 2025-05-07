"""Frontend utilities for Streamlit app.

This module contains utilities to be used by the Streamlit frontend.
"""

from typing import Any, Dict, List, Optional

import httpx

from parkings_ch_api.config.settings import get_settings


class ApiClient:
    """Client for interacting with the Parking API."""

    def __init__(self) -> None:
        """Initialize the API client."""
        self.settings = get_settings()
        self.base_url = f"http://{self.settings.host}:{self.settings.port}"
        self.timeout = httpx.Timeout(self.settings.request_timeout)

    async def get_cities(self) -> List[Dict[str, Any]]:
        """Get list of supported cities.

        Returns:
            List[Dict[str, Any]]: List of city information
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/cities")
            response.raise_for_status()
            return response.json()

    async def get_parkings(self, city_id: str) -> List[Dict[str, Any]]:
        """Get parking information for a specific city.

        Args:
            city_id: City identifier

        Returns:
            List[Dict[str, Any]]: List of parking information
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/cities/{city_id}/parkings")
            response.raise_for_status()
            return response.json()

    async def get_parking(self, city_id: str, parking_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific parking.

        Args:
            city_id: City identifier
            parking_id: Parking identifier

        Returns:
            Dict[str, Any]: Detailed parking information
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/cities/{city_id}/parkings/{parking_id}")
            response.raise_for_status()
            return response.json()
