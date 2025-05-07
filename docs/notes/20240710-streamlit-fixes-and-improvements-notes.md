# Coding Notes: Streamlit App Fixes and Improvements

Link to plan: [20240710-streamlit-fixes-and-improvements.md](/Users/sascha/Code/Local/Python/parkings_ch_rest/docs/plans/20240710-streamlit-fixes-and-improvements.md)

## Phase 1: Fix Critical Issues
- Completed on: 2024-07-10T12:30:00Z
- Completed by: Sascha Corti

### Major files added, updated, removed
- Updated `/Users/sascha/Code/Local/Python/parkings_ch_rest/src/streamlit_app.py`
  - Removed unsupported `key` parameter from `st.tabs()` function
  - Kept other necessary key parameters for selectbox and plotly charts

### Major features added, updated, removed
- Fixed TypeError that was preventing the app from running properly
- Maintained the unique keys for other widgets to prevent duplicate widget ID errors

### Patterns, abstractions, data structures, algorithms, etc.
- Maintained consistent widget key naming convention for components that support it
- Removed keys from components that don't support the key parameter

### Governing design principles
- Compatibility with the installed Streamlit version
- Maintaining unique IDs for widgets that support and require keys
- Ensuring app runs without TypeErrors or other exceptions
