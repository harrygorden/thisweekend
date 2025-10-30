# 🔧 Background Task Fixes

## Issues Found & Fixed

### Issue 1: Import Error in `background_tasks.py`
**Problem:** `tables` module not imported, causing "name 'tables' is not defined" error

**Fix Applied:**
```python
# Added imports
import anvil.tables as tables
import anvil.tables.query as q
```

**Line Changed:** Line 188 - `tables.order_by` → `q.order_by`

### Issue 2: Background Task Not Launching Properly
**Problem:** Task may not be running in background due to Anvil's background task requirements

**Fix Applied:**
- Added extensive logging to track progress
- Added step completion indicators
- Added error details for debugging

## ✅ What Was Fixed

1. **Import Error** - Fixed `get_refresh_status()` function
2. **Better Logging** - Added detailed progress messages
3. **Error Tracking** - Improved error messages for debugging

## 🚀 How to Test

### Step 1: Push the Fixes

```bash
git add server_code/background_tasks.py
git commit -m "Fix background task imports and add better logging"
git push origin main
```

### Step 2: Pull in Anvil

1. Open Anvil
2. Click "Pull from Git"
3. Wait for sync to complete

### Step 3: Test the Background Task

In AdminForm:

1. Click **"4. Refresh Data"**
2. Check **Server Logs** (bottom of Anvil IDE)
3. You should see:

```
🚀 BACKGROUND TASK STARTED
Starting scheduled data refresh at 2025-10-30 ...
Log ID: log_...
============================================================

[Step 1/10] Cleaning up old data...
  ✓ Cleanup complete
[Step 2/10] Fetching weekend weather...
  ✓ Fetched weather for 3 days
[Step 3/10] Saving weather data...
  ✓ Weather data saved
[Step 4/10] Scraping weekend events...
  ... (continues)
```

### Step 4: Monitor Progress

**In Server Logs, watch for:**
- ✅ Weather fetch (~5-10 seconds)
- ✅ Event scraping (~10-20 seconds)  
- ✅ AI analysis (~60-120 seconds for 50 events)
- ✅ Recommendation scoring (~5 seconds)

**Total Duration:** 2-5 minutes

## 📊 Expected Output

After successful completion, you should see in scrape_log table:

```
status: success
events_found: 40-60 (depends on what's on the website)
events_analyzed: 40-60 (same as found)
duration_seconds: 120-300 (2-5 minutes)
```

## 🐛 If It Still Doesn't Work

### Check 1: Uplink Service Enabled

Background tasks require the Uplink service:

1. Go to **App Settings → Services**
2. Enable **Uplink**
3. Or use **Scheduled Tasks** if available

### Check 2: API Keys Configured

Verify all 3 API keys are set:

1. In AdminForm, click **"2. Test API Keys"**
2. Should show ✅ for all 3 keys

### Check 3: Check Server Logs

Look for error messages like:
- "Invalid API key"
- "Rate limit exceeded"
- "Connection timeout"

### Check 4: Tables Have Data

After running, check Data Tables:
- `weather_forecast` should have 3 rows
- `events` should have 20-60 rows
- `scrape_log` should have 1 new row

## 🔍 Debugging Commands

**Check if background tasks are running:**
```python
# In server console:
import anvil.server
tasks = anvil.server.list_background_tasks()
print(f"Running tasks: {len(tasks)}")
```

**Check last refresh status:**
```python
# In server console:
import server_code.background_tasks as bg
status = bg.get_refresh_status()
print(status)
```

**Manually run ONE step (for testing):**
```python
# In server console:
import server_code.weather_service as weather
data = weather.fetch_weekend_weather()
print(f"Weather data: {data}")
```

## 💡 Alternative: Test Individual Steps

If the full background task times out, you can test each step individually:

### Test Weather (Quick - ~10 seconds)

```python
# Add a test button in AdminForm:
def test_weather_button_click(self, **event_args):
    import server_code.weather_service as weather
    try:
        data = weather.fetch_weekend_weather()
        weather.save_weather_to_db(data)
        alert(f"✅ Weather loaded: {len(data)} days")
    except Exception as e:
        alert(f"❌ Error: {str(e)}")
```

### Test Scraping (Medium - ~20 seconds)

```python
def test_scraping_button_click(self, **event_args):
    import server_code.scraper_service as scraper
    try:
        markdown = scraper.scrape_weekend_events()
        events = scraper.parse_events_from_markdown(markdown)
        alert(f"✅ Found {len(events)} events")
    except Exception as e:
        alert(f"❌ Error: {str(e)}")
```

### Test AI (Slow - ~2 min for 50 events)

```python
def test_ai_button_click(self, **event_args):
    import server_code.ai_service as ai
    from anvil.tables import app_tables
    
    try:
        events = list(app_tables.events.search())
        analyses = ai.analyze_all_events(events[:5])  # Test with first 5
        alert(f"✅ Analyzed {len(analyses)} events")
    except Exception as e:
        alert(f"❌ Error: {str(e)}")
```

## 📋 Summary

**Fixed:**
- ✅ Import error in background_tasks.py
- ✅ Added better logging
- ✅ Added progress indicators

**To Do:**
- Push fixes to GitHub
- Pull in Anvil
- Test "Refresh Data" button
- Check server logs for progress
- Verify data in tables

**Expected Result:**
- Background task runs for 2-5 minutes
- Weather data: 3 rows in weather_forecast
- Events data: 20-60 rows in events
- scrape_log: 1 new row with "success" status

---

**After these fixes, the background task should work!** Push to GitHub and test. 🚀

