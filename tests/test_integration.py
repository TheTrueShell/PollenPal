"""
Integration tests for PollenPal API
"""

import pytest
from unittest.mock import patch, Mock
import requests


class TestFullAPIFlow:
    """Integration tests for complete API workflows"""
    
    @patch('requests.Session.post')
    def test_complete_pollen_data_flow(self, mock_post, client, mock_html_response):
        """Test complete flow from API request to response"""
        # Mock the external API response
        mock_response = Mock()
        mock_response.text = mock_html_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Make request to our API
        response = client.get("/pollen/London")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "location" in data
        assert "coordinates" in data
        assert "current_day" in data
        assert "forecast" in data
        assert "detailed_breakdown" in data
        
        # Verify external API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["data"]["city"] == "London"
        assert call_args[1]["data"]["country"] == "UK"
    
    @patch('requests.Session.post')
    def test_health_advice_integration(self, mock_post, client, mock_html_response):
        """Test health advice endpoint integration"""
        # Mock the external API response
        mock_response = Mock()
        mock_response.text = mock_html_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Make request to health advice endpoint
        response = client.get("/pollen/London/advice")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify health advice structure
        assert "advice" in data
        assert "alert_level" in data
        assert "high_levels" in data
        assert "moderate_levels" in data
        
        # Verify advice is generated based on pollen levels
        assert isinstance(data["advice"], list)
        assert len(data["advice"]) > 0
    
    @patch('requests.Session.post')
    def test_error_handling_integration(self, mock_post, client):
        """Test error handling in integration scenario"""
        # Mock network error
        mock_post.side_effect = requests.RequestException("Network error")
        
        # Make request
        response = client.get("/pollen/London")
        
        # Should return 500 error
        assert response.status_code == 500
        data = response.json()
        assert "Error fetching data" in data["detail"]


class TestAPIConsistency:
    """Tests for API response consistency across endpoints"""
    
    @patch('main.tracker.get_pollen_data')
    def test_location_consistency(self, mock_get_data, client, mock_pollen_data):
        """Test that location is consistent across all endpoints"""
        mock_get_data.return_value = mock_pollen_data
        
        endpoints = [
            "/pollen/London",
            "/pollen/London/current",
            "/pollen/London/forecast",
            "/pollen/London/detailed"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            assert data["location"] == "London"
    
    @patch('main.tracker.get_pollen_data')
    def test_coordinates_consistency(self, mock_get_data, client, mock_pollen_data):
        """Test that coordinates are consistent across endpoints"""
        mock_get_data.return_value = mock_pollen_data
        
        endpoints = [
            "/pollen/London",
            "/pollen/London/current",
            "/pollen/London/forecast",
            "/pollen/London/detailed"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            assert "coordinates" in data
            assert data["coordinates"]["latitude"] == "51.5074"
            assert data["coordinates"]["longitude"] == "-0.1278"


class TestRealWorldScenarios:
    """Tests simulating real-world usage scenarios"""
    
    @patch('main.tracker.get_pollen_data')
    def test_high_pollen_day_scenario(self, mock_get_data, client):
        """Test scenario with high pollen levels"""
        high_pollen_data = {
            "location": "London",
            "coordinates": {"latitude": "51.5074", "longitude": "-0.1278"},
            "current_day": {
                "day_name": "Today",
                "day_number": "15",
                "grass": {"level": "Very High", "count": "5", "detail": "Very high grass pollen"},
                "trees": {"level": "High", "count": "4", "detail": "High tree pollen"},
                "weeds": {"level": "Moderate", "count": "3", "detail": "Moderate weed pollen"}
            },
            "forecast": [],
            "detailed_breakdown": {}
        }
        mock_get_data.return_value = high_pollen_data
        
        # Test advice endpoint
        response = client.get("/pollen/London/advice")
        assert response.status_code == 200
        
        data = response.json()
        assert data["alert_level"] == "high"
        assert len(data["high_levels"]) >= 2  # grass and trees
        assert any("HIGH ALERT" in advice for advice in data["advice"])
    
    @patch('main.tracker.get_pollen_data')
    def test_low_pollen_day_scenario(self, mock_get_data, client):
        """Test scenario with low pollen levels"""
        low_pollen_data = {
            "location": "London",
            "coordinates": {"latitude": "51.5074", "longitude": "-0.1278"},
            "current_day": {
                "day_name": "Today",
                "day_number": "15",
                "grass": {"level": "Low", "count": "1", "detail": "Low grass pollen"},
                "trees": {"level": "Low", "count": "1", "detail": "Low tree pollen"},
                "weeds": {"level": "Low", "count": "1", "detail": "Low weed pollen"}
            },
            "forecast": [],
            "detailed_breakdown": {}
        }
        mock_get_data.return_value = low_pollen_data
        
        # Test advice endpoint
        response = client.get("/pollen/London/advice")
        assert response.status_code == 200
        
        data = response.json()
        assert data["alert_level"] == "low"
        assert len(data["high_levels"]) == 0
        assert len(data["moderate_levels"]) == 0
        assert any("GOOD NEWS" in advice for advice in data["advice"]) 