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
    
    # Processing forecasts (logging reduced for brevity)
    
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


def parse_time_to_hour(time_str):
    """
    Parse a time string and return the hour (0-23).
    Handles formats like "3:00 PM", "7:30 PM", "11:00 AM", "1 p.m.", "10 a.m.", etc.
    
    Args:
        time_str: Time string (e.g., "7:30 PM", "1 p.m.", "10 a.m.")
        
    Returns:
        int: Hour in 24-hour format (0-23), or None if parsing fails
    """
    if not time_str or time_str == "TBD":
        return None
    
    try:
        # Remove periods and normalize (convert "p.m." to "PM", "a.m." to "AM")
        time_normalized = time_str.replace('.', '').upper().strip()
        
        # Extract hour
        if ":" in time_normalized:
            time_part = time_normalized.split(":")[0]
            hour = int(time_part)
        else:
            # Handle formats like "3 PM" without colon
            time_part = time_normalized.split()[0]
            hour = int(time_part)
        
        # Convert to 24-hour format
        # Check for both "PM" and "P M" (in case of extra spaces)
        is_pm = "PM" in time_normalized.replace(' ', '')
        is_am = "AM" in time_normalized.replace(' ', '')
        
        if is_pm and hour != 12:
            hour += 12
        elif is_am and hour == 12:
            hour = 0
        
        return hour
    except (ValueError, IndexError):
        return None


def find_closest_hourly_forecast(event_time, hourly_data_list):
    """
    Find the hourly forecast closest to the event time.
    
    Args:
        event_time: Time string (e.g., "7:30 PM")
        hourly_data_list: List of hourly forecast dictionaries
        
    Returns:
        dict: Closest hourly forecast, or None if not found
    """
    event_hour = parse_time_to_hour(event_time)
    
    if event_hour is None or not hourly_data_list:
        return None
    
    closest_forecast = None
    min_diff = float('inf')
    
    for hour_data in hourly_data_list:
        forecast_hour = parse_time_to_hour(hour_data.get("time", ""))
        
        if forecast_hour is not None:
            # Calculate hour difference (accounting for day wrap)
            diff = abs(forecast_hour - event_hour)
            
            if diff < min_diff:
                min_diff = diff
                closest_forecast = hour_data
    
    return closest_forecast


def get_weather_for_datetime(event_date, event_time=None):
    """
    Get weather forecast for a specific date and time.
    Uses hourly_weather table for precise forecasts when available.
    Finds the NEAREST hour if exact match not found.
    
    Args:
        event_date: datetime.date object
        event_time: Optional time string (e.g., "3:00 PM", "7:30 PM")
        
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
        # First try exact match in hourly_weather table
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
            # hourly_weather table doesn't exist or no exact match found
            pass
        
        # Fallback: Find CLOSEST hourly forecast from hourly_data
        if forecast["hourly_data"]:
            closest_hour = find_closest_hourly_forecast(event_time, forecast["hourly_data"])
            
            if closest_hour:
                weather_info["hourly"] = closest_hour
                # Log the match for debugging
                event_hour = parse_time_to_hour(event_time)
                forecast_hour = parse_time_to_hour(closest_hour.get("time", ""))
                if event_hour != forecast_hour:
                    # Event time doesn't match exactly - using nearest hour
                    print(f"  Using {closest_hour.get('time')} forecast for {event_time} event")
    
    return weather_info


def get_best_weather_values(weather_data):
    """
    Extract the best available weather values from weather_data.
    Prioritizes hourly data when available, falls back to daily forecast.
    
    Args:
        weather_data: Weather forecast dictionary (may include hourly data)
        
    Returns:
        dict: Normalized weather values with keys:
            - temp: Temperature in °F
            - feels_like: Feels-like temperature in °F
            - precipitation_chance: Percentage (0-100)
            - wind_speed: Wind speed in mph
            - conditions: Description string
            - is_hourly: Boolean indicating if hourly data was used
    """
    hourly_data = weather_data.get("hourly")
    
    if hourly_data:
        # Use precise event-time weather
        return {
            "temp": hourly_data.get("temp", 70),
            "feels_like": hourly_data.get("feels_like", hourly_data.get("temp", 70)),
            "precipitation_chance": hourly_data.get("precipitation_chance", 0),
            "wind_speed": hourly_data.get("wind_speed", 0),
            "conditions": hourly_data.get("conditions", "unknown"),
            "humidity": hourly_data.get("humidity", 0),
            "is_hourly": True
        }
    else:
        # Fallback to daily forecast
        temp_high = weather_data.get("temp_high", 70)
        return {
            "temp": temp_high,
            "feels_like": temp_high,  # No feels_like in daily forecast
            "precipitation_chance": weather_data.get("precipitation_chance", 0),
            "wind_speed": weather_data.get("wind_speed", 0),
            "conditions": weather_data.get("conditions", "unknown"),
            "humidity": 0,  # Not available in daily forecast
            "is_hourly": False
        }


def calculate_weather_score(event_data, weather_data):
    """
    Calculate weather suitability score for an event (0-100).
    Uses event-specific hourly forecast when available for maximum accuracy.
    
    Args:
        event_data: Event dictionary with is_outdoor, date, time info
        weather_data: Weather forecast dictionary (may include hourly data)
        
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
    
    # Get best available weather values (hourly if available, daily otherwise)
    weather_values = get_best_weather_values(weather_data)
    
    precip_chance = weather_values["precipitation_chance"]
    effective_temp = weather_values["feels_like"]  # Use feels_like for comfort
    wind_speed = weather_values["wind_speed"]
    
    # Check precipitation
    if precip_chance > config.PRECIP_THRESHOLDS["high"]:
        score -= 40  # Major penalty for high rain chance
    elif precip_chance > config.PRECIP_THRESHOLDS["medium"]:
        score -= 20  # Moderate penalty
    elif precip_chance > config.PRECIP_THRESHOLDS["low"]:
        score -= 10  # Small penalty
    
    # Check temperature (using feels-like)
    if effective_temp < config.TEMP_THRESHOLDS["too_cold"]:
        score -= 30  # Too cold
    elif effective_temp < config.TEMP_THRESHOLDS["cold"]:
        score -= 15  # Cold
    elif effective_temp > config.TEMP_THRESHOLDS["too_hot"]:
        score -= 30  # Too hot
    elif effective_temp > config.TEMP_THRESHOLDS["hot"]:
        score -= 15  # Hot
    
    # Check wind
    if wind_speed > config.WIND_THRESHOLDS["windy"]:
        score -= 15  # Windy conditions
    elif wind_speed > config.WIND_THRESHOLDS["breezy"]:
        score -= 5   # Breezy
    
    # Ensure score stays in valid range
    return max(0, min(100, score))


