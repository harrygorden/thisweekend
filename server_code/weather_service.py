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
        # In Anvil, http.request returns a StreamingMedia object
        # We need to convert it to bytes/string first
        response = anvil.http.request(
            url,
            method="GET",
            data=params,
            timeout=30
        )
        
        # Convert StreamingMedia to string
        response_text = response.get_bytes().decode('utf-8')
        
        # Parse response
        weather_data = json.loads(response_text)
        
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
    Includes all 48 hours of hourly forecasts available.
    
    Args:
        weather_data: Raw API response
        
    Returns:
        dict: Processed weather data for weekend days
    """
    weekend_dates = api_helpers.get_weekend_dates()
    weekend_forecasts = {}
    
    daily_forecasts = weather_data.get("daily", [])
    hourly_forecasts = weather_data.get("hourly", [])  # 48 hours available
    
    print(f"  Processing {len(daily_forecasts)} daily forecasts and {len(hourly_forecasts)} hourly forecasts")
    
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
                        "wind_speed": round(hour_forecast.get("wind_speed", 0)),
                        "humidity": hour_forecast.get("humidity", 0),
                        "uvi": round(hour_forecast.get("uvi", 0), 1)
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
    Also saves 48-hour hourly forecasts to hourly_weather table.
    Clears old data first.
    
    Args:
        weather_data: Dictionary of weather forecasts
    """
    print("Saving weather data to database...")
    
    try:
        # Clear old weather data
        for row in app_tables.weather_forecast.search():
            row.delete()
        
        # Clear old hourly data if table exists
        try:
            for row in app_tables.hourly_weather.search():
                row.delete()
        except AttributeError:
            # hourly_weather table doesn't exist yet
            print("  Note: hourly_weather table not found (will be created if needed)")
            pass
        
        # Insert new daily forecasts
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
            
            # Save detailed hourly data to separate table
            try:
                for hour_data in forecast["hourly_data"]:
                    # Parse the time to create a full datetime
                    hour_str = hour_data["time"]
                    try:
                        hour_time = datetime.strptime(hour_str, "%I:%M %p").time()
                        full_datetime = datetime.combine(forecast["date"], hour_time)
                    except:
                        # If time parsing fails, use a default
                        full_datetime = datetime.combine(forecast["date"], datetime.min.time())
                    
                    app_tables.hourly_weather.add_row(
                        timestamp=full_datetime,
                        hour_time=hour_data["time"],
                        date=forecast["date"],
                        temp=hour_data["temp"],
                        feels_like=hour_data["feels_like"],
                        conditions=hour_data["conditions"],
                        precipitation_chance=hour_data["precipitation_chance"],
                        wind_speed=hour_data["wind_speed"],
                        humidity=hour_data.get("humidity", 0),
                        uvi=hour_data.get("uvi", 0),
                        fetched_at=datetime.now()
                    )
            except AttributeError:
                # hourly_weather table doesn't exist, skip saving hourly data
                pass
        
        print(f"Saved {len(weather_data)} weather forecasts to database")
        
    except Exception as e:
        print(f"Error saving weather to database: {str(e)}")
        raise


def get_weather_for_datetime(event_date, event_time=None):
    """
    Get weather forecast for a specific date and time.
    Uses hourly_weather table for precise forecasts when available.
    
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
    
    # If specific time is provided, try to get precise hourly data
    if event_time and event_time != "TBD":
        # First try the hourly_weather table (more accurate)
        try:
            hourly_row = app_tables.hourly_weather.get(
                date=event_date,
                hour_time=event_time
            )
            if hourly_row:
                weather_info["hourly"] = {
                    "time": hourly_row["hour_time"],
                    "temp": hourly_row["temp"],
                    "feels_like": hourly_row["feels_like"],
                    "conditions": hourly_row["conditions"],
                    "precipitation_chance": hourly_row["precipitation_chance"],
                    "wind_speed": hourly_row["wind_speed"],
                    "humidity": hourly_row["humidity"],
                    "uvi": hourly_row["uvi"]
                }
                return weather_info
        except (AttributeError, KeyError):
            # hourly_weather table doesn't exist or no match found
            pass
        
        # Fallback: Use hourly_data from forecast
        if forecast["hourly_data"]:
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

