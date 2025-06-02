"""
Tests for Pydantic models
"""

import pytest
from pydantic import ValidationError

from main import (
    PollenLevel,
    DayForecast,
    DetailedBreakdown,
    Coordinates,
    PollenData,
    HealthAdvice
)


class TestPollenLevel:
    """Tests for PollenLevel model"""
    
    def test_valid_pollen_level(self):
        """Test creating valid PollenLevel"""
        pollen_level = PollenLevel(
            level="High",
            count="4",
            detail="High grass pollen levels"
        )
        
        assert pollen_level.level == "High"
        assert pollen_level.count == "4"
        assert pollen_level.detail == "High grass pollen levels"
    
    def test_pollen_level_with_empty_strings(self):
        """Test PollenLevel with empty strings"""
        pollen_level = PollenLevel(
            level="",
            count="",
            detail=""
        )
        
        assert pollen_level.level == ""
        assert pollen_level.count == ""
        assert pollen_level.detail == ""
    
    def test_pollen_level_missing_fields(self):
        """Test PollenLevel with missing required fields"""
        with pytest.raises(ValidationError):
            PollenLevel(level="High", count="4")  # Missing detail


class TestDayForecast:
    """Tests for DayForecast model"""
    
    def test_valid_day_forecast(self):
        """Test creating valid DayForecast"""
        day_forecast = DayForecast(
            day_name="Today",
            day_number="15",
            grass=PollenLevel(level="High", count="4", detail="High grass"),
            trees=PollenLevel(level="Moderate", count="3", detail="Moderate trees"),
            weeds=PollenLevel(level="Low", count="1", detail="Low weeds")
        )
        
        assert day_forecast.day_name == "Today"
        assert day_forecast.day_number == "15"
        assert day_forecast.grass.level == "High"
        assert day_forecast.trees.level == "Moderate"
        assert day_forecast.weeds.level == "Low"
    
    def test_day_forecast_with_dict_input(self):
        """Test DayForecast creation with dictionary input for nested models"""
        day_forecast = DayForecast(
            day_name="Tomorrow",
            day_number="16",
            grass={"level": "Moderate", "count": "3", "detail": "Moderate grass"},
            trees={"level": "Low", "count": "2", "detail": "Low trees"},
            weeds={"level": "Low", "count": "1", "detail": "Low weeds"}
        )
        
        assert isinstance(day_forecast.grass, PollenLevel)
        assert day_forecast.grass.level == "Moderate"


class TestDetailedBreakdown:
    """Tests for DetailedBreakdown model"""
    
    def test_valid_detailed_breakdown(self):
        """Test creating valid DetailedBreakdown"""
        breakdown = DetailedBreakdown(
            level="High",
            ppm="50-100 ppm"
        )
        
        assert breakdown.level == "High"
        assert breakdown.ppm == "50-100 ppm"
    
    def test_detailed_breakdown_empty_values(self):
        """Test DetailedBreakdown with empty values"""
        breakdown = DetailedBreakdown(level="", ppm="")
        
        assert breakdown.level == ""
        assert breakdown.ppm == ""


class TestCoordinates:
    """Tests for Coordinates model"""
    
    def test_valid_coordinates(self):
        """Test creating valid Coordinates"""
        coords = Coordinates(
            latitude="51.5074",
            longitude="-0.1278"
        )
        
        assert coords.latitude == "51.5074"
        assert coords.longitude == "-0.1278"
    
    def test_coordinates_as_strings(self):
        """Test that coordinates are stored as strings"""
        coords = Coordinates(latitude="51.5074", longitude="-0.1278")
        
        assert isinstance(coords.latitude, str)
        assert isinstance(coords.longitude, str)


