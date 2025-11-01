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
        
        # Temperature - Overall for the day
        temp_high = weather.get('temp_high', 0)
        temp_low = weather.get('temp_low', 0)
        self.temp_label.text = f"{int(temp_high)}°F / {int(temp_low)}°F"
        
        # Conditions with weather icon
        conditions = weather.get('conditions', 'Unknown')
        self.conditions_label.text = conditions
        
        # Set weather icon based on conditions
        weather_icon = self.get_weather_icon(conditions)
        self.weather_icon_label.text = weather_icon
        
        # Precipitation (overall for the day)
        precip = weather.get('precipitation_chance', 0)
        self.precip_label.text = f"💧 {int(precip)}% rain"
        
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
        
        # Time period breakdowns
        self.display_time_periods(weather)
        
        # Set card background based on conditions
        self.set_card_style(conditions, precip)
    
    
    def display_time_periods(self, weather):
        """Display morning/afternoon/evening forecast breakdowns (future periods only)"""
        # Check if we have time period data
        morning = weather.get('morning')
        afternoon = weather.get('afternoon')
        evening = weather.get('evening')
        is_today = weather.get('is_today', False)
        
        # Build time period text
        period_lines = []
        
        if morning:
            morning_icon = self.get_weather_icon(morning.get('conditions', ''))
            morning_temp = morning.get('temp_avg', 0)
            morning_precip = morning.get('precipitation_chance', 0)
            period_lines.append(
                f"{morning_icon} Morning: {int(morning_temp)}°F, {int(morning_precip)}% rain"
            )
        
        if afternoon:
            afternoon_icon = self.get_weather_icon(afternoon.get('conditions', ''))
            afternoon_temp = afternoon.get('temp_avg', 0)
            afternoon_precip = afternoon.get('precipitation_chance', 0)
            period_lines.append(
                f"{afternoon_icon} Afternoon: {int(afternoon_temp)}°F, {int(afternoon_precip)}% rain"
            )
        
        if evening:
            evening_icon = self.get_weather_icon(evening.get('conditions', ''))
            evening_temp = evening.get('temp_avg', 0)
            evening_precip = evening.get('precipitation_chance', 0)
            period_lines.append(
                f"{evening_icon} Evening: {int(evening_temp)}°F, {int(evening_precip)}% rain"
            )
        
        # Display time periods if we have any
        if period_lines:
            # Check if temp_range_label exists and update it with time periods
            if hasattr(self, 'temp_range_label'):
                self.temp_range_label.text = "\n".join(period_lines)
                self.temp_range_label.font_size = 11
                self.temp_range_label.align = "left"
        elif is_today and not period_lines:
            # Today but no future periods - day has passed
            if hasattr(self, 'temp_range_label'):
                self.temp_range_label.text = "📅 Rest of day looks clear"
                self.temp_range_label.font_size = 11
                self.temp_range_label.italic = True
    
    
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

