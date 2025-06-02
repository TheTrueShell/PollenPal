"""
Pytest configuration and fixtures for PollenPal API tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.pollenpal.api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_pollen_data():
    """Mock pollen data for testing"""
    return {
        "location": "London",
        "coordinates": {
            "latitude": "51.5074",
            "longitude": "-0.1278"
        },
        "current_day": {
            "day_name": "Today",
            "day_number": "15",
            "grass": {
                "level": "High",
                "count": "4",
                "detail": "High grass pollen levels"
            },
            "trees": {
                "level": "Moderate",
                "count": "3",
                "detail": "Moderate tree pollen levels"
            },
            "weeds": {
                "level": "Low",
                "count": "1",
                "detail": "Low weed pollen levels"
            }
        },
        "forecast": [
            {
                "day_name": "Today",
                "day_number": "15",
                "grass": {"level": "High", "count": "4", "detail": "High grass pollen levels"},
                "trees": {"level": "Moderate", "count": "3", "detail": "Moderate tree pollen levels"},
                "weeds": {"level": "Low", "count": "1", "detail": "Low weed pollen levels"}
            },
            {
                "day_name": "Tomorrow",
                "day_number": "16",
                "grass": {"level": "Moderate", "count": "3", "detail": "Moderate grass pollen levels"},
                "trees": {"level": "Low", "count": "2", "detail": "Low tree pollen levels"},
                "weeds": {"level": "Low", "count": "1", "detail": "Low weed pollen levels"}
            }
        ],
        "detailed_breakdown": {
            "grass": {
                "level": "High",
                "ppm": "50-100 ppm"
            },
            "trees": {
                "level": "Moderate",
                "ppm": "20-50 ppm"
            },
            "weeds": {
                "level": "Low",
                "ppm": "0-20 ppm"
            }
        }
    }


@pytest.fixture
def mock_empty_response():
    """Mock empty response for testing error cases"""
    return None


@pytest.fixture
def mock_html_response():
    """Mock HTML response from Kleenex API"""
    return """
    <html>
        <input id="cityName" value="London" />
        <input class="pollen-lat" value="51.5074" />
        <input class="pollen-lng" value="-0.1278" />
        
        <button class="day-link active" 
                data-grass="High" data-grass-count="4" data-grass-detail="High grass pollen levels"
                data-trees="Moderate" data-trees-count="3" data-tree-detail="Moderate tree pollen levels"
                data-weeds="Low" data-weeds-count="1" data-weed-detail="Low weed pollen levels">
            <span class="day-name">Today</span>
            <span class="day-number">15</span>
        </button>
        
        <li class="diagram-container" data-details="grass">
            <p class="level-text">High</p>
            <p class="ppm-level">50-100 ppm</p>
        </li>
        
        <li class="diagram-container" data-details="trees">
            <p class="level-text">Moderate</p>
            <p class="ppm-level">20-50 ppm</p>
        </li>
        
        <li class="diagram-container" data-details="weeds">
            <p class="level-text">Low</p>
            <p class="ppm-level">0-20 ppm</p>
        </li>
    </html>
    """ 