"""Chart components for Streamlit frontend."""

from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st


def create_availability_chart(parkings: List[Dict[str, Any]]) -> Any:
    """Create a bar chart showing parking availability.

    Args:
        parkings: List of parking information

    Returns:
        Any: Plotly figure or None if no data available
    """
    if not parkings:
        return None

    # Filter out parkings without required data
    valid_parkings = [
        p for p in parkings 
        if "total_spaces" in p and "available_spaces" in p and p["total_spaces"] > 0
    ]
    
    if not valid_parkings:
        return None

    data = []
    for parking in valid_parkings:
        data.append(
            {
                "name": parking["name"],
                "available": parking["available_spaces"],
                "occupied": parking["total_spaces"] - parking["available_spaces"],
            }
        )

    df = pd.DataFrame(data)
    
    # Reshape data for stacked bar chart
    df_melted = pd.melt(
        df,
        id_vars=["name"],
        value_vars=["available", "occupied"],
        var_name="status",
        value_name="spaces",
    )

    fig = px.bar(
        df_melted,
        x="name",
        y="spaces",
        color="status",
        title="Parking Spaces Availability",
        color_discrete_map={"available": "green", "occupied": "red"},
        labels={"name": "Parking", "spaces": "Number of spaces", "status": "Status"},
    )

    return fig


def create_occupancy_gauge_chart(parking: Dict[str, Any]) -> Any:
    """Create a gauge chart for parking occupancy.

    Args:
        parking: Parking information

    Returns:
        Any: Plotly figure or None if insufficient data
    """
    if (
        "total_spaces" not in parking
        or "available_spaces" not in parking
        or parking["total_spaces"] == 0
    ):
        return None

    occupancy_percentage = (
        (parking["total_spaces"] - parking["available_spaces"]) / parking["total_spaces"] * 100
    )

    fig = px.pie(
        values=[occupancy_percentage, 100 - occupancy_percentage],
        names=["Occupied", "Available"],
        color=["red", "green"],
        hole=0.7,
        title=f"{parking['name']} Occupancy",
    )

    # Add text in the center
    fig.update_layout(
        annotations=[
            dict(
                text=f"{occupancy_percentage:.1f}%<br>Occupied",
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False,
            )
        ]
    )

    return fig


def create_trend_chart(parking_history: List[Dict[str, Any]], parking_name: str) -> Any:
    """Create a line chart showing parking availability trend.

    Args:
        parking_history: Historical parking data
        parking_name: Name of the parking

    Returns:
        Any: Plotly figure or None if insufficient data
    """
    if not parking_history:
        return None

    # Convert to DataFrame
    df = pd.DataFrame(parking_history)
    
    # Ensure datetime type
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Create line chart
    fig = px.line(
        df,
        x="timestamp",
        y="available_spaces",
        title=f"{parking_name} - Availability Trend",
        labels={
            "timestamp": "Time",
            "available_spaces": "Available Spaces"
        },
    )
    
    # Add reference line for total spaces if available
    if "total_spaces" in df.columns:
        fig.add_hline(
            y=df["total_spaces"].iloc[0],
            line_dash="dash",
            line_color="gray",
            annotation_text="Total Capacity",
        )
    
    return fig
