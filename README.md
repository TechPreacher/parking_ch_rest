# Swiss Parking Spaces API and Dashboard

This project provides real-time information about parking spaces availability in Swiss cities through a REST API and a Streamlit web dashboard.

## Features

- **REST API** for accessing parking data
  - Get a list of supported cities
  - Query parking information for a specific city
  - Get detailed information about specific parking facilities

- **Interactive Streamlit Dashboard**
  - Interactive map with parking locations and availability status
  - Visual charts and graphs showing parking occupancy
  - Historical trends of parking availability
  - Responsive design for both desktop and mobile

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **Streamlit**: Framework for creating data applications
- **Poetry**: Dependency management
- **Pydantic**: Data validation and settings management
- **Pydantic-Settings**: Configuration management using Pydantic
- **Folium**: Interactive map visualization
- **Plotly**: Interactive charts and graphs
- **Docker**: Containerization for easy deployment

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry package manager
- Docker and Docker Compose (for containerized deployment)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd parkings_ch_rest
   ```

2. Install dependencies:
   ```
   poetry install
   ```

3. Configure environment variables (optional):
   ```
   cp src/.env.example src/.env
   ```
   Edit the `.env` file to customize settings.

### Running the Application

#### Standard Method

**Run the API server:**

```bash
poetry run python src/main.py
```

The API will be available at http://127.0.0.1:8000

**Run the Streamlit dashboard:**

```bash
poetry run streamlit run src/streamlit_app.py
```

The dashboard will be available at http://127.0.0.1:8501

#### Using Docker (Recommended for Production)

Build and start both the API and Streamlit dashboard containers:

```bash
docker-compose up -d
```

- API will be available at http://localhost:8000
- Streamlit dashboard will be available at http://localhost:8501

To stop the containers:

```bash
docker-compose down
```

To rebuild the containers after code changes:

```bash
docker-compose up -d --build
```

Note: The Dockerfiles use `requirements.txt` for dependency management instead of Poetry, making the container builds more reliable. If you update dependencies in `pyproject.toml`, remember to update `requirements.txt` accordingly.

### API Documentation

Once the API is running, you can access the Swagger UI documentation at:
```
http://127.0.0.1:8000/docs
```

## Project Structure

```
parkings_ch_rest/
│
├── docs/                        # Documentation
│   ├── notes/                   # Implementation notes
│   └── plans/                   # Implementation plans
│
├── src/                         # Source code
│   ├── main.py                  # API entry point
│   ├── streamlit_app.py         # Streamlit dashboard entry point
│   │
│   ├── parkings_ch_api/         # API package
│   │   ├── api/                 # API routes
│   │   ├── config/              # Configuration management
│   │   ├── core/                # Core functionality
│   │   ├── data_sources/        # Data source implementations
│   │   ├── models/              # Data models
│   │   └── utils/               # Utilities
│   │
│   └── parkings_ch_frontend/    # Frontend package
│       ├── api_client.py        # API client for Streamlit
│       └── components/          # UI components
│
├── tests/                       # Test suite
│   └── ...
│
├── Dockerfile.api               # Dockerfile for API server
├── Dockerfile.streamlit         # Dockerfile for Streamlit dashboard
└── docker-compose.yml           # Docker Compose configuration
```

## Adding New Data Sources

The application is designed to be easily extensible with new data sources. To add a new city's parking data:

1. Create a new file in `src/parkings_ch_api/data_sources/`
2. Implement the `DataSource` protocol
3. Register the data source in the application

See existing implementations like `zurich.py` for examples.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Sascha Corti