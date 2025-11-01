"""
AI service module for This Weekend app.
Handles integration with OpenAI SDK for event analysis.
"""

import anvil.server
from datetime import datetime
import json
import time

from . import config
from . import api_helpers

# Import OpenAI SDK (required dependency)
from openai import OpenAI


def analyze_event(event):
    """
    Analyze a single event using ChatGPT to extract:
    - Indoor/outdoor classification
    - Audience type
    - Categories
    - Cost level refinement
    
    Args:
        event: Event dictionary with title, description, location
        
    Returns:
        dict: Analysis results
    """
    # Get API key
    api_key = api_helpers.get_api_key("OPENAI_API_KEY")
    
    # Build the prompt
    prompt = build_analysis_prompt(event)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Make API call
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an event categorization assistant. Analyze events and return structured JSON data."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=config.OPENAI_TEMPERATURE,
        max_tokens=config.OPENAI_MAX_TOKENS,
        response_format={"type": "json_object"}
    )
    
    # Extract and parse response
    content = response.choices[0].message.content
    analysis = json.loads(content)
    
    return analysis


def build_analysis_prompt(event):
    """
    Build the ChatGPT prompt for event analysis.
    
    Args:
        event: Event dictionary
        
    Returns:
        str: Formatted prompt
    """
    prompt = f"""Analyze this event and return a JSON object with the following fields:

Event Details:
Title: {event.get('title', 'Unknown')}
Description: {event.get('description', 'No description')}
Location: {event.get('location', 'Unknown')}
Cost: {event.get('cost_raw', 'Unknown')}

Please analyze and return JSON with these exact fields:
{{
  "is_indoor": boolean (true if event is primarily indoors),
  "is_outdoor": boolean (true if event is primarily outdoors),
  "audience_type": string (one of: "adults", "family-friendly", "all-ages"),
  "categories": array of strings (choose from: {', '.join(config.CATEGORIES)}),
  "cost_level": string (one of: "Free", "$", "$$", "$$$", "$$$$")
}}

Rules:
- An event can be both indoor AND outdoor if it has both components
- Choose 1-3 most relevant categories
- For cost_level: Free=no cost, $=under $20, $$=$20-50, $$$=$50-100, $$$$=over $100
- If cost is ambiguous or says "varies", use "$$" as default
- Be accurate and specific based on the event description

Return ONLY valid JSON, no additional text."""
    
    return prompt


def get_default_analysis():
    """
    Return default analysis values when AI analysis fails.
    
    Returns:
        dict: Default analysis values
    """
    return {
        "is_indoor": True,
        "is_outdoor": False,
        "audience_type": "all-ages",
        "categories": ["Other"],
        "cost_level": "$$"
    }


def parse_ai_response(ai_response):
    """
    Parse and validate AI response.
    
    Args:
        ai_response: Response from ChatGPT
        
    Returns:
        dict: Validated analysis data
    """
    try:
        # Ensure all required fields are present
        required_fields = ["is_indoor", "is_outdoor", "audience_type", "categories", "cost_level"]
        
        for field in required_fields:
            if field not in ai_response:
                print(f"Missing field in AI response: {field}")
                return get_default_analysis()
        
        # Validate audience_type
        if ai_response["audience_type"] not in config.AUDIENCE_TYPES:
            print(f"Invalid audience_type: {ai_response['audience_type']}")
            ai_response["audience_type"] = "all-ages"
        
        # Validate cost_level
        valid_cost_levels = ["Free", "$", "$$", "$$$", "$$$$"]
        if ai_response["cost_level"] not in valid_cost_levels:
            print(f"Invalid cost_level: {ai_response['cost_level']}")
            ai_response["cost_level"] = "$$"
        
        # Ensure categories is a list
        if not isinstance(ai_response["categories"], list):
            ai_response["categories"] = ["Other"]
        
        return ai_response
        
    except Exception as e:
        print(f"Error parsing AI response: {str(e)}")
        return get_default_analysis()


def analyze_all_events(events):
    """
    Analyze all events using AI with rate limiting.
    
    Args:
        events: List of event rows from database
        
    Returns:
        dict: Event ID to analysis mapping
    """
    total = len(events)
    print(f"Analyzing {total} events with AI (showing progress at 25%, 50%, 75%, 100%)...")
    
    analyses = {}
    milestones = [int(total * 0.25), int(total * 0.5), int(total * 0.75), total]
    
    for i, event in enumerate(events):
        event_id = event["event_id"]
        
        # Show progress only at key milestones
        if (i + 1) in milestones:
            percent = int(((i + 1) / total) * 100)
            print(f"  ✓ {percent}% complete ({i+1}/{total})")
        
        # Prepare event data for analysis
        event_data = {
            "title": event["title"],
            "description": event["description"],
            "location": event["location"],
            "cost_raw": event["cost_raw"]
        }
        
        # Analyze with retry logic
        try:
            analysis = api_helpers.retry_with_backoff(
                lambda: analyze_event(event_data),
                max_retries=config.OPENAI_MAX_RETRIES,
                initial_delay=config.OPENAI_RETRY_DELAY
            )
            
            # Validate and parse response
            analyses[event_id] = parse_ai_response(analysis)
            
        except Exception as e:
            print(f"  ❌ Failed to analyze '{event['title']}': {str(e)}")
            analyses[event_id] = get_default_analysis()
        
        # Rate limiting delay (except for last event)
        if i < len(events) - 1:
            time.sleep(config.OPENAI_RATE_LIMIT_DELAY)
    
    print(f"Completed AI analysis for {len(analyses)} events")
    return analyses


