"""API endpoints for parking data."""

from fastapi import APIRouter, HTTPException, Path

from ..core.errors import DataSourceError
from ..data_sources import registry
from ..models.models import City, CityList, Parking
from ..utils.logging import setup_logging

logger = setup_logging(__name__)

router = APIRouter(prefix="/api/v1", tags=["parking"])


@router.get("/cities", response_model=CityList, summary="Get all supported cities")
async def get_cities() -> CityList:
    """Get a list of all cities supported by the API.

    Returns:
        CityList: List of available cities
    """
    logger.info("Getting list of cities")
    cities = []

    # Import city data utility
    from ..data import load_cities_data

    cities_data = load_cities_data()

    for source in registry.get_all_sources():
        city_id = source.city_id
        city_data = cities_data.get(city_id, {})

        cities.append(
            City(
                id=city_id,
                name=source.city_name,
                latitude=city_data.get("latitude"),
                longitude=city_data.get("longitude"),
                last_updated=source.last_updated,
            ),
        )

    return CityList(cities=cities)


@router.get(
    "/cities/{city_id}",
    response_model=City,
    summary="Get parking information for a specific city",
)
async def get_city_parkings(
    city_id: str = Path(..., description="City ID"),
) -> City:
    """Get parking information for a specific city.

    Args:
        city_id: City identifier

    Returns:
        City: City with parking data

    Raises:
        HTTPException: If city is not found or data cannot be retrieved
    """
    logger.info(f"Getting parking data for city: {city_id}")

    source = registry.get_source(city_id)
    if not source:
        logger.warning(f"City not found: {city_id}")
        raise HTTPException(status_code=404, detail=f"City not found: {city_id}")

    try:
        # Get city coordinates from JSON data
        from ..data import get_city_details

        city_details = get_city_details(city_id) or {}

        # Get parking data from data source
        city = await source.get_data()

        # Add coordinates if available
        if city_details:
            city.latitude = city_details.get("latitude")
            city.longitude = city_details.get("longitude")

        return city
    except DataSourceError as e:
        error_msg = f"Error getting parking data: {e!s}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg) from e


@router.get(
    "/cities/{city_id}/parkings/{parking_id}",
    response_model=Parking,
    summary="Get information for a specific parking",
)
async def get_parking(
    city_id: str = Path(..., description="City ID"),
    parking_id: str = Path(..., description="Parking ID"),
) -> Parking:
    """Get information for a specific parking.

    Args:
        city_id: City identifier
        parking_id: Parking identifier

    Returns:
        Parking: Parking information

    Raises:
        HTTPException: If city/parking is not found or data cannot be retrieved
    """
    logger.info(f"Getting parking data for {parking_id} in city: {city_id}")

    source = registry.get_source(city_id)
    if not source:
        logger.warning(f"City not found: {city_id}")
        raise HTTPException(status_code=404, detail=f"City not found: {city_id}")

    try:
        city_data = await source.get_data()
        for parking in city_data.parkings:
            if parking.id == parking_id:
                return parking

        logger.warning(f"Parking not found: {parking_id}")
        raise HTTPException(status_code=404, detail=f"Parking not found: {parking_id}")
    except DataSourceError as e:
        error_msg = f"Error getting parking data: {e!s}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg) from e


@router.get(
    "/cities/{city_id}/parkings",
    response_model=list[Parking],
    summary="Get all parkings for a specific city",
)
async def get_city_parkings_list(
    city_id: str = Path(..., description="City ID"),
) -> list[Parking]:
    """Get all parkings for a specific city.

    Args:
        city_id: City identifier

    Returns:
        list[Parking]: List of parking data for the city

    Raises:
        HTTPException: If city is not found or data cannot be retrieved
    """
    logger.info(f"Getting parkings list for city: {city_id}")

    source = registry.get_source(city_id)
    if not source:
        logger.warning(f"City not found: {city_id}")
        raise HTTPException(status_code=404, detail=f"City not found: {city_id}")

    try:
        city = await source.get_data()
        return city.parkings
    except DataSourceError as e:
        error_msg = f"Error getting parking data: {e!s}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg) from e


@router.get("/health", summary="Health check endpoint")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        dict: Status information
    """
    return {"status": "ok", "version": "0.1.0"}
