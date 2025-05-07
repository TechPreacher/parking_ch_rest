"""Utilities for city data management."""

import json
import os
from typing import Any, Dict, Optional

from ..utils.logging import setup_logging

logger = setup_logging(__name__)

# Path to the cities data file
CITIES_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cities.json")


def load_cities_data() -> Dict[str, Dict[str, Any]]:
    """Load cities data from the JSON file.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with city data
    """
    try:
        with open(CITIES_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading cities data: {str(e)}")
        return {}


def get_city_details(city_id: str) -> Optional[Dict[str, Any]]:
    """Get details for a specific city.
    
    Args:
        city_id: City identifier
        
    Returns:
        Optional[Dict[str, Any]]: City details or None if not found
    """
    cities = load_cities_data()
    return cities.get(city_id)
