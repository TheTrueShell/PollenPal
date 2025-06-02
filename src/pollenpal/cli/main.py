#!/usr/bin/env python3
"""
Interactive CLI for UK Pollen Tracking

Command-line interface for fetching and displaying pollen data.
"""

import argparse
import json
import sys
from typing import Dict, List

import requests

from ..core.tracker import PollenTracker
from ..core.health import get_health_advice


class PollenCLI:
    """CLI interface for pollen tracking with display formatting."""
    
    def __init__(self):
        self.tracker = PollenTracker()
        self.last_data = None

    def format_pollen_level(self, level: str) -> str:
        """Format pollen level with appropriate emoji"""
        level_lower = level.lower()
        if level_lower == "low":
            return f"🟢 {level}"
        elif level_lower == "moderate":
            return f"🟡 {level}"
        elif level_lower == "high":
            return f"🔴 {level}"
        elif level_lower == "very high":
            return f"🔴 {level}"
        else:
            return f"⚪ {level}"

    def display_current_conditions(self, data: Dict):
        """Display current pollen conditions"""
        if not data:
            print("❌ No data available")
            return

        print(
            f"\n🌾 POLLEN REPORT FOR {data.get('location', 'Unknown Location').upper()}"
        )
        print("=" * 60)

        if data.get("current_day"):
            current = data["current_day"]
            print(f"📅 {current.get('day_name', '')} {current.get('day_number', '')}")
            print()

            # Display main categories
            categories = [
                ("Grass", current.get("grass", {})),
                ("Trees", current.get("trees", {})),
                ("Weeds", current.get("weeds", {})),
            ]

            for name, category in categories:
                level = self.format_pollen_level(category.get("level", ""))
                count = category.get("count", "")
                print(f"{name:10} {level:15} {count}")

        # Display detailed breakdown if available
        if data.get("detailed_breakdown"):
            print("\n📊 DETAILED BREAKDOWN")
            print("-" * 30)
            for pollen_type, details in data["detailed_breakdown"].items():
                level = self.format_pollen_level(details.get("level", ""))
                ppm = details.get("ppm", "")
                print(f"{pollen_type.title():10} {level:15} {ppm}")

    def display_forecast(self, data: Dict):
        """Display 5-day pollen forecast"""
        if not data or not data.get("forecast"):
            print("❌ No forecast data available")
            return

        print(f"\n📈 5-DAY POLLEN FORECAST")
        print("=" * 80)

        # Header
        print(f"{'Day':<8} {'Grass':<12} {'Trees':<12} {'Weeds':<12}")
        print("-" * 80)

        for day in data["forecast"]:
            day_name = f"{day.get('day_name', '')}"
            grass_level = self.format_pollen_level(
                day.get("grass", {}).get("level", "")
            )
            trees_level = self.format_pollen_level(
                day.get("trees", {}).get("level", "")
            )
            weeds_level = self.format_pollen_level(
                day.get("weeds", {}).get("level", "")
            )

            print(
                f"{day_name:<8} {grass_level:<20} {trees_level:<20} {weeds_level:<20}"
            )

    def display_detailed_analysis(self, data: Dict):
        """Display detailed pollen type breakdown"""
        if not data or not data.get("current_day"):
            print("❌ No detailed data available")
            return

        current = data["current_day"]
        print(f"\n🔬 DETAILED POLLEN ANALYSIS")
        print("=" * 60)

        categories = [
            ("GRASS POLLEN", current.get("grass", {})),
            ("TREE POLLEN", current.get("trees", {})),
            ("WEED POLLEN", current.get("weeds", {})),
        ]

        for category_name, category_data in categories:
            print(f"\n{category_name}")
            print("-" * len(category_name))

            detail = category_data.get("detail", "")
            if detail:
                # Parse detail string (format: "Type,PPM,level|Type2,PPM,level")
                pollen_types = detail.split("|")
                for pollen_type in pollen_types:
                    if "," in pollen_type:
                        parts = pollen_type.split(",")
                        if len(parts) >= 3:
                            name, ppm, level = parts[0], parts[1], parts[2]
                            if int(ppm) > 0:  # Only show non-zero values
                                formatted_level = self.format_pollen_level(level)
                                print(f"  {name:<12} {ppm:>6} PPM  {formatted_level}")

    def display_health_advice(self, data: Dict):
        """Display health advice based on pollen levels"""
        advice_data = get_health_advice(data)
        advice = advice_data.get("advice", [])
        
        print(f"\n💊 HEALTH ADVICE")
        print("=" * 40)
        
        for tip in advice:
            if tip.startswith("HIGH ALERT"):
                print(f"⚠️  {tip}")
            elif tip.startswith("MODERATE"):
                print(f"⚡ {tip}")
            elif tip.startswith("GOOD NEWS"):
                print(f"✅ {tip}")
            elif tip == "Check forecast daily":
                print(f"\n💡 GENERAL TIPS:")
                print(f"   • {tip}")
            elif tip.startswith(("Stay indoors", "Keep windows", "Consider", "Wear", "Monitor", "Generally")):
                print(f"   • {tip}")
            else:
                print(f"   • {tip}")

    def process_query(self, city_input: str, show_forecast=False, show_detailed=False, show_advice=False, output_json=False):
        """Process a pollen query for a given city"""
        print(f"\n🔍 Fetching pollen data for: {city_input}")
        
        try:
            data = self.tracker.get_pollen_data(city_input)
        except requests.RequestException as e:
            print(f"❌ Error fetching data: {e}")
            return None

        if not data:
            print("❌ No data found. Please check the location and try again.")
            return None

        self.last_data = data

        if output_json:
            print(json.dumps(data, indent=2))
            return data

        # Always show current conditions
        self.display_current_conditions(data)

        if show_forecast:
            self.display_forecast(data)

        if show_detailed:
            self.display_detailed_analysis(data)

        if show_advice:
            self.display_health_advice(data)

        return data


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="UK Pollen Tracker CLI")
    parser.add_argument(
        "city",
        nargs="?",
        help='City or postcode to check (e.g., "London" or "SW1A 1AA")',
    )
    parser.add_argument(
        "--forecast", "-f", action="store_true", help="Show 5-day forecast"
    )
    parser.add_argument(
        "--detailed",
        "-d",
        action="store_true",
        help="Show detailed breakdown by pollen type",
    )
    parser.add_argument(
        "--advice", "-a", action="store_true", help="Show health advice"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON data")

    args = parser.parse_args()

    cli = PollenCLI()

    if args.interactive:
        print("🌾 UK Pollen Tracker - Interactive Mode")
        print("Enter 'quit' or 'exit' to stop")
        print("Commands: forecast, detailed, advice, help")
        print()

        while True:
            try:
                user_input = input("Enter city/postcode (or command): ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == "help":
                    print("\nAvailable commands:")
                    print("  forecast  - Show 5-day forecast for last queried location")
                    print("  detailed  - Show detailed breakdown")
                    print("  advice    - Show health advice")
                    print("  help      - Show this help")
                    print("  quit/exit - Exit the programme")
                    continue
                elif user_input.lower() == "forecast" and cli.last_data:
                    cli.display_forecast(cli.last_data)
                    continue
                elif user_input.lower() == "detailed" and cli.last_data:
                    cli.display_detailed_analysis(cli.last_data)
                    continue
                elif user_input.lower() == "advice" and cli.last_data:
                    cli.display_health_advice(cli.last_data)
                    continue
                elif user_input.lower() in ["forecast", "detailed", "advice"]:
                    print("❌ No previous data available. Please query a location first.")
                    continue

                if user_input:
                    cli.process_query(
                        user_input,
                        show_forecast=True,
                        show_detailed=True,
                        show_advice=True,
                        output_json=args.json
                    )

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break

    elif args.city:
        cli.process_query(
            args.city,
            show_forecast=args.forecast,
            show_detailed=args.detailed,
            show_advice=args.advice,
            output_json=args.json
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 