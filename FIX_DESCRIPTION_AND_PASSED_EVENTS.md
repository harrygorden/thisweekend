# Fix Event Descriptions and Filter Passed Events

## Problems Identified

### 1. Calendar Markup in Descriptions
Event descriptions were showing calendar markdown tables instead of actual event descriptions:
```
| su | mo | tu | we | th | fr | sa | | --- | --- | --- | --- | --- | --- | --- | | 26 | 27 | 28 | 29 | 30 | 31 | | |
```

This affected events like:
- Memphis Grizzlies vs Los Angeles Lakers
- Memphis Rap OGz
- Other events scraped from ilovememphisblog.com

### 2. Past Events Not Being Filtered
Events that have already occurred were still being scraped and displayed, even though the source website redirects them to:
```
https://ilovememphisblog.com/event-has-passed
```

## Solutions Implemented

### Fix 1: Enhanced Description Filtering

Updated `extract_details_from_event_page()` in `scraper_service.py` to skip:

1. **Markdown tables** - Lines containing `|` character
2. **Calendar day names** - Lines with "su, mo, tu, we, th, fr, sa" patterns
3. **Table data** - Lines with only numbers and separators (e.g., "26 | 27 | 28")
4. **Very short lines** - Lines under 30 characters (likely headers)
5. **Navigation elements** - Already skipped, but now more robust

```python
# Collect description lines
if in_description_section:
    # Skip markdown bold headers
    if line.startswith('**'):
        continue
    # Skip lines with lots of links
    if line.count('[') > 2:
        continue
    # Skip markdown tables (calendar, navigation, etc.)
    if '|' in line:
        continue
    # Skip lines that look like calendar day names
    if re.search(r'\b(su|mo|tu|we|th|fr|sa)\b', line, re.IGNORECASE) and len(line) < 50:
        continue
    # Skip lines with only numbers and separators (table data)
    if re.match(r'^[\d\s\|\-]+$', line):
        continue
    # Skip very short lines (likely headers or navigation)
    if len(line) < 30:
        continue
    # Skip image markdown
    if line.startswith('!'):
        continue
    
    # Clean and add valid description lines
    clean_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
    description_lines.append(clean_line)
```

### Fix 2: Redirect Detection for Passed Events

Updated `scrape_event_details_from_url()` to detect when events have passed:

```python
def scrape_event_details_from_url(event_url, api_key):
    """
    Scrape individual event page for detailed information.
    Detects if event has passed via redirect.
    """
    try:
        firecrawl = Firecrawl(api_key=api_key)
        result = firecrawl.scrape(
            url=event_url,
            formats=['markdown']
        )
        
        # Check if the event has passed (redirects to event-has-passed page)
        if hasattr(result, 'metadata') and result.metadata:
            # Check the final URL after any redirects
            final_url = getattr(result.metadata, 'url', event_url)
            if 'event-has-passed' in final_url:
                print(f"  ⏭️  Event has passed (redirected): {event_url}")
                return {'event_has_passed': True}
        
        # Also check markdown content for "event has passed" message
        if hasattr(result, 'markdown'):
            if 'event has passed' in result.markdown.lower():
                print(f"  ⏭️  Event has passed (content check): {event_url}")
                return {'event_has_passed': True}
            
            return extract_details_from_event_page(result.markdown)
    except Exception:
        pass
    
    return None
```

**Two-layer detection:**
1. **URL redirect check**: Detects if Firecrawl followed redirect to `/event-has-passed`
2. **Content check**: Searches markdown for "event has passed" text as backup

### Fix 3: Skip Passed Events During Parsing

Updated `parse_event_link_text()` to skip events that have passed:

```python
detailed_info = scrape_event_details_from_url(link_url, api_key)

# Check if event has passed
if detailed_info and detailed_info.get('event_has_passed'):
    return None  # Skip this event entirely

if detailed_info:
    # Override with better data from event page
    ...
```

Events that have passed are now completely filtered out and won't appear in the database.

## How It Works

### Before the Fix

**Grizzlies game scenario:**
1. Main page lists "Memphis Grizzlies vs Los Angeles Lakers"
2. Scraper visits: `https://ilovememphisblog.com/events/sports/memphis-grizzlies-vs-los-angeles-lakers`
3. Page redirects to: `https://ilovememphisblog.com/event-has-passed`
4. ❌ Scraper extracts calendar markup as description
5. ❌ Event still added to database even though it's passed
6. ❌ User sees: "| su | mo | tu | we | th | fr | sa | | --- |..."

### After the Fix

