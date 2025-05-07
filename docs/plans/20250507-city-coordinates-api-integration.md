# City Coordinates in API Layer and Streamlit API Integration

- [x] Phase 1: Setup City Data in API Layer
- [x] Task 1.1: Create a JSON file with city coordinates in the API layer
- [x] Task 1.2: Update the City model to include latitude and longitude
- [x] Task 1.3: Create utility functions to load city data

- [x] Phase 2: Update API Routes
- [x] Task 2.1: Update the cities endpoint to include coordinates from JSON file
- [x] Task 2.2: Update the city-specific endpoint to include coordinates

- [x] Phase 3: Update Streamlit App
- [x] Task 3.1: Modify Streamlit app to use the API client for getting cities
- [x] Task 3.2: Update Streamlit app to get parkings from API
- [x] Task 3.3: Implement async-to-sync wrapper for Streamlit compatibility
- [x] Task 3.4: Fix API client to include correct API endpoint prefix

## Success Criteria

- City coordinates are stored in the API layer and not hardcoded in the Streamlit app
- Streamlit app fetches all parkings from the API, not just the 3 hardcoded ones
- All changes are properly integrated and tested
- Streamlit UI displays all parkings returned by the API
