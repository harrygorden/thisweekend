# This Weekend - Next Steps

## ✅ What We've Completed

### Phase 1: Project Setup & Configuration

We've successfully created all **7 server modules** with complete implementations:

1. **`server_code/config.py`** ✅
   - Memphis coordinates (35.1495, -90.0490)
   - API endpoints and configuration
   - Weather score weights and thresholds
   - Category and audience type definitions

2. **`server_code/api_helpers.py`** ✅
   - API key retrieval from Anvil Secrets
   - Retry logic with exponential backoff
   - Date/time parsing utilities
   - Text sanitization functions
   - Weekend date calculations

3. **`server_code/weather_service.py`** ✅
   - OpenWeather One Call API 3.0 integration
   - Weekend forecast extraction (Fri/Sat/Sun)
   - Hourly weather data processing
   - Weather score calculation for events
   - Database storage functions

4. **`server_code/scraper_service.py`** ✅
   - Firecrawl API integration
   - Event parsing from markdown content
   - Cost level extraction and standardization
   - Event data storage functions

5. **`server_code/ai_service.py`** ✅
   - OpenAI ChatGPT integration
   - Event analysis prompt engineering
   - Indoor/outdoor classification
   - Audience type and category tagging
   - Batch processing with rate limiting

6. **`server_code/data_processor.py`** ✅
   - Weather-event matching logic
   - Recommendation score calculation
   - Time-of-day bonus scoring
   - Event filtering functions
   - Search functionality

7. **`server_code/background_tasks.py`** ✅
   - Complete orchestration workflow
   - 10-step data refresh process
   - Error handling and logging
   - Manual trigger functions
   - Data cleanup utilities

## 🚀 NEW: Automatic Setup Available!

**You no longer need to manually add columns!** We've created an automatic setup tool.

### Option 1: Automatic Setup (RECOMMENDED) ⚡

**See:** [`ADMIN_TOOLS_GUIDE.md`](ADMIN_TOOLS_GUIDE.md)

**Quick steps:**
1. Ensure your 3 empty tables are created (`events`, `weather_forecast`, `scrape_log`)
2. Add a button to any form and call: `anvil.server.call('run_database_setup')`
3. Click the button - all columns will be created automatically!

**That's it!** Skip to the "Testing" section below.

---

### Option 2: Manual Setup (Original Method)

If you prefer to manually add columns, follow these steps:

## 🔧 Manual Configuration

Before testing, you need to complete these manual steps in the Anvil UI:

### 1. Verify Anvil Secrets ✓ (You said you've done this)

Ensure these are configured in **App Settings → Secrets**:
- `OPENWEATHER_API_KEY`
- `FIRECRAWL_API_KEY`
- `OPENAI_API_KEY`

### 2. Add Columns to Data Tables (MANUAL METHOD)

You created the **empty tables**, but now you need to add columns to each:

#### Table: `events`
Navigate to **Data Tables → events** and add these columns:

| Column Name | Type | Notes |
|------------|------|-------|
| `event_id` | Text | Primary identifier |
| `title` | Text | Event name |
| `description` | Text | Full description |
| `date` | Date | Event date |
| `start_time` | Text | Start time string |
| `end_time` | Text | End time (optional) |
| `location` | Text | Venue/location |
| `cost_raw` | Text | Original cost text |
| `cost_level` | Text | Standardized: Free/$/$$/$$$/$$$$  |
| `is_indoor` | Boolean | Indoor event flag |
| `is_outdoor` | Boolean | Outdoor event flag |
| `audience_type` | Text | adults/family-friendly/all-ages |
| `categories` | SimpleObject | List of categories (JSON) |
| `weather_score` | Number | Weather suitability (0-100) |
| `recommendation_score` | Number | Overall score (0-100) |
| `scraped_at` | DateTime | Scrape timestamp |
| `analyzed_at` | DateTime | AI analysis timestamp |

#### Table: `weather_forecast`
Navigate to **Data Tables → weather_forecast** and add these columns:

