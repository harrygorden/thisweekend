"""
Web scraping service module for This Weekend app.
Handles integration with Firecrawl API for event data collection.
"""

import anvil.server
import anvil.http
from datetime import datetime
import json
import re

from . import config
from . import api_helpers

# Import direct scraper for fallback
try:
    from . import scraper_direct
    DIRECT_SCRAPER_AVAILABLE = True
except ImportError:
    DIRECT_SCRAPER_AVAILABLE = False
    print("Warning: Direct scraper not available")


def scrape_weekend_events():
    """
    Scrape weekend events from ilovememphisblog.com/weekend.
    Tries Firecrawl API first, falls back to direct scraping.
    
    Returns:
        str: Raw text content from the website
        
    Raises:
        Exception: If all scraping methods fail
    """
    print(f"Scraping events from {config.TARGET_WEBSITE_URL}...")
    
    # Try Firecrawl first
    try:
        return scrape_with_firecrawl()
    except Exception as firecrawl_error:
        print(f"  ⚠️ Firecrawl failed: {str(firecrawl_error)[:200]}")
        
        # Fall back to direct scraping
        if DIRECT_SCRAPER_AVAILABLE:
            print("  🔄 Switching to direct HTTP scraping...")
            try:
                return scraper_direct.scrape_weekend_events_direct()
            except Exception as direct_error:
                print(f"  ❌ Direct scraping also failed: {direct_error}")
                raise Exception(f"All scraping methods failed. Firecrawl: {str(firecrawl_error)[:100]}, Direct: {str(direct_error)[:100]}")
        else:
            raise


def scrape_with_firecrawl():
    """
    Scrape using Firecrawl API.
    
    Returns:
        str: Markdown content from Firecrawl
        
    Raises:
        Exception: If Firecrawl fails
    """
    print("  Trying Firecrawl API...")
    
    # Get API key
    api_key = api_helpers.get_api_key("FIRECRAWL_API_KEY")
    
    # Firecrawl API v2 endpoint (updated from v1)
    url = "https://api.firecrawl.dev/v2/scrape"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Updated payload format for Firecrawl v2
    # Reference: https://context7.com/firecrawl/firecrawl/llms.txt
    payload = {
        "url": config.TARGET_WEBSITE_URL,
        "formats": ["markdown", "html"]  # Request markdown and html
    }
    
    try:
        print(f"  Making request to {url}")
        print(f"  Payload: {payload}")
        print(f"  API Key (first 10 chars): {api_key[:10]}...")
        
        # In Anvil, http.request returns a StreamingMedia object
        # Anvil throws HttpError on non-2xx responses
        response = anvil.http.request(
            url,
            method="POST",
            json=payload,
            headers=headers,
            timeout=config.FIRECRAWL_TIMEOUT
        )
        
        # Convert StreamingMedia to string
        response_text = response.get_bytes().decode('utf-8')
        print(f"  Received {len(response_text)} bytes")
        
        # Parse response
        result = json.loads(response_text)
        
        # Check if request was successful
        if not result.get("success", False):
            error_msg = result.get("error", "Unknown error")
            raise Exception(f"Firecrawl returned error: {error_msg}")
        
        # Extract markdown content from v2 response format
        # v2 format: {"success": true, "data": {"markdown": "...", "metadata": {...}}}
        if "data" in result:
            data = result["data"]
            markdown_content = data.get("markdown", "")
            
            # Log metadata for debugging
            if "metadata" in data:
                metadata = data["metadata"]
                print(f"  Page title: {metadata.get('title', 'Unknown')}")
                print(f"  Status code: {metadata.get('statusCode', 'Unknown')}")
        else:
            # Fallback for unexpected format
            markdown_content = result.get("markdown", "")
        
        if not markdown_content:
            raise Exception(f"No markdown content returned from Firecrawl. Response keys: {list(result.keys())}")
        
        print(f"Successfully scraped {len(markdown_content)} characters of content")
        return markdown_content
        
    except anvil.http.HttpError as e:
        # Capture the error response body for HTTP errors
        error_details = "No details available"
        try:
            # Try different ways to get error content from Anvil HttpError
            if hasattr(e, 'content') and e.content:
                # e.content might be a StreamingMedia object
                if hasattr(e.content, 'get_bytes'):
                    error_body = e.content.get_bytes().decode('utf-8')
                elif isinstance(e.content, bytes):
                    error_body = e.content.decode('utf-8')
                elif isinstance(e.content, str):
                    error_body = e.content
                else:
                    error_body = str(e.content)
                
                # Try to parse as JSON
                try:
                    error_json = json.loads(error_body)
                    error_details = json.dumps(error_json, indent=2)
                except:
                    error_details = error_body
                
                print(f"  Firecrawl error response: {error_details}")
            
            # Also check if error message is in the exception itself
            if hasattr(e, 'args') and e.args:
                print(f"  Exception args: {e.args}")
                
        except Exception as err:
            print(f"  Could not extract error details: {err}")
        
        print(f"HTTP Error {e.status}: {error_details}")
        
        # Always try fallback on Firecrawl error
        print(f"\n  ⚠️ Firecrawl API failed with error: {error_details}")
        print("  Possible causes:")
        print("    1. API key doesn't have v2 access")
        print("    2. Free tier limitation")
        print("    3. URL validation issue (Firecrawl rejects this URL)")
        print("    4. Plan doesn't support this feature")
        
        # Try direct scraper as fallback
        if DIRECT_SCRAPER_AVAILABLE:
            print("\n  🔄 Switching to direct scraper as fallback...")
            try:
                print("  Attempting direct HTTP scraping...")
                return scraper_direct.scrape_weekend_events_direct()
            except Exception as direct_error:
                print(f"  ❌ Direct scraping also failed: {direct_error}")
                raise Exception(f"Both Firecrawl AND direct scraping failed. Firecrawl: {error_details}, Direct: {str(direct_error)}")
        else:
            raise Exception(f"Firecrawl failed and no backup scraper available: {error_details}")
        
    except Exception as e:
        print(f"Error scraping website: {str(e)}")
        # Log the full error for debugging
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        raise


