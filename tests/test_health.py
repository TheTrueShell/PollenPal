"""
Tests for health advice functionality
"""

import pytest

from src.pollenpal.core.health import get_health_advice


class TestGetHealthAdvice:
    """Tests for get_health_advice function"""
    
    def test_high_pollen_advice(self):
        """Test health advice for high pollen levels"""
        data = {
            "current_day": {
                "grass": {"level": "High"},
                "trees": {"level": "Moderate"},
                "weeds": {"level": "Low"}
            }
        }
        
        result = get_health_advice(data)
        
        assert result["alert_level"] == "high"
        assert "grass" in result["high_levels"]
        assert "trees" in result["moderate_levels"]
        assert len(result["advice"]) > 0
        assert any("HIGH ALERT" in advice for advice in result["advice"])
    
    def test_moderate_pollen_advice(self):
        """Test health advice for moderate pollen levels"""
        data = {
            "current_day": {
                "grass": {"level": "Moderate"},
                "trees": {"level": "Low"},
                "weeds": {"level": "Low"}
            }
        }
        
        result = get_health_advice(data)
        
        assert result["alert_level"] == "moderate"
        assert "grass" in result["moderate_levels"]
        assert result["high_levels"] == []
        assert any("MODERATE" in advice for advice in result["advice"])
    
    def test_low_pollen_advice(self):
        """Test health advice for low pollen levels"""
        data = {
            "current_day": {
                "grass": {"level": "Low"},
                "trees": {"level": "Low"},
                "weeds": {"level": "Low"}
            }
        }
        
        result = get_health_advice(data)
        
        assert result["alert_level"] == "low"
        assert result["high_levels"] == []
        assert result["moderate_levels"] == []
        assert any("GOOD NEWS" in advice for advice in result["advice"])
    
    def test_no_data_advice(self):
        """Test health advice when no data is available"""
        result = get_health_advice(None)
        
        assert result["alert_level"] == "unknown"
        assert "Unable to provide advice" in result["advice"][0]
    
    def test_empty_current_day_advice(self):
        """Test health advice when current_day is empty"""
        data = {"current_day": None}
        
        result = get_health_advice(data)
        
        assert result["alert_level"] == "unknown"
        assert "Unable to provide advice" in result["advice"][0]
    
    def test_very_high_pollen_levels(self):
        """Test health advice for very high pollen levels"""
        data = {
            "current_day": {
                "grass": {"level": "Very High"},
                "trees": {"level": "High"},
                "weeds": {"level": "Low"}
            }
        }
        
        result = get_health_advice(data)
        
        assert result["alert_level"] == "high"
        assert "grass" in result["high_levels"]
        assert "trees" in result["high_levels"]
        assert len(result["high_levels"]) == 2
    
    def test_case_insensitive_levels(self):
        """Test that level checking is case insensitive"""
        data = {
            "current_day": {
                "grass": {"level": "HIGH"},
                "trees": {"level": "moderate"},
                "weeds": {"level": "Low"}
            }
        }
        
        result = get_health_advice(data)
        
        assert result["alert_level"] == "high"
        assert "grass" in result["high_levels"]
        assert "trees" in result["moderate_levels"]
    
    def test_missing_level_data(self):
        """Test handling of missing level data"""
        data = {
            "current_day": {
                "grass": {},
                "trees": {"level": ""},
                "weeds": {"level": "Low"}
            }
        }
        
        result = get_health_advice(data)
        
        # Should default to low since no high/moderate levels found
        assert result["alert_level"] == "low"
        assert result["high_levels"] == []
        assert result["moderate_levels"] == [] 