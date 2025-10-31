from ._anvil_designer import WeatherCardTemplate
from anvil import *
import anvil.server


class WeatherCard(WeatherCardTemplate):
    """
    Weather card component for displaying a single day's weather forecast
    
    Displays:
    - Day name
    - High/Low temperatures
    - Weather conditions with icon
    - Precipitation chance
    - Wind speed
    """
    
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Store weather data
        self.weather_data = None
    
    
    def set_weather_data(self, weather):
        """Set the weather data and update display"""
        self.weather_data = weather
        
        if not weather:
            return
        
        # Check if components are initialized
        if not hasattr(self, 'day_label'):
            print("Warning: WeatherCard components not initialized yet")
            return
        
        # Day name
        self.day_label.text = weather.get('day_name', 'Unknown')
        
        # Temperature
        temp_high = weather.get('temp_high', 0)
        temp_low = weather.get('temp_low', 0)
        self.temp_label.text = f"{int(temp_high)}°F"
        self.temp_range_label.text = f"Low: {int(temp_low)}°F"
        
        # Conditions with weather icon
        conditions = weather.get('conditions', 'Unknown')
        self.conditions_label.text = conditions
        
        # Set weather icon based on conditions
        weather_icon = self.get_weather_icon(conditions)
        self.weather_icon_label.text = weather_icon
        
        # Precipitation
        precip = weather.get('precipitation_chance', 0)
        self.precip_label.text = f"💧 {int(precip)}%"
        
        # Set precipitation color
        if precip >= 60:
            self.precip_label.foreground = "#F44336"  # Red for high chance
        elif precip >= 30:
            self.precip_label.foreground = "#FF9800"  # Orange for medium
        else:
            self.precip_label.foreground = "#4CAF50"  # Green for low
        
        # Wind
        wind = weather.get('wind_speed', 0)
        self.wind_label.text = f"💨 {int(wind)} mph"
        
        # Set card background based on conditions
        self.set_card_style(conditions, precip)
    
    
    def get_weather_icon(self, conditions):
        """Get weather icon emoji based on conditions"""
        conditions_lower = conditions.lower()
        
        if 'clear' in conditions_lower or 'sunny' in conditions_lower:
            return '☀️'
        elif 'partly cloudy' in conditions_lower or 'few clouds' in conditions_lower:
            return '⛅'
        elif 'cloudy' in conditions_lower or 'overcast' in conditions_lower:
            return '☁️'
        elif 'rain' in conditions_lower or 'shower' in conditions_lower:
            return '🌧️'
        elif 'storm' in conditions_lower or 'thunder' in conditions_lower:
            return '⛈️'
        elif 'snow' in conditions_lower:
            return '❄️'
        elif 'fog' in conditions_lower or 'mist' in conditions_lower:
            return '🌫️'
        else:
            return '🌤️'
    
    
    def set_card_style(self, conditions, precip):
        """Set card background color based on weather"""
        # Good weather - light blue/green
        if precip < 20 and ('clear' in conditions.lower() or 'sunny' in conditions.lower()):
            self.card_1.background = "#E3F2FD"  # Light blue
        # Decent weather - light gray
        elif precip < 40:
            self.card_1.background = "#F5F5F5"  # Light gray
        # Poor weather - light orange/yellow
        else:
            self.card_1.background = "#FFF3E0"  # Light orange