def parse_events_from_markdown(markdown_content):
    """
    Parse event data from markdown or text content.
    Extracts event details using pattern matching.
    Works with both Firecrawl markdown and direct HTML text.
    
    Args:
        markdown_content: Raw markdown or text from website
        
    Returns:
        list: List of event dictionaries
    """
    print(f"Parsing events from content ({len(markdown_content)} characters)...")
    
    events = []
    weekend_dates = api_helpers.get_weekend_dates()
    
    # Split content into sections by headings or separators
    # This is a simplified parser - may need adjustment based on actual website structure
    lines = markdown_content.split('\n')
    
    current_event = {}
    current_day = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Check if line indicates a day (Friday, Saturday, Sunday)
        if re.search(r'\b(Friday|Saturday|Sunday)\b', line, re.IGNORECASE):
            day_match = re.search(r'\b(Friday|Saturday|Sunday)\b', line, re.IGNORECASE)
            current_day = day_match.group(1).lower()
            continue
        
        # Look for event patterns
        # This is a simplified approach - actual parsing will depend on website structure
        if line.startswith('#') or line.startswith('##'):
            # This might be an event title
            if current_event and current_event.get("title"):
                # Save previous event
                events.append(current_event)
            
            # Start new event
            current_event = {
                "title": line.lstrip('#').strip(),
                "date": weekend_dates.get(current_day) if current_day else None,
                "description": "",
                "location": "",
                "cost_raw": "",
                "scraped_at": datetime.now()
            }
        else:
            # Accumulate description or extract metadata
            if current_event:
                # Try to extract specific information
                
                # Look for time patterns (e.g., "3:00 PM - 5:00 PM" or "3 PM")
                time_match = re.search(r'(\d{1,2}:\d{2}\s*[APap][Mm]|\d{1,2}\s*[APap][Mm])', line)
                if time_match and not current_event.get("start_time"):
                    current_event["start_time"] = api_helpers.parse_time_string(time_match.group(1))
                
                # Look for cost indicators
                if re.search(r'\$|free|cost|price|admission', line, re.IGNORECASE):
                    if not current_event.get("cost_raw"):
                        current_event["cost_raw"] = line
                
                # Look for location indicators
                if re.search(r'\bat\b|\blocation\b|venue', line, re.IGNORECASE):
                    if not current_event.get("location"):
                        # Extract location from line
                        location_match = re.search(r'at\s+([^,\.\n]+)', line, re.IGNORECASE)
                        if location_match:
                            current_event["location"] = location_match.group(1).strip()
                
                # Add to description
                current_event["description"] += " " + line
    
    # Don't forget the last event
    if current_event and current_event.get("title"):
        events.append(current_event)
    
    # Clean up events
    for event in events:
        event["description"] = api_helpers.sanitize_text(event.get("description", ""))
        event["location"] = api_helpers.sanitize_text(event.get("location", "Unknown"))
        event["cost_raw"] = api_helpers.sanitize_text(event.get("cost_raw", ""))
        event["event_id"] = api_helpers.generate_unique_id("evt")
        
        # Ensure we have basic required fields
        if not event.get("start_time"):
            event["start_time"] = "TBD"
        if not event.get("end_time"):
            event["end_time"] = None
    
    print(f"Parsed {len(events)} events from markdown")
    return events


