"""Basel parking data source implementation."""

import json
from datetime import datetime
from typing import Any

from ..core.data_source import BaseDataSource
from ..models.models import City, Parking, ParkingStatus
from ..utils.http import fetch_url
from ..utils.logging import setup_logging

logger = setup_logging(__name__)

# URL for Basel parking data in JSON format
BASEL_PARKING_API_URL = "https://data.bs.ch/api/v2/catalog/datasets/100088/exports/json"

# Default availability percentage for static-only parkings
DEFAULT_AVAILABILITY_PERCENT = 0.3

# Mapping between API parking IDs and our internal IDs
PARKING_ID_MAP = {
    "elisabethen": "parkhaus-elisabethen",
    "steinen": "parkhaus-steinen",
    "storchen": "parkhaus-storchen",
    "badbahnhof": "parkhaus-bad-bahnhof",
    "rebgasse": "parkhaus-rebgasse",
    "postbasel": "parkhaus-post-basel",
    "centralbahn": "parkhaus-centralbahn",
    "bahnhofsued": "parkhaus-bahnhof-sued",
    "anfos": "parkhaus-anfos",
    "city": "parkhaus-city",
    "clarahuus": "parkhaus-clarahuus",
    "aeschen": "parkhaus-aeschen",
    "kunstmuseum": "parkhaus-kunstmuseum",
    "messe": "parkhaus-messe",
    "europe": "parkhaus-europe",
    "claramatte": "parkhaus-claramatte",
}


