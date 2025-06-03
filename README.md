# PollenPal API 🌾

A FastAPI-based REST API for tracking UK pollen levels and forecasts. Get real-time pollen data, 5-day forecasts, and personalised health advice for any UK location.

## Features

- 🌍 **Real-time pollen data** for any UK city or postcode
- 📅 **5-day pollen forecast** with detailed breakdowns
- 🏥 **Health advice** tailored to current pollen conditions
- 🔬 **Detailed pollen analysis** by type (grass, trees, weeds)
- 📍 **Location coordinates** for mapping integration
- 🚀 **Fast and reliable** FastAPI-based REST API
- 📚 **Interactive documentation** with Swagger UI
- 🖥️ **Command-line interface** for terminal usage

## Quick Start

### Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Clone the repository
git clone <your-repo-url>
cd PollenPal

# Install dependencies and the package in development mode
uv sync
uv pip install -e .

# Run the API server
python scripts/run_dev.py
# Or alternatively:
uv run scripts/run_dev_uv.py
```

The API will be available at `http://localhost:3000`

### Alternative Installation

If you prefer using pip:

```bash
# Install dependencies and package in development mode
pip install -e .

# Run the API server
python scripts/run_dev.py

# Or use uvicorn directly
uvicorn src.pollenpal.api.main:app --reload --port 3000
```

### CLI Installation

After installing the package, you can use the command-line interface:

```bash
# The CLI is automatically available after installation
pollenpal London
pollenpal "SW1A 1AA" --forecast --advice
```

## API Endpoints

### Base URL: `http://localhost:3000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/pollen/{city}` | GET | Complete pollen data for a location |
| `/pollen/{city}/current` | GET | Current day pollen levels only |
| `/pollen/{city}/forecast` | GET | 5-day pollen forecast |
| `/pollen/{city}/advice` | GET | Health advice based on pollen levels |
| `/pollen/{city}/detailed` | GET | Detailed pollen breakdown by type |
| `/health` | GET | API health check |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

## Usage Examples

### API Usage

#### Get Current Pollen Data

```bash
# For a city
curl "http://localhost:3000/pollen/London"

# For a postcode
curl "http://localhost:3000/pollen/SW1A%201AA"
```

#### Get 5-Day Forecast

```bash
curl "http://localhost:3000/pollen/Manchester/forecast"
```

#### Get Health Advice

```bash
curl "http://localhost:3000/pollen/Birmingham/advice"
```

### CLI Usage

```bash
# Basic pollen check
pollenpal London

# Get forecast and advice
pollenpal Manchester --forecast --advice

# Detailed analysis
pollenpal "M1 1AA" --detailed

# Interactive mode
pollenpal --interactive

# JSON output
pollenpal London --json
```

### Response Examples

#### Current Pollen Data
```json
{
  "location": "London, UK",
  "coordinates": {
    "latitude": "51.5074",
    "longitude": "-0.1278"
  },
  "current_day": {
    "day_name": "Today",
    "day_number": "15",
    "grass": {
      "level": "High",
      "count": "8",
      "detail": "Timothy,45,high|Ryegrass,32,moderate"
    },
    "trees": {
      "level": "Low",
      "count": "2",
      "detail": "Oak,5,low|Birch,3,low"
    },
    "weeds": {
      "level": "Moderate",
      "count": "4",
      "detail": "Nettle,12,moderate|Plantain,8,low"
    }
  },
  "forecast": [...],
  "detailed_breakdown": {...}
}
```

#### Health Advice
```json
{
  "advice": [
    "HIGH ALERT: Grass pollen levels are high",
    "Stay indoors during peak hours (5-10 AM and dusk)",
    "Keep windows closed",
    "Consider antihistamines",
    "Wear wraparound sunglasses outdoors",
    "Check forecast daily",
    "Shower after being outdoors",
    "Dry clothes indoors",
    "Use HEPA air filters"
  ],
  "alert_level": "high",
  "high_levels": ["grass"],
  "moderate_levels": ["weeds"]
}
```

## Docker Deployment 🐳

For easy deployment and production use, PollenPal includes comprehensive Docker support with automated deployment scripts.

### Quick Docker Start

**Linux/macOS:**
```bash
# Simple development deployment
./scripts/deploy.sh

# Production deployment with nginx reverse proxy
./scripts/deploy.sh prod --build
```

