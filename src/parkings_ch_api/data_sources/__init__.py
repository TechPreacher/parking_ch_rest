"""Data sources package for parking data."""

from ..core.data_source import DataSourceRegistry
from .zurich import ZurichParkingDataSource

# Create and populate the registry
registry = DataSourceRegistry()

# Register data sources
registry.register(ZurichParkingDataSource())