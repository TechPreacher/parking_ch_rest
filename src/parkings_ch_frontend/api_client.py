"""Frontend utilities for Streamlit app.

This module contains utilities to be used by the Streamlit frontend.
It works in both local development and Docker environments using environment variables.
"""

import os
from typing import Any

import httpx

try:
    # Try to import settings from the API module (local development)
    from parkings_ch_api.config.settings import get_settings
    settings_available = True
except ImportError:
    # If settings are not available, we'll use environment variables
    settings_available = False


class ApiClient:
    """Client for interacting with the Parking API.
    
    This client handles both local development and containerized environments
    by checking for environment variables and falling back to settings module.
    """

    def __init__(self) -> None:
        """Initialize the API client with configuration from environment variables or settings."""
        # Get configuration from environment variables with fallbacks
        api_url = os.environ.get("APP_API_URL")
        request_timeout = int(os.environ.get("APP_REQUEST_TIMEOUT", "10"))
        
        if api_url:
            # Direct API URL is provided (highest priority)
            self.base_url = f"{api_url}/api/v1"
        else:
            # Construct URL from host and port
            host = os.environ.get("APP_HOST")
            port = os.environ.get("APP_PORT")
            
            if host and port:
                # Environment variables are available
                self.base_url = f"http://{host}:{port}/api/v1"
            elif settings_available:
                # Use settings from API module (local development)
                settings = get_settings()
                self.base_url = f"http://{settings.host}:{settings.port}/api/v1"
                request_timeout = settings.request_timeout
            else:
                # Fallback to default values
                self.base_url = "http://localhost:8000/api/v1"
        
        # Set request timeout
        self.timeout = httpx.Timeout(request_timeout)

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
