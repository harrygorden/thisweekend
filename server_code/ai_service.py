"""
AI service module for This Weekend app.
Handles integration with OpenAI ChatGPT API for event analysis.
"""

import anvil.server
import anvil.http
from datetime import datetime
import json
import time

from . import config
from . import api_helpers


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
    
    # OpenAI API endpoint
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": config.OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an event categorization assistant. Analyze events and return structured JSON data."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": config.OPENAI_TEMPERATURE,
        "max_tokens": config.OPENAI_MAX_TOKENS,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = anvil.http.request(
            url,
            method="POST",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API returned status {response.status_code}: {response.get_text()}")
        
        # Parse response
        result = json.loads(response.get_text())
        content = result["choices"][0]["message"]["content"]
        analysis = json.loads(content)
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing event '{event.get('title', 'Unknown')}': {str(e)}")
        # Return default values on error
        return get_default_analysis()


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
        "is_indoor": True,  # Conservative default
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
    print(f"Analyzing {len(events)} events with AI...")
    
    analyses = {}
    
    for i, event in enumerate(events):
        event_id = event["event_id"]
        
        print(f"Analyzing event {i+1}/{len(events)}: {event['title']}")
        
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
            print(f"Failed to analyze event after retries: {str(e)}")
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
                event["categories"] = analysis["categories"]  # Store as SimpleObject/list
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

