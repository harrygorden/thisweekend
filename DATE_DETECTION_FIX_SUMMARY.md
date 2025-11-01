# Date Detection Fix - November 1, 2025

## Problem Identified

The Memphis Japan Festival and other events were showing incorrect dates:
- **Actual**: Event on "SUNDAY, November 2, 2025" (per event detail page)
- **Displayed**: "Friday, October 31, 2025" (incorrectly)

## Root Cause

The scraper had **two fundamental flaws**:

### 1. Header Detection Pattern Mismatch
The code was looking for day headers like:
- `# FRIDAY`
- `SATURDAY`
- `## SUNDAY`

But the website uses headers like:
- `THINGS TO DO ON FRIDAY`
- `THINGS TO DO ON SATURDAY`
- `THINGS TO DO ON SUNDAY`

**Result**: The day header was never detected, so `current_day` stayed `None` and defaulted to `friday` for all events.

### 2. Date Information Ignored from Event Pages
The previous "fix" intentionally ignored dates from event detail pages based on the assumption that recurring events would show future dates. However, this threw away valuable date information that could have corrected the header detection failure.

## Solution Implemented

### Fix 1: Enhanced Header Detection (scraper_service.py)

Updated the day header detection to match multiple patterns:

```python
# Pattern 4: Common patterns like "THINGS TO DO ON SUNDAY" or "FRIDAY NIGHT"
day_match = re.search(r'\b(FRIDAY|SATURDAY|SUNDAY)\b', line, re.IGNORECASE)

if day_match:
    detected_day = day_match.group(1).lower()
    # Only update current_day if this looks like a header
    is_header = (
        len(line) < 100 and  # Not too long
        (line.isupper() or  # All caps
         re.search(r'(THINGS TO DO|EVENTS ON|HAPPENING)', line, re.IGNORECASE) or
         line.startswith('#'))  # Markdown header
    )
    if is_header:
        current_day = detected_day
        print(f"  📅 Found day header: '{line[:60]}...' → {current_day}")
```

**Key improvements**:
- Detects day names anywhere in the line (not just at start)
- Validates it's a header using:
  - Length check (< 100 chars)
  - ALL CAPS text
  - Keywords: "THINGS TO DO", "EVENTS ON", "HAPPENING"
  - Markdown header indicator (#)

### Fix 2: Smart Date Extraction from Event Pages (scraper_service.py)

Added date extraction from event detail pages with validation:

```python
# Look for date patterns - extract the FIRST date found (usually the correct one)
if not details['date']:
    # Pattern for dates like "Nov 2, 2025" or "November 2, 2025"
    date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})\b', line, re.IGNORECASE)
    if date_match:
        date_str = date_match.group(0)
        parsed_date = api_helpers.parse_date_string(date_str)
        if parsed_date:
            details['date'] = parsed_date
```

Then validates and uses the date intelligently:

```python
if detailed_info.get('date'):
    extracted_date = detailed_info['date']
    # Check if extracted date is within this weekend (Fri-Sun)
    if extracted_date in [weekend_dates['friday'], weekend_dates['saturday'], weekend_dates['sunday']]:
        # Date from event page matches this weekend - use it!
        event["date"] = extracted_date
        # Verify it matches the assigned_day, if not update for accuracy
        if expected_date != extracted_date:
            print(f"  ⚠️ Date mismatch: header={assigned_day} ({expected_date}), event page={day_name} ({extracted_date}). Using event page date.")
```

**Key logic**:
1. Extract the first date found on the event page
2. Validate it's within this weekend (Fri-Sun)
3. If yes, use it and correct any header mismatch
4. If no, keep the header-based date (filters recurring events)

### Fix 3: Enhanced Date Parsing (api_helpers.py)

Added support for more date formats:

```python
formats = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m-%d-%Y",
    "%B %d, %Y",      # November 2, 2025
    "%b %d, %Y",      # Nov 2, 2025
    "%B %d %Y",       # November 2 2025 (without comma)
    "%b %d %Y",       # Nov 2 2025 (without comma)
    "%A, %B %d, %Y",  # Friday, November 2, 2025
    "%a, %b %d, %Y",  # Fri, Nov 2, 2025
]
```

## How It Works Now

### Scenario 1: Header Detected Correctly
- Main page: Event under "THINGS TO DO ON SUNDAY"
- Header detected: `current_day = 'sunday'`
- Assigned date: November 2, 2025
- Event page confirms: "Nov 2, 2025"
- **Result**: ✅ Correct date (November 2)

### Scenario 2: Header Detection Failed
- Main page: Event under "THINGS TO DO ON SUNDAY"
- Header NOT detected: `current_day = None` → defaults to `'friday'`
- Assigned date: October 31, 2025 (wrong)
- Event page says: "Nov 2, 2025"
- Date is within weekend? Yes (Sunday)
- **Result**: ✅ Corrected to November 2 with warning message

### Scenario 3: Recurring Event
- Main page: Event under "FRIDAY"
- Header detected: `current_day = 'friday'`
- Assigned date: November 1, 2025
- Event page says: "Nov 8, 2025" (next week's occurrence)
- Date is within weekend? No
- **Result**: ✅ Keeps November 1 (this weekend)

## Expected Behavior After Fix

For the Memphis Japan Festival:
- **Main page**: Listed under "THINGS TO DO ON SUNDAY"
- **Header detection**: Matches "SUNDAY" in header → `current_day = 'sunday'`
- **Initial date**: November 2, 2025 ✅
- **Event page**: Confirms "Nov 2, 2025" ✅
- **Final date**: November 2, 2025 ✅
- **Display**: "Sunday, November 2, 2025" ✅

## Testing the Fix

To test the fix, trigger a data refresh:

```python
# In Anvil console
anvil.server.call('clear_all_data')
anvil.server.call('trigger_data_refresh')
```

Look for these log messages:
```
📅 Found day header: 'THINGS TO DO ON SUNDAY' → sunday
```

If header detection still fails, you'll see:
```
⚠️ Date mismatch: header=friday (2025-10-31), event page=sunday (2025-11-02). Using event page date.
```

## Files Changed

1. **server_code/scraper_service.py**
   - Enhanced header detection (lines 104-130)
   - Added date extraction from event pages (lines 294-313)
   - Implemented smart date validation logic (lines 421-439)

2. **server_code/api_helpers.py**
   - Added more date format patterns (lines 79-89)

3. **DATE_DETECTION_FIX_SUMMARY.md** (this file)
   - Documentation of the fix

## Deployment

Changes are ready to commit and push to GitHub. After pushing:

1. Pull changes in Anvil
2. Clear existing data: `anvil.server.call('clear_all_data')`
3. Refresh data: `anvil.server.call('trigger_data_refresh')`
4. Verify events show correct dates

---

**Fix completed**: November 1, 2025
**Issue**: Header pattern mismatch + ignored event page dates
**Solution**: Enhanced header detection + smart date extraction with validation

