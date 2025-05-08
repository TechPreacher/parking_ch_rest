"""Utilities for city data management."""

import json
import os
from typing import Any

from ..utils.logging import setup_logging

logger = setup_logging(__name__)

# Base data directory
DATA_DIR = os.path.dirname(__file__)

# Path to the cities data file
CITIES_JSON_PATH = os.path.join(DATA_DIR, "cities.json")

# Path to the parkings data directory
PARKINGS_DATA_DIR = os.path.join(DATA_DIR, "parkings")


def load_cities_data() -> dict[str, dict[str, Any]]:
    """Load cities data from the JSON file.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with city data
    """
    try:
        with open(CITIES_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading cities data: {e!s}")
        return {}


def get_city_details(city_id: str) -> dict[str, Any] | None:
    """Get details for a specific city.

    Args:
        city_id: City identifier

    Returns:
        dict[str, Any] | None: City details or None if not found
    """
    cities = load_cities_data()
    return cities.get(city_id)


def load_parkings_data(city_id: str) -> dict[str, dict[str, Any]]:
    """Load parkings data for a specific city from the JSON file.

    Args:
        city_id: City identifier

    Returns:
        dict[str, dict[str, Any]]: Dictionary with parking data
    """
    parkings_file = os.path.join(PARKINGS_DATA_DIR, f"{city_id}.json")
    try:
        with open(parkings_file, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading parkings data for {city_id}: {e!s}")
        return {}


def get_parking_details(city_id: str, parking_id: str) -> dict[str, Any] | None:
    """Get details for a specific parking.

    Args:
        city_id: City identifier
        parking_id: Parking identifier

    Returns:
        dict[str, Any] | None: Parking details or None if not found
    """
    parkings = load_parkings_data(city_id)
    return parkings.get(parking_id)
