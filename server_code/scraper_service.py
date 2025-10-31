"""
Web scraping service module for This Weekend app.
Handles integration with Firecrawl API for event data collection.

This module tries to use the Firecrawl Python SDK for reliability,
with automatic fallback to raw HTTP if the SDK is not available.
"""

import anvil.server
import anvil.http
from datetime import datetime
import json
import re

from . import config
from . import api_helpers

# Try to import Firecrawl Python SDK (more reliable)
try:
    from firecrawl import Firecrawl
    FIRECRAWL_SDK_AVAILABLE = True
    print("✅ Firecrawl Python SDK available - using SDK mode")
except ImportError:
    FIRECRAWL_SDK_AVAILABLE = False
    print("⚠️ Firecrawl SDK not installed - using fallback HTTP mode")
    print("   Install with: pip install firecrawl-py")
    print("   See server_code/requirements.txt for instructions")

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
    Tries to use the Python SDK first, falls back to raw HTTP if SDK unavailable.
    
    Returns:
        str: Markdown content from Firecrawl
        
    Raises:
        Exception: If Firecrawl fails
    """
    print("  Trying Firecrawl API...")
    
    # Get API key
    api_key = api_helpers.get_api_key("FIRECRAWL_API_KEY")
    
    # Try SDK first if available (more reliable)
    if FIRECRAWL_SDK_AVAILABLE:
        try:
            return scrape_with_firecrawl_sdk(api_key)
        except Exception as sdk_error:
            print(f"  ⚠️ SDK method failed: {str(sdk_error)[:200]}")
            print("  🔄 Falling back to raw HTTP method...")
            # Continue to raw HTTP fallback below
    
    # Fallback to raw HTTP
    return scrape_with_firecrawl_http(api_key)


def scrape_with_firecrawl_sdk(api_key):
    """
    Scrape using Firecrawl Python SDK (recommended method).
    
    Args:
        api_key: Firecrawl API key
        
    Returns:
        str: Markdown content from Firecrawl
        
    Raises:
        Exception: If scraping fails
    """
    try:
        # Initialize Firecrawl client and scrape (SDK handles stealth mode automatically)
        firecrawl = Firecrawl(api_key=api_key)
        result = firecrawl.scrape(
            url=config.TARGET_WEBSITE_URL,
            formats=['markdown', 'html']
        )
        
        # SDK returns a Document object with markdown, html, metadata properties
        if hasattr(result, 'markdown') and result.markdown:
            markdown_content = result.markdown
            
            # Get page title for confirmation
            title = "Unknown"
            if hasattr(result, 'metadata') and result.metadata:
                metadata = result.metadata
                title = getattr(metadata, 'title', 'Unknown')
            
            print(f"  ✅ Scraped {len(markdown_content)} chars from '{title[:50]}...'")
            return markdown_content
        else:
            raise Exception("SDK returned no markdown content")
            
    except Exception as e:
        print(f"  ❌ SDK error: {str(e)}")
        raise


def scrape_with_firecrawl_http(api_key):
    """
    Scrape using raw HTTP requests to Firecrawl API (fallback method).
    
    Args:
        api_key: Firecrawl API key
        
    Returns:
        str: Markdown content from Firecrawl
        
    Raises:
        Exception: If scraping fails
    """
    print("  📡 Using raw HTTP method (fallback)")
    
    # Firecrawl API v2 endpoint
    url = "https://api.firecrawl.dev/v2/scrape"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Payload format for Firecrawl v2 with Stealth Mode
    # Reference: https://docs.firecrawl.dev/features/scrape
    # Stealth mode bypasses Cloudflare protection
    payload = {
        "url": config.TARGET_WEBSITE_URL,
        "formats": ["markdown", "html"],
        "stealth": True,  # Enable stealth mode for Cloudflare bypass
        "timeout": 60000  # 60 second timeout for Cloudflare challenge
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
    Parse event data from markdown content from ilovememphisblog.com/weekend.
    
    Events are formatted as markdown links: [Event Details](URL)
    Example: [Concert, Venue, Time, Price](http://example.com)
    
    Args:
        markdown_content: Raw markdown from Firecrawl
        
    Returns:
        list: List of event dictionaries
    """
    events = []
    weekend_dates = api_helpers.get_weekend_dates()
    
    # Track current day context for dating events
    current_day = None
    
    # Pattern to match markdown links: [text](url)
    # This captures events formatted as links
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    
    # Skip patterns - links we don't want to treat as events
    skip_patterns = [
        r'^reply$',  # Comment reply links
        r'comment/reply',  # Comment reply URLs
        r'submit\s+here',
        r'click\s+here',
        r'read\s+more',
        r'learn\s+more',
        r'view\s+all',
        r'see\s+all',
        r'share',
        r'tweet',
        r'i\s+love\s+memphis\s+blog',
        r'ilovememphisblog\.com/events/add',  # Submit event page
        r'ilovememphisblog\.com/search',  # Search page
        r'^www\.',
        r'^https?://(www\.)?facebook\.com',  # Skip Facebook links (require login)
    ]
    
    lines = markdown_content.split('\n')
    total_links_found = 0
    links_skipped = 0
    skip_reasons = {}  # Track why links were skipped
    
    # Debug: Look for day keywords in content
    day_keywords_found = []
    for line in markdown_content.split('\n')[:100]:  # Check first 100 lines
        if re.search(r'\b(friday|saturday|sunday)\b', line, re.IGNORECASE):
            day_keywords_found.append(line.strip()[:80])  # First 80 chars
            if len(day_keywords_found) >= 3:  # Just show first 3
                break
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Track day headers - try multiple patterns
        # Pattern 1: ## FRIDAY or ### FRIDAY
        day_match = re.search(r'#{1,3}\s*(FRIDAY|SATURDAY|SUNDAY)', line, re.IGNORECASE)
        # Pattern 2: Just the word FRIDAY/SATURDAY/SUNDAY on its own line or in caps
        if not day_match:
            day_match = re.search(r'^(FRIDAY|SATURDAY|SUNDAY)\s*$', line, re.IGNORECASE)
        # Pattern 3: Day name at start of line
        if not day_match:
            day_match = re.search(r'^(FRIDAY|SATURDAY|SUNDAY)\b', line, re.IGNORECASE)
        
        if day_match:
            current_day = day_match.group(1).lower()
            print(f"  📅 Found day header: {day_match.group(1)}")
            continue
        
        # Find all markdown links in this line
        matches = list(re.finditer(link_pattern, line))
        if matches:
            total_links_found += len(matches)
        
        for match in matches:
            link_text = match.group(1).strip()
            link_url = match.group(2).strip()
            
            # Skip if this matches any skip pattern (text)
            skip_reason = None
            for pattern in skip_patterns:
                if re.search(pattern, link_text, re.IGNORECASE):
                    skip_reason = f"text:{pattern}"
                    break
            
            if skip_reason:
                links_skipped += 1
                skip_reasons[skip_reason] = skip_reasons.get(skip_reason, 0) + 1
                continue
            
            # Skip if URL matches skip patterns
            for pattern in skip_patterns:
                if re.search(pattern, link_url, re.IGNORECASE):
                    skip_reason = f"url:{pattern}"
                    break
            
            if skip_reason:
                links_skipped += 1
                skip_reasons[skip_reason] = skip_reasons.get(skip_reason, 0) + 1
                continue
            
            # Parse event details from link text
            # Format: "Event Title, Location, Time, Price" or variations
            event = parse_event_link_text(link_text, link_url, current_day, weekend_dates)
            
            if event:
                events.append(event)
            else:
                links_skipped += 1
                skip_reasons["no_day_context_or_invalid"] = skip_reasons.get("no_day_context_or_invalid", 0) + 1
    
    # Print summary with details
    print(f"  🔍 Parser stats: {total_links_found} links found, {links_skipped} skipped, {len(events)} events parsed")
    if day_keywords_found:
        print(f"  📅 Day keywords found in content (first 3):")
        for line in day_keywords_found:
            print(f"     '{line}'")
    else:
        print(f"  ⚠️ No day keywords (FRIDAY/SATURDAY/SUNDAY) found in first 100 lines!")
    
    if links_skipped > 0 and len(skip_reasons) > 0:
        print(f"  ❌ Skip reasons (top 3):")
        for reason, count in sorted(skip_reasons.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"     {reason}: {count} links")
    
    return events


