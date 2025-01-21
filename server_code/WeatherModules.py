import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.secrets
import anvil.server
import requests
from datetime import datetime, timedelta, timezone
from . import CoreServerModule

def format_weather_data(weather_data):
    """
    Formats the OpenWeatherMap JSON data into a human-readable string
    """
    try:
        current = weather_data.get('current', {})
        daily = weather_data.get('daily', [{}])[0]  # Get today's forecast
        
        # Convert temperature from Kelvin to Fahrenheit
        def k_to_f(k):
            return round((k - 273.15) * 9/5 + 32, 1)
        
        current_temp = k_to_f(current.get('temp', 0))
        feels_like = k_to_f(current.get('feels_like', 0))
        humidity = current.get('humidity', 0)
        wind_speed = round(current.get('wind_speed', 0) * 2.237, 1)  # Convert m/s to mph
        
        # Get daily high/low
        daily_high = k_to_f(daily.get('temp', {}).get('max', 0))
        daily_low = k_to_f(daily.get('temp', {}).get('min', 0))
        
        # Get weather description
        weather = current.get('weather', [{}])[0]
        description = weather.get('description', 'No description available').capitalize()
        
        formatted_weather = [
            "Current Weather Conditions:",
            f"Temperature: {current_temp}°F (Feels like: {feels_like}°F)",
            f"Conditions: {description}",
            f"Humidity: {humidity}%",
            f"Wind Speed: {wind_speed} mph",
            "",
            "Today's Forecast:",
            f"High: {daily_high}°F",
            f"Low: {daily_low}°F"
        ]
        
        return "\n".join(formatted_weather)
    except Exception as e:
        return f"Error formatting weather data: {str(e)}"

@anvil.server.callable
def check_weather_cache():
    """
    Check if we have recent weather data within the cache expiration window.
    Returns a tuple of (status_message, weather_data, formatted_weather) where weather_data may be None if cache is invalid
    """
    try:
        # Get the most recent weather data entry
        recent_weather = app_tables.weatherdata.search(
            tables.order_by("timestamp", ascending=False)
        )
        
        if recent_weather and len(recent_weather) > 0:
            most_recent = recent_weather[0]
            current_time = datetime.now(timezone.utc)
            cache_age = current_time - most_recent['timestamp']
            minutes_old = int(cache_age.total_seconds() / 60)
            
            # Format the creation time in a readable format (convert from UTC to local time)
            creation_time = most_recent['timestamp'].replace(tzinfo=timezone.utc).astimezone()
            creation_time_str = creation_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            
            status_lines = [
                f"Entry creation time: {creation_time_str}",
                f"Entry age: {minutes_old} minutes",
            ]
            
            weather_data = most_recent['weatherdata_openweathermap']
            formatted_weather = format_weather_data(weather_data)
            
            # If the cache is still valid (less than WeatherDataCacheExpiration minutes old)
            if cache_age < timedelta(minutes=CoreServerModule.WeatherDataCacheExpiration):
                status_lines.append("Expiration not reached, using cached data")
                return "\n".join(status_lines), weather_data, formatted_weather
            else:
                status_lines.append("Expiration reached, requesting updated information")
                return "\n".join(status_lines), None, None
        
        return "No existing weather data found in cache", None, None
    except Exception as e:
        error_msg = f"Error checking weather cache: {str(e)}"
        print(f"Server Error in check_weather_cache: {str(e)}")  # Server-side logging
        return error_msg, None, None

@anvil.server.callable
def update_all_weather():
    """
    Updates weather data from all available weather sources.
    Currently only fetches from OpenWeatherMap, but is designed to be extended
    for additional weather data sources in the future.
    Returns a tuple of (status_message, weather_data, formatted_weather)
    """
    try:
        status, data, formatted = get_weather_openweathermap()
        if data is None:
            return f"Failed to update weather data: {status}", None, None
        return f"Updated weather data from all sources:\n{status}", data, formatted
    except Exception as e:
        error_msg = f"Error in update_all_weather: {str(e)}"
        print(f"Server Error in update_all_weather: {str(e)}")  # Server-side logging
        return error_msg, None, None

@anvil.server.callable
def get_weather_openweathermap():
    """
    Fetches weather data from OpenWeatherMap API and stores it in the database.
    Returns a tuple of (status_message, weather_data, formatted_weather)
    """
    try:
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat=35.1495&lon=-90.049&appid={anvil.secrets.get_secret('OpenWeatherMap_Key')}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code != 200:
            error_msg = f"OpenWeatherMap API returned status code {response.status_code}"
            print(f"Server Error in get_weather_openweathermap: {error_msg}")  # Server-side logging
            return error_msg, None, None
            
        weather_data = response.json()  # Parse JSON response
        formatted_weather = format_weather_data(weather_data)
        
        # Add new row to weatherdata table with current timestamp and weather data
        app_tables.weatherdata.add_row(
            timestamp=datetime.now(timezone.utc),
            weatherdata_openweathermap=weather_data
        )
        
        return "Successfully retrieved and stored OpenWeatherMap data", weather_data, formatted_weather
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error while fetching OpenWeatherMap data: {str(e)}"
        print(f"Server Error in get_weather_openweathermap: {str(e)}")  # Server-side logging
        return error_msg, None, None
    except Exception as e:
        error_msg = f"Error fetching OpenWeatherMap data: {str(e)}"
        print(f"Server Error in get_weather_openweathermap: {str(e)}")  # Server-side logging
        return error_msg, None, None