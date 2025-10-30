"""
Configuration module for This Weekend app.
Contains constants and configuration values used across the application.
"""

# Memphis, TN Coordinates
MEMPHIS_LAT = 35.1495
MEMPHIS_LON = -90.0490
MEMPHIS_TIMEZONE = "America/Chicago"  # Central Time

# Target Website
TARGET_WEBSITE_URL = "https://ilovememphisblog.com/weekend"

# OpenWeather API Configuration
OPENWEATHER_API_VERSION = "3.0"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

# OpenAI Configuration
OPENAI_MODEL = "gpt-3.5-turbo"  # Use gpt-4 for better accuracy if needed
OPENAI_MAX_TOKENS = 500  # Per event analysis
OPENAI_TEMPERATURE = 0.3  # Lower temperature for more consistent categorization

# Firecrawl Configuration
FIRECRAWL_TIMEOUT = 60  # seconds
FIRECRAWL_FORMATS = ["markdown"]

# Weekend Days Configuration
WEEKEND_DAYS = ["Friday", "Saturday", "Sunday"]

# Cost Level Mapping
COST_LEVELS = {
    "free": "Free",
    "$": "$",
    "$$": "$$",
    "$$$": "$$$",
    "$$$$": "$$$$"
}

# Category Options (will be expanded based on AI analysis)
CATEGORIES = [
    "Arts",
    "Music",
    "Sports",
    "Food & Drink",
    "Outdoor Activities",
    "Cultural Events",
    "Theater/Performance",
    "Family/Kids",
    "Nightlife",
    "Shopping",
    "Educational",
    "Community Events",
    "Other"
]

# Audience Types
AUDIENCE_TYPES = ["adults", "family-friendly", "all-ages"]

# Weather Score Weights (for recommendation calculation)
WEATHER_WEIGHTS = {
    "outdoor_weather_score": 0.70,  # 70% weight for outdoor events
    "outdoor_time_of_day": 0.30,    # 30% weight for time of day
    "indoor_baseline": 80,           # Indoor events baseline score
    "bad_weather_indoor_boost": 10   # Boost indoor events when weather is bad
}

# Precipitation thresholds
PRECIP_THRESHOLDS = {
    "low": 20,      # < 20% chance = good
    "medium": 50,   # 20-50% = fair
    "high": 50      # > 50% = poor
}

# Temperature thresholds (Fahrenheit)
TEMP_THRESHOLDS = {
    "too_cold": 40,     # Below 40°F
    "cold": 50,         # 40-50°F
    "comfortable": 85,  # 50-85°F is ideal
    "hot": 95,          # 85-95°F
    "too_hot": 95       # Above 95°F
}

# Wind speed thresholds (mph)
WIND_THRESHOLDS = {
    "calm": 10,         # < 10 mph
    "breezy": 20,       # 10-20 mph
    "windy": 20         # > 20 mph
}

# Data Retention (days)
DATA_RETENTION = {
    "events": 7,        # Keep events for 1 week
    "weather": 3,       # Keep weather for 3 days
    "scrape_log": 30    # Keep logs for 30 days
}

# Background Task Configuration
BACKGROUND_TASK_TIMEOUT = 600  # 10 minutes in seconds
BACKGROUND_TASK_SCHEDULE = "Weekly on Monday at 6:00 AM"

# API Rate Limiting
OPENAI_RATE_LIMIT_DELAY = 0.5  # seconds between API calls
OPENAI_MAX_RETRIES = 3
OPENAI_RETRY_DELAY = 2  # seconds

# Logging Configuration
LOG_LEVEL = "INFO"