class TestPollenData:
    """Tests for PollenData model"""
    
    def test_valid_pollen_data(self):
        """Test creating valid PollenData"""
        pollen_data = PollenData(
            location="London",
            coordinates={"latitude": "51.5074", "longitude": "-0.1278"},
            current_day={
                "day_name": "Today",
                "day_number": "15",
                "grass": {"level": "High", "count": "4", "detail": "High grass"},
                "trees": {"level": "Moderate", "count": "3", "detail": "Moderate trees"},
                "weeds": {"level": "Low", "count": "1", "detail": "Low weeds"}
            },
            forecast=[
                {
                    "day_name": "Today",
                    "day_number": "15",
                    "grass": {"level": "High", "count": "4", "detail": "High grass"},
                    "trees": {"level": "Moderate", "count": "3", "detail": "Moderate trees"},
                    "weeds": {"level": "Low", "count": "1", "detail": "Low weeds"}
                }
            ],
            detailed_breakdown={
                "grass": {"level": "High", "ppm": "50-100 ppm"},
                "trees": {"level": "Moderate", "ppm": "20-50 ppm"}
            }
        )
        
        assert pollen_data.location == "London"
        assert isinstance(pollen_data.coordinates, Coordinates)
        assert isinstance(pollen_data.current_day, DayForecast)
        assert len(pollen_data.forecast) == 1
        assert isinstance(pollen_data.forecast[0], DayForecast)
        assert "grass" in pollen_data.detailed_breakdown
        assert isinstance(pollen_data.detailed_breakdown["grass"], DetailedBreakdown)
    
    def test_pollen_data_empty_forecast(self):
        """Test PollenData with empty forecast list"""
        pollen_data = PollenData(
            location="London",
            coordinates={"latitude": "51.5074", "longitude": "-0.1278"},
            current_day={
                "day_name": "Today",
                "day_number": "15",
                "grass": {"level": "High", "count": "4", "detail": "High grass"},
                "trees": {"level": "Moderate", "count": "3", "detail": "Moderate trees"},
                "weeds": {"level": "Low", "count": "1", "detail": "Low weeds"}
            },
            forecast=[],
            detailed_breakdown={}
        )
        
        assert len(pollen_data.forecast) == 0
        assert len(pollen_data.detailed_breakdown) == 0


class TestHealthAdvice:
    """Tests for HealthAdvice model"""
    
    def test_valid_health_advice(self):
        """Test creating valid HealthAdvice"""
        health_advice = HealthAdvice(
            advice=["Stay indoors", "Take antihistamines"],
            alert_level="high",
            high_levels=["grass", "trees"],
            moderate_levels=["weeds"]
        )
        
        assert len(health_advice.advice) == 2
        assert health_advice.alert_level == "high"
        assert "grass" in health_advice.high_levels
        assert "weeds" in health_advice.moderate_levels
    
    def test_health_advice_empty_lists(self):
        """Test HealthAdvice with empty lists"""
        health_advice = HealthAdvice(
            advice=[],
            alert_level="low",
            high_levels=[],
            moderate_levels=[]
        )
        
        assert len(health_advice.advice) == 0
        assert len(health_advice.high_levels) == 0
        assert len(health_advice.moderate_levels) == 0
    
    def test_health_advice_alert_levels(self):
        """Test different alert levels"""
        for level in ["low", "moderate", "high", "unknown"]:
            health_advice = HealthAdvice(
                advice=["General advice"],
                alert_level=level,
                high_levels=[],
                moderate_levels=[]
            )
            assert health_advice.alert_level == level


class TestModelIntegration:
    """Integration tests for models working together"""
    
    def test_complete_api_response_structure(self):
        """Test that models can represent a complete API response"""
        # This tests the full structure that would be returned by the API
        complete_data = {
            "location": "London",
            "coordinates": {"latitude": "51.5074", "longitude": "-0.1278"},
            "current_day": {
                "day_name": "Today",
                "day_number": "15",
                "grass": {"level": "High", "count": "4", "detail": "High grass pollen"},
                "trees": {"level": "Moderate", "count": "3", "detail": "Moderate tree pollen"},
                "weeds": {"level": "Low", "count": "1", "detail": "Low weed pollen"}
            },
            "forecast": [
                {
                    "day_name": "Today",
                    "day_number": "15",
                    "grass": {"level": "High", "count": "4", "detail": "High grass pollen"},
                    "trees": {"level": "Moderate", "count": "3", "detail": "Moderate tree pollen"},
                    "weeds": {"level": "Low", "count": "1", "detail": "Low weed pollen"}
                },
                {
                    "day_name": "Tomorrow",
                    "day_number": "16",
                    "grass": {"level": "Moderate", "count": "3", "detail": "Moderate grass pollen"},
                    "trees": {"level": "Low", "count": "2", "detail": "Low tree pollen"},
                    "weeds": {"level": "Low", "count": "1", "detail": "Low weed pollen"}
                }
            ],
            "detailed_breakdown": {
                "grass": {"level": "High", "ppm": "50-100 ppm"},
                "trees": {"level": "Moderate", "ppm": "20-50 ppm"},
                "weeds": {"level": "Low", "ppm": "0-20 ppm"}
            }
        }
        
        # Should be able to create PollenData from this structure
        pollen_data = PollenData(**complete_data)
        
        # Verify the structure is preserved
        assert pollen_data.location == "London"
        assert len(pollen_data.forecast) == 2
        assert len(pollen_data.detailed_breakdown) == 3
        
        # Verify nested models are correctly instantiated
        assert isinstance(pollen_data.current_day.grass, PollenLevel)
        assert isinstance(pollen_data.forecast[0], DayForecast)
        assert isinstance(pollen_data.detailed_breakdown["grass"], DetailedBreakdown) 