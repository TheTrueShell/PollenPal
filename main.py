#!/usr/bin/env python3
"""
FastAPI application for UK Pollen Tracking
Provides REST API endpoints for pollen data from Kleenex UK pollen API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from pydantic import BaseModel


# Pydantic models for API responses
class PollenLevel(BaseModel):
    level: str
    count: str
    detail: str


class DayForecast(BaseModel):
    day_name: str
    day_number: str
    grass: PollenLevel
    trees: PollenLevel
    weeds: PollenLevel


class DetailedBreakdown(BaseModel):
    level: str
    ppm: str


class Coordinates(BaseModel):
    latitude: str
    longitude: str


class PollenData(BaseModel):
    location: str
    coordinates: Coordinates
    current_day: DayForecast
    forecast: List[DayForecast]
    detailed_breakdown: Dict[str, DetailedBreakdown]


class HealthAdvice(BaseModel):
    advice: List[str]
    alert_level: str
    high_levels: List[str]
    moderate_levels: List[str]


class PollenTracker:
    def __init__(self):
        self.base_url = "https://www.kleenex.co.uk/api/sitecore/Pollen/GetPollenContentCountryCity"
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup session with required headers"""
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'dnt': '1',
            'origin': 'https://www.kleenex.co.uk',
            'priority': 'u=1, i',
            'referer': 'https://www.kleenex.co.uk/pollen-count',
            'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        })
        
        # Add cookies
        self.session.cookies.update({
            'shell#lang': 'en',
            'deviceType': 'desktop',
            'BIGipServerwww.v3.kleenex.com_pool': '2183760906.20480.0000'
        })
    
    def get_pollen_data(self, city: str, country: str = "UK") -> Optional[Dict]:
        """Fetch pollen data for a given city"""
        try:
            data = {'city': city, 'country': country}
            response = self.session.post(self.base_url, data=data)
            response.raise_for_status()
            
            if response.text.strip():
                return self.parse_html_response(response.text)
            else:
                return None
                
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
    
    def parse_html_response(self, html_content: str) -> Dict:
        """Parse HTML response to extract pollen data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        data = {
            'location': '',
            'coordinates': {'latitude': '', 'longitude': ''},
            'current_day': {},
            'forecast': [],
            'detailed_breakdown': {}
        }
        
        # Extract location information
        city_input = soup.find('input', {'id': 'cityName'})
        if city_input:
            data['location'] = city_input.get('value', '')
        
        # Extract coordinates
        lat_input = soup.find('input', {'class': 'pollen-lat'})
        lng_input = soup.find('input', {'class': 'pollen-lng'})
        if lat_input and lng_input:
            data['coordinates'] = {
                'latitude': lat_input.get('value', ''),
                'longitude': lng_input.get('value', '')
            }
        
        # Extract forecast data from day buttons
        day_buttons = soup.find_all('button', {'class': 'day-link'})
        for button in day_buttons:
            day_data = {
                'day_name': button.find('span', {'class': 'day-name'}).text.strip() if button.find('span', {'class': 'day-name'}) else '',
                'day_number': button.find('span', {'class': 'day-number'}).text.strip() if button.find('span', {'class': 'day-number'}) else '',
                'grass': {
                    'level': button.get('data-grass', ''),
                    'count': button.get('data-grass-count', ''),
                    'detail': button.get('data-grass-detail', '')
                },
                'trees': {
                    'level': button.get('data-trees', ''),
                    'count': button.get('data-trees-count', ''),
                    'detail': button.get('data-tree-detail', '')
                },
                'weeds': {
                    'level': button.get('data-weeds', ''),
                    'count': button.get('data-weeds-count', ''),
                    'detail': button.get('data-weed-detail', '')
                }
            }
            
            if 'active' in button.get('class', []):
                data['current_day'] = day_data
            
            data['forecast'].append(day_data)
        
        # Extract current day detailed breakdown from diagram containers
        diagram_containers = soup.find_all('li', {'class': 'diagram-container'})
        for container in diagram_containers:
            pollen_type = container.get('data-details', '')
            if pollen_type:
                level_text = container.find('p', {'class': 'level-text'})
                ppm_level = container.find('p', {'class': 'ppm-level'})
                
                data['detailed_breakdown'][pollen_type] = {
                    'level': level_text.text.strip() if level_text else '',
                    'ppm': ppm_level.text.strip() if ppm_level else ''
                }
        
        return data
    
    def get_health_advice(self, data: Dict) -> Dict:
        """Generate health advice based on pollen levels"""
        advice = []
        
        if not data or not data.get('current_day'):
            return {
                "advice": ["Unable to provide advice - no data available"],
                "alert_level": "unknown",
                "high_levels": [],
                "moderate_levels": []
            }
        
        current = data['current_day']
        
        # Check overall levels
        high_levels = []
        moderate_levels = []
        
        for category_name, category in [('grass', current.get('grass', {})), 
                                       ('trees', current.get('trees', {})), 
                                       ('weeds', current.get('weeds', {}))]:
            level = category.get('level', '').lower()
            if level in ['high', 'very high']:
                high_levels.append(category_name)
            elif level == 'moderate':
                moderate_levels.append(category_name)
        
        alert_level = "low"
        if high_levels:
            alert_level = "high"
            advice.append(f"HIGH ALERT: {', '.join(high_levels).title()} pollen levels are high")
            advice.extend([
                "Stay indoors during peak hours (5-10 AM and dusk)",
                "Keep windows closed",
                "Consider antihistamines",
                "Wear wraparound sunglasses outdoors"
            ])
        elif moderate_levels:
            alert_level = "moderate"
            advice.append(f"MODERATE: {', '.join(moderate_levels).title()} pollen levels are moderate")
            advice.extend([
                "Monitor symptoms closely",
                "Consider limiting outdoor activities"
            ])
        else:
            advice.append("GOOD NEWS: All pollen levels are currently low")
            advice.append("Generally safe for outdoor activities")
        
        # General advice
        advice.extend([
            "Check forecast daily",
            "Shower after being outdoors",
            "Dry clothes indoors",
            "Use HEPA air filters"
        ])
        
        return {
            "advice": advice,
            "alert_level": alert_level,
            "high_levels": high_levels,
            "moderate_levels": moderate_levels
        }


# Initialize FastAPI app and pollen tracker
app = FastAPI(
    title="PollenPal API",
    description="UK Pollen Tracking API - Get current pollen levels and forecasts for UK locations",
    version="1.0.0",
    docs_url=None,
    redoc_url="/docs"
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
            "/redoc": "Alternative API documentation"
        }
    }


@app.get("/pollen/{city}", response_model=PollenData, summary="Get Current Pollen Data")
async def get_pollen_data(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)")
):
    """
    Get current pollen data for a specified city or postcode.
    
    - **city**: City name or UK postcode (e.g., "London" or "SW1A 1AA")
    - **country**: Country code (default: UK)
    
    Returns detailed pollen information including current conditions, 
    5-day forecast, and detailed breakdown by pollen type.
    """
    data = tracker.get_pollen_data(city, country)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No pollen data found for '{city}'. Please check the location and try again."
        )
    
    return data


@app.get("/pollen/{city}/current", summary="Get Current Day Pollen Levels Only")
async def get_current_pollen(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)")
):
    """
    Get only the current day's pollen levels for a specified city.
    
    Returns a simplified response with just today's pollen data.
    """
    data = tracker.get_pollen_data(city, country)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No pollen data found for '{city}'. Please check the location and try again."
        )
    
    return {
        "location": data.get("location"),
        "current_day": data.get("current_day"),
        "coordinates": data.get("coordinates")
    }


@app.get("/pollen/{city}/forecast", summary="Get 5-Day Pollen Forecast")
async def get_pollen_forecast(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)")
):
    """
    Get 5-day pollen forecast for a specified city.
    
    Returns forecast data showing pollen levels for the next 5 days.
    """
    data = tracker.get_pollen_data(city, country)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No pollen data found for '{city}'. Please check the location and try again."
        )
    
    return {
        "location": data.get("location"),
        "forecast": data.get("forecast", []),
        "coordinates": data.get("coordinates")
    }


@app.get("/pollen/{city}/advice", response_model=HealthAdvice, summary="Get Health Advice")
async def get_health_advice(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)")
):
    """
    Get personalised health advice based on current pollen levels.
    
    Returns advice tailored to the current pollen conditions in the specified location.
    """
    data = tracker.get_pollen_data(city, country)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No pollen data found for '{city}'. Please check the location and try again."
        )
    
    advice_data = tracker.get_health_advice(data)
    return advice_data


@app.get("/pollen/{city}/detailed", summary="Get Detailed Pollen Breakdown")
async def get_detailed_breakdown(
    city: str,
    country: str = Query(default="UK", description="Country code (default: UK)")
):
    """
    Get detailed breakdown of pollen types and their specific levels.
    
    Returns detailed information about specific pollen types and their PPM levels.
    """
    data = tracker.get_pollen_data(city, country)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No pollen data found for '{city}'. Please check the location and try again."
        )
    
    return {
        "location": data.get("location"),
        "detailed_breakdown": data.get("detailed_breakdown", {}),
        "current_day": data.get("current_day"),
        "coordinates": data.get("coordinates")
    }


@app.get("/health", summary="Health Check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
