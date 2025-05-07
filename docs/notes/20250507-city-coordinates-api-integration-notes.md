# City Coordinates in API Layer and Streamlit API Integration - Notes

Link to plan: [20250507-city-coordinates-api-integration.md](../plans/20250507-city-coordinates-api-integration.md)

## Phase 1: Setup City Data in API Layer
- Completed on: 2025-05-07 14:30 UTC
- Completed by: Sascha Corti

### Major files added, updated, removed
- Created `/src/parkings_ch_api/data/cities.json` to store city coordinates data
- Created `/src/parkings_ch_api/data/__init__.py` with utility functions for loading city data
- Updated `/src/parkings_ch_api/models/models.py` to include latitude and longitude in the City model

### Major features added, updated, removed
- Added centralized city coordinates storage in JSON format
- Added utility functions to load and access city data

### Patterns, abstractions, data structures, algorithms, etc.
- Used a simple key-value JSON structure for storing city information
- Created utility functions to abstract the loading of JSON data

### Governing design principles
- Single source of truth: Moved hardcoded city coordinates from frontend to API layer
- Separation of concerns: API now handles all data concerns, frontend just displays data

## Phase 2: Update API Routes
- Completed on: 2025-05-07 15:00 UTC
- Completed by: Sascha Corti

### Major files added, updated, removed
- Updated `/src/parkings_ch_api/api/routes.py` to include coordinates in API responses

### Major features added, updated, removed
- Enhanced city endpoints to include latitude and longitude coordinates

### Patterns, abstractions, data structures, algorithms, etc.
- Used the utility functions for city data loading to integrate with the API routes

### Governing design principles
- API completeness: Ensuring the API provides all necessary data to the frontend
- Data consistency: Same coordinate data is used in all API endpoints

## Phase 3: Update Streamlit App
- Completed on: 2025-05-07 17:30 UTC
- Completed by: Sascha Corti

### Major files added, updated, removed
- Updated `/src/streamlit_app.py` to use the API client instead of hardcoded data
- Updated `/src/parkings_ch_frontend/api_client.py` to include the correct API endpoint prefix

### Major features added, updated, removed
- Added async-to-sync wrapper to handle asynchronous API calls in Streamlit
- Updated get_cities and get_parkings functions to use the API client
- Made the Streamlit app use real data from the API
- Fixed API client to include the "/api/v1" prefix in endpoint URLs
- Fixed response handling to properly extract data from CityList and City objects
- Updated type annotations to use modern Python syntax (list[dict] instead of List[Dict])
- Fixed duplicated main() call in streamlit_app.py

### Patterns, abstractions, data structures, algorithms, etc.
- Used decorator pattern for wrapping async functions in synchronous calls
- Added fallback mechanism when API is not available
- Ensured correct API endpoint construction with proper path prefixes
- Implemented proper response parsing for API responses

### Governing design principles
- Resilience: Added fallback to static data when API is unavailable
- DRY (Don't Repeat Yourself): Removed duplicate data definitions between API and frontend
- Separation of concerns: Frontend now only handles display and user interaction
- API Consistency: Updated the API client to match the FastAPI API route structure
- Type safety: Updated type annotations to use the latest Python conventions

## Additional Fixes: May 7, 2025
- Completed on: 2025-05-07 18:30 UTC
- Completed by: Sascha Corti

### Major files added, updated, removed
- Updated `/src/parkings_ch_api/api/routes.py` to add a new endpoint for retrieving parkings list
- Fixed `/src/parkings_ch_frontend/api_client.py` to use the correct endpoint
- Updated `/src/streamlit_app.py` to handle API responses properly and add error checks for chart creation

### Major features added, updated, removed
- Added a new API endpoint `/cities/{city_id}/parkings` that returns just the parkings list
- Fixed API client to use the new endpoint for retrieving parkings
- Added null-safety checks for Plotly chart creation to prevent errors
- Fixed response parsing in the Streamlit app

### Patterns, abstractions, data structures, algorithms, etc.
- Improved error handling with specific error messages
- Used defensive programming techniques to handle edge cases with null checks

### Governing design principles
- API consistency: Added an endpoint that follows REST principles to get a list of parkings
- Robustness: Added proper error handling to prevent app crashes
- User experience: Added informative messages when charts can't be created due to missing data
