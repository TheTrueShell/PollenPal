#!/usr/bin/env python3
"""
FastAPI application for UK Pollen Tracking

Provides REST API endpoints for pollen data from Kleenex UK pollen API.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from ..core.tracker import PollenTracker
from ..core.health import get_health_advice
from .models import PollenData, HealthAdvice


# Initialize FastAPI app and pollen tracker
app = FastAPI(
    title="PollenPal API",
    description="UK Pollen Tracking API - Get current pollen levels and forecasts for UK locations",
    version="1.0.0",
    docs_url=None,
    redoc_url="/docs",
)

tracker = PollenTracker()


@app.get("/", summary="API Information")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "PollenPal API",
        "version": "1.0.0",
        "description": "UK Pollen Tracking API",
        "endpoints": {
            "/pollen/{city}": "Get current pollen data for a city",
            "/pollen/{city}/forecast": "Get 5-day pollen forecast",
            "/pollen/{city}/advice": "Get health advice based on pollen levels",
            "/docs": "Interactive API documentation",
            "/redoc": "Alternative API documentation",
        },
    }


@app.get("/pollen/{city}", response_model=PollenData, summary="Get Current Pollen Data")
async def get_pollen_data_endpoint(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)"),
):
    """
    Get current pollen data for a specified city or postcode.

    - **city**: City name or UK postcode (e.g., "London" or "SW1A 1AA")
    - **country**: Country code (default: UK)

    Returns detailed pollen information including current conditions,
    5-day forecast, and detailed breakdown by pollen type.
    """
    try:
        data = tracker.get_pollen_data(city, country)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No pollen data found for '{city}'. Please check the location and try again.",
        )

    return data


@app.get("/pollen/{city}/current", summary="Get Current Day Pollen Levels Only")
async def get_current_pollen(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)"),
):
    """
    Get only the current day's pollen levels for a specified city.

    Returns a simplified response with just today's pollen data.
    """
    try:
        data = tracker.get_pollen_data(city, country)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No pollen data found for '{city}'. Please check the location and try again.",
        )

    return {
        "location": data.get("location"),
        "current_day": data.get("current_day"),
        "coordinates": data.get("coordinates"),
    }


@app.get("/pollen/{city}/forecast", summary="Get 5-Day Pollen Forecast")
async def get_pollen_forecast(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)"),
):
    """
    Get 5-day pollen forecast for a specified city.

    Returns forecast data showing pollen levels for the next 5 days.
    """
    try:
        data = tracker.get_pollen_data(city, country)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No pollen data found for '{city}'. Please check the location and try again.",
        )

    return {
        "location": data.get("location"),
        "forecast": data.get("forecast", []),
        "coordinates": data.get("coordinates"),
    }


@app.get(
    "/pollen/{city}/advice", response_model=HealthAdvice, summary="Get Health Advice"
)
async def get_health_advice_endpoint(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)"),
):
    """
    Get personalised health advice based on current pollen levels.

    Returns advice tailored to the current pollen conditions in the specified location.
    """
    try:
        data = tracker.get_pollen_data(city, country)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No pollen data found for '{city}'. Please check the location and try again.",
        )

    advice_data = get_health_advice(data)
    return advice_data


@app.get("/pollen/{city}/detailed", summary="Get Detailed Pollen Breakdown")
async def get_detailed_breakdown(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)"),
):
    """
    Get detailed breakdown of pollen types and their specific levels.

    Returns detailed information about specific pollen types and their PPM levels.
    """
    try:
        data = tracker.get_pollen_data(city, country)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No pollen data found for '{city}'. Please check the location and try again.",
        )

    return {
        "location": data.get("location"),
        "detailed_breakdown": data.get("detailed_breakdown", {}),
        "coordinates": data.get("coordinates"),
    }


@app.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy", "message": "PollenPal API is running"} 