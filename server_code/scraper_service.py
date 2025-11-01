"""
Web scraping service module for This Weekend app.
Handles integration with Firecrawl SDK for event data collection.
"""

import anvil.server
from datetime import datetime
import re

from . import config
from . import api_helpers

# Import Firecrawl SDK (required dependency)
from firecrawl import Firecrawl


def scrape_weekend_events():
    """
    Scrape weekend events from ilovememphisblog.com/weekend using Firecrawl SDK.
    
    Returns:
        str: Markdown content from the website
        
    Raises:
        Exception: If scraping fails
    """
    print(f"Scraping events from {config.TARGET_WEBSITE_URL}...")
    
    # Get API key
    api_key = api_helpers.get_api_key("FIRECRAWL_API_KEY")
    
    # Initialize Firecrawl client and scrape
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
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    
    # ONLY accept links to /events/ - these are real event pages
    event_url_pattern = r'ilovememphisblog\.com/events/[^/]+/[^/]+'
    
    # Additional skip patterns for event URLs we don't want
    skip_event_patterns = [
        r'/events/add',  # Submit event page
        r'/events/category/all-events',  # Calendar page
    ]
    
    lines = markdown_content.split('\n')
    total_links_found = 0
    links_skipped = 0
    skip_reasons = {}
    
    # Debug: Look for day keywords in content
    day_keywords_found = []
    for line in markdown_content.split('\n')[:100]:
        if re.search(r'\b(friday|saturday|sunday)\b', line, re.IGNORECASE):
            day_keywords_found.append(line.strip()[:80])
            if len(day_keywords_found) >= 3:
                break
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Track day headers - try multiple patterns
        day_match = re.search(r'#{1,3}\s*(FRIDAY|SATURDAY|SUNDAY)', line, re.IGNORECASE)
        if not day_match:
            day_match = re.search(r'^(FRIDAY|SATURDAY|SUNDAY)\s*$', line, re.IGNORECASE)
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
            
            # Check if this is a real event URL
            if not re.search(event_url_pattern, link_url):
                links_skipped += 1
                skip_reasons["not_event_url"] = skip_reasons.get("not_event_url", 0) + 1
                continue
            
            # Check skip patterns
            skip_reason = None
            for pattern in skip_event_patterns:
                if re.search(pattern, link_url, re.IGNORECASE):
                    skip_reason = f"skip_event:{pattern}"
                    break
            
            if skip_reason:
                links_skipped += 1
                skip_reasons[skip_reason] = skip_reasons.get(skip_reason, 0) + 1
                continue
            
            # Parse event details from link text and scrape the event page
            event = parse_event_link_text(link_text, link_url, current_day, weekend_dates)
            
            if event:
                events.append(event)
            else:
                links_skipped += 1
                skip_reasons["parse_failed"] = skip_reasons.get("parse_failed", 0) + 1
    
    # Print summary
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
    
    if len(events) > 0:
        print(f"  ℹ️ Note: Scraping {len(events)} individual event pages for detailed info...")
        print(f"     This will take ~{len(events) * 3} seconds ({len(events)} Firecrawl calls)")
    
    return events


def scrape_event_details_from_url(event_url, api_key):
    """
    Scrape individual event page for detailed information.
    
    Args:
        event_url: URL to the specific event page
        api_key: Firecrawl API key
        
    Returns:
        dict: Detailed event information or None if scraping fails
    """
    try:
        firecrawl = Firecrawl(api_key=api_key)
        result = firecrawl.scrape(
            url=event_url,
            formats=['markdown']
        )
        if hasattr(result, 'markdown'):
            return extract_details_from_event_page(result.markdown)
    except Exception:
        # Silently fail - we'll use the data from the weekend page
        pass
    
    return None