def get_time_period_forecast(hourly_data, start_hour, end_hour):
    """
    Extract forecast for a specific time period from hourly data.
    
    Args:
        hourly_data: List of hourly forecast dictionaries
        start_hour: Start hour (0-23)
        end_hour: End hour (0-23)
        
    Returns:
        dict: Aggregated forecast for the time period
    """
    if not hourly_data:
        return None
    
    # Filter hourly data for the time period
    period_forecasts = []
    for hour in hourly_data:
        hour_num = parse_time_to_hour(hour.get("time", ""))
        if hour_num is not None and start_hour <= hour_num < end_hour:
            period_forecasts.append(hour)
    
    if not period_forecasts:
        return None
    
    # Calculate average/aggregate values
    temps = [h.get("temp", 0) for h in period_forecasts]
    feels_like_temps = [h.get("feels_like", h.get("temp", 0)) for h in period_forecasts]
    precip_chances = [h.get("precipitation_chance", 0) for h in period_forecasts]
    
    # Get most common conditions
    conditions_list = [h.get("conditions", "") for h in period_forecasts]
    most_common_conditions = max(set(conditions_list), key=conditions_list.count) if conditions_list else "unknown"
    
    return {
        "temp_avg": round(sum(temps) / len(temps)) if temps else 0,
        "temp_high": round(max(temps)) if temps else 0,
        "temp_low": round(min(temps)) if temps else 0,
        "feels_like_avg": round(sum(feels_like_temps) / len(feels_like_temps)) if feels_like_temps else 0,
        "precipitation_chance": round(max(precip_chances)) if precip_chances else 0,
        "conditions": most_common_conditions,
        "hour_count": len(period_forecasts)
    }


@anvil.server.callable
def get_weather_data():
    """
    Get all weather forecasts from the database.
    Only returns FUTURE time periods - filters out past periods.
    Callable from client-side code.
    
    Returns:
        list: List of weather forecast dictionaries with future-only data
    """
    import pytz
    
    forecasts = []
    
    # Get current time in Central timezone
    central_tz = pytz.timezone(config.MEMPHIS_TIMEZONE)
    now_central = datetime.now(central_tz)
    current_hour = now_central.hour
    today = now_central.date()
    
    for row in app_tables.weather_forecast.search():
        hourly_data = row["hourly_data"]
        forecast_date = row["forecast_date"]
        
        # Extract time period forecasts from hourly data
        morning = get_time_period_forecast(hourly_data, 6, 12)    # 6 AM - 12 PM
        afternoon = get_time_period_forecast(hourly_data, 12, 18)  # 12 PM - 6 PM
        evening = get_time_period_forecast(hourly_data, 18, 24)    # 6 PM - 12 AM
        
        # Determine which periods are in the future
        is_today = (forecast_date == today)
        
        if is_today:
            # Filter out past periods for today
            if current_hour >= 18:
                # It's evening (6 PM+) - only show evening
                morning = None
                afternoon = None
            elif current_hour >= 12:
                # It's afternoon (12 PM+) - show afternoon and evening
                morning = None
            else:
                # It's morning - show all periods
                pass
        
        # Collect future time periods for calculating actual conditions
        future_periods = []
        if morning:
            future_periods.append(morning)
        if afternoon:
            future_periods.append(afternoon)
        if evening:
            future_periods.append(evening)
        
        # Calculate future-only precipitation and conditions
        if future_periods:
            # Use max precipitation from FUTURE periods only
            future_precip_chances = [p.get("precipitation_chance", 0) for p in future_periods]
            actual_precip_chance = max(future_precip_chances)
            
            # Get most common future conditions
            future_conditions = [p.get("conditions", "") for p in future_periods]
            most_common_condition = max(set(future_conditions), key=future_conditions.count) if future_conditions else row["conditions"]
        else:
            # No future periods (day has passed)
            actual_precip_chance = 0
            most_common_condition = row["conditions"]
        
        forecasts.append({
            "date": forecast_date,
            "day_name": row["day_name"],
            "temp_high": row["temp_high"],
            "temp_low": row["temp_low"],
            "conditions": most_common_condition,  # Future conditions
            "precipitation_chance": actual_precip_chance,  # Future precipitation only!
            "wind_speed": row["wind_speed"],
            "hourly_data": hourly_data,
            "fetched_at": row["fetched_at"],
            # Time period breakdowns (filtered to future only)
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            # Metadata
            "is_today": is_today,
            "has_future_periods": len(future_periods) > 0
        })
    
    return forecasts

