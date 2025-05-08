"""Data sources package for parking data."""

from ..core.data_source import DataSourceRegistry
from .basel import BaselParkingDataSource
from .bern import BernParkingDataSource
from .lucerne import LucerneParkingDataSource
from .zurich import ZurichParkingDataSource

# Create and populate the registry
registry = DataSourceRegistry()

# Register data sources
registry.register(ZurichParkingDataSource())
registry.register(BernParkingDataSource())
registry.register(BaselParkingDataSource())
registry.register(LucerneParkingDataSource())