def extract_details_from_event_page(markdown):
    """
    Extract structured details from an individual event page markdown.
    
    Args:
        markdown: Markdown content from event page
        
    Returns:
        dict: Extracted details (location, time, cost, description, etc.)
    """
    details = {
        'location': None,
        'start_time': None,
        'end_time': None,
        'cost_raw': None,
        'description': None
        # NOTE: We do NOT extract 'date' from event pages
        # Event pages show recurring events with multiple future dates
        # We trust the Friday/Saturday/Sunday assignment from /weekend page instead
    }
    
    lines = markdown.split('\n')
    description_lines = []
    in_description_section = False
    
    # Navigation links to skip
    nav_skip_patterns = [
        r'skip to content',
        r'^\[calendar\]',
        r'^\[visit website\]',
        r'^\[get tickets\]',
        r'^\[share\]',
        r'^\[tweet\]',
        r'^!\[',  # Image markdown
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip navigation links
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in nav_skip_patterns):
            continue
        
        # Skip standalone markdown links (likely navigation)
        if re.match(r'^\[.+\]\(.+\)$', line):
            if len(line) <= 100:
                continue
        
        # Look for location patterns
        if re.search(r'\*\*Location\*\*:?\s*(.+)', line, re.IGNORECASE):
            match = re.search(r'\*\*Location\*\*:?\s*(.+)', line, re.IGNORECASE)
            location_text = match.group(1).strip()
            location_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', location_text)
            details['location'] = location_text
            continue
        elif re.search(r'\*\*Venue\*\*:?\s*(.+)', line, re.IGNORECASE):
            match = re.search(r'\*\*Venue\*\*:?\s*(.+)', line, re.IGNORECASE)
            venue_text = match.group(1).strip()
            venue_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', venue_text)
            details['location'] = venue_text
            continue
        
        # Look for time patterns
        if re.search(r'\*\*Time\*\*:?\s*(.+)', line, re.IGNORECASE):
            match = re.search(r'\*\*Time\*\*:?\s*(.+)', line, re.IGNORECASE)
            time_text = match.group(1).strip()
            time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:a\.m\.|p\.m\.|am|pm))', time_text, re.IGNORECASE)
            if time_match:
                details['start_time'] = time_match.group(1)
            continue
        
        # Look for cost/price patterns
        if re.search(r'\*\*(Cost|Price|Admission|Tickets?)\*\*:?\s*(.+)', line, re.IGNORECASE):
            match = re.search(r'\*\*(Cost|Price|Admission|Tickets?)\*\*:?\s*(.+)', line, re.IGNORECASE)
            cost_text = match.group(2).strip()
            cost_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cost_text)
            details['cost_raw'] = cost_text
            continue
        
        # NOTE: We intentionally do NOT extract dates from event pages
        # Event pages often show ALL occurrences (Nov 1, Nov 7, Nov 14, etc.)
        # The /weekend page day header (Friday/Saturday/Sunday) is more reliable
        # for determining THIS weekend's specific occurrence
        
        # Start collecting description after heading
        if line.startswith('# ') and not in_description_section:
            in_description_section = True
            continue
        
        # Collect description lines
        if in_description_section:
            if line.startswith('**'):
                continue
            if line.count('[') > 2:
                continue
            if len(line) > 30 and not line.startswith('!'):
                clean_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
                description_lines.append(clean_line)
    
    # Build description
    if description_lines:
        details['description'] = ' '.join(description_lines[:3])
        if len(details['description']) > 500:
            details['description'] = details['description'][:500] + '...'
    
    return details


def parse_event_link_text(link_text, link_url, current_day, weekend_dates):
    """
    Parse event details from a markdown link's text, then scrape the event page for better details.
    
    Args:
        link_text: The text inside [...]
        link_url: The URL to the event page
        current_day: Current day context (friday/saturday/sunday)
        weekend_dates: Dict of weekend dates
        
    Returns:
        dict: Event dictionary with details from both link text and event page
    """
    # Skip very short links (likely navigation, not events)
    if len(link_text) < 5:
        return None
    
    # Determine day assignment
    assigned_day = current_day
    if not assigned_day:
        if re.search(r'\bfriday\b', link_text, re.IGNORECASE):
            assigned_day = 'friday'
        elif re.search(r'\bsaturday\b', link_text, re.IGNORECASE):
            assigned_day = 'saturday'
        elif re.search(r'\bsunday\b', link_text, re.IGNORECASE):
            assigned_day = 'sunday'
        elif re.search(r'\ball\s+weekend\b', link_text, re.IGNORECASE):
            assigned_day = 'friday'
        else:
            assigned_day = 'friday'
    
    # Parse basic info from link text
    parts = [p.strip() for p in link_text.split(',')]
    
    if len(parts) < 1 or not parts[0]:
        return None
    
    # Create event with basic info
    event = {
        "event_id": api_helpers.generate_unique_id("evt"),
        "title": parts[0],
        "description": link_text,
        "location": "TBD",
        "start_time": "TBD",
        "end_time": None,
        "cost_raw": "",
        "date": weekend_dates.get(assigned_day),
        "scraped_at": datetime.now(),
        "source_url": link_url
    }
    
    # Extract from link text (basic fallback)
    if len(parts) >= 2:
        potential_location = parts[1]
        if not re.search(r'\d+\s*(am|pm|p\.m\.|a\.m\.)', potential_location, re.IGNORECASE):
            if not re.search(r'\$\d+', potential_location):
                event["location"] = potential_location
    
    for part in parts[1:]:
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:a\.m\.|p\.m\.|am|pm))', part, re.IGNORECASE)
        if time_match and event["start_time"] == "TBD":
            event["start_time"] = api_helpers.parse_time_string(time_match.group(1))
        
        if re.search(r'\$|free|price', part, re.IGNORECASE):
            event["cost_raw"] = part
    
    # Scrape the individual event page for better details
    try:
        api_key = api_helpers.get_api_key("FIRECRAWL_API_KEY")
        detailed_info = scrape_event_details_from_url(link_url, api_key)
        
        if detailed_info:
            # Override with better data from event page
            if detailed_info.get('location'):
                event["location"] = detailed_info['location']
            if detailed_info.get('start_time'):
                event["start_time"] = api_helpers.parse_time_string(detailed_info['start_time'])
            if detailed_info.get('cost_raw'):
                event["cost_raw"] = detailed_info['cost_raw']
            if detailed_info.get('description') and len(detailed_info['description']) > 20:
                event["description"] = detailed_info['description']
            
            # IMPORTANT: Do NOT override date from event pages!
            # Event pages often show ALL occurrences of recurring events (Nov 7, Nov 14, etc.)
            # The /weekend page listing under Friday/Saturday/Sunday is more reliable
            # for determining which specific occurrence is THIS weekend.
            # 
            # We trust: The day assignment from the /weekend page (Fri/Sat/Sun header)
            # We ignore: Dates from individual event pages (often wrong/future dates)
            #
            # If you need to debug date issues, check the weekend_dates assignment above
    except Exception:
        # If scraping individual page fails, use link text data
        pass
    
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
        return "$"
    
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
            
            # Determine initial cost level
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
