#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Streamlit frontend for the Swiss Parking API.

This module serves as the entry point for the Streamlit web application.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from parkings_ch_api.config.settings import get_settings
from parkings_ch_frontend.api_client import ApiClient
from parkings_ch_frontend.components.charts import (
    create_availability_chart,
    create_occupancy_gauge_chart,
    create_trend_chart,
)
from parkings_ch_frontend.components.map import display_map

# Configure the page
st.set_page_config(
    page_title="Swiss Parking Spaces",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=60)
def get_cities() -> List[Dict[str, Any]]:
    """Get list of available cities from the API.

    Returns:
        List[Dict[str, Any]]: List of city information
    """
    # For initial setup, we'll use hardcoded data
    # In a real implementation, this would make an API call using the ApiClient
    return [
        {"id": "zurich", "name": "Zürich", "latitude": 47.3769, "longitude": 8.5417},
        {"id": "bern", "name": "Bern", "latitude": 46.9480, "longitude": 7.4474},
        {"id": "basel", "name": "Basel", "latitude": 47.5596, "longitude": 7.5886},
        {"id": "geneva", "name": "Geneva", "latitude": 46.2044, "longitude": 6.1432},
        {"id": "lausanne", "name": "Lausanne", "latitude": 46.5197, "longitude": 6.6323},
    ]


@st.cache_data(ttl=30)
def get_parkings(city_id: str) -> List[Dict[str, Any]]:
    """Get parking information for a specific city.

    Args:
        city_id: City identifier

    Returns:
        List[Dict[str, Any]]: List of parking information
    """
    # For initial setup, we'll use hardcoded data
    # In a real implementation, this would make an API call using the ApiClient
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
    else:
        return []


def main() -> None:
    """Main function for the Streamlit app."""
    st.title("🅿️ Swiss Parking Spaces")
    st.write("Find available parking spaces in Swiss cities")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    cities = get_cities()
    city_names = [city["name"] for city in cities]
    city_ids = [city["id"] for city in cities]
    city_dict = dict(zip(city_names, city_ids))
    
    selected_city_name = st.sidebar.selectbox("Select a city", city_names, key="city_selector")
    selected_city_id = city_dict[selected_city_name]
    
    # Get selected city information
    selected_city = next((city for city in cities if city["id"] == selected_city_id), cities[0])
    
    # Get parking information for the selected city
    parkings = get_parkings(selected_city_id)
    
    # Display tabs for different views
    tab1, tab2, tab3 = st.tabs(["Map View", "Chart View", "List View"])
    
    with tab1:
        st.header(f"Parking Map for {selected_city_name}")
        if parkings:
            display_map(
                parkings, 
                (selected_city["latitude"], selected_city["longitude"]),
                width=1000,
                height=600,
            )
        else:
            st.write("No parking data available for this city")
    
    with tab2:
        st.header("Parking Availability")
        if parkings:
            fig = create_availability_chart(parkings)
            st.plotly_chart(fig, use_container_width=True, key="availability_chart")
            
            # Add historical trend chart (demo with static data)
            st.subheader("Availability Trend (24h)")
            st.info("This is a demonstration with simulated data. In a production environment, this would show real historical data.")
            
            # Simulate historical data for the first parking
            if parkings:
                import datetime
                import random
                
                parking = parkings[0]
                history = []
                
                now = datetime.datetime.now()
                for i in range(24, -1, -1):
                    history.append({
                        "timestamp": (now - datetime.timedelta(hours=i)).isoformat(),
                        "available_spaces": max(0, min(parking["total_spaces"], 
                                               int(parking["available_spaces"] + random.randint(-50, 50)))),
                        "total_spaces": parking["total_spaces"],
                    })
                
                trend_fig = create_trend_chart(history, parking["name"])
                st.plotly_chart(trend_fig, use_container_width=True, key="trend_chart")
        else:
            st.write("No parking data available for this city")
    
    with tab3:
        st.header("List of Parkings")
        if parkings:
            for parking in parkings:
                occupancy_percentage = (
                    (parking["total_spaces"] - parking["available_spaces"]) 
                    / parking["total_spaces"] * 100
                )
                
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.subheader(parking["name"])
                    st.write(parking["address"])
                with col2:
                    st.metric(
                        "Available Spaces", 
                        parking["available_spaces"],
                        f"{parking['available_spaces'] - 100}" if parking['id'] == 'parking1' else None,
                    )
                with col3:
                    st.progress(min(occupancy_percentage / 100, 1.0))
                    st.write(f"{occupancy_percentage:.1f}% occupied")
                st.write("---")
        else:
            st.write("No parking data available for this city")
    
    # Add footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
        **About this app**
        
        This application shows real-time information about parking availability in Swiss cities.
        
        Data is refreshed every 5 minutes.
        
        Created by Sascha Corti
        """
    )


if __name__ == "__main__":
    main()
