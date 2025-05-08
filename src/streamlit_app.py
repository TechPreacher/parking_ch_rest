#!/usr/bin/env python
"""Streamlit frontend for the Swiss Parking API.

This module serves as the entry point for the Streamlit web application.
"""

# Streamlit type annotations are challenging, so we handle them selectively

import asyncio
import datetime
import os
import random
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

import streamlit as st

# Use the Docker API client in Docker environment
if os.environ.get("USE_DOCKER_CLIENT") == "1":
    from parkings_ch_frontend.docker_api_client import DockerApiClient as ApiClient
else:
    from parkings_ch_frontend.api_client import ApiClient

from parkings_ch_frontend.components.charts import (
    create_availability_chart,
    create_trend_chart,
)
from parkings_ch_frontend.components.map import display_map

# Type variable for generic decorator
T = TypeVar("T")

# Constants
CITY_CACHE_TTL = 60  # Time to live for city data cache in seconds
PARKING_CACHE_TTL = 30  # Time to live for parking data cache in seconds
MAP_WIDTH = 1000  # Default map width in pixels
MAP_HEIGHT = 600  # Default map height in pixels
TREND_HOURS = 24  # Number of hours for trend data


# Helper function to run async functions in Streamlit
def async_to_sync(async_func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """Decorator to run async functions in Streamlit."""
    import functools

    @functools.wraps(async_func)
    def wrapper(*args: object, **kwargs: object) -> T:
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
        return result

    return wrapper


# Configure the page
st.set_page_config(
    page_title="Swiss Parking Spaces",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=CITY_CACHE_TTL)
def get_cities() -> list[dict[str, Any]]:
    """Get list of available cities from the API.

    Returns:
        list[dict[str, Any]]: List of city information
    """

    @async_to_sync
    async def fetch_cities() -> list[dict[str, Any]]:
        client = ApiClient()
        try:
            response = await client.get_cities()
            # Extract cities from the response - the API returns a CityList object
            # with a cities field
            if isinstance(response, dict) and "cities" in response:
                return response["cities"]
            st.error(f"Unexpected response format: {response}")
            error_msg = "Invalid API response format"
            raise ValueError(error_msg)
        except (ValueError, ConnectionError, TimeoutError) as e:
            st.error(f"Error fetching cities: {e!s}")
            # Fallback to hardcoded data if API is unavailable
            return [
                {"id": "zurich", "name": "Zürich", "latitude": 47.3769, "longitude": 8.5417},
                {"id": "bern", "name": "Bern", "latitude": 46.9480, "longitude": 7.4474},
                {"id": "basel", "name": "Basel", "latitude": 47.5596, "longitude": 7.5886},
                {"id": "geneva", "name": "Geneva", "latitude": 46.2044, "longitude": 6.1432},
                {"id": "lausanne", "name": "Lausanne", "latitude": 46.5197, "longitude": 6.6323},
            ]

    return fetch_cities()


@st.cache_data(ttl=PARKING_CACHE_TTL)
def get_parkings(city_id: str) -> list[dict[str, Any]]:
    """Get parking information for a specific city.

    Args:
        city_id: City identifier

    Returns:
        list[dict[str, Any]]: List of parking information
    """

    @async_to_sync
    async def fetch_parkings(city_id: str) -> list[dict[str, Any]]:
        client = ApiClient()
        try:
            # Fetch real data from the API
            # The API client now correctly calls the /cities/{city_id}/parkings endpoint
            # which returns a list of parkings directly
            response = await client.get_parkings(city_id)
            if isinstance(response, list):
                # Add address field to parking data if missing
                for parking in response:
                    if "address" not in parking:
                        parking["address"] = f"{parking['name']}, {parking['city']}"
                return response
            st.error(f"Unexpected response format: {response}")
            error_msg = "Invalid API response format"
            raise ValueError(error_msg)
        except (ValueError, ConnectionError, TimeoutError) as e:
            st.error(f"Error fetching parking data: {e!s}")
            # Fallback to hardcoded data if API is unavailable
            if city_id == "zurich":
                return [
                    {
                        "id": "parking1",
                        "name": "Parkhaus Urania",
                        "address": "Uraniastrasse 3, 8001 Zürich",
                        "total_spaces": 600,
                        "available_spaces": 120,
                        "latitude": 47.3739,
                        "longitude": 8.5371,
                        "last_updated": "2025-05-07T10:30:00Z",
                    },
                    {
                        "id": "parking2",
                        "name": "Parkhaus Hauptbahnhof",
                        "address": "Sihlquai 41, 8005 Zürich",
                        "total_spaces": 400,
                        "available_spaces": 35,
                        "latitude": 47.3784,
                        "longitude": 8.5392,
                        "last_updated": "2025-05-07T10:30:00Z",
                    },
                    {
                        "id": "parking3",
                        "name": "Parkhaus Gessnerallee",
                        "address": "Gessnerallee 14, 8001 Zürich",
                        "total_spaces": 300,
                        "available_spaces": 78,
                        "latitude": 47.3737,
                        "longitude": 8.5338,
                        "last_updated": "2025-05-07T10:30:00Z",
                    },
                ]
            return []

    return fetch_parkings(city_id)


def get_city_selection() -> tuple[dict[str, Any], str, str]:
    """Set up the city selection UI and return the selected city.

    Returns:
        tuple[dict[str, Any], str, str]:
            Selected city data, city ID, and city name
    """
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    cities = get_cities()
    city_names = [city["name"] for city in cities]
    city_ids = [city["id"] for city in cities]
    city_dict = dict(zip(city_names, city_ids, strict=False))

    selected_city_name = st.sidebar.selectbox("Select a city", city_names, key="city_selector")
    selected_city_id = cast(str, city_dict[selected_city_name])

    # Get selected city information
    selected_city = next((city for city in cities if city["id"] == selected_city_id), cities[0])

    return selected_city, selected_city_id, selected_city_name


def render_map_view(
    tab: Any,
    parkings: list[dict[str, Any]],
    selected_city: dict[str, Any],
    selected_city_name: str,
) -> None:
    """Render the map view tab.

    Args:
        tab: The tab to render content in
        parkings: List of parking data
        selected_city: The selected city data
        selected_city_name: The name of the selected city
    """
    with tab:
        st.header(f"Parking Map for {selected_city_name}")
        if parkings:
            display_map(
                parkings,
                (cast(float, selected_city["latitude"]), cast(float, selected_city["longitude"])),
                width=MAP_WIDTH,
                height=MAP_HEIGHT,
            )
        else:
            st.write("No parking data available for this city")


def generate_trend_data(
    parking: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate simulated trend data for a parking.

    Args:
        parking: Parking data to generate trend for

    Returns:
        list[dict[str, Any]]: Generated trend data
    """
    history = []
    now = datetime.datetime.now()

    for i in range(TREND_HOURS, -1, -1):
        # Limit spaces between 0 and max capacity with some random variation
        available_spaces = max(
            0,
            min(
                int(parking["total_spaces"]),
                int(parking["available_spaces"] + random.randint(-50, 50)),
            ),
        )

        history.append(
            {
                "timestamp": (now - datetime.timedelta(hours=i)).isoformat(),
                "available_spaces": available_spaces,
                "total_spaces": parking["total_spaces"],
            },
        )

    return history


def render_chart_view(
    tab: Any,
    parkings: list[dict[str, Any]],
) -> None:
    """Render the chart view tab.

    Args:
        tab: The tab to render content in
        parkings: List of parking data
    """
    with tab:
        st.header("Parking Availability")
        if not parkings:
            st.write("No parking data available for this city")
            return

        # Availability chart
        fig = create_availability_chart(parkings)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, key="availability_chart")
        else:
            st.info("Could not create chart: insufficient data available.")

        # Trend chart (simulated data)
        st.subheader("Availability Trend (24h)")
        st.info(
            "This is a demonstration with simulated data. "
            "In a production environment, this would show real historical data.",
        )

        # Generate and display trend data for the first parking
        if parkings:
            parking = parkings[0]
            history = generate_trend_data(parking)

            trend_fig = create_trend_chart(history, cast(str, parking["name"]))
            if trend_fig is not None:
                st.plotly_chart(trend_fig, use_container_width=True, key="trend_chart")
            else:
                st.info("Could not create trend chart: insufficient data available.")


def calculate_occupancy(
    parking: dict[str, Any],
) -> tuple[float, int]:
    """Calculate occupancy percentage and available spaces for a parking.

    Args:
        parking: Parking data

    Returns:
        tuple[float, int]: Occupancy percentage and available spaces
    """
    total_spaces = int(parking["total_spaces"])
    if total_spaces <= 0:
        return 0.0, int(parking["available_spaces"])

    # Ensure available_spaces doesn't exceed total_spaces (data consistency)
    available = min(int(parking["available_spaces"]), total_spaces)

    # Calculate occupancy percentage
    occupancy_percentage = ((total_spaces - available) / total_spaces) * 100

    # Ensure percentage is between 0 and 100
    occupancy_percentage = max(0, min(100, occupancy_percentage))

    return occupancy_percentage, available


def render_list_view(
    tab: Any,
    parkings: list[dict[str, Any]],
) -> None:
    """Render the list view tab.

    Args:
        tab: The tab to render content in
        parkings: List of parking data
    """
    with tab:
        st.header("List of Parkings")
        if not parkings:
            st.write("No parking data available for this city")
            return

        for parking in parkings:
            col1, col2, col3 = st.columns([3, 2, 1])

            # Column 1: Name and address
            with col1:
                st.subheader(parking["name"])
                if "address" in parking:
                    st.write(parking["address"])

            # Column 2: Available spaces metric
            with col2:
                # Show delta for demo purposes on the first parking
                delta = (
                    f"{int(parking['available_spaces']) - 100}"
                    if parking["id"] == "parking1"
                    else None
                )

                st.metric(
                    "Available Spaces",
                    int(parking["available_spaces"]),
                    delta,
                )

            # Column 3: Occupancy visualization
            with col3:
                # Handle case when total_spaces is 0 or not available
                if int(parking["total_spaces"]) > 0:
                    occupancy_percentage, _ = calculate_occupancy(parking)
                    st.progress(occupancy_percentage / 100)
                    st.write(f"{occupancy_percentage:.1f}% occupied")
                else:
                    st.info("Total capacity not available")

            st.write("---")


def render_footer() -> None:
    """Render the app footer in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
        **About this app**

        This application shows real-time information about parking availability in Swiss cities.

        Data is refreshed every 5 minutes.

        Created by Sascha Corti
        """,
    )


def main() -> None:
    """Main function for the Streamlit app."""
    # App header
    st.title("🅿️ Swiss Parking Spaces")
    st.write("Find available parking spaces in Swiss cities")

    # City selection sidebar
    selected_city, selected_city_id, selected_city_name = get_city_selection()

    # Get parking information for the selected city
    parkings = get_parkings(selected_city_id)

    # Display tabs for different views
    tab1, tab2, tab3 = st.tabs(["Map View", "Chart View", "List View"])

    # Render each view
    render_map_view(tab1, parkings, selected_city, selected_city_name)
    render_chart_view(tab2, parkings)
    render_list_view(tab3, parkings)

    # Add footer
    render_footer()


if __name__ == "__main__":
    main()