def parse_event_link_text(link_text, link_url, current_day, weekend_dates):
    """
    Parse event details from a markdown link's text.
    
    Args:
        link_text: The text inside [...]
        link_url: The URL
        current_day: Current day context (friday/saturday/sunday)
        weekend_dates: Dict of weekend dates
        
    Returns:
        dict: Event dictionary or None if not a valid event
    """
    # Events typically have commas separating components
    # Format: "Event Name, Location, Time, Price"
    
    # Skip very short links (likely navigation, not events)
    if len(link_text) < 5:  # Reduced from 10 to be more lenient
        return None
    
    # If no current day context, try to infer from link text
    # or default to Friday (most common posting day)
    assigned_day = current_day
    if not assigned_day:
        # Check if day is mentioned in the link text
        if re.search(r'\bfriday\b', link_text, re.IGNORECASE):
            assigned_day = 'friday'
        elif re.search(r'\bsaturday\b', link_text, re.IGNORECASE):
            assigned_day = 'saturday'
        elif re.search(r'\bsunday\b', link_text, re.IGNORECASE):
            assigned_day = 'sunday'
        elif re.search(r'\ball\s+weekend\b', link_text, re.IGNORECASE):
            assigned_day = 'friday'  # Default to Friday for "All Weekend" events
        else:
            # Default to Friday if no day context (most events are weekend-long)
            assigned_day = 'friday'
    
    # Split by comma to get components
    parts = [p.strip() for p in link_text.split(',')]
    
    # Need at least event name (title)
    if len(parts) < 1 or not parts[0]:
        return None
    
    event = {
        "event_id": api_helpers.generate_unique_id("evt"),
        "title": parts[0],
        "description": link_text,  # Full text as description
        "location": "TBD",
        "start_time": "TBD",
        "end_time": None,
        "cost_raw": "",
        "date": weekend_dates.get(assigned_day),
        "scraped_at": datetime.now(),
        "source_url": link_url
    }
    
    # Extract location (usually second component)
    if len(parts) >= 2:
        # Check if second part looks like a location (not time/price)
        potential_location = parts[1]
        if not re.search(r'\d+\s*(am|pm|p\.m\.|a\.m\.)', potential_location, re.IGNORECASE):
            if not re.search(r'\$\d+', potential_location):
                event["location"] = potential_location
    
    # Extract time and cost from remaining parts
    for part in parts[1:]:
        # Time pattern: "7 p.m.", "7:00 PM", "7 p.m. - 10 p.m."
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:a\.m\.|p\.m\.|am|pm))', part, re.IGNORECASE)
        if time_match and event["start_time"] == "TBD":
            event["start_time"] = api_helpers.parse_time_string(time_match.group(1))
        
        # Cost pattern: "$10", "free", "prices vary", "$10-$20"
        if re.search(r'\$|free|price', part, re.IGNORECASE):
            event["cost_raw"] = part
    
    return event


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
    
    saved_count = 0
    skipped_count = 0
    
    try:
        for event in events:
            # Skip events without required fields
            if not event.get("title") or not event.get("date"):
                skipped_count += 1
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
        
        # Summary message
        if skipped_count > 0:
            print(f"  ✓ Saved {saved_count} events ({skipped_count} skipped - missing title/date)")
        else:
            print(f"  ✓ Saved {saved_count} events")
        return saved_count
        
    except Exception as e:
        print(f"Error saving events to database: {str(e)}")
        raise

