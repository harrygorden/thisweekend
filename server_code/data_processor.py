"""
Data processing module for This Weekend app.
Handles event-weather matching and recommendation scoring.
"""

import anvil.server
from anvil.tables import app_tables
from datetime import datetime

from . import config
from . import weather_service


def match_events_with_weather():
    """
    Match all events with their corresponding weather forecasts
    and calculate weather scores.
    
    Returns:
        int: Number of events processed
    """
    print("Matching events with weather data...")
    
    processed_count = 0
    
    try:
        # Get all events from database
        events = app_tables.events.search()
        
        for event in events:
            # Get weather for event date
            weather_data = weather_service.get_weather_for_datetime(
                event["date"],
                event["start_time"]
            )
            
            if weather_data:
                # Calculate weather score
                event_data = {
                    "is_outdoor": event["is_outdoor"],
                    "is_indoor": event["is_indoor"],
                    "date": event["date"],
                    "start_time": event["start_time"]
                }
                
                weather_score = weather_service.calculate_weather_score(
                    event_data,
                    weather_data
                )
                
                # Update event with weather score
                event["weather_score"] = weather_score
                
                processed_count += 1
            else:
                print(f"No weather data found for event: {event['title']} on {event['date']}")
                # Assign neutral score if no weather data
                event["weather_score"] = 50
                processed_count += 1
        
        print(f"Processed weather matching for {processed_count} events")
        return processed_count
        
    except Exception as e:
        print(f"Error matching events with weather: {str(e)}")
        raise


def calculate_recommendation_score(event):
    """
    Calculate overall recommendation score for an event (0-100).
    
    Args:
        event: Event row from database
        
    Returns:
        int: Recommendation score (0-100)
    """
    # Anvil rows don't have .get() - use direct access with defaults
    weather_score = event["weather_score"] if event["weather_score"] is not None else 50
    is_outdoor = event["is_outdoor"] if event["is_outdoor"] is not None else False
    is_indoor = event["is_indoor"] if event["is_indoor"] is not None else True
    start_time = event["start_time"] or ""
    
    if is_outdoor and not is_indoor:
        # Pure outdoor event - heavily weighted by weather
        score = weather_score * (config.WEATHER_WEIGHTS["outdoor_weather_score"])
        
        # Add time of day bonus (evening outdoor events are nice)
        time_bonus = calculate_time_of_day_bonus(start_time)
        score += time_bonus * (config.WEATHER_WEIGHTS["outdoor_time_of_day"])
        
    elif is_indoor and not is_outdoor:
        # Pure indoor event - baseline score
        score = config.WEATHER_WEIGHTS["indoor_baseline"]
        
        # Boost slightly if weather is bad (people prefer indoor activities)
        if weather_score < 50:
            score += config.WEATHER_WEIGHTS["bad_weather_indoor_boost"]
        
    else:
        # Mixed indoor/outdoor event - moderate weather influence
        score = (weather_score * 0.4) + (config.WEATHER_WEIGHTS["indoor_baseline"] * 0.6)
    
    # Ensure score is in valid range
    return int(max(0, min(100, score)))


def calculate_time_of_day_bonus(start_time):
    """
    Calculate bonus points based on time of day.
    Evening events (5 PM - 9 PM) get higher scores for outdoor activities.
    
    Args:
        start_time: Time string (e.g., "3:00 PM")
        
    Returns:
        int: Bonus points (0-30)
    """
    if not start_time or start_time == "TBD":
        return 15  # Neutral bonus
    
    try:
        # Parse time
        time_str = start_time.upper()
        
        # Extract hour
        if "PM" in time_str:
            hour = int(time_str.split(":")[0])
            if hour != 12:
                hour += 12
        else:
            hour = int(time_str.split(":")[0])
            if hour == 12:
                hour = 0
        
        # Score based on time
        if 17 <= hour <= 21:  # 5 PM - 9 PM
            return 30  # Peak outdoor evening time
        elif 14 <= hour <= 17 or 21 <= hour <= 23:  # 2-5 PM or 9-11 PM
            return 20  # Good time
        elif 10 <= hour <= 14:  # 10 AM - 2 PM
            return 15  # Daytime
        else:
            return 10  # Early morning or late night
        
    except:
        return 15  # Default if parsing fails


def update_all_recommendation_scores():
    """
    Calculate and update recommendation scores for all events.
    
    Returns:
        int: Number of events updated
    """
    print("Calculating recommendation scores for all events...")
    
    updated_count = 0
    
    try:
        events = app_tables.events.search()
        
        for event in events:
            score = calculate_recommendation_score(event)
            event["recommendation_score"] = score
            updated_count += 1
        
        print(f"Updated recommendation scores for {updated_count} events")
        return updated_count
        
    except Exception as e:
        print(f"Error updating recommendation scores: {str(e)}")
        raise


