"""
AI service module for This Weekend app.
Handles integration with OpenAI ChatGPT API for event analysis.

This module tries to use the OpenAI Python SDK for reliability,
with automatic fallback to raw HTTP if the SDK is not available.
"""

import anvil.server
import anvil.http
from datetime import datetime
import json
import time

from . import config
from . import api_helpers

# Try to import OpenAI Python SDK (more reliable)
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
    print("✅ OpenAI Python SDK available - using SDK mode")
except ImportError:
    OPENAI_SDK_AVAILABLE = False
    print("⚠️ OpenAI SDK not installed - using fallback HTTP mode")
    print("   Install with: pip install openai")
    print("   See server_code/requirements.txt for instructions")


def analyze_event(event):
    """
    Analyze a single event using ChatGPT to extract:
    - Indoor/outdoor classification
    - Audience type
    - Categories
    - Cost level refinement
    
    Tries to use OpenAI SDK first, falls back to raw HTTP if SDK unavailable.
    
    Args:
        event: Event dictionary with title, description, location
        
    Returns:
        dict: Analysis results
    """
    # Get API key
    api_key = api_helpers.get_api_key("OPENAI_API_KEY")
    
    # Build the prompt
    prompt = build_analysis_prompt(event)
    
    # Try SDK first if available (more reliable)
    if OPENAI_SDK_AVAILABLE:
        try:
            return analyze_event_with_sdk(api_key, event, prompt)
        except Exception as sdk_error:
            print(f"  ⚠️ SDK method failed: {str(sdk_error)[:200]}")
            print("  🔄 Falling back to raw HTTP method...")
            # Continue to raw HTTP fallback below
    
    # Fallback to raw HTTP
    return analyze_event_with_http(api_key, event, prompt)


def analyze_event_with_sdk(api_key, event, prompt):
    """
    Analyze event using OpenAI Python SDK (recommended method).
    
    Args:
        api_key: OpenAI API key
        event: Event dictionary
        prompt: Analysis prompt
        
    Returns:
        dict: Analysis results
    """
    # Reduced verbosity - only log on first call or errors
    try:
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
        
    except Exception as e:
        print(f"  ❌ SDK error for '{event.get('title', 'Unknown')}': {str(e)}")
        raise


def analyze_event_with_http(api_key, event, prompt):
    """
    Analyze event using raw HTTP requests to OpenAI API (fallback method).
    
    Args:
        api_key: OpenAI API key
        event: Event dictionary
        prompt: Analysis prompt
        
    Returns:
        dict: Analysis results
    """
    # Reduced verbosity - only log on errors
    
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
        # In Anvil, http.request returns a StreamingMedia object
        response = anvil.http.request(
            url,
            method="POST",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Convert StreamingMedia to string
        response_text = response.get_bytes().decode('utf-8')
        
        # Parse response
        result = json.loads(response_text)
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
        
        # Show progress every 10 events or on first/last event
        if i == 0 or (i + 1) % 10 == 0 or i == len(events) - 1:
            print(f"  Progress: {i+1}/{len(events)} events analyzed")
        
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

