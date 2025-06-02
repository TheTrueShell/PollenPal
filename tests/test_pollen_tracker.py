"""
Tests for PollenTracker class
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from fastapi import HTTPException

from src.pollenpal.core.tracker import PollenTracker


class TestPollenTrackerInit:
    """Tests for PollenTracker initialisation"""
    
    def test_init_sets_base_url(self):
        """Test that initialisation sets the correct base URL"""
        tracker = PollenTracker()
        expected_url = "https://www.kleenex.co.uk/api/sitecore/Pollen/GetPollenContentCountryCity"
        assert tracker.base_url == expected_url
    
    def test_init_creates_session(self):
        """Test that initialisation creates a requests session"""
        tracker = PollenTracker()
        assert isinstance(tracker.session, requests.Session)
    
    def test_session_headers_setup(self):
        """Test that session headers are properly configured"""
        tracker = PollenTracker()
        headers = tracker.session.headers
        
        # Check key headers
        assert headers["accept"] == "*/*"
        assert headers["content-type"] == "application/x-www-form-urlencoded; charset=UTF-8"
        assert headers["origin"] == "https://www.kleenex.co.uk"
        assert headers["referer"] == "https://www.kleenex.co.uk/pollen-count"
        assert "user-agent" in headers
    
    def test_session_cookies_setup(self):
        """Test that session cookies are properly configured"""
        tracker = PollenTracker()
        cookies = tracker.session.cookies
        
        assert cookies.get("shell#lang") == "en"
        assert cookies.get("deviceType") == "desktop"
        assert "BIGipServerwww.v3.kleenex.com_pool" in cookies


class TestGetPollenData:
    """Tests for get_pollen_data method"""
    
    @patch('src.pollenpal.core.tracker.PollenTracker.parse_html_response')
    def test_successful_request(self, mock_parse, mock_html_response):
        """Test successful pollen data request"""
        tracker = PollenTracker()
        
        # Mock the session.post response
        mock_response = Mock()
        mock_response.text = mock_html_response
        mock_response.raise_for_status.return_value = None
        tracker.session.post = Mock(return_value=mock_response)
        
        # Mock parse_html_response return
        expected_data = {"location": "London", "current_day": {}}
        mock_parse.return_value = expected_data
        
        result = tracker.get_pollen_data("London", "UK")
        
        # Verify the request was made correctly
        tracker.session.post.assert_called_once_with(
            tracker.base_url,
            data={"city": "London", "country": "UK"}
        )
        
        # Verify parsing was called
        mock_parse.assert_called_once_with(mock_html_response)
        
        # Verify result
        assert result == expected_data
    
    def test_empty_response(self):
        """Test handling of empty response"""
        tracker = PollenTracker()
        
        # Mock empty response
        mock_response = Mock()
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None
        tracker.session.post = Mock(return_value=mock_response)
        
        result = tracker.get_pollen_data("London", "UK")
        assert result is None
    
    def test_request_exception(self):
        """Test handling of request exceptions"""
        tracker = PollenTracker()
        
        # Mock request exception
        tracker.session.post = Mock(side_effect=requests.RequestException("Network error"))
        
        with pytest.raises(requests.RequestException):
            tracker.get_pollen_data("London", "UK")
    
    def test_default_country_parameter(self):
        """Test default country parameter"""
        tracker = PollenTracker()
        
        mock_response = Mock()
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None
        tracker.session.post = Mock(return_value=mock_response)
        
        tracker.get_pollen_data("London")
        
        tracker.session.post.assert_called_once_with(
            tracker.base_url,
            data={"city": "London", "country": "UK"}
        )


class TestParseHtmlResponse:
    """Tests for parse_html_response method"""
    
    def test_parse_complete_html(self, mock_html_response):
        """Test parsing complete HTML response"""
        tracker = PollenTracker()
        result = tracker.parse_html_response(mock_html_response)
        
        # Check basic structure
        assert "location" in result
        assert "coordinates" in result
        assert "current_day" in result
        assert "forecast" in result
        assert "detailed_breakdown" in result
        
        # Check location extraction
        assert result["location"] == "London"
        
        # Check coordinates
        assert result["coordinates"]["latitude"] == "51.5074"
        assert result["coordinates"]["longitude"] == "-0.1278"
        
        # Check current day data
        current_day = result["current_day"]
        assert current_day["day_name"] == "Today"
        assert current_day["day_number"] == "15"
        assert current_day["grass"]["level"] == "High"
        assert current_day["trees"]["level"] == "Moderate"
        assert current_day["weeds"]["level"] == "Low"
        
        # Check detailed breakdown
        breakdown = result["detailed_breakdown"]
        assert "grass" in breakdown
        assert breakdown["grass"]["level"] == "High"
        assert breakdown["grass"]["ppm"] == "50-100 ppm"
    
    def test_parse_empty_html(self):
        """Test parsing empty HTML"""
        tracker = PollenTracker()
        result = tracker.parse_html_response("<html></html>")
        
        # Should return default structure with empty values
        assert result["location"] == ""
        assert result["coordinates"]["latitude"] == ""
        assert result["coordinates"]["longitude"] == ""
        assert result["current_day"] == {}
        assert result["forecast"] == []
        assert result["detailed_breakdown"] == {}
    
    def test_parse_malformed_html(self):
        """Test parsing malformed HTML"""
        tracker = PollenTracker()
        malformed_html = "<html><div>incomplete"
        
        # Should not raise exception and return default structure
        result = tracker.parse_html_response(malformed_html)
        assert isinstance(result, dict)
        assert "location" in result 