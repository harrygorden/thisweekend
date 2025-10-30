"""
Weather service module for This Weekend app.
Handles integration with OpenWeather One Call API 3.0.
"""

import anvil.server
import anvil.http
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta
import json

from . import config
from . import api_helpers


def fetch_weekend_weather():
    """
    Fetch weather forecast for the upcoming weekend (Friday, Saturday, Sunday).
    Uses OpenWeather One Call API 3.0.
    
    Returns:
        dict: Weather data for Friday, Saturday, Sunday
        
    Raises:
        Exception: If API call fails
    """
    print("Fetching weekend weather from OpenWeather API...")
    
    # Get API key
    api_key = api_helpers.get_api_key("OPENWEATHER_API_KEY")
    
    # Build API request
    url = config.OPENWEATHER_BASE_URL
    params = {
        "lat": config.MEMPHIS_LAT,
        "lon": config.MEMPHIS_LON,
        "appid": api_key,
        "units": "imperial",  # Fahrenheit
        "exclude": "current,minutely,alerts"  # We only need daily and hourly
    }
    
    try:
        response = anvil.http.request(
            url,
            method="GET",
            data=params,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenWeather API returned status {response.status_code}: {response.get_text()}")
        
        # Parse response
        weather_data = json.loads(response.get_text())
        
        # Extract weekend forecasts
        weekend_data = extract_weekend_forecasts(weather_data)
        
        print(f"Successfully fetched weather for {len(weekend_data)} days")
        return weekend_data
        
    except Exception as e:
        print(f"Error fetching weather: {str(e)}")
        raise


def extract_weekend_forecasts(weather_data):
    """
    Extract Friday, Saturday, Sunday forecasts from API response.
    
    Args:
        weather_data: Raw API response
        
    Returns:
        dict: Processed weather data for weekend days
    """
    weekend_dates = api_helpers.get_weekend_dates()
    weekend_forecasts = {}
    
    daily_forecasts = weather_data.get("daily", [])
    hourly_forecasts = weather_data.get("hourly", [])
    
    for day_name, target_date in weekend_dates.items():
        # Find matching daily forecast
        daily_data = None
        for forecast in daily_forecasts:
            forecast_date = datetime.fromtimestamp(forecast["dt"]).date()
            if forecast_date == target_date:
                daily_data = forecast
                break
        
        if daily_data:
            # Extract hourly data for this day
            hourly_data = []
            for hour_forecast in hourly_forecasts:
                hour_date = datetime.fromtimestamp(hour_forecast["dt"]).date()
                if hour_date == target_date:
                    hourly_data.append({
                        "time": datetime.fromtimestamp(hour_forecast["dt"]).strftime("%I:%M %p"),
                        "temp": round(hour_forecast["temp"]),
                        "feels_like": round(hour_forecast.get("feels_like", hour_forecast["temp"])),
                        "precipitation_chance": round(hour_forecast.get("pop", 0) * 100),
                        "conditions": hour_forecast["weather"][0]["description"],
                        "wind_speed": round(hour_forecast.get("wind_speed", 0))
                    })
            
            weekend_forecasts[day_name] = {
                "date": target_date,
                "day_name": day_name.capitalize(),
                "temp_high": round(daily_data["temp"]["max"]),
                "temp_low": round(daily_data["temp"]["min"]),
                "conditions": daily_data["weather"][0]["description"],
                "precipitation_chance": round(daily_data.get("pop", 0) * 100),
                "wind_speed": round(daily_data.get("wind_speed", 0)),
                "humidity": daily_data.get("humidity", 0),
                "hourly_data": hourly_data
            }
    
    return weekend_forecasts


def save_weather_to_db(weather_data):
    """
    Save weather forecasts to the weather_forecast Data Table.
    Clears old data first.
    
    Args:
        weather_data: Dictionary of weather forecasts
    """
    print("Saving weather data to database...")
    
    try:
        # Clear old weather data
        for row in app_tables.weather_forecast.search():
            row.delete()
        
        # Insert new forecasts
        for day_name, forecast in weather_data.items():
            app_tables.weather_forecast.add_row(
                forecast_date=forecast["date"],
                day_name=forecast["day_name"],
                temp_high=forecast["temp_high"],
                temp_low=forecast["temp_low"],
                conditions=forecast["conditions"],
                precipitation_chance=forecast["precipitation_chance"],
                wind_speed=forecast["wind_speed"],
                hourly_data=forecast["hourly_data"],  # Store as SimpleObject
                fetched_at=datetime.now()
            )
        
        print(f"Saved {len(weather_data)} weather forecasts to database")
        
    except Exception as e:
        print(f"Error saving weather to database: {str(e)}")
        raise


def get_weather_for_datetime(event_date, event_time=None):
    """
    Get weather forecast for a specific date and time.
    
    Args:
        event_date: datetime.date object
        event_time: Optional time string (e.g., "3:00 PM")
        
    Returns:
        dict: Weather data for that date/time, or None if not found
    """
    # Query weather forecast table for the date
    forecast = app_tables.weather_forecast.get(forecast_date=event_date)
    
    if not forecast:
        return None
    
    weather_info = {
        "day_name": forecast["day_name"],
        "temp_high": forecast["temp_high"],
        "temp_low": forecast["temp_low"],
        "conditions": forecast["conditions"],
        "precipitation_chance": forecast["precipitation_chance"],
        "wind_speed": forecast["wind_speed"]
    }
    
    # If specific time is provided, try to get hourly data
    if event_time and forecast["hourly_data"]:
        # Find closest hourly forecast
        for hour_data in forecast["hourly_data"]:
            if hour_data["time"] == event_time:
                weather_info["hourly"] = hour_data
                break
    
    return weather_info


def calculate_weather_score(event_data, weather_data):
    """
    Calculate weather suitability score for an event (0-100).
    
    Args:
        event_data: Event dictionary with is_outdoor, date, time info
        weather_data: Weather forecast dictionary
        
    Returns:
        int: Weather score (0-100)
    """
    if not weather_data:
        return 50  # Neutral score if no weather data
    
    # Indoor events get high baseline score
    if not event_data.get("is_outdoor", False):
        return 90  # Indoor events mostly unaffected by weather
    
    # For outdoor events, calculate based on conditions
    score = 100
    
    # Check precipitation
    precip_chance = weather_data.get("precipitation_chance", 0)
    if precip_chance > config.PRECIP_THRESHOLDS["high"]:
        score -= 40  # Major penalty for high rain chance
    elif precip_chance > config.PRECIP_THRESHOLDS["medium"]:
        score -= 20  # Moderate penalty
    elif precip_chance > config.PRECIP_THRESHOLDS["low"]:
        score -= 10  # Small penalty
    
    # Check temperature
    temp = weather_data.get("temp_high", 70)
    if temp < config.TEMP_THRESHOLDS["too_cold"]:
        score -= 30  # Too cold
    elif temp < config.TEMP_THRESHOLDS["cold"]:
        score -= 15  # Cold
    elif temp > config.TEMP_THRESHOLDS["too_hot"]:
        score -= 30  # Too hot
    elif temp > config.TEMP_THRESHOLDS["hot"]:
        score -= 15  # Hot
    
    # Check wind
    wind_speed = weather_data.get("wind_speed", 0)
    if wind_speed > config.WIND_THRESHOLDS["windy"]:
        score -= 15  # Windy conditions
    elif wind_speed > config.WIND_THRESHOLDS["breezy"]:
        score -= 5   # Breezy
    
    # Ensure score stays in valid range
    return max(0, min(100, score))


@anvil.server.callable
def get_weather_data():
    """
    Get all weather forecasts from the database.
    Callable from client-side code.
    
    Returns:
        list: List of weather forecast dictionaries
    """
    forecasts = []
    
    for row in app_tables.weather_forecast.search():
        forecasts.append({
            "date": row["forecast_date"],
            "day_name": row["day_name"],
            "temp_high": row["temp_high"],
            "temp_low": row["temp_low"],
            "conditions": row["conditions"],
            "precipitation_chance": row["precipitation_chance"],
            "wind_speed": row["wind_speed"],
            "hourly_data": row["hourly_data"],
            "fetched_at": row["fetched_at"]
        })
    
    return forecasts

