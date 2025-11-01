"""
Common API utility functions for This Weekend app.
Provides shared functionality for API calls, error handling, and data processing.
"""

import anvil.server
import anvil.secrets
import time
from datetime import datetime, timedelta
import json

def get_api_key(secret_name):
    """
    Retrieve an API key from Anvil Secrets.
    
    Args:
        secret_name: Name of the secret in Anvil Secrets
        
    Returns:
        API key string
        
    Raises:
        ValueError: If the secret is not configured
    """
    api_key = anvil.secrets.get_secret(secret_name)
    if not api_key:
        raise ValueError(f"API key '{secret_name}' not configured in Anvil Secrets")
    return api_key


def retry_with_backoff(func, max_retries=3, initial_delay=1, backoff_factor=2):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        
    Returns:
        Result of the function call
        
    Raises:
        Exception: Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= backoff_factor
    
    raise last_exception


def parse_date_string(date_str):
    """
    Parse various date string formats.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        datetime.date object or None if parsing fails
    """
    if not date_str:
        return None
    
    # Common date formats to try
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%A, %B %d, %Y",
        "%a, %b %d, %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    print(f"Unable to parse date: {date_str}")
    return None


def parse_time_string(time_str):
    """
    Parse various time string formats.
    
    Args:
        time_str: Time string in various formats
        
    Returns:
        Formatted time string (HH:MM AM/PM) or original string if parsing fails
    """
    if not time_str:
        return None
    
    time_str = time_str.strip().lower()
    
    # Common time formats to try
    formats = [
        "%I:%M %p",    # 3:00 PM
        "%I:%M%p",     # 3:00PM
        "%I %p",       # 3 PM
        "%I%p",        # 3PM
        "%H:%M",       # 15:00
    ]
    
    for fmt in formats:
        try:
            time_obj = datetime.strptime(time_str.upper(), fmt)
            return time_obj.strftime("%I:%M %p")
        except ValueError:
            continue
    
    # Return original if parsing fails
    return time_str


def sanitize_text(text):
    """
    Clean and sanitize text content.
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Remove any unusual control characters
    text = "".join(char for char in text if ord(char) >= 32 or char == '\n')
    
    return text.strip()


def get_weekend_dates():
    """
    Get the weekend dates for the events on ilovememphisblog.com/weekend (Central Time).
    
    The website is updated Mon/Tue for the upcoming weekend, so:
    - Mon-Thu: Returns the upcoming weekend (this week's Fri-Sun)  
    - Fri-Sun: Returns the current weekend (started last/this Friday)
    
    Returns:
        dict: Dictionary with 'friday', 'saturday', 'sunday' as datetime.date objects
    """
    from . import date_utils
    
    # Use Central Time, not UTC
    today = date_utils.get_current_central_date()
    current_weekday = today.weekday()  # Monday = 0, Sunday = 6
    
    # The website shows events for:
    # - Mon-Thu: UPCOMING weekend (this week's Fri-Sun)
    # - Fri-Sun: CURRENT weekend (most recent Friday)
    
    if current_weekday <= 3:
        # Monday (0) through Thursday (3): Get upcoming Friday
        days_to_friday = 4 - current_weekday
        friday = today + timedelta(days=days_to_friday)
    elif current_weekday == 4:
        # Friday (4): The weekend just started
        # But website was updated Mon/Tue for "this weekend"
        # So if it's early Friday (before noon), events might be for today
        # If it's late Friday (after noon), events started yesterday
        current_time = date_utils.get_current_central_time()
        if current_time.hour < 12:
            # Before noon Friday: events are for today's weekend
            friday = today
        else:
            # After noon Friday: page shows events that started earlier
            # Most events are done or in progress, use today anyway
            # (filtering will remove past events)
            friday = today
    else:
        # Saturday (5) or Sunday (6): Get last Friday
        days_since_friday = current_weekday - 4
        friday = today - timedelta(days=days_since_friday)
    
    saturday = friday + timedelta(days=1)
    sunday = friday + timedelta(days=2)
    
    print(f"Weekend dates (Central Time, {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][current_weekday]}): Fri={friday}, Sat={saturday}, Sun={sunday}")
    
    return {
        "friday": friday,
        "saturday": saturday,
        "sunday": sunday
    }


def get_day_name(date_obj):
    """
    Get the day name from a date object.
    
    Args:
        date_obj: datetime.date object
        
    Returns:
        Day name string (e.g., "Friday", "Saturday", "Sunday")
    """
    if not date_obj:
        return None
    
    return date_obj.strftime("%A")


def calculate_duration(start_time, end_time):
    """
    Calculate duration between two times.
    
    Args:
        start_time: Start time string
        end_time: End time string
        
    Returns:
        Duration in hours (float) or None if calculation fails
    """
    if not start_time or not end_time:
        return None
    
    try:
        start = datetime.strptime(start_time, "%I:%M %p")
        end = datetime.strptime(end_time, "%I:%M %p")
        
        # Handle times that span midnight
        if end < start:
            end += timedelta(days=1)
        
        duration = (end - start).total_seconds() / 3600
        return duration
    except:
        return None


def truncate_text(text, max_length=200):
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def format_currency(cost_level):
    """
    Format cost level as currency symbols.
    
    Args:
        cost_level: Cost level string
        
    Returns:
        Formatted cost string
    """
    if not cost_level:
        return "Unknown"
    
    cost_level = cost_level.lower()
    
    if cost_level == "free":
        return "Free"
    elif cost_level in ["$", "$$", "$$$", "$$$$"]:
        return cost_level
    else:
        return cost_level.title()


def generate_unique_id(prefix=""):
    """
    Generate a unique ID based on timestamp.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    if prefix:
        return f"{prefix}_{timestamp}"
    return timestamp


def safe_json_parse(json_str):
    """
    Safely parse JSON string.
    
    Args:
        json_str: JSON string to parse
        
    Returns:
        Parsed JSON object or None if parsing fails
    """
    if not json_str:
        return None
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {str(e)}")
        return None


def safe_json_dumps(obj):
    """
    Safely convert object to JSON string.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON string or empty string if conversion fails
    """
    try:
        return json.dumps(obj)
    except Exception as e:
        print(f"JSON dumps error: {str(e)}")
        return ""

