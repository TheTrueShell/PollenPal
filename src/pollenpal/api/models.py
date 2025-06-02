#!/usr/bin/env python3
"""
Pydantic models for API responses

Contains all data models used by the FastAPI application.
"""

from typing import Dict, List
from pydantic import BaseModel


class PollenLevel(BaseModel):
    """Model for individual pollen level data."""
    level: str
    count: str
    detail: str


class DayForecast(BaseModel):
    """Model for daily pollen forecast data."""
    day_name: str
    day_number: str
    grass: PollenLevel
    trees: PollenLevel
    weeds: PollenLevel


class DetailedBreakdown(BaseModel):
    """Model for detailed pollen breakdown data."""
    level: str
    ppm: str


class Coordinates(BaseModel):
    """Model for geographical coordinates."""
    latitude: str
    longitude: str


class PollenData(BaseModel):
    """Main model for complete pollen data response."""
    location: str
    coordinates: Coordinates
    current_day: DayForecast
    forecast: List[DayForecast]
    detailed_breakdown: Dict[str, DetailedBreakdown]


class HealthAdvice(BaseModel):
    """Model for health advice response."""
    advice: List[str]
    alert_level: str
    high_levels: List[str]
    moderate_levels: List[str] 