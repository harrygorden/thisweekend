"""
Direct web scraping fallback for This Weekend app.
Used if Firecrawl API is unavailable or has issues.

This scraper uses direct HTTP requests and HTML parsing
to extract event data from ilovememphisblog.com/weekend
"""

import anvil.server
import anvil.http
from datetime import datetime
import json
import re

from . import config
from . import api_helpers


def scrape_weekend_events_direct():
    """
    Scrape weekend events directly from the website without Firecrawl API.
    Falls back to basic HTML parsing.
    
    Returns:
        str: Extracted text content from the website
        
    Raises:
        Exception: If scraping fails
    """
    print(f"Scraping events DIRECTLY from {config.TARGET_WEBSITE_URL}...")
    print("  (Using direct HTTP, no Firecrawl API)")
    
    try:
        # Make direct HTTP request to the website
        response = anvil.http.request(
            config.TARGET_WEBSITE_URL,
            method="GET",
            timeout=30
        )
        
        # Convert to string
        html_content = response.get_bytes().decode('utf-8')
        print(f"  Downloaded {len(html_content)} bytes of HTML")
        
        # Extract text content from HTML
        # This is a simple approach - removes HTML tags
        text_content = extract_text_from_html(html_content)
        
        print(f"  Extracted {len(text_content)} characters of text")
        return text_content
        
    except Exception as e:
        print(f"Error in direct scraping: {str(e)}")
        raise


def extract_text_from_html(html):
    """
    Extract text content from HTML.
    Simple tag removal for basic parsing.
    
    Args:
        html: HTML string
        
    Returns:
        str: Text content
    """
    # Remove script and style tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '\n', html)
    
    # Clean up whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    return text


def parse_events_from_html_text(text_content):
    """
    Parse events from extracted HTML text.
    Looks for event patterns in the text.
    
    Args:
        text_content: Extracted text from HTML
        
    Returns:
        list: List of event dictionaries
    """
    print("Parsing events from HTML text...")
    
    events = []
    weekend_dates = api_helpers.get_weekend_dates()
    
    lines = text_content.split('\n')
    
    current_event = None
    current_day = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Detect day markers
        if re.search(r'\b(Friday|Saturday|Sunday)\b', line, re.IGNORECASE):
            day_match = re.search(r'\b(Friday|Saturday|Sunday)\b', line, re.IGNORECASE)
            current_day = day_match.group(1).lower()
            continue
        
        # Look for event title patterns
        # Typically longer lines without common words
        if len(line) > 15 and not any(word in line.lower() for word in ['advertisement', 'subscribe', 'follow', 'share']):
            # Might be an event title
            if current_event and current_event.get('title'):
                # Save previous event if it has enough data
                if current_event.get('title') and current_event.get('date'):
                    events.append(current_event)
            
            # Start new event
            current_event = {
                'title': line,
                'date': weekend_dates.get(current_day) if current_day else None,
                'description': '',
                'location': '',
                'cost_raw': '',
                'start_time': 'TBD',
                'scraped_at': datetime.now()
            }
        
        elif current_event:
            # Accumulate data for current event
            
            # Look for time patterns
            time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm|a\.m\.|p\.m\.))', line, re.IGNORECASE)
            if time_match and current_event['start_time'] == 'TBD':
                current_event['start_time'] = api_helpers.parse_time_string(time_match.group(1))
            
            # Look for cost indicators
            if re.search(r'\$\d+|free|donation', line, re.IGNORECASE) and not current_event.get('cost_raw'):
                current_event['cost_raw'] = line
            
            # Look for location patterns
            if re.search(r'\b(at|venue|location)\b', line, re.IGNORECASE) and not current_event.get('location'):
                location_match = re.search(r'(?:at|venue|location):?\s*(.+?)(?:\.|$)', line, re.IGNORECASE)
                if location_match:
                    current_event['location'] = location_match.group(1).strip()
            
            # Add to description
            if len(line) > 20:  # Only add substantial lines
                current_event['description'] += ' ' + line
    
    # Don't forget last event
    if current_event and current_event.get('title') and current_event.get('date'):
        events.append(current_event)
    
    # Clean up events
    for event in events:
        event['description'] = api_helpers.sanitize_text(event.get('description', ''))[:500]
        event['location'] = api_helpers.sanitize_text(event.get('location', 'TBD'))
        event['event_id'] = api_helpers.generate_unique_id('evt')
    
    print(f"Parsed {len(events)} events from HTML text")
    return events


@anvil.server.callable
def test_direct_scraping():
    """
    Test the direct scraping method.
    Callable for debugging.
    
    Returns:
        dict: Scraping results
    """
    try:
        text = scrape_weekend_events_direct()
        events = parse_events_from_html_text(text)
        
        return {
            'success': True,
            'text_length': len(text),
            'events_found': len(events),
            'sample_events': events[:3] if events else []
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

