"""Bern parking data source implementation."""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Optional, Tuple

from ..core.data_source import BaseDataSource
from ..models.models import City, Parking, ParkingStatus
from ..utils.http import fetch_url
from ..utils.logging import setup_logging

logger = setup_logging(__name__)

# URL for Bern parking data
BERN_PARKING_XML_URL = "https://www.parking-bern.ch/parkdata.xml"

# Mapping between parking names in XML and our IDs
PARKING_NAME_MAP = {
    "P01": "parkhaus-bahnhof",         # Bahnhof Parking
    "P02": "parkhaus-metro",           # Metro Parking
    "P03": "parkhaus-rathaus",         # Rathaus Parking
    "City West Parking Mu": "parkhaus-city-west",  # City West
    "P04": "parkhaus-bundesplatz",     # Bundesplatz (best guess)
    "P05": "parkhaus-mobiliar",        # Mobiliar Parking
    "P06": "parkhaus-casino",          # Casino Parking
    "P+R": "parkhaus-neufeld-p+r",     # P+R Neufeld
    "P10": "parkhaus-kursaal",         # Kursaal Parking (best guess)
    # Add more mappings as needed
}


class BernParkingDataSource(BaseDataSource):
    """Data source for Bern parking data."""

    def __init__(self) -> None:
        """Initialize the Bern parking data source."""
        super().__init__(city_id="bern", city_name="Bern")

    async def fetch_data(self) -> City:
        """Fetch parking data for Bern from the official XML feed.
        
        Returns:
            City: City object with parking data
            
        Raises:
            DataSourceError: If data fetching or parsing fails
        """
        from ..core.errors import DataFetchError, DataParseError, handle_data_source_error
        
        try:
            logger.info(f"Fetching Bern parking data from {BERN_PARKING_XML_URL}")
            
            # Fetch XML data
            xml_data = await fetch_url(BERN_PARKING_XML_URL)
            
            if not isinstance(xml_data, str):
                raise DataParseError("Expected XML string data", self.name)
            
            # Parse the XML data
            parsed_data = self._parse_xml(xml_data)
            
            # Create city object with parsed data
            city = City(
                id=self.city_id,
                name=self.city_name,
                parkings=[],
                last_updated=datetime.now(),
            )
            
            # Load static parking data for additional information
            from ..data import load_parkings_data
            static_parkings_data = load_parkings_data(self.city_id)
            
            # Process each parking from XML and combine with static data
            for xml_parking_name, (spaces_total, spaces_free, is_open) in parsed_data.items():
                # Map XML parking name to our ID
                parking_id = PARKING_NAME_MAP.get(xml_parking_name)
                
                # Skip if we don't have a mapping for this parking
                if not parking_id:
                    logger.warning(f"No mapping found for parking: {xml_parking_name}")
                    continue
                
                # Get static data for this parking
                static_data = static_parkings_data.get(parking_id, {})
                
                if not static_data:
                    logger.warning(f"No static data found for parking_id: {parking_id}")
                    
                # Use XML data for availability, but prefer static data for metadata
                parking = Parking(
                    id=parking_id,
                    name=static_data.get("name", f"Parking {xml_parking_name}"),
                    city=self.city_name,
                    # Use XML data for available/total spaces
                    available_spaces=spaces_free if is_open else 0,
                    # Use XML total if available, otherwise fall back to static data
                    total_spaces=spaces_total if spaces_total > 0 else static_data.get("total_spaces", 0),
                    status=ParkingStatus.OPEN if is_open else ParkingStatus.CLOSED,
                    # Use static data for these fields
                    latitude=static_data.get("latitude"),
                    longitude=static_data.get("longitude"),
                    address=static_data.get("address"),
                    last_updated=datetime.now(),
                )
                
                city.parkings.append(parking)
            
            # Add static-only parkings that aren't in the XML feed
            for parking_id, parking_data in static_parkings_data.items():
                # Skip if we already added this parking from the XML
                if any(p.id == parking_id for p in city.parkings):
                    continue
                
                # For parkings not in the XML, create a parking with static data
                # and estimate availability as 30% of capacity
                total_spaces = parking_data.get("total_spaces", 0)
                available_spaces = int(total_spaces * 0.3)  # Estimate 30% availability
                
                parking = Parking(
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
                
                city.parkings.append(parking)
            
            return city
            
        except Exception as e:
            # Convert other exceptions to data source errors
            raise handle_data_source_error(e, self.name)
    
    def _parse_xml(self, xml_data: str) -> Dict[str, Tuple[int, int, bool]]:
        """Parse XML data from Bern parking feed.
        
        Args:
            xml_data: XML string data
            
        Returns:
            Dict[str, Tuple[int, int, bool]]: Dictionary with parking data
                Key: Parking name in XML
                Value: Tuple of (total_spaces, available_spaces, is_open)
        """
        result = {}
        
        try:
            # Parse XML
            root = ET.fromstring(xml_data)
            
            # Extract updated timestamp if available
            updated = root.get("updated", "")
            if updated:
                logger.info(f"Bern parking data updated at: {updated}")
            
            # Process each parking element
            for parking in root.findall("./parking"):
                name = parking.get("name", "")
                if not name:
                    continue
                
                # Extract data
                state = parking.get("state", "0")
                space_count_str = parking.get("spacecount", "-1")
                space_free_str = parking.get("spacefree", "0")
                
                # Parse values
                try:
                    space_count = int(space_count_str)
                    space_free = int(space_free_str)
                    is_open = state == "1"
                except ValueError:
                    logger.warning(f"Invalid values in parking {name}: count={space_count_str}, free={space_free_str}")
                    continue
                
                # Store result
                result[name] = (space_count, space_free, is_open)
            
        except Exception as e:
            logger.error(f"Error parsing Bern XML: {str(e)}")
            
        return result