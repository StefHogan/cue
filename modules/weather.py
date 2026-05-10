from datetime import datetime, timedelta, timezone
from typing import Any

import requests

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def fetch_weather(config: dict[str, Any]) -> str:
    api_key = config["weather"].get("api_key", "")
    location = config["user"].get("location", "your area")

    if not api_key or api_key == "YOUR_OPENWEATHER_API_KEY":
        return "Weather is unavailable — no OpenWeatherMap API key configured."

    params = {
        "lat": config["user"]["latitude"],
        "lon": config["user"]["longitude"],
        "appid": api_key,
        "units": config["weather"].get("units", "imperial"),
    }

    try:
        current = requests.get(CURRENT_URL, params=params, timeout=10).json()
        description = current["weather"][0]["description"]
        current_temp = round(current["main"]["temp"])

        forecast = requests.get(FORECAST_URL, params=params, timeout=10).json()
        tz_offset = forecast.get("city", {}).get("timezone", 0)
        city_today = (datetime.now(timezone.utc) + timedelta(seconds=tz_offset)).date()

        today_temps = [
            item["main"]["temp"]
            for item in forecast["list"]
            if (
                datetime.fromtimestamp(item["dt"], tz=timezone.utc)
                + timedelta(seconds=tz_offset)
            ).date() == city_today
        ]

        if today_temps:
            high = round(max(today_temps))
            low = round(min(today_temps))
            return (
                f"Weather in {location} is {description} with a high of {high} "
                f"and a low of {low}."
            )

        return f"Weather in {location} is {description}, currently {current_temp} degrees."
    except (requests.RequestException, KeyError, ValueError):
        return "Weather is unavailable right now."
