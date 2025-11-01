"""
Debug Tools for This Weekend App

Diagnostic functions to help troubleshoot issues.
"""

import anvil.server
from anvil.tables import app_tables
from datetime import datetime


@anvil.server.callable
def show_event_dates():
    """
    Show what dates events are actually assigned to in the database.
    Useful for debugging date issues.
    
    Returns:
        dict: Summary of event dates
    """
    from . import date_utils
    
    events = list(app_tables.events.search())
    
    # Group events by date
    by_date = {}
    for event in events:
        event_date = event['date']
        if event_date:
            date_str = event_date.strftime('%Y-%m-%d (%A)')
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append({
                'title': event['title'],
                'time': event['start_time'],
                'is_future': date_utils.is_event_in_future(event_date, event['start_time'])
            })
    
    # Get current time info
    current_central = date_utils.get_current_central_time()
    current_date = current_central.date()
    current_time_str = current_central.strftime('%I:%M %p')
    
    result = {
        'current_central_time': f"{current_date} {current_time_str}",
        'current_weekday': current_date.strftime('%A'),
        'total_events': len(events),
        'events_by_date': by_date,
        'date_summary': []
    }
    
    # Create summary
    for date_str in sorted(by_date.keys()):
        event_count = len(by_date[date_str])
        future_count = sum(1 for e in by_date[date_str] if e['is_future'])
        past_count = event_count - future_count
        
        result['date_summary'].append(
            f"{date_str}: {event_count} events ({future_count} future, {past_count} past)"
        )
    
    return result


@anvil.server.callable
def show_weekend_date_calculation():
    """
    Show what weekend dates the system is calculating.
    Useful for debugging weekend date logic.
    
    Returns:
        dict: Weekend date calculation details
    """
    from . import api_helpers
    from . import date_utils
    
    current_central = date_utils.get_current_central_time()
    weekend_dates = api_helpers.get_weekend_dates()
    
    return {
        'current_central_time': current_central.strftime('%Y-%m-%d %I:%M %p %A'),
        'current_weekday_num': current_central.weekday(),
        'current_weekday_name': current_central.strftime('%A'),
        'weekend_friday': weekend_dates['friday'].strftime('%Y-%m-%d (%A)'),
        'weekend_saturday': weekend_dates['saturday'].strftime('%Y-%m-%d (%A)'),
        'weekend_sunday': weekend_dates['sunday'].strftime('%Y-%m-%d (%A)')
    }


@anvil.server.callable
def count_events_by_day():
    """
    Count events grouped by day name.
    
    Returns:
        dict: Count of events for each day
    """
    events = list(app_tables.events.search())
    
    counts = {
        'Friday': 0,
        'Saturday': 0,
        'Sunday': 0,
        'Other': 0,
        'No Date': 0
    }
    
    for event in events:
        if not event['date']:
            counts['No Date'] += 1
        else:
            day_name = event['date'].strftime('%A')
            if day_name in counts:
                counts[day_name] += 1
            else:
                counts['Other'] += 1
    
    counts['Total'] = len(events)
    return counts