**Grizzlies game scenario:**
1. Main page lists "Memphis Grizzlies vs Los Angeles Lakers"
2. Scraper visits: `https://ilovememphisblog.com/events/sports/memphis-grizzlies-vs-los-angeles-lakers`
3. Page redirects to: `https://ilovememphisblog.com/event-has-passed`
4. ✅ Redirect detected: "Event has passed (redirected)"
5. ✅ Event skipped entirely
6. ✅ User sees: Nothing (event not in database)

**For current events:**
1. Scraper visits valid event page
2. Extracts details from markdown
3. ✅ Skips calendar tables
4. ✅ Skips navigation elements
5. ✅ Extracts actual event description text
6. ✅ User sees: Real event description

## Expected Results

### Cleaner Event List
- **Before**: ~80 events including past events
- **After**: ~20-30 current events only

### Better Descriptions
- **Before**: "| su | mo | tu | we | th | fr | sa | | --- |..."
- **After**: Actual event descriptions from the page content

### Console Output
During scraping, you'll see:
```
Scraping events from https://ilovememphisblog.com/weekend...
  📅 Found day header: 'THINGS TO DO ON SUNDAY' → sunday
  ⏭️  Event has passed (redirected): https://ilovememphisblog.com/events/sports/memphis-grizzlies-vs-los-angeles-lakers
  ⏭️  Event has passed (redirected): https://ilovememphisblog.com/events/music-nightlife/memphis-rap-ogz
  ✓ 25% complete (5/20)
```

## Benefits

1. **Accurate Event List**: Only shows events that haven't happened yet
2. **Cleaner Descriptions**: Real event info instead of calendar markup
3. **Better User Experience**: Users see relevant, current events
4. **Fewer API Calls**: Passed events detected early, reducing AI analysis costs
5. **Automatic Cleanup**: No manual intervention needed to remove old events

## Testing

To verify the fix works:

1. **Clear old data**:
   ```python
   anvil.server.call('clear_all_data')
   ```

2. **Refresh with new logic**:
   ```python
   anvil.server.call('trigger_data_refresh')
   ```

3. **Check console output** for:
   - "⏭️ Event has passed" messages
   - Fewer total events scraped
   - No calendar markup in descriptions

4. **Verify in app**:
   - Event descriptions should be readable text
   - No "| su | mo |..." markup
   - Only current/future events visible

## Example Event Descriptions

### Before (broken):
```
Memphis Grizzlies vs Los Angeles Lakers
Saturday, November 01 • 7 p.m.
FedForum

| su | mo | tu | we | th | fr | sa | | --- | --- | --- | --- | --- | --- | --- | | 26 | 27 | 28 | 29 | 30 | 31 | | |
```

### After (fixed):
```
Memphis Grizzlies vs Los Angeles Lakers
Saturday, November 01 • 7 p.m.
FedForum

[Either skipped because it's passed, OR shows actual event description if current]
```

For a current event like Memphis Japan Festival:
```
Memphis Japan Festival
Sunday, November 02 • 9:30 a.m.
Botanic Garden

Admission is $12 for adults, $10 for seniors and $7.00 for students and children 
2-12 years old. For children under 2 years and Memphis Botanic Garden members, 
admission is free. The Memphis Japan Festival is a fun, family-friendly, interactive 
and hands-on experience of Japanese culture.
```

## Files Modified

1. **server_code/scraper_service.py**
   - Enhanced `extract_details_from_event_page()` to skip calendar/table markup
   - Updated `scrape_event_details_from_url()` to detect passed events
   - Updated `parse_event_link_text()` to skip passed events

2. **FIX_DESCRIPTION_AND_PASSED_EVENTS.md** (this file)
   - Complete documentation of the fixes

## Technical Details

### Regex Patterns Used

**Skip calendar day names:**
```python
re.search(r'\b(su|mo|tu|we|th|fr|sa)\b', line, re.IGNORECASE)
```

**Skip table row data:**
```python
re.match(r'^[\d\s\|\-]+$', line)
```

**Detect event-has-passed redirect:**
```python
if 'event-has-passed' in final_url:
```

### Firecrawl Metadata

The Firecrawl SDK provides metadata including the final URL after redirects:
```python
final_url = getattr(result.metadata, 'url', event_url)
```

This allows detection of redirects without additional HTTP requests.

---

**Fix completed**: November 1, 2025
**Issues resolved**: 
1. Calendar markup in descriptions ✅
2. Past events not filtered ✅
**Impact**: Cleaner event list, better descriptions, only current events shown