| Column Name | Type | Notes |
|------------|------|-------|
| `forecast_date` | Date | Date of forecast |
| `day_name` | Text | Friday/Saturday/Sunday |
| `temp_high` | Number | High temperature (°F) |
| `temp_low` | Number | Low temperature (°F) |
| `conditions` | Text | Weather description |
| `precipitation_chance` | Number | Rain chance (0-100%) |
| `wind_speed` | Number | Wind speed (mph) |
| `hourly_data` | SimpleObject | Hourly forecasts (JSON) |
| `fetched_at` | DateTime | Fetch timestamp |

#### Table: `scrape_log`
Navigate to **Data Tables → scrape_log** and add these columns:

| Column Name | Type | Notes |
|------------|------|-------|
| `log_id` | Text | Unique log ID |
| `run_date` | DateTime | Task run time |
| `status` | Text | success/partial/failed |
| `events_found` | Number | Events scraped count |
| `events_analyzed` | Number | Events analyzed count |
| `error_message` | Text | Error details if failed |
| `duration_seconds` | Number | Task duration |

### 3. Set Table Permissions

For each table, click **Table Settings → Permissions**:

- **Server code**: Full access (read/write/delete)
- **Client code**: Read-only or None (we'll access via callable functions)

### 4. Enable Background Tasks Scheduler (if not already enabled)

Go to **App Settings → Services**:
- Enable **Uplink** service (for background tasks)
- OR use **Anvil Scheduled Tasks** if available on your plan

## 🧪 Testing the Implementation

### Step 1: Create a Test Form

1. In Anvil, create a new form called `TestForm` or add to your existing `Form1`
2. Add a button called `test_refresh_button`
3. Add a label called `status_label` to show results

### Step 2: Add Test Code

In your test form's `__init__.py`:

```python
from anvil import *
import anvil.server

class TestForm(TestFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
  
  def test_refresh_button_click(self, **event_args):
    self.status_label.text = "Starting data refresh..."
    
    try:
      # Trigger the background task
      task = anvil.server.call('trigger_data_refresh')
      self.status_label.text = "Data refresh started! Check server logs for progress."
      
    except Exception as e:
      self.status_label.text = f"Error: {str(e)}"
```

### Step 3: Run the Test

1. Click the **test_refresh_button**
2. Open **Server Logs** (bottom of Anvil IDE) to watch progress
3. The background task will:
   - Fetch weather for Memphis
   - Scrape ilovememphisblog.com/weekend
   - Parse events
   - Analyze with ChatGPT
   - Calculate recommendations
   - Store everything in your Data Tables

**Expected Duration:** 2-5 minutes (depending on number of events)

### Step 4: Verify Results

After the task completes, check:

1. **Data Tables → events** - Should have events for upcoming weekend
2. **Data Tables → weather_forecast** - Should have 3 rows (Fri/Sat/Sun)
3. **Data Tables → scrape_log** - Should have 1 log entry with "success" status

## 🚀 Next Phase: Build the UI

Once testing is successful, we'll move to **Phase 6: Anvil UI Development**:

1. Design main form layout
2. Create weather display cards
3. Build event card component (RepeatingPanel)
4. Add filter panel
5. Implement itinerary builder
6. Add search functionality

## 📞 Need Help?

If you encounter any issues:

1. **Check Server Logs** for detailed error messages
2. **Verify API Keys** are correct in Anvil Secrets
3. **Check Data Table Schemas** match the specifications above
4. **Test Individual Functions** by creating callable test functions

## 📋 Current Progress

- [x] Phase 1.1: Manual Configuration (Secrets)
- [x] Phase 1.2: Data Tables Created (Empty)
- [ ] **Phase 1.2: Add Columns to Tables** ← YOU ARE HERE
- [x] Phase 1.3: Server Module Structure
- [ ] Phase 2-5: Test Data Pipeline
- [ ] Phase 6-8: Build UI
- [ ] Phase 9-12: Testing & Deployment

---

**Ready to proceed?** Start by adding the columns to your Data Tables, then run the test refresh!