def update_events_with_analysis(analyses):
    """
    Update events in database with AI analysis results.
    
    Args:
        analyses: Dictionary of event_id to analysis results
        
    Returns:
        int: Number of events updated
    """
    from anvil.tables import app_tables
    
    print(f"Updating {len(analyses)} events with AI analysis...")
    
    updated_count = 0
    
    try:
        for event_id, analysis in analyses.items():
            # Find the event in the database
            event = app_tables.events.get(event_id=event_id)
            
            if event:
                # Update with AI analysis
                event["is_indoor"] = analysis["is_indoor"]
                event["is_outdoor"] = analysis["is_outdoor"]
                event["audience_type"] = analysis["audience_type"]
                event["categories"] = analysis["categories"]
                event["cost_level"] = analysis["cost_level"]
                event["analyzed_at"] = datetime.now()
                
                updated_count += 1
            else:
                print(f"Event not found in database: {event_id}")
        
        print(f"Successfully updated {updated_count} events with AI analysis")
        return updated_count
        
    except Exception as e:
        print(f"Error updating events with analysis: {str(e)}")
        raise


def generate_weather_aware_suggestions(weather_data, events):
    """
    Generate AI-powered suggestions based on weather forecast and available events.
    
    Args:
        weather_data: List of weather forecast dictionaries for the weekend
        events: List of event dictionaries
        
    Returns:
        str: AI-generated suggestions text
    """
    # Get API key
    api_key = api_helpers.get_api_key("OPENAI_API_KEY")
    
    # Build the prompt
    prompt = build_suggestions_prompt(weather_data, events)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Make API call
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a friendly local events guide for Memphis, TN. Recommend specific events from the provided list based on weather conditions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,  # More creative for suggestions
        max_tokens=400  # Allow for specific event recommendations with explanations
    )
    
    # Extract response
    suggestions = response.choices[0].message.content.strip()
    
    return suggestions


def build_suggestions_prompt(weather_data, events):
    """
    Build the ChatGPT prompt for weather-aware suggestions.
    
    Args:
        weather_data: List of weather forecast dictionaries
        events: List of event dictionaries
        
    Returns:
        str: Formatted prompt
    """
    # Summarize weather
    weather_summary = []
    for day in weather_data[:3]:  # Fri, Sat, Sun
        weather_summary.append(
            f"{day['day_name']}: {day['temp_high']}°F/{day['temp_low']}°F, "
            f"{day['conditions']}, {day['precipitation_chance']}% rain"
        )
    
    # Separate events by weather suitability
    # Good for nice weather (outdoor, low rain days)
    outdoor_suitable = []
    # Good for rainy weather (indoor, any day)
    indoor_suitable = []
    
    for event in events[:20]:  # Top 20 by recommendation score
        if event.get('is_outdoor'):
            outdoor_suitable.append(event)
        if event.get('is_indoor'):
            indoor_suitable.append(event)
    
    # Build event details for AI
    event_details = []
    for event in events[:15]:  # Top 15 events
        venue_type = "outdoor" if event.get('is_outdoor') else "indoor"
        cost = event.get('cost_level', '$$')
        event_details.append(
            f"- {event['title']} ({venue_type}, {event['day_name']}, {cost}, {event.get('location', 'TBD')})"
        )
    
    prompt = f"""Based on this weekend's weather forecast, recommend 3-4 SPECIFIC events from the list below that would be most enjoyable given the conditions.

Weather Forecast:
{chr(10).join(weather_summary)}

Available Events (pre-sorted by recommendation score):
{chr(10).join(event_details)}

Instructions:
- Recommend 3-4 SPECIFIC event names from the list above
- If weather is nice (low rain, comfortable temps), prioritize outdoor events
- If weather is rainy or extreme, prioritize indoor events
- Mix different types of activities if possible
- Keep it to 3-4 sentences total
- Be warm and conversational, like a local friend giving advice
- Briefly explain WHY each event is good for the weather

Example format:
"With [weather description], I'd definitely check out [Event Name] on [Day] - perfect for [reason]. [Event Name] is another great option if you're looking for [activity type]. Don't miss [Event Name], especially with this [weather condition]!"

Now write specific event recommendations for THIS weekend:"""
    
    return prompt


@anvil.server.callable
def get_weekend_suggestions():
    """
    Get AI-generated weather-aware weekend suggestions.
    Callable from client-side code.
    
    Returns:
        str: Suggestion text, or None if generation fails
    """
    try:
        # Get weather data
        from . import weather_service
        weather_data = weather_service.get_weather_data()
        
        if not weather_data:
            return None
        
        # Get events
        from . import data_processor
        events = data_processor.get_all_events(sort_by='recommendation')
        
        if not events:
            return None
        
        # Generate suggestions
        suggestions = generate_weather_aware_suggestions(weather_data, events)
        
        return suggestions
        
    except Exception as e:
        print(f"Error generating weekend suggestions: {str(e)}")
        return None