**Windows (PowerShell):**
```powershell
# Simple development deployment
.\scripts\deploy.ps1

# Production deployment with nginx reverse proxy
.\scripts\deploy.ps1 prod -Build
```

**Windows (Command Prompt):**
```cmd
REM Simple development deployment
scripts\deploy.bat

REM Production deployment with nginx reverse proxy
scripts\deploy.bat prod --build
```

### Manual Docker Commands

```bash
# Build and run with docker-compose
docker-compose up --build

# Production deployment with nginx
docker-compose -f docker-compose.prod.yml up --build

# Run in background
docker-compose up -d --build
```

### Docker Features

- ✅ **Multi-stage builds** for optimised image size
- ✅ **Non-root user** for enhanced security
- ✅ **Health checks** for monitoring
- ✅ **Nginx reverse proxy** for production
- ✅ **Rate limiting** and security headers
- ✅ **Resource limits** for production stability
- ✅ **Automated deployment scripts** for all platforms

### Accessing the Dockerised API

- **Development**: `http://localhost:3000`
- **Production** (with nginx): `http://localhost`
- **Documentation**: `/docs` endpoint
- **Health Check**: `/health` endpoint

For detailed Docker documentation, see [`docker/README.md`](docker/README.md).

## Development

### Project Structure

```
PollenPal/
├── src/
│   └── pollenpal/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── main.py         # FastAPI application and routes
│       │   └── models.py       # Pydantic models
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py         # CLI interface and formatting
│       └── core/
│           ├── __init__.py
│           ├── tracker.py      # Shared PollenTracker class
│           └── health.py       # Health advice logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test configuration and fixtures
│   ├── test_api_endpoints.py   # API endpoint tests
│   ├── test_models.py          # Pydantic model tests
│   ├── test_pollen_tracker.py  # Core tracker tests
│   ├── test_health.py          # Health advice tests
│   └── test_integration.py     # Integration tests
├── scripts/
│   └── run_dev.py              # Development server script
├── docs/
│   └── RESTRUCTURE.md          # Project restructuring documentation
├── pyproject.toml              # Project configuration
├── pytest.ini                 # Test configuration
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

### Running in Development

```bash
# Run API server with auto-reload
python scripts/run_dev.py

# Or using uvicorn directly
uvicorn src.pollenpal.api.main:app --reload --host 0.0.0.0 --port 3000

# Run CLI directly (without installation)
python -m src.pollenpal.cli.main London

# Run CLI in interactive mode
python -m src.pollenpal.cli.main --interactive
```

### Testing

Run the test suite to verify everything is working:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_health.py -v

# Run tests with coverage
pytest --cov=src/pollenpal

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

### Code Quality

Format and lint your code:

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Run both formatting tools
black src/ tests/ && isort src/ tests/
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## Architecture

### Modular Design

The project follows a clean modular architecture:

- **Core Module** (`src/pollenpal/core/`): Shared business logic
  - `tracker.py`: Main PollenTracker class for data fetching and parsing
  - `health.py`: Health advice generation logic

- **API Module** (`src/pollenpal/api/`): FastAPI application
  - `main.py`: FastAPI routes and application setup
  - `models.py`: Pydantic models for request/response validation

- **CLI Module** (`src/pollenpal/cli/`): Command-line interface
  - `main.py`: CLI argument parsing and display formatting

### Key Benefits

- **No Code Duplication**: Single source of truth for core functionality
- **Separation of Concerns**: Clear boundaries between API, CLI, and business logic
- **Testability**: Each module can be tested independently
- **Maintainability**: Easy to understand and modify
- **Extensibility**: New features can be added to appropriate modules

## Data Source

This API fetches data from the Kleenex UK pollen API, providing accurate and up-to-date pollen information for UK locations.

## Supported Locations

- Any UK city name (e.g., "London", "Manchester", "Edinburgh")
- UK postcodes (e.g., "SW1A 1AA", "M1 1AA")
- Major towns and villages across the UK

## Error Handling

The API provides clear error messages:

- `404 Not Found`: Location not found or no data available
- `500 Internal Server Error`: Issues fetching data from the source
- `422 Validation Error`: Invalid request parameters

## Rate Limiting

Please be respectful with API usage. The underlying data source may have rate limits.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite: `pytest`
6. Format your code: `black src/ tests/ && isort src/ tests/`
7. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Note**: This API is for educational and personal use. Please respect the terms of service of the underlying data providers.
