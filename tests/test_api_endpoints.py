"""
Tests for FastAPI endpoints
"""

import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "PollenPal API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "/pollen/{city}" in data["endpoints"]


class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestPollenEndpoints:
    """Tests for pollen data endpoints"""
    
    @patch('main.tracker.get_pollen_data')
    def test_get_pollen_data_success(self, mock_get_data, client, mock_pollen_data):
        """Test successful pollen data retrieval"""
        mock_get_data.return_value = mock_pollen_data
        
        response = client.get("/pollen/London")
        assert response.status_code == 200
        
        data = response.json()
        assert data["location"] == "London"
        assert "current_day" in data
        assert "forecast" in data
        assert "detailed_breakdown" in data
        assert "coordinates" in data
        
        mock_get_data.assert_called_once_with("London", "UK")
    
    @patch('main.tracker.get_pollen_data')
    def test_get_pollen_data_not_found(self, mock_get_data, client):
        """Test pollen data not found scenario"""
        mock_get_data.return_value = None
        
        response = client.get("/pollen/InvalidCity")
        assert response.status_code == 404
        
        data = response.json()
        assert "No pollen data found" in data["detail"]
    
    @patch('main.tracker.get_pollen_data')
    def test_get_pollen_data_with_country(self, mock_get_data, client, mock_pollen_data):
        """Test pollen data retrieval with custom country parameter"""
        mock_get_data.return_value = mock_pollen_data
        
        response = client.get("/pollen/London?country=GB")
        assert response.status_code == 200
        
        mock_get_data.assert_called_once_with("London", "GB")
    
    @patch('main.tracker.get_pollen_data')
    def test_get_current_pollen_success(self, mock_get_data, client, mock_pollen_data):
        """Test current pollen data endpoint"""
        mock_get_data.return_value = mock_pollen_data
        
        response = client.get("/pollen/London/current")
        assert response.status_code == 200
        
        data = response.json()
        assert data["location"] == "London"
        assert "current_day" in data
        assert "coordinates" in data
        # Should not include forecast or detailed_breakdown
        assert "forecast" not in data
        assert "detailed_breakdown" not in data
    
    @patch('main.tracker.get_pollen_data')
    def test_get_pollen_forecast_success(self, mock_get_data, client, mock_pollen_data):
        """Test pollen forecast endpoint"""
        mock_get_data.return_value = mock_pollen_data
        
        response = client.get("/pollen/London/forecast")
        assert response.status_code == 200
        
        data = response.json()
        assert data["location"] == "London"
        assert "forecast" in data
        assert "coordinates" in data
        assert len(data["forecast"]) == 2  # Based on mock data
    
    @patch('main.tracker.get_pollen_data')
    def test_get_detailed_breakdown_success(self, mock_get_data, client, mock_pollen_data):
        """Test detailed breakdown endpoint"""
        mock_get_data.return_value = mock_pollen_data
        
        response = client.get("/pollen/London/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["location"] == "London"
        assert "detailed_breakdown" in data
        assert "current_day" in data
        assert "coordinates" in data
        
        # Check detailed breakdown structure
        breakdown = data["detailed_breakdown"]
        assert "grass" in breakdown
        assert "trees" in breakdown
        assert "weeds" in breakdown
    
    @patch('main.tracker.get_pollen_data')
    @patch('main.tracker.get_health_advice')
    def test_get_health_advice_success(self, mock_get_advice, mock_get_data, client, mock_pollen_data):
        """Test health advice endpoint"""
        mock_get_data.return_value = mock_pollen_data
        mock_advice = {
            "advice": ["HIGH ALERT: Grass pollen levels are high", "Stay indoors during peak hours"],
            "alert_level": "high",
            "high_levels": ["grass"],
            "moderate_levels": ["trees"]
        }
        mock_get_advice.return_value = mock_advice
        
        response = client.get("/pollen/London/advice")
        assert response.status_code == 200
        
        data = response.json()
        assert data["alert_level"] == "high"
        assert "advice" in data
        assert "high_levels" in data
        assert "moderate_levels" in data
        assert len(data["advice"]) >= 1
        
        mock_get_advice.assert_called_once_with(mock_pollen_data)


class TestErrorHandling:
    """Tests for error handling scenarios"""
    
    def test_invalid_endpoint(self, client):
        """Test invalid endpoint returns 404"""
        response = client.get("/invalid/endpoint")
        assert response.status_code == 404
    
    @patch('main.tracker.get_pollen_data')
    def test_empty_city_parameter(self, mock_get_data, client):
        """Test empty city parameter handling"""
        response = client.get("/pollen/")
        assert response.status_code == 404  # FastAPI returns 404 for missing path parameter


class TestPostcodeHandling:
    """Tests for UK postcode handling"""
    
    @patch('main.tracker.get_pollen_data')
    def test_postcode_with_space(self, mock_get_data, client, mock_pollen_data):
        """Test postcode with space"""
        mock_get_data.return_value = mock_pollen_data
        
        response = client.get("/pollen/SW1A 1AA")
        assert response.status_code == 200
        
        mock_get_data.assert_called_once_with("SW1A 1AA", "UK")
    
    @patch('main.tracker.get_pollen_data')
    def test_postcode_without_space(self, mock_get_data, client, mock_pollen_data):
        """Test postcode without space"""
        mock_get_data.return_value = mock_pollen_data
        
        response = client.get("/pollen/SW1A1AA")
        assert response.status_code == 200
        
        mock_get_data.assert_called_once_with("SW1A1AA", "UK") 