"""Core data models for the parking data API."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ParkingStatus(str, Enum):
    """Enumeration of possible parking facility statuses."""

    OPEN = "open"
    CLOSED = "closed"
    UNKNOWN = "unknown"


class Parking(BaseModel):
    """Model representing a parking facility."""

    id: str = Field(..., description="Unique identifier for the parking facility")
    name: str = Field(..., description="Name of the parking facility")
    city: str = Field(..., description="City where the parking facility is located")
    available_spaces: int = Field(..., description="Number of available parking spaces")
    total_spaces: int = Field(..., description="Total number of parking spaces")
    status: ParkingStatus = Field(
        default=ParkingStatus.UNKNOWN,
        description="Current status of the parking facility",
    )
    latitude: float | None = Field(
        None,
        description="Latitude coordinate of the parking facility",
    )
    longitude: float | None = Field(
        None,
        description="Longitude coordinate of the parking facility",
    )
    last_updated: datetime = Field(..., description="Timestamp of when the data was last updated")


class City(BaseModel):
    """Model representing a city with parking facilities."""

    id: str = Field(..., description="Unique identifier for the city")
    name: str = Field(..., description="Name of the city")
    country_code: str = Field(default="CH", description="Country code (ISO 3166-1 alpha-2)")
    latitude: float | None = Field(
        None,
        description="Latitude coordinate of the city center",
    )
    longitude: float | None = Field(
        None,
        description="Longitude coordinate of the city center",
    )
    parkings: list[Parking] = Field(
        default_factory=list,
        description="List of parking facilities in the city",
    )
    last_updated: datetime | None = Field(
        None,
        description="Timestamp of when the data was last updated",
    )


class CityList(BaseModel):
    """Model representing a list of cities."""

    cities: list[City] = Field(..., description="List of cities with parking data available")
