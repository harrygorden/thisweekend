"""
Date and Time Utilities

Handles timezone-aware date comparisons and filtering for Central Time events.
"""

from datetime import datetime, date, time, timedelta
import pytz


# Memphis is in Central Time
CENTRAL_TZ = pytz.timezone('America/Chicago')


def get_current_central_time():
    """
    Get the current datetime in Central Time.
    
    Returns:
        datetime: Current time in Central timezone
    """
    return datetime.now(CENTRAL_TZ)


def get_current_central_date():
    """
    Get the current date in Central Time.
    
    Returns:
        date: Current date in Central timezone
    """
    return get_current_central_time().date()


def is_event_in_future(event_date, event_time_str=None):
    """
    Check if an event is in the future (Central Time).
    
    Args:
        event_date: date object or datetime object
        event_time_str: Optional time string (e.g., "7:00 PM", "2:30 PM")
        
    Returns:
        bool: True if event is in the future, False if past
    """
    # Get current Central time
    now_central = get_current_central_time()
    
    # If event_date is a datetime, convert to date
    if isinstance(event_date, datetime):
        event_date = event_date.date()
    
    # If no time provided, be conservative
    if not event_time_str:
        # If event is today and it's past 6 PM, consider it past
        # (Most events without times are all-day or don't have reliable end times)
        if event_date == now_central.date():
            # It's today - check if it's late in the day (after 6 PM)
            if now_central.hour >= 18:
                # After 6 PM, hide today's events without specific times
                return False
            else:
                # Before 6 PM, still show today's events
                return True
        # For future dates, show the event
        return event_date > now_central.date()
    
    # Parse the time string
    try:
        # Try common formats
        for fmt in ["%I:%M %p", "%H:%M", "%I %p", "%I:%M%p"]:
            try:
                event_time = datetime.strptime(event_time_str.strip(), fmt).time()
                break
            except ValueError:
                continue
        else:
            # Couldn't parse time, assume whole day
            return event_date >= now_central.date()
        
        # Combine date and time
        event_datetime = datetime.combine(event_date, event_time)
        
        # Make it timezone-aware (Central Time)
        event_datetime_central = CENTRAL_TZ.localize(event_datetime)
        
        # Compare with current Central time
        return event_datetime_central > now_central
        
    except Exception as e:
        print(f"Error parsing event time '{event_time_str}': {e}")
        # If we can't parse the time, just check the date
        return event_date >= now_central.date()


def filter_future_events(events):
    """
    Filter a list of events to only include future events.
    
    Args:
        events: List of event dictionaries or database rows
        
    Returns:
        list: Filtered list containing only future events
    """
    future_events = []
    current_date = get_current_central_date()
    
    print(f"Filtering events (current Central date: {current_date})")
    
    for event in events:
        # Handle both dict and database row
        if isinstance(event, dict):
            event_date = event.get('date')
            event_time = event.get('start_time')
        else:
            # Database row
            event_date = event['date']
            event_time = event['start_time']
        
        if not event_date:
            # No date, skip this event
            continue
        
        if is_event_in_future(event_date, event_time):
            future_events.append(event)
    
    print(f"Filtered {len(events)} events -> {len(future_events)} future events")
    return future_events


def get_days_until_event(event_date):
    """
    Get the number of days until an event.
    
    Args:
        event_date: date object
        
    Returns:
        int: Number of days (0 = today, negative = past)
    """
    current_date = get_current_central_date()
    
    if isinstance(event_date, datetime):
        event_date = event_date.date()
    
    delta = event_date - current_date
    return delta.days

