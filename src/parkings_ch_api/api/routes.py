"""API endpoints for parking data."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query

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
    
    for source in registry.get_all_sources():
        cities.append(
            City(
                id=source.city_id,
                name=source.city_name,
                last_updated=source.last_updated,
            )
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
        return await source.get_data()
    except DataSourceError as e:
        logger.error(f"Error getting parking data: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error getting parking data: {str(e)}")


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
        logger.error(f"Error getting parking data: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error getting parking data: {str(e)}")


@router.get("/health", summary="Health check endpoint")
async def health_check() -> dict:
    """Health check endpoint.
    
    Returns:
        dict: Status information
    """
    return {"status": "ok", "version": "0.1.0"}
