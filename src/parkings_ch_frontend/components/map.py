"""Map components for Streamlit frontend."""

from typing import Any, Dict, List, Optional, Tuple

import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static


def create_parking_map(
    parkings: List[Dict[str, Any]], city_location: Tuple[float, float]
) -> folium.Map:
    """Create a folium map with parking markers.

    Args:
        parkings: List of parking information
        city_location: (latitude, longitude) tuple for the city center

    Returns:
        folium.Map: Map with parking markers
    """
    m = folium.Map(location=city_location, zoom_start=14)
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for each parking
    for parking in parkings:
        if (
            "total_spaces" not in parking
            or "available_spaces" not in parking
            or parking["total_spaces"] == 0
        ):
            continue

        occupancy = 1 - (parking["available_spaces"] / parking["total_spaces"])
        color = "green"
        if occupancy > 0.7:
            color = "orange"
        if occupancy > 0.9:
            color = "red"

        # Create popup HTML content
        popup_content = f"""
        <div style="width:200px">
            <h4>{parking['name']}</h4>
            <p>{parking.get('address', 'Address not available')}</p>
            <p><b>Available:</b> {parking['available_spaces']} / {parking['total_spaces']}</p>
            <p><b>Last Updated:</b> {parking.get('last_updated', 'Unknown')}</p>
        </div>
        """

        # Get coordinates with fallbacks
        lat = parking.get("latitude", city_location[0])
        lon = parking.get("longitude", city_location[1])

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content),
            icon=folium.Icon(color=color, icon="car", prefix="fa"),
        ).add_to(marker_cluster)

    return m


def display_map(
    parkings: List[Dict[str, Any]], city_location: Tuple[float, float], width: int = 1000, height: int = 600
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
        m = folium.Map(location=city_location, zoom_start=13)
        folium_static(m, width=width, height=height)
