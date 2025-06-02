# PollenPal API 🌾

A production-ready FastAPI-based REST API for tracking UK pollen levels and forecasts. Get real-time pollen data, 5-day forecasts, and personalised health advice for any UK location.

## Features

- 🌍 **Real-time pollen data** for any UK city or postcode
- 📅 **5-day pollen forecast** with detailed breakdowns
- 🏥 **Health advice** tailored to current pollen conditions
- 🔬 **Detailed pollen analysis** by type (grass, trees, weeds)
- 📍 **Location coordinates** for mapping integration
- 🚀 **Fast and reliable** FastAPI-based REST API
- 📚 **Interactive documentation** with Swagger UI
- 🖥️ **Command-line interface** for terminal usage
- 🐳 **Production-ready** with Docker and automated deployment
- 🔒 **Security-focused** with Nginx, SSL, and rate limiting
- 📊 **Monitoring** with health checks and comprehensive logging

## Quick Start

### Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd PollenPal

# Install dependencies
python scripts/run.py install

# Start development server
python scripts/run.py dev
```

The API will be available at `http://localhost:3000`

### Production Deployment

```bash
# Build production image
python scripts/run.py build

# Deploy to production
python scripts/run.py deploy

# Check status
python scripts/run.py status
```

See [Production Deployment Guide](docs/PRODUCTION.md) for detailed instructions.

## Script Commands

Our script runner provides npm-like commands for all development and production tasks:

### Development
```bash
python scripts/run.py dev              # Start development server
python scripts/run.py dev:docker       # Start dev server in Docker
python scripts/run.py install          # Install dependencies
```

### Testing
```bash
python scripts/run.py test             # Run all tests
python scripts/run.py test:unit        # Unit tests only
python scripts/run.py test:docker      # Docker container tests
python scripts/run.py lint             # Code quality checks
python scripts/run.py lint:fix         # Fix formatting issues
```

### Build & Deploy
```bash
python scripts/run.py build            # Build production image
python scripts/run.py deploy           # Deploy to production
python scripts/run.py start            # Start services
python scripts/run.py stop             # Stop services
python scripts/run.py logs             # View logs
python scripts/run.py health           # Health check
```

Run `python scripts/run.py help` to see all available commands.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Clone the repository
git clone <your-repo-url>
cd PollenPal

# Install dependencies and the package in development mode
uv sync
uv pip install -e .

# Run the API server
python scripts/run.py dev
```

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

### Base URL: `http://localhost:3000` (dev) / `http://localhost:8000` (prod)

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

## Production Features

### Docker Support

- **Multi-stage builds** for optimised production images
- **Non-root user** for enhanced security
- **Health checks** for container monitoring
- **Automatic restarts** with proper error handling

### Load Balancing & Scaling

- **Nginx reverse proxy** with rate limiting
- **Horizontal scaling** support (multiple API instances)
- **SSL/TLS termination** with modern cipher suites
- **Gzip compression** for improved performance

### Monitoring & Logging

- **Structured logging** with configurable levels
- **Health check endpoints** for monitoring systems
- **Comprehensive error handling** with proper HTTP status codes
- **Request/response logging** for debugging

### Security

- **Rate limiting** to prevent abuse
- **CORS configuration** for web applications
- **Security headers** (HSTS, X-Frame-Options, etc.)
- **Input validation** with Pydantic models

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
│   ├── run.py                  # Main script runner (npm-like commands)
│   ├── build.py                # Production build script
│   ├── deploy.py               # Deployment script
│   ├── test.py                 # Comprehensive test runner
│   ├── run_dev.py              # Development server script
│   └── run_dev_uv.py           # Alternative dev script
├── nginx/
│   └── nginx.conf              # Nginx configuration
├── docs/
│   ├── PRODUCTION.md           # Production deployment guide
│   └── RESTRUCTURE.md          # Project restructuring documentation
├── Dockerfile                  # Multi-stage production Dockerfile
├── docker-compose.yml          # Development and production services
├── .dockerignore               # Docker build context exclusions
├── env.example                 # Environment configuration template
├── pyproject.toml              # Project configuration
├── pytest.ini                 # Test configuration
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

### Running in Development

```bash
# Run API server with auto-reload
python scripts/run.py dev

# Or using uvicorn directly
uvicorn src.pollenpal.api.main:app --reload --host 0.0.0.0 --port 3000

# Run CLI directly (without installation)
python -m src.pollenpal.cli.main London

# Run CLI in interactive mode
python -m src.pollenpal.cli.main --interactive
```

### Testing

Run the comprehensive test suite:

```bash
# Run all tests
python scripts/run.py test

# Run specific test types
python scripts/run.py test:unit
python scripts/run.py test:integration
python scripts/run.py test:docker

# Run tests with coverage
pytest --cov=src/pollenpal

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

### Code Quality

Format and lint your code:

```bash
# Check code quality
python scripts/run.py lint

# Fix formatting issues
python scripts/run.py lint:fix

# Or run tools directly
black src/ tests/
isort src/ tests/
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:3000/docs (dev) / http://localhost:8000/docs (prod)
- **ReDoc**: http://localhost:3000/redoc (dev) / http://localhost:8000/redoc (prod)

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
- **Production Ready**: Docker, monitoring, and deployment automation

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
- `429 Too Many Requests`: Rate limit exceeded

## Rate Limiting

The production deployment includes rate limiting:
- **Development**: No limits
- **Production**: 100 requests per minute per IP (configurable)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite: `python scripts/run.py test`
6. Format your code: `python scripts/run.py lint:fix`
7. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues, questions, or contributions, please open an issue on the repository.

For production deployment help, see the [Production Deployment Guide](docs/PRODUCTION.md).

---

**Note**: This API is for educational and personal use. Please respect the terms of service of the underlying data providers.
