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

## Quick Start

### Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Clone the repository
git clone <your-repo-url>
cd PollenPal

# Install dependencies
uv sync

# Run the API server
uv run python main.py
```

The API will be available at `http://localhost:8000`

### Alternative Installation

If you prefer using pip:

```bash
pip install fastapi uvicorn requests beautifulsoup4 pydantic
python main.py
```

## API Endpoints

### Base URL: `http://localhost:8000`

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
| `/redoc` | GET | Alternative API documentation |

## Usage Examples

### Get Current Pollen Data

```bash
# For a city
curl "http://localhost:8000/pollen/London"

# For a postcode
curl "http://localhost:8000/pollen/SW1A%201AA"
```

### Get 5-Day Forecast

```bash
curl "http://localhost:8000/pollen/Manchester/forecast"
```

### Get Health Advice

```bash
curl "http://localhost:8000/pollen/Birmingham/advice"
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

## Development

### Project Structure

```
PollenPal/
├── main.py              # FastAPI application
├── cli.py               # Original CLI version
├── run_dev.py           # Development server runner
├── test_api.py          # API tests
├── pyproject.toml       # Project configuration
├── README.md            # This file
└── .python-version      # Python version specification
```

### Running in Development

```bash
# Run with auto-reload for development
uv run python run_dev.py

# Or using uvicorn directly
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

Run the test suite to verify everything is working:

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest test_api.py -v
```

### Code Quality

Format and lint your code:

```bash
# Format code with black
uv run black .

# Sort imports with isort
uv run isort .

# Run both formatting tools
uv run black . && uv run isort .
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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
5. Run the test suite: `uv run pytest`
6. Format your code: `uv run black . && uv run isort .`
7. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Note**: This API is for educational and personal use. Please respect the terms of service of the underlying data providers.
