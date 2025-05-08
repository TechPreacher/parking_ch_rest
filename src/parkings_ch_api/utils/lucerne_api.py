"""API client for Lucerne parking data."""

from typing import Any, Dict, List, Optional

from ..utils.http import fetch_url
from ..utils.logging import setup_logging

logger = setup_logging(__name__)

# URL for Lucerne parking API
LUCERNE_PARKING_API_URL = "https://info.pls-luzern.ch/TeqParkingWS/GetFreeParks"

# Mapping between API parking codes and our internal IDs
PARKING_CODE_MAP = {
    "AP01": "parkhaus-altstadt",      # Altstadt-Parking
    "NP02": "parkhaus-bahnhof",       # Bahnhof-Parking
    "NU01": "parkhaus-kesselturm",    # Kesselturm-Parking
    "VS01": "parkhaus-sempacherstrasse", # Sempacherstrasse-Parking
    "KP01": "parkhaus-europagarage",  # Europa-Garage
    "NP08": "parkhaus-musegg",        # Musegg-Parking
    "SP01": "parkhaus-casino-palace", # Casino Palace-Parking
}


async def fetch_lucerne_parking_data() -> Dict[str, Dict[str, Any]]:
    """Fetch parking data from the Lucerne parking API.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with parking data, keyed by our internal parking ID
        
    Raises:
        ValueError: If API request fails or returns invalid data
    """
    try:
        logger.info(f"Fetching Lucerne parking data from {LUCERNE_PARKING_API_URL}")
        
        # Fetch data from API
        response = await fetch_url(LUCERNE_PARKING_API_URL)
        
        # Parse JSON response
        if isinstance(response, dict):
            data = response
        else:
            import json
            data = json.loads(response)
        
        # Check that we have a valid response with parking data
        if not data.get("status") == "success" or "data" not in data or "parkings" not in data["data"]:
            raise ValueError("Invalid response format from Lucerne parking API")
        
        # Process parking data
        result = {}
        parkings_data = data["data"]["parkings"]
        
        for parking_code, parking_info in parkings_data.items():
            # Map API code to our internal ID
            internal_id = PARKING_CODE_MAP.get(parking_code)
            if not internal_id:
                logger.warning(f"Unknown parking code: {parking_code} - {parking_info.get('description')}")
                continue
            
            # Extract data
            result[internal_id] = {
                "name": parking_info.get("description", f"Parking {parking_code}"),
                "available_spaces": int(parking_info.get("vacancy", 0)),
                "total_spaces": int(parking_info.get("capacity", 0)),
                "is_open": parking_info.get("opened", False) and not parking_info.get("maintenance", False),
                "last_updated": parking_info.get("datestamp"),
            }
        
        logger.info(f"Processed {len(result)} parkings from Lucerne API")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching Lucerne parking data: {str(e)}")
        raise ValueError(f"Failed to fetch Lucerne parking data: {str(e)}")