def get_weather_warning(event):
    """
    Generate weather warning message for outdoor events.
    
    Args:
        event: Event row from database
        
    Returns:
        str: Warning message or None if no warning needed
    """
    if not event["is_outdoor"]:
        return None
    
    weather_score = event["weather_score"] if event["weather_score"] is not None else 100
    
    # Get weather details
    weather_data = weather_service.get_weather_for_datetime(
        event["date"],
        event["start_time"]
    )
    
    if not weather_data:
        return None
    
    warnings = []
    
    # Check precipitation
    precip = weather_data.get("precipitation_chance", 0)
    if precip > 70:
        warnings.append(f"High chance of rain ({precip}%)")
    elif precip > 40:
        warnings.append(f"Possible rain ({precip}%)")
    
    # Check temperature
    temp = weather_data.get("temp_high", 70)
    if temp < 40:
        warnings.append(f"Very cold ({temp}°F)")
    elif temp > 95:
        warnings.append(f"Very hot ({temp}°F)")
    
    # Check wind
    wind = weather_data.get("wind_speed", 0)
    if wind > 20:
        warnings.append(f"Windy conditions ({wind} mph)")
    
    if warnings:
        return " • ".join(warnings)
    
    return None


@anvil.server.callable
def get_filtered_events(filters=None):
    """
    Get events filtered by various criteria.
    Callable from client-side code.
    
    Args:
        filters: Dictionary of filter criteria:
            - days: List of day names (e.g., ["Friday", "Saturday"])
            - cost_levels: List of cost levels (e.g., ["Free", "$"])
            - categories: List of categories
            - audience_types: List of audience types
            - indoor: Boolean - include indoor events
            - outdoor: Boolean - include outdoor events
            
    Returns:
        list: List of filtered event dictionaries
    """
    from anvil.tables import query as q
    
    # Start with all events
    events = app_tables.events.search()
    
    if not filters:
        return serialize_events(events)
    
    # Apply filters
    filtered_events = []
    
    for event in events:
        # Filter by day
        if filters.get("days"):
            day_name = event["date"].strftime("%A") if event["date"] else None
            if day_name not in filters["days"]:
                continue
        
        # Filter by cost
        if filters.get("cost_levels"):
            if event["cost_level"] not in filters["cost_levels"]:
                continue
        
        # Filter by categories
        if filters.get("categories"):
            event_categories = event["categories"] or []
            if not any(cat in event_categories for cat in filters["categories"]):
                continue
        
        # Filter by audience type
        if filters.get("audience_types"):
            if event["audience_type"] not in filters["audience_types"]:
                continue
        
        # Filter by indoor/outdoor
        include_indoor = filters.get("indoor", True)
        include_outdoor = filters.get("outdoor", True)
        
        if not include_indoor and event["is_indoor"]:
            continue
        if not include_outdoor and event["is_outdoor"]:
            continue
        
        filtered_events.append(event)
    
    return serialize_events(filtered_events)


@anvil.server.callable
def get_all_events(sort_by="recommendation"):
    """
    Get all future events from the database.
    Callable from client-side code.
    
    Args:
        sort_by: Sort criteria ("recommendation", "time", "cost")
        
    Returns:
        list: List of event dictionaries
    """
    try:
        from . import date_utils
        
        events = list(app_tables.events.search())
        print(f"Found {len(events)} total events in database")
        
        # Filter to only future events
        events = date_utils.filter_future_events(events)
        
        # Sort events
        if sort_by == "recommendation":
            events.sort(key=lambda e: e["recommendation_score"] or 0, reverse=True)
        elif sort_by == "time":
            events.sort(key=lambda e: (e["date"] or datetime.max.date(), e["start_time"] or "ZZZ"))
        elif sort_by == "cost":
            cost_order = {"Free": 0, "$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
            events.sort(key=lambda e: cost_order.get(e["cost_level"] or "$", 5))
        
        return serialize_events(events)
    except Exception as e:
        print(f"Error in get_all_events: {e}")
        import traceback
        traceback.print_exc()
        raise


def serialize_events(events):
    """
    Convert event rows to dictionaries for client consumption.
    
    Args:
        events: List of event rows
        
    Returns:
        list: List of event dictionaries
    """
    serialized = []
    
    for event in events:
        try:
            serialized.append({
                "event_id": event["event_id"],
                "title": event["title"] or "Untitled Event",
                "description": event["description"] or "",
                "date": event["date"],
                "day_name": event["date"].strftime("%A") if event["date"] else None,
                "start_time": event["start_time"] or "Time TBD",
                "end_time": event["end_time"] or "",
                "location": event["location"] or "Location TBD",
                "cost_raw": event["cost_raw"] or "",
                "cost_level": event["cost_level"] or "$",
                "is_indoor": event["is_indoor"] if event["is_indoor"] is not None else False,
                "is_outdoor": event["is_outdoor"] if event["is_outdoor"] is not None else False,
                "audience_type": event["audience_type"] or "all-ages",
                "categories": event["categories"] or [],
                "weather_score": event["weather_score"] or 0,
                "recommendation_score": event["recommendation_score"] or 0,
                "weather_warning": get_weather_warning(event)
            })
        except Exception as e:
            print(f"Error serializing event {event.get_id()}: {e}")
            # Skip this event but continue with others
            continue
    
    return serialized

