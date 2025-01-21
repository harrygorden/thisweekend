import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.secrets
import anvil.server
import requests
from datetime import datetime, timedelta, timezone
from . import CoreServerModule

@anvil.server.callable
def check_weather_cache():
    """
    Check if we have recent weather data within the cache expiration window.
    Returns the most recent weather data if valid, None if we need to fetch new data.
    """
    # Get the most recent weather data entry
    recent_weather = app_tables.weatherdata.search(
        tables.order_by("timestamp", ascending=False)
    )
    
    if recent_weather and len(recent_weather) > 0:
        most_recent = recent_weather[0]
        current_time = datetime.now(timezone.utc)
        cache_age = current_time - most_recent['timestamp']
        
        # If the cache is still valid (less than WeatherDataCacheExpiration minutes old)
        if cache_age < timedelta(minutes=CoreServerModule.WeatherDataCacheExpiration):
            return most_recent['weatherdata_openweathermap']
    
    return None

@anvil.server.callable
def update_all_weather():
    """
    Updates weather data from all available weather sources.
    Currently only fetches from OpenWeatherMap, but is designed to be extended
    for additional weather data sources in the future.
    """
    return get_weather_openweathermap()

@anvil.server.callable
def get_weather_openweathermap():
    """
    Fetches weather data from OpenWeatherMap API and stores it in the database.
    """
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat=35.1495&lon=-90.049&appid={anvil.secrets.get_secret('OpenWeatherMap_Key')}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    weather_data = response.json()  # Parse JSON response
    
    # Add new row to weatherdata table with current timestamp and weather data
    app_tables.weatherdata.add_row(
        timestamp=datetime.now(timezone.utc),
        weatherdata_openweathermap=weather_data
    )
    
    return weather_data