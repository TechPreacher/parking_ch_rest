"""Zurich parking data source implementation."""

from datetime import datetime

from lxml import etree

from ..core.data_source import BaseDataSource
from ..models.models import City, Parking, ParkingStatus
from ..utils.http import fetch_url
from ..utils.logging import setup_logging

logger = setup_logging(__name__)

# URL for Zurich parking data
ZURICH_PARKING_URL = "https://www.pls-zh.ch/plsFeed/rss"
MINIMUM_PARTS = 2  # Need at least 2 parts for a valid format

class ZurichParkingDataSource(BaseDataSource):
    """Data source for Zurich parking data."""

    def __init__(self) -> None:
        """Initialize the Zurich parking data source."""
        super().__init__(city_id="zurich", city_name="Zürich")

    async def fetch_data(self) -> City:
        """Fetch parking data from Zurich RSS feed.

        Returns:
            City: City object with parking data

        Raises:
            DataSourceError: If data fetching or parsing fails
        """
        from ..core.errors import DataFetchError, DataParseError, handle_data_source_error

        try:
            logger.info(f"Fetching parking data from {ZURICH_PARKING_URL}")
            xml_data = await fetch_url(ZURICH_PARKING_URL)

            expected_xml_error_msg = "Expected XML string data"
            if not isinstance(xml_data, str):
                raise DataParseError(expected_xml_error_msg, self.name)

            city = self._parse_xml(xml_data)
            city.last_updated = datetime.now()
            return city

        except (DataFetchError, DataParseError):
            # Re-raise existing data source errors
            raise
        except Exception as e:
            # Convert other exceptions to data source errors
            raise handle_data_source_error(e, self.name) from e

    def _parse_xml(self, xml_data: str) -> City:
        """Parse XML data from Zurich parking RSS feed.

        Args:
            xml_data: XML string data

        Returns:
            City: City object with parking data

        Raises:
            ValueError: If XML parsing fails
        """
        try:
            # Create empty city
            city = City(
                id=self.city_id,
                name=self.city_name,
                parkings=[],
                latitude=None,
                longitude=None,
                last_updated=None,
            )

            # Parse XML
            root = etree.fromstring(xml_data.encode("utf-8"))

            # Find all <item> elements (each represents a parking)
            items = root.findall(".//item")

            # Load static parking data
            from ..data import load_parkings_data

            static_parkings_data = load_parkings_data(self.city_id)

            for item in items:
                # Extract data from RSS item
                title = self._get_element_text(item, "title", "")
                description = self._get_element_text(item, "description", "")

                # Extract parking data from description
                parking_data = self._parse_description(description)
                if not parking_data:
                    continue

                # Generate parking ID
                parking_id = self._normalize_id(title)

                # Get additional data from static file if available
                static_data = static_parkings_data.get(parking_id, {})

                # Create a fields dictionary that will be passed to Parking constructor
                parking_fields = {
                    "id": parking_id,
                    "name": static_data.get("name", title),
                    "city": self.city_name,
                    "available_spaces": parking_data.get("available", 0),
                    # Use total spaces from static data if available, otherwise use the RSS value
                    "total_spaces": static_data.get("total_spaces", parking_data.get("total", 0)),
                    "status": ParkingStatus.OPEN
                    if parking_data.get("is_open", True)
                    else ParkingStatus.CLOSED,
                    # Use coordinates from static data if available
                    "latitude": static_data.get("latitude"),
                    "longitude": static_data.get("longitude"),
                    "last_updated": datetime.now(),
                }

                # Add address if available in static data
                if "address" in static_data:
                    parking_fields["address"] = static_data["address"]

                # Create parking object
                parking = Parking(**parking_fields)

                city.parkings.append(parking)

            return city

        except Exception as e:
            logger.error(f"Error parsing XML data: {e!s}")
            err = f"Failed to parse Zurich parking data: {e!s}"
            raise ValueError(err) from e

    def _get_element_text(self, element: etree._Element, tag_name: str, default: str = "") -> str:
        """Extract text from an XML element.

        Args:
            element: XML element
            tag_name: Tag name to find
            default: Default value if not found

        Returns:
            str: Element text or default value
        """
        child = element.find(tag_name)
        return child.text if child is not None and child.text else default

    def _parse_description(self, description: str) -> dict[str, int]:
        """Parse parking description to extract data.

        Args:
            description: Description string from RSS feed

        Returns:
            Dict[str, int]: Dictionary with parking data
        """
        result = {
            "available": 0,
            "total": 0,
            "is_open": True,
        }

        try:
            # Example description format: "open / 234"
            parts = description.split("/")
            if len(parts) < MINIMUM_PARTS:
                return result

            available = int(parts[1].strip())
            open_status = parts[0].strip().lower()
            total = 0  # Unknown for Zurich

            result["available"] = available
            result["total"] = total
            result["is_open"] = True if open_status == "open" else False

        except (ValueError, IndexError):
            logger.warning(f"Could not parse description: {description}")

        return result

    def _normalize_id(self, name: str) -> str:
        """Convert a parking name to an ID.

        Args:
            name: Parking name

        Returns:
            str: Normalized ID
        """
        return (
            name.lower().replace(" ", "-").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        )