class BaselParkingDataSource(BaseDataSource):
    """Data source for Basel parking data."""

    def __init__(self) -> None:
        """Initialize the Basel parking data source."""
        super().__init__(city_id="basel", city_name="Basel")

    async def fetch_data(self) -> City:
        """Fetch parking data for Basel from the official JSON API.

        Returns:
            City: City object with parking data

        Raises:
            DataSourceError: If data fetching or parsing fails
        """
        from ..core.errors import handle_data_source_error

        try:
            # Fetch and parse JSON data
            parsed_data = await self._fetch_and_parse_data()

            # Create basic city object
            city = self._create_empty_city()

            # Load static parking data for additional information
            from ..data import load_parkings_data

            static_parkings_data = load_parkings_data(self.city_id)

            # Process each parking from the API data
            self._process_api_parkings(parsed_data, city, static_parkings_data)

            # Add static-only parkings that aren't in the API data
            self._add_static_only_parkings(city, static_parkings_data)

            return city

        except (ValueError, ConnectionError, TimeoutError) as e:
            # Convert common exceptions to data source errors
            raise handle_data_source_error(e, self.name) from e
        except Exception as e:
            # Convert unexpected exceptions to data source errors
            logger.error(f"Unexpected error in Basel data source: {e!s}")
            raise handle_data_source_error(e, self.name) from e

    async def _fetch_and_parse_data(self) -> list[dict[str, Any]]:
        """Fetch JSON data from API and parse it.

        Returns:
            List[Dict[str, Any]]: Parsed parking data
        """
        logger.info(f"Fetching Basel parking data from {BASEL_PARKING_API_URL}")
        json_data = await fetch_url(BASEL_PARKING_API_URL)
        logger.info(f"Received Basel parking data of type: {type(json_data)}")
        return self._parse_json(json_data)

    def _create_empty_city(self) -> City:
        """Create an empty city object.

        Returns:
            City: Empty city object
        """
        return City(
            id=self.city_id,
            name=self.city_name,
            parkings=[],
            latitude=None,
            longitude=None,
            last_updated=datetime.now(),
        )

    def _process_api_parkings(
        self,
        parsed_data: list[dict[str, Any]],
        city: City,
        static_parkings_data: dict[str, dict[str, Any]],
    ) -> None:
        """Process parking data from API and add to city.

        Args:
            parsed_data: Parsed API data
            city: City object to add parkings to
            static_parkings_data: Static parking data
        """
        for api_parking in parsed_data:
            # Get the id2 value for mapping to our internal ID
            api_id = api_parking.get("id2")
            if not api_id:
                logger.warning(
                    f"Missing id2 in parking data: {api_parking.get('name', 'unknown')}",
                )
                continue

            # Map API ID to our internal ID
            parking_id = PARKING_ID_MAP.get(api_id)
            if not parking_id:
                logger.warning(f"No mapping found for parking ID: {api_id}")
                continue

            # Create and add parking object
            parking = self._create_parking_from_api(
                api_parking, parking_id, static_parkings_data.get(parking_id, {}),
            )
            city.parkings.append(parking)

    def _create_parking_from_api(
        self,
        api_parking: dict[str, Any],
        parking_id: str,
        static_data: dict[str, Any],
    ) -> Parking:
        """Create a parking object from API data.

        Args:
            api_parking: API parking data
            parking_id: Internal parking ID
            static_data: Static data for this parking

        Returns:
            Parking: Created parking object
        """
        # Check status
        status_str = api_parking.get("status", "").lower()
        status = ParkingStatus.OPEN if status_str == "offen" else ParkingStatus.CLOSED

        # Get free and total spaces
        free_spaces = api_parking.get("free", 0)
        total_spaces = api_parking.get("total")

        # Use static total if API returns null
        if total_spaces is None:
            total_spaces = static_data.get("total_spaces", 0)

        # Ensure available spaces doesn't exceed total spaces
        if total_spaces > 0:
            free_spaces = min(free_spaces, total_spaces)

        # Create a fields dictionary for the Parking constructor
        parking_fields = {
            "id": parking_id,
            "name": static_data.get("name", api_parking.get("title", f"Parking {parking_id}")),
            "city": self.city_name,
            "available_spaces": free_spaces if status == ParkingStatus.OPEN else 0,
            "total_spaces": total_spaces,
            "status": status,
            "last_updated": datetime.now(),
        }

        # Add coordinates from static data or API
        self._add_coordinates(parking_fields, api_parking, static_data)

        # Add address if available
        self._add_address(parking_fields, api_parking, static_data)

        # Create parking object
        return Parking(**parking_fields)

    def _add_coordinates(
        self,
        parking_fields: dict[str, Any],
        api_parking: dict[str, Any],
        static_data: dict[str, Any],
    ) -> None:
        """Add coordinates to parking fields.

        Args:
            parking_fields: Parking fields to update
            api_parking: API parking data
            static_data: Static parking data
        """
        geo_point = api_parking.get("geo_point_2d", {})
        if geo_point and "lat" in geo_point and "lon" in geo_point:
            parking_fields["latitude"] = geo_point["lat"]
            parking_fields["longitude"] = geo_point["lon"]
        else:
            parking_fields["latitude"] = static_data.get("latitude")
            parking_fields["longitude"] = static_data.get("longitude")

    def _add_address(
        self,
        parking_fields: dict[str, Any],
        api_parking: dict[str, Any],
        static_data: dict[str, Any],
    ) -> None:
        """Add address to parking fields.

        Args:
            parking_fields: Parking fields to update
            api_parking: API parking data
            static_data: Static parking data
        """
        address = api_parking.get("address")
        if address:
            parking_fields["address"] = address
        elif "address" in static_data:
            parking_fields["address"] = static_data["address"]

    def _add_static_only_parkings(
        self, city: City, static_parkings_data: dict[str, dict[str, Any]],
    ) -> None:
        """Add parkings from static data that aren't in the API.

        Args:
            city: City object to add parkings to
            static_parkings_data: Static parking data
        """
        parking_ids_from_api = {p.id for p in city.parkings}
        for parking_id, parking_data in static_parkings_data.items():
            # Skip if we already added this parking from the API
            if parking_id in parking_ids_from_api:
                continue

            # Create a parking with static data and estimated availability
            parking = self._create_parking_from_static(parking_id, parking_data)
            city.parkings.append(parking)

    def _create_parking_from_static(
        self, parking_id: str, parking_data: dict[str, Any],
    ) -> Parking:
        """Create a parking object from static data.

        Args:
            parking_id: Parking ID
            parking_data: Static parking data

        Returns:
            Parking: Created parking object
        """
        # For parkings not in the API, create a parking with static data
        # and estimate availability as 30% of capacity
        total_spaces = parking_data.get("total_spaces", 0)
        available_spaces = int(total_spaces * DEFAULT_AVAILABILITY_PERCENT)

        return Parking(
            id=parking_id,
            name=parking_data.get("name", f"Parking {parking_id}"),
            city=self.city_name,
            available_spaces=available_spaces,
            total_spaces=total_spaces,
            status=ParkingStatus.OPEN,
            latitude=parking_data.get("latitude"),
            longitude=parking_data.get("longitude"),
            address=parking_data.get("address"),
            last_updated=datetime.now(),
        )

    def _parse_json(self, json_data: str) -> list[dict[str, Any]]:
        """Parse JSON data from Basel parking API.

        Args:
            json_data: JSON string data

        Returns:
            List[Dict[str, Any]]: List of parking data dictionaries
        """
        try:
            # If the data is already parsed as JSON (dict or list), return it directly
            if isinstance(json_data, list):
                return json_data
            if isinstance(json_data, dict):
                return [json_data]

            # Otherwise try to parse JSON string
            return json.loads(json_data)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing Basel JSON: {e!s}")
            return []
