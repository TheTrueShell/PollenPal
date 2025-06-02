#!/usr/bin/env python3
"""
Core pollen tracking functionality

Contains the main PollenTracker class for fetching and parsing pollen data.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException


class PollenTracker:
    """Main class for fetching and parsing UK pollen data from Kleenex API."""
    
    def __init__(self):
        self.base_url = (
            "https://www.kleenex.co.uk/api/sitecore/Pollen/GetPollenContentCountryCity"
        )
        self.session = requests.Session()
        self.setup_session()

    def setup_session(self):
        """Setup session with required headers and cookies."""
        self.session.headers.update(
            {
                "accept": "*/*",
                "accept-language": "en-GB,en;q=0.7",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "dnt": "1",
                "origin": "https://www.kleenex.co.uk",
                "priority": "u=1, i",
                "referer": "https://www.kleenex.co.uk/pollen-count",
                "sec-ch-ua": '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            }
        )

        # Add cookies
        self.session.cookies.update(
            {
                "shell#lang": "en",
                "deviceType": "desktop",
                "BIGipServerwww.v3.kleenex.com_pool": "2183760906.20480.0000",
            }
        )

    def get_pollen_data(self, city: str, country: str = "UK") -> Optional[Dict]:
        """
        Fetch pollen data for a given city.
        
        Args:
            city: The city name to fetch data for
            country: The country code (default: UK)
            
        Returns:
            Dictionary containing pollen data or None if no data available
            
        Raises:
            HTTPException: If there's an error fetching data (for API usage)
            requests.RequestException: If there's a network error (for CLI usage)
        """
        try:
            data = {"city": city, "country": country}
            response = self.session.post(self.base_url, data=data)
            response.raise_for_status()

            if response.text.strip():
                return self.parse_html_response(response.text)
            else:
                return None

        except requests.RequestException as e:
            # Re-raise as HTTPException for API usage, or let CLI handle it
            raise e

    def parse_html_response(self, html_content: str) -> Dict:
        """
        Parse HTML response to extract pollen data.
        
        Args:
            html_content: Raw HTML response from the API
            
        Returns:
            Dictionary containing structured pollen data
        """
        soup = BeautifulSoup(html_content, "html.parser")
        data = {
            "location": "",
            "coordinates": {"latitude": "", "longitude": ""},
            "current_day": {},
            "forecast": [],
            "detailed_breakdown": {},
        }

        # Extract location information
        city_input = soup.find("input", {"id": "cityName"})
        if city_input:
            data["location"] = city_input.get("value", "")

        # Extract coordinates
        lat_input = soup.find("input", {"class": "pollen-lat"})
        lng_input = soup.find("input", {"class": "pollen-lng"})
        if lat_input and lng_input:
            data["coordinates"] = {
                "latitude": lat_input.get("value", ""),
                "longitude": lng_input.get("value", ""),
            }

        # Extract forecast data from day buttons
        day_buttons = soup.find_all("button", {"class": "day-link"})
        for button in day_buttons:
            day_data = {
                "day_name": (
                    button.find("span", {"class": "day-name"}).text.strip()
                    if button.find("span", {"class": "day-name"})
                    else ""
                ),
                "day_number": (
                    button.find("span", {"class": "day-number"}).text.strip()
                    if button.find("span", {"class": "day-number"})
                    else ""
                ),
                "grass": {
                    "level": button.get("data-grass", ""),
                    "count": button.get("data-grass-count", ""),
                    "detail": button.get("data-grass-detail", ""),
                },
                "trees": {
                    "level": button.get("data-trees", ""),
                    "count": button.get("data-trees-count", ""),
                    "detail": button.get("data-tree-detail", ""),
                },
                "weeds": {
                    "level": button.get("data-weeds", ""),
                    "count": button.get("data-weeds-count", ""),
                    "detail": button.get("data-weed-detail", ""),
                },
            }

            if "active" in button.get("class", []):
                data["current_day"] = day_data

            data["forecast"].append(day_data)

        # Extract current day detailed breakdown from diagram containers
        diagram_containers = soup.find_all("li", {"class": "diagram-container"})
        for container in diagram_containers:
            pollen_type = container.get("data-details", "")
            if pollen_type:
                level_text = container.find("p", {"class": "level-text"})
                ppm_level = container.find("p", {"class": "ppm-level"})

                data["detailed_breakdown"][pollen_type] = {
                    "level": level_text.text.strip() if level_text else "",
                    "ppm": ppm_level.text.strip() if ppm_level else "",
                }

        return data 