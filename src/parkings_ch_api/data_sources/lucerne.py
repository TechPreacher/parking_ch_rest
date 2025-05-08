"""Lucerne parking data source implementation."""

from datetime import datetime
from typing import Any

from ..core.data_source import BaseDataSource
from ..models.models import City, Parking, ParkingStatus
from ..utils.logging import setup_logging
from ..utils.lucerne_api import fetch_lucerne_parking_data

logger = setup_logging(__name__)


class LucerneParkingDataSource(BaseDataSource):
    """Data source for Lucerne parking data.

    This implementation uses the official Lucerne parking API.
    """

    def __init__(self) -> None:
        """Initialize the Lucerne parking data source."""
        super().__init__(city_id="lucerne", city_name="Luzern")

    async def fetch_data(self) -> City:
        """Fetch parking data for Lucerne from the official API.

        Returns:
            City: City object with parking data

        Raises:
            DataSourceError: If data fetching or processing fails
        """
        from ..core.errors import DataFetchError, DataParseError, handle_data_source_error

        try:
            logger.info("Fetching Lucerne parking data from API")

            # Load city data for coordinates
            from ..data import get_city_details

            city_details = get_city_details(self.city_id) or {}

            # Create city object
            city = City(
                id=self.city_id,
                name=self.city_name,
                parkings=[],
                latitude=city_details.get("latitude"),
                longitude=city_details.get("longitude"),
                last_updated=datetime.now(),
            )

            # Load static parking data for additional information
            from ..data import load_parkings_data

            static_parkings_data = load_parkings_data(self.city_id)

            try:
                # Fetch real-time data from API
                api_parkings_data = await fetch_lucerne_parking_data()

                # Process each parking from the API data
                for parking_id, api_data in api_parkings_data.items():
                    # Get static data for this parking
                    static_data = static_parkings_data.get(parking_id, {})

                    # Determine status
                    is_open = api_data.get("is_open", False)
                    status = ParkingStatus.OPEN if is_open else ParkingStatus.CLOSED

                    # Get available and total spaces
                    available_spaces = api_data.get("available_spaces", 0)
                    total_spaces = api_data.get("total_spaces", 0)

                    # Use static total if API returns zero
                    if total_spaces == 0:
                        total_spaces = static_data.get("total_spaces", 0)

                    # Create parking object
                    parking = Parking(
                        id=parking_id,
                        name=api_data.get("name", static_data.get("name", f"Parking {parking_id}")),
                        city=self.city_name,
                        available_spaces=available_spaces if status == ParkingStatus.OPEN else 0,
                        total_spaces=total_spaces,
                        status=status,
                        latitude=static_data.get("latitude"),
                        longitude=static_data.get("longitude"),
                        address=static_data.get("address"),
                        last_updated=datetime.now(),
                    )

                    city.parkings.append(parking)

                # Add missing parkings from static data
                self._add_missing_parkings(city, static_parkings_data)

                return city

            except (ValueError, DataFetchError, DataParseError) as e:
                # Log error and return a city with no available parking data
                logger.error(
                    f"Error fetching real-time data: {e!s}. Real-time data unavailable.",
                )

                # Return city with unavailable status
                return self._create_unavailable_data()

        except (ValueError, ConnectionError, TimeoutError) as e:
            # Convert common exceptions to data source errors
            raise handle_data_source_error(e, self.name) from e
        except Exception as e:
            # Convert unexpected exceptions to data source errors
            logger.error(f"Unexpected error in Lucerne data source: {e!s}")
            raise handle_data_source_error(e, self.name) from e

    def _add_missing_parkings(
        self,
        city: City,
        static_parkings_data: dict[str, dict[str, Any]],
    ) -> None:
        """Add parkings from static data that aren't in the API data.

        Args:
            city: City object to add parkings to
            static_parkings_data: Static parking data dictionary
        """
        # Get list of parking IDs already in the city
        existing_ids = {p.id for p in city.parkings}

        # Add any parkings from static data that aren't already included
        for parking_id, parking_data in static_parkings_data.items():
            if parking_id in existing_ids:
                continue

            # For parkings not in the API, create with UNKNOWN status
            total_spaces = parking_data.get("total_spaces", 0)

            parking = Parking(
                id=parking_id,
                name=parking_data.get("name", f"Parking {parking_id}"),
                city=self.city_name,
                available_spaces=0,  # No available spaces when real-time data is unavailable
                total_spaces=total_spaces,
                status=ParkingStatus.UNKNOWN,  # Set status to UNKNOWN
                latitude=parking_data.get("latitude"),
                longitude=parking_data.get("longitude"),
                address=parking_data.get("address"),
                last_updated=datetime.now(),
            )

            city.parkings.append(parking)

    def _create_unavailable_data(self) -> City:
        """Create a city object with unavailable parking status.

        This is used when the API fails to indicate that real-time data is not available.

        Returns:
            City: City object with UNKNOWN status for all parkings
        """
        # Load city data for coordinates
        from ..data import get_city_details, load_parkings_data

        city_details = get_city_details(self.city_id) or {}
        static_parkings_data = load_parkings_data(self.city_id)

        # Create city object
        city = City(
            id=self.city_id,
            name=self.city_name,
            parkings=[],
            latitude=city_details.get("latitude"),
            longitude=city_details.get("longitude"),
            last_updated=datetime.now(),
        )

        # Create parking objects with UNKNOWN status
        for parking_id, parking_data in static_parkings_data.items():
            # Get total spaces from static data
            total_spaces = parking_data.get("total_spaces", 0)

            # Create parking object with UNKNOWN status and 0 available spaces
            parking = Parking(
                id=parking_id,
                name=parking_data.get("name", f"Parking {parking_id}"),
                city=self.city_name,
                available_spaces=0,  # No available spaces when real-time data is unavailable
                total_spaces=total_spaces,
                status=ParkingStatus.UNKNOWN,  # Set status to UNKNOWN
                latitude=parking_data.get("latitude"),
                longitude=parking_data.get("longitude"),
                address=parking_data.get("address"),
                last_updated=datetime.now(),
            )

            city.parkings.append(parking)

        return city
