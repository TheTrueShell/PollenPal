#!/usr/bin/env python3
"""
Interactive CLI for UK Pollen Tracking
Fetches pollen data from Kleenex UK pollen API
"""

import requests
import argparse
import json
import sys
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import re


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
            print(f"❌ Error fetching data: {e}")
            return None
    
    def parse_html_response(self, html_content: str) -> Dict:
        """Parse HTML response to extract pollen data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        data = {
            'location': '',
            'coordinates': {},
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
    
    def format_pollen_level(self, level: str) -> str:
        """Format pollen level with appropriate emoji"""
        level_lower = level.lower()
        if level_lower == 'low':
            return f"🟢 {level}"
        elif level_lower == 'moderate':
            return f"🟡 {level}"
        elif level_lower == 'high':
            return f"🔴 {level}"
        elif level_lower == 'very high':
            return f"🔴 {level}"
        else:
            return f"⚪ {level}"
    
    def display_current_conditions(self, data: Dict):
        """Display current pollen conditions"""
        if not data:
            print("❌ No data available")
            return
        
        print(f"\n🌾 POLLEN REPORT FOR {data.get('location', 'Unknown Location').upper()}")
        print("=" * 60)
        
        if data.get('current_day'):
            current = data['current_day']
            print(f"📅 {current.get('day_name', '')} {current.get('day_number', '')}")
            print()
            
            # Display main categories
            categories = [
                ('Grass', current.get('grass', {})),
                ('Trees', current.get('trees', {})),
                ('Weeds', current.get('weeds', {}))
            ]
            
            for name, category in categories:
                level = self.format_pollen_level(category.get('level', ''))
                count = category.get('count', '')
                print(f"{name:10} {level:15} {count}")
        
        # Display detailed breakdown if available
        if data.get('detailed_breakdown'):
            print("\n📊 DETAILED BREAKDOWN")
            print("-" * 30)
            for pollen_type, details in data['detailed_breakdown'].items():
                level = self.format_pollen_level(details.get('level', ''))
                ppm = details.get('ppm', '')
                print(f"{pollen_type.title():10} {level:15} {ppm}")
    
    def display_forecast(self, data: Dict):
        """Display 5-day pollen forecast"""
        if not data or not data.get('forecast'):
            print("❌ No forecast data available")
            return
        
        print(f"\n📈 5-DAY POLLEN FORECAST")
        print("=" * 80)
        
        # Header
        print(f"{'Day':<8} {'Grass':<12} {'Trees':<12} {'Weeds':<12}")
        print("-" * 80)
        
        for day in data['forecast']:
            day_name = f"{day.get('day_name', '')}"
            grass_level = self.format_pollen_level(day.get('grass', {}).get('level', ''))
            trees_level = self.format_pollen_level(day.get('trees', {}).get('level', ''))
            weeds_level = self.format_pollen_level(day.get('weeds', {}).get('level', ''))
            
            print(f"{day_name:<8} {grass_level:<20} {trees_level:<20} {weeds_level:<20}")
    
    def display_detailed_analysis(self, data: Dict):
        """Display detailed pollen type breakdown"""
        if not data or not data.get('current_day'):
            print("❌ No detailed data available")
            return
        
        current = data['current_day']
        print(f"\n🔬 DETAILED POLLEN ANALYSIS")
        print("=" * 60)
        
        categories = [
            ('GRASS POLLEN', current.get('grass', {})),
            ('TREE POLLEN', current.get('trees', {})),
            ('WEED POLLEN', current.get('weeds', {}))
        ]
        
        for category_name, category_data in categories:
            print(f"\n{category_name}")
            print("-" * len(category_name))
            
            detail = category_data.get('detail', '')
            if detail:
                # Parse detail string (format: "Type,PPM,level|Type2,PPM,level")
                pollen_types = detail.split('|')
                for pollen_type in pollen_types:
                    if ',' in pollen_type:
                        parts = pollen_type.split(',')
                        if len(parts) >= 3:
                            name, ppm, level = parts[0], parts[1], parts[2]
                            if int(ppm) > 0:  # Only show non-zero values
                                formatted_level = self.format_pollen_level(level)
                                print(f"  {name:<12} {ppm:>6} PPM  {formatted_level}")
    
    def get_health_advice(self, data: Dict) -> List[str]:
        """Generate health advice based on pollen levels"""
        advice = []
        
        if not data or not data.get('current_day'):
            return ["Unable to provide advice - no data available"]
        
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
        
        if high_levels:
            advice.append(f"⚠️  HIGH ALERT: {', '.join(high_levels).title()} pollen levels are high")
            advice.append("   • Stay indoors during peak hours (5-10 AM and dusk)")
            advice.append("   • Keep windows closed")
            advice.append("   • Consider antihistamines")
            advice.append("   • Wear wraparound sunglasses outdoors")
        
        if moderate_levels:
            advice.append(f"⚡ MODERATE: {', '.join(moderate_levels).title()} pollen levels are moderate")
            advice.append("   • Monitor symptoms closely")
            advice.append("   • Consider limiting outdoor activities")
        
        if not high_levels and not moderate_levels:
            advice.append("✅ GOOD NEWS: All pollen levels are currently low")
            advice.append("   • Generally safe for outdoor activities")
        
        # General advice
        advice.extend([
            "",
            "💡 GENERAL TIPS:",
            "   • Check forecast daily",
            "   • Shower after being outdoors",
            "   • Dry clothes indoors",
            "   • Use HEPA air filters"
        ])
        
        return advice


def main():
    parser = argparse.ArgumentParser(description="UK Pollen Tracker CLI")
    parser.add_argument('city', nargs='?', help='City or postcode to check (e.g., "London" or "SW1A 1AA")')
    parser.add_argument('--forecast', '-f', action='store_true', help='Show 5-day forecast')
    parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed breakdown by pollen type')
    parser.add_argument('--advice', '-a', action='store_true', help='Show health advice')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--json', action='store_true', help='Output raw JSON data')
    
    args = parser.parse_args()
    
    tracker = PollenTracker()
    
    def process_query(city_input: str):
        """Process a pollen query for a given city"""
        print(f"\n🔍 Fetching pollen data for: {city_input}")
        data = tracker.get_pollen_data(city_input)
        
        if not data:
            print("❌ No data found. Please check the location and try again.")
            return
        
        if args.json:
            print(json.dumps(data, indent=2))
            return
        
        # Always show current conditions
        tracker.display_current_conditions(data)
        
        if args.forecast:
            tracker.display_forecast(data)
        
        if args.detailed:
            tracker.display_detailed_analysis(data)
        
        if args.advice:
            advice = tracker.get_health_advice(data)
            print(f"\n💊 HEALTH ADVICE")
            print("=" * 40)
            for tip in advice:
                print(tip)
    
    if args.interactive:
        print("🌾 UK Pollen Tracker - Interactive Mode")
        print("Enter 'quit' or 'exit' to stop")
        print("Commands: forecast, detailed, advice, help")
        print()
        
        while True:
            try:
                user_input = input("Enter city/postcode (or command): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  forecast  - Show 5-day forecast for last queried location")
                    print("  detailed  - Show detailed breakdown")
                    print("  advice    - Show health advice")
                    print("  help      - Show this help")
                    print("  quit/exit - Exit the programme")
                    continue
                elif user_input.lower() in ['forecast', 'detailed', 'advice']:
                    print(f"Please enter a location first, then use '{user_input}' command")
                    continue
                elif not user_input:
                    continue
                
                process_query(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    elif args.city:
        process_query(args.city)
    else:
        # No city provided and not interactive - show help
        parser.print_help()
        print("\nExamples:")
        print("  python pollen_tracker.py London")
        print("  python pollen_tracker.py 'CF14 2LX' --forecast --advice")
        print("  python pollen_tracker.py --interactive")


if __name__ == "__main__":
    main()