def extract_cost_level(cost_raw_text):
    """
    Extract and standardize cost level from raw cost text.
    
    Args:
        cost_raw_text: Raw cost text from event description
        
    Returns:
        str: Standardized cost level (Free, $, $$, $$$, $$$$)
    """
    if not cost_raw_text:
        return "$"  # Default to $ if unknown
    
    cost_text = cost_raw_text.lower()
    
    # Check for free
    if re.search(r'\bfree\b', cost_text):
        return "Free"
    
    # Count dollar signs
    dollar_count = cost_text.count('$')
    if dollar_count >= 4:
        return "$$$$"
    elif dollar_count == 3:
        return "$$$"
    elif dollar_count == 2:
        return "$$"
    elif dollar_count == 1:
        return "$"
    
    # Try to extract numeric price and categorize
    price_match = re.search(r'\$?\s*(\d+)', cost_text)
    if price_match:
        price = int(price_match.group(1))
        if price == 0:
            return "Free"
        elif price < 20:
            return "$"
        elif price < 50:
            return "$$"
        elif price < 100:
            return "$$$"
        else:
            return "$$$$"
    
    # Default to moderate cost
    return "$$"


def save_events_to_db(events):
    """
    Save parsed events to the events Data Table.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        int: Number of events saved
    """
    from anvil.tables import app_tables
    
    print(f"Saving {len(events)} events to database...")
    
    saved_count = 0
    
    try:
        for event in events:
            # Skip events without required fields
            if not event.get("title") or not event.get("date"):
                print(f"Skipping event without title or date: {event.get('title', 'Unknown')}")
                continue
            
            # Determine initial cost level (will be refined by AI)
            cost_level = extract_cost_level(event.get("cost_raw", ""))
            
            # Add event to database
            app_tables.events.add_row(
                event_id=event["event_id"],
                title=event["title"],
                description=event.get("description", ""),
                date=event["date"],
                start_time=event.get("start_time", "TBD"),
                end_time=event.get("end_time"),
                location=event.get("location", "TBD"),
                cost_raw=event.get("cost_raw", ""),
                cost_level=cost_level,
                scraped_at=event["scraped_at"],
                # Fields to be filled by AI analysis
                is_indoor=None,
                is_outdoor=None,
                audience_type=None,
                categories=None,
                weather_score=None,
                recommendation_score=None,
                analyzed_at=None
            )
            
            saved_count += 1
        
        print(f"Successfully saved {saved_count} events to database")
        return saved_count
        
    except Exception as e:
        print(f"Error saving events to database: {str(e)}")
        raise

