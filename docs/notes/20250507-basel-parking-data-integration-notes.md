# Basel Parking Data Integration - Notes

## Implementation: Basel Parking Data
- Completed on: 2025-05-07 16:45 UTC
- Completed by: Sascha Corti

### Major files added, updated, removed
- Created `/src/parkings_ch_api/data/parkings/basel.json` with static data for Basel parkings
- Created `/src/parkings_ch_api/data_sources/basel.py` with Basel data source implementation
- Updated `/src/parkings_ch_api/data_sources/__init__.py` to register the Basel data source

### Major features added, updated, removed
- Added Basel as a new city with 16 parking facilities
- Implemented real-time data fetching from the official Basel parking JSON API
- Integrated location data including coordinates and addresses for all facilities
- Created a mapping system between API identifiers and our internal IDs

### Patterns, abstractions, data structures, algorithms, etc.
- Used the same hybrid data approach as other cities for consistent architecture
- Fetched real-time availability from the official JSON API (https://data.bs.ch/api/v2/catalog/datasets/100088/exports/json)
- Used static data combined with real-time data for a complete parking information
- Enhanced JSON parsing to handle already-parsed JSON data from the API client

### Governing design principles
- Single source of truth: Static data stored in JSON, dynamic data fetched from the official API
- Separation of concerns: Data source handles data retrieval, API layer handles presentation
- Extensibility: Following the same pattern as other cities makes adding more cities easier
- Resilience: System works with mix of API and static data sources

### Technical Notes
- The Basel parking data is available via a JSON API from the Basel open data portal
- The API provides real-time available spaces, total spaces, and status information
- Parking facilities in the API are identified by an 'id2' field, which we map to our internal IDs
- The API also provides geographic coordinates and addresses, which we can use directly
- For some properties (such as a null 'total_spaces'), we fall back to static data
- The BaselParkingDataSource handles both parsing already-parsed JSON and string JSON

## Update: Data Consistency Fixes - 2025-05-07 17:30 UTC
- Fixed an issue where some Basel parkings had more available spaces than total spaces
- Implemented data validation to ensure available spaces never exceed total spaces
- Updated Streamlit UI to handle invalid occupancy percentages
- Enhanced chart components to ensure data consistency across all views
- Improved error handling for edge cases in the Basel data source