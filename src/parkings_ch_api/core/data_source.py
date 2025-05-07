"""Data source interface and base classes for parking data."""

import abc
from datetime import datetime
from typing import ClassVar, Protocol

from ..core.cache import Cache
from ..models.models import City


class DataSource(Protocol):
    """Protocol defining the interface for parking data sources."""

    @property
    def name(self) -> str:
        """Return the name of the data source."""
        ...

    @property
    def city_id(self) -> str:
        """Return the city ID this data source provides data for."""
        ...

    @property
    def city_name(self) -> str:
        """Return the city name this data source provides data for."""
        ...

    @property
    def last_updated(self) -> datetime | None:
        """Return the timestamp of the last update."""
        ...

    async def fetch_data(self) -> City:
        """Fetch parking data from the source.

        Returns:
            City: City object with parking data.
        """
        ...


class BaseDataSource(abc.ABC):
    """Base abstract class for parking data sources."""

    # Class-level cache shared by all instances
    _cache: ClassVar[Cache[City]] = Cache()

    def __init__(self, city_id: str, city_name: str) -> None:
        """Initialize the data source.

        Args:
            city_id: The unique identifier for the city.
            city_name: The name of the city.
        """
        self._city_id = city_id
        self._city_name = city_name
        self._last_updated: datetime | None = None

    @property
    def name(self) -> str:
        """Return the name of the data source."""
        return self.__class__.__name__

    @property
    def city_id(self) -> str:
        """Return the city ID this data source provides data for."""
        return self._city_id

    @property
    def city_name(self) -> str:
        """Return the city name this data source provides data for."""
        return self._city_name

    @property
    def last_updated(self) -> datetime | None:
        """Return the timestamp of the last update."""
        return self._last_updated

    @property
    def cache_key(self) -> str:
        """Return the cache key for this data source.
        
        Returns:
            str: Cache key
        """
        return f"city:{self._city_id}"

    async def get_data(self) -> City:
        """Get data for the city, using cache if available.
        
        Returns:
            City: City with parking data
            
        Raises:
            Exception: If data fetching fails
        """
        # Check cache first
        cached_data = self._cache.get(self.cache_key)
        if cached_data:
            return cached_data
            
        # If not in cache, fetch fresh data
        data = await self.fetch_data()
        self._last_updated = datetime.now()
        
        # Update cache
        self._cache.set(self.cache_key, data)
        
        return data

    @abc.abstractmethod
    async def fetch_data(self) -> City:
        """Fetch parking data from the source.

        Returns:
            City: City object with parking data.
            
        Raises:
            Exception: If data fetching fails
        """


class DataSourceRegistry:
    """Registry for parking data sources."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._sources: dict[str, DataSource] = {}

    def register(self, source: DataSource) -> None:
        """Register a data source.

        Args:
            source: The data source to register.
        """
        self._sources[source.city_id] = source

    def get_source(self, city_id: str) -> DataSource | None:
        """Get a data source by city ID.

        Args:
            city_id: The city ID to get the data source for.

        Returns:
            DataSource | None: The data source, or None if not found.
        """
        return self._sources.get(city_id)

    def get_all_sources(self) -> list[DataSource]:
        """Get all registered data sources.

        Returns:
            list[DataSource]: List of all registered data sources.
        """
        return list(self._sources.values())

    def get_city_ids(self) -> list[str]:
        """Get IDs of all registered cities.

        Returns:
            list[str]: List of city IDs.
        """
        return list(self._sources.keys())
