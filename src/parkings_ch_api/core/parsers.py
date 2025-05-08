"""Base parser classes for different data formats."""

from typing import Any, Protocol, TypeVar

from ..models.models import City
from ..utils.logging import setup_logging

logger = setup_logging(__name__)
T = TypeVar("T")


class Parser(Protocol[T]):
    """Protocol defining the interface for data parsers."""

    def parse(self, data: Any) -> T:
        """Parse data from a source into the target format.

        Args:
            data: Raw data from source

        Returns:
            T: Parsed data
        """
        ...


class XmlRssParser:
    """Parser for XML/RSS feed data."""

    def __init__(self, city_id: str, city_name: str) -> None:
        """Initialize the parser.

        Args:
            city_id: The city ID
            city_name: The city name
        """
        self.city_id = city_id
        self.city_name = city_name

    def parse(self, xml_data: str) -> City:
        """Parse XML data into a City object.

        Args:
            xml_data: XML string data

        Returns:
            City: City object with parking data

        Raises:
            ValueError: If XML parsing fails
        """
        try:
            from lxml import etree

            # Create empty city object
            city = City(
                id=self.city_id,
                name=self.city_name,
                parkings=[],
                latitude=None,
                longitude=None,
                last_updated=None,
            )

            # Parse XML - this is a placeholder implementation
            _ = etree.fromstring(xml_data.encode("utf-8"))

            # Process parsed XML data
            # Each specific data source will need to customize this
            # to extract data according to its specific XML structure
            logger.debug("Parsing XML data")

            return city
        except Exception as e:
            logger.error(f"Error parsing XML data: {e!s}")
            error_msg = f"Failed to parse XML data: {e!s}"
            raise ValueError(error_msg) from e


class JsonParser:
    """Parser for JSON data."""

    def __init__(self, city_id: str, city_name: str) -> None:
        """Initialize the parser.

        Args:
            city_id: The city ID
            city_name: The city name
        """
        self.city_id = city_id
        self.city_name = city_name

    def parse(self, json_data: dict[str, Any]) -> City:
        """Parse JSON data into a City object.

        Args:
            json_data: JSON data (already deserialized)

        Returns:
            City: City object with parking data

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Create empty city object
            city = City(
                id=self.city_id,
                name=self.city_name,
                parkings=[],
                latitude=None,
                longitude=None,
                last_updated=None,
            )

            # This is a placeholder implementation
            # Each specific data source will need to customize this
            # to extract data according to its specific JSON structure
            logger.debug("Parsing JSON data")

            return city
        except Exception as e:
            logger.error(f"Error parsing JSON data: {e!s}")
            error_msg = f"Failed to parse JSON data: {e!s}"
            raise ValueError(error_msg) from e


class CsvParser:
    """Parser for CSV data."""

    def __init__(self, city_id: str, city_name: str) -> None:
        """Initialize the parser.

        Args:
            city_id: The city ID
            city_name: The city name
        """
        self.city_id = city_id
        self.city_name = city_name

    def parse(self, csv_data: str) -> City:
        """Parse CSV data into a City object.

        Args:
            csv_data: CSV string data

        Returns:
            City: City object with parking data

        Raises:
            ValueError: If CSV parsing fails
        """
        try:
            # Create empty city object
            city = City(
                id=self.city_id,
                name=self.city_name,
                parkings=[],
                latitude=None,
                longitude=None,
                last_updated=None,
            )

            # This is a placeholder implementation
            # Each specific data source will need to customize this
            # to extract data according to its specific CSV structure
            logger.debug("Parsing CSV data")

            return city
        except Exception as e:
            logger.error(f"Error parsing CSV data: {e!s}")
            error_msg = f"Failed to parse CSV data: {e!s}"
            raise ValueError(error_msg) from e
