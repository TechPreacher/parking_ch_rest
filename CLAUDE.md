# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project provides real-time information about parking spaces availability in Swiss cities through a REST API and a Streamlit web dashboard. It consists of:

1. A FastAPI backend that fetches, processes, and serves parking data
2. A Streamlit frontend that visualizes parking information with maps and charts

## Commands

### Setup and Installation

```bash
# Install dependencies
poetry install

# Run the API server
poetry run python src/main.py

# Run the Streamlit dashboard
poetry run streamlit run src/streamlit_app.py
```

### Development

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src

# Type checking
poetry run mypy .

# Linting
poetry run ruff check .

# Format code
poetry run ruff format .
```

## Architecture

### Backend (FastAPI)

The backend is organized into a modular structure:

- **API Layer**: Defines all routes and endpoints (`src/parkings_ch_api/api/routes.py`)
- **Data Sources**: Implementations for each city's parking data (`src/parkings_ch_api/data_sources/`)
- **Models**: Pydantic models for data validation (`src/parkings_ch_api/models/models.py`)
- **Core**: Interface definitions and base classes (`src/parkings_ch_api/core/`)
- **Config**: Application settings (`src/parkings_ch_api/config/`)
- **Utils**: General utilities for HTTP, logging, etc. (`src/parkings_ch_api/utils/`)

The backend follows a **data source pattern** where each city's parking data is provided by a class implementing the `DataSource` protocol. This makes it easy to add new cities.

### Frontend (Streamlit)

The Streamlit app communicates with the backend API to display:

- Interactive maps showing parking locations
- Charts visualizing parking availability
- Lists of parking facilities with key metrics

The frontend is organized into:

- **Main App**: Entry point and page layout (`src/streamlit_app.py`)
- **API Client**: For backend communication (`src/parkings_ch_frontend/api_client.py`)
- **Components**: Reusable UI elements (`src/parkings_ch_frontend/components/`)

## Key Patterns

1. **Protocol-based interfaces**: The `DataSource` protocol defines what each city data source must implement
2. **Caching**: `Cache` class provides in-memory caching for data sources
3. **Registry pattern**: The `DataSourceRegistry` manages data sources
4. **Decorator pattern**: `async_to_sync` decorator used to run async functions in Streamlit
5. **Dependency injection**: FastAPI's dependency system for configuration and services
6. **Single source of truth**: City information stored centrally in a JSON file

## Adding a New City Data Source

1. Create a new Python file in `src/parkings_ch_api/data_sources/` (e.g., `basel.py`)
2. Implement a class that extends `BaseDataSource` and implements the `fetch_data` method
3. Add the city coordinates to `src/parkings_ch_api/data/cities.json`
4. Register the data source in `src/parkings_ch_api/data_sources/__init__.py`

## Testing

The test suite uses pytest. The `/tests` directory contains base test files. New tests should follow the existing structure:

- Unit tests for individual components
- Integration tests for API endpoints

## Documentation

The `/docs` directory contains:
- Implementation notes in `/docs/notes/`
- Implementation plans in `/docs/plans/`

The Swagger API documentation is available at `http://127.0.0.1:8000/docs` when running the API server.

## Guidelines for Creating or Updating a Plan

- When creating a plan, organize it into numbered phases (e.g., "Phase 1: Setup Dependencies")
- Break down each phase into specific tasks with numeric identifiers (e.g., "Task 1.1: Add Dependencies")
- Please only create one document per plan
- Mark phases and tasks as `- [ ]` while not complete and `- [x]` once completed
- End the plan with success criteria that define when the implementation is complete
- Plans that you produce should go under `docs/plans`
- Use a consistent naming convention `YYYYMMDD-<short-description>.md` for plan files

## Guidelines for Implementing a Plan

- Code you write should go under `src`
- When coding you need to follow the plan and check off phases and tasks as they are completed
- As you complete a task, update the plan by marking that task as complete before you begin the next task
- As you complete a phase, update the plan by marking that phase as complete before you begin the next phase
- Tasks that involve tests should not be marked complete until the tests pass
- Create one coding notes file per plan, in `docs/notes` with naming convention `<plan-file-name>-notes.md`
  - Include a link to the plan file
- When you complete implementation for a plan phase, create a notes entry in the notes file for the plan and summarize the completed work as follows:

   ```markdown
   ## Phase <phase-number>: <phase-name>
   - Completed on: <current UTC date and time>
   - Completed by: <name of the person who completed the phase, not Copilot>

   ### Major files added, updated, removed
   <list of files and brief summary of changes>

   ### Major features added, updated, removed
   <list of features and brief summary of changes>

   ### Patterns, abstractions, data structures, algorithms, etc.
   <list of patterns, abstractions, data structures, algorithms, etc. and brief summary of changes>

   ### Governing design principles
   <list of design principles and brief summary of changes>

## Personal information
- Name: Sascha Corti
- Email: sascha@corti.com
- GitHub: TechPreacher
