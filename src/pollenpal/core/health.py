#!/usr/bin/env python3
"""
Health advice functionality

Contains logic for generating health advice based on pollen levels.
"""

from typing import Dict, List


def get_health_advice(data: Dict) -> Dict:
    """
    Generate health advice based on pollen levels.
    
    Args:
        data: Dictionary containing pollen data from PollenTracker
        
    Returns:
        Dictionary containing health advice, alert level, and categorised pollen types
    """
    advice = []

    if not data or not data.get("current_day"):
        return {
            "advice": ["Unable to provide advice - no data available"],
            "alert_level": "unknown",
            "high_levels": [],
            "moderate_levels": [],
        }

    current = data["current_day"]

    # Check overall levels
    high_levels = []
    moderate_levels = []

    for category_name, category in [
        ("grass", current.get("grass", {})),
        ("trees", current.get("trees", {})),
        ("weeds", current.get("weeds", {})),
    ]:
        level = category.get("level", "").lower()
        if level in ["high", "very high"]:
            high_levels.append(category_name)
        elif level == "moderate":
            moderate_levels.append(category_name)

    alert_level = "low"
    if high_levels:
        alert_level = "high"
        advice.append(
            f"HIGH ALERT: {', '.join(high_levels).title()} pollen levels are high"
        )
        advice.extend(
            [
                "Stay indoors during peak hours (5-10 AM and dusk)",
                "Keep windows closed",
                "Consider antihistamines",
                "Wear wraparound sunglasses outdoors",
            ]
        )
    elif moderate_levels:
        alert_level = "moderate"
        advice.append(
            f"MODERATE: {', '.join(moderate_levels).title()} pollen levels are moderate"
        )
        advice.extend(
            ["Monitor symptoms closely", "Consider limiting outdoor activities"]
        )
    else:
        advice.append("GOOD NEWS: All pollen levels are currently low")
        advice.append("Generally safe for outdoor activities")

    # General advice
    advice.extend(
        [
            "Check forecast daily",
            "Shower after being outdoors",
            "Dry clothes indoors",
            "Use HEPA air filters",
        ]
    )

    return {
        "advice": advice,
        "alert_level": alert_level,
        "high_levels": high_levels,
        "moderate_levels": moderate_levels,
    } 