"""Map components for Streamlit frontend."""

# Folium library lacks type stubs, handled via mypy config

from typing import Any

import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Constants for map configuration
DEFAULT_ZOOM_LEVEL = 14
FALLBACK_ZOOM_LEVEL = 13

# Constants for occupancy thresholds
HIGH_OCCUPANCY_THRESHOLD = 0.7  # 70% occupancy - orange warning
CRITICAL_OCCUPANCY_THRESHOLD = 0.9  # 90% occupancy - red warning

# Constants for available spaces thresholds when total is unknown
HIGH_AVAILABILITY_THRESHOLD = 20  # More than 20 spaces - green
LOW_AVAILABILITY_THRESHOLD = 5  # Less than 5 spaces - red

# Map marker colors
COLOR_GREEN = "green"  # Good availability
COLOR_ORANGE = "orange"  # Limited availability
COLOR_RED = "red"  # Very limited availability


def create_parking_map(
    parkings: list[dict[str, Any]],
    city_location: tuple[float, float],
) -> folium.Map:
    """Create a folium map with parking markers.

    Args:
        parkings: List of parking information
        city_location: (latitude, longitude) tuple for the city center

    Returns:
        folium.Map: Map with parking markers
    """
    m = folium.Map(location=city_location, zoom_start=DEFAULT_ZOOM_LEVEL)
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for each parking
    for parking in parkings:
        # Skip parking without available_spaces
        if "available_spaces" not in parking:
            continue

        # Determine marker color based on occupancy or available spaces
        if "total_spaces" in parking and parking["total_spaces"] > 0:
            # Calculate occupancy when total spaces is available
            occupancy = 1 - (parking["available_spaces"] / parking["total_spaces"])
            color = COLOR_GREEN
            if occupancy > HIGH_OCCUPANCY_THRESHOLD:
                color = COLOR_ORANGE
            if occupancy > CRITICAL_OCCUPANCY_THRESHOLD:
                color = COLOR_RED

            # Show both available and total spaces
            availability_text = (
                f"<p><b>Available:</b> {parking['available_spaces']} / "
                f"{parking['total_spaces']}</p>"
            )
        else:
            # With missing total, use a default color based on available spaces
            if parking["available_spaces"] > HIGH_AVAILABILITY_THRESHOLD:
                color = COLOR_GREEN
            elif parking["available_spaces"] < LOW_AVAILABILITY_THRESHOLD:
                color = COLOR_RED
            else:
                color = COLOR_ORANGE

            # Show only available spaces
            availability_text = f"<p><b>Available:</b> {parking['available_spaces']}</p>"

        # Create popup HTML content
        popup_content = f"""
        <div style="width:200px">
            <h4>{parking["name"]}</h4>
            <p>{parking.get("address", "Address not available")}</p>
            {availability_text}
            <p><b>Last Updated:</b> {parking.get("last_updated", "Unknown")}</p>
        </div>
        """

        # Get coordinates with fallbacks
        lat = parking.get("latitude")
        lon = parking.get("longitude")

        # Skip this parking if coordinates are missing
        if lat is None or lon is None:
            # Use city location as fallback coordinates
            lat = city_location[0]
            lon = city_location[1]

            # Add a note about missing coordinates to the popup
            popup_content += """
            <p><i>Note: Exact location not available, showing city center</i></p>
            """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content),
            icon=folium.Icon(color=color, icon="car", prefix="fa"),
        ).add_to(marker_cluster)

    return m


def display_map(
    parkings: list[dict[str, Any]],
    city_location: tuple[float, float],
    width: int = 1000,
    height: int = 600,
) -> None:
    """Display the parking map in the Streamlit app.

    Args:
        parkings: List of parking information
        city_location: (latitude, longitude) tuple for the city center
        width: Width of the map in pixels
        height: Height of the map in pixels
    """
    if parkings:
        parking_map = create_parking_map(parkings, city_location)
        folium_static(parking_map, width=width, height=height)
    else:
        st.warning("No parking data available for this city")
        # Display an empty map centered on the city
        m = folium.Map(location=city_location, zoom_start=FALLBACK_ZOOM_LEVEL)
        folium_static(m, width=width, height=height)
