# This Weekend - Administrator Guide

Complete guide for managing and operating the This Weekend Memphis Event Planner.

## Table of Contents

1. [Admin Panel Overview](#admin-panel-overview)
2. [Database Management](#database-management)
3. [Data Refresh Operations](#data-refresh-operations)
4. [API Testing & Monitoring](#api-testing--monitoring)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Maintenance Schedule](#maintenance-schedule)
7. [Cost Optimization](#cost-optimization)

---

## Admin Panel Overview

Access the admin panel by clicking the "Admin" link in the main app and entering your admin password.

### Main Functions

| Button | Function | When to Use |
|--------|----------|-------------|
| **Setup Database** | Auto-creates all table columns | Initial setup, after schema changes |
| **Health Check** | System-wide diagnostics | Weekly maintenance, troubleshooting |
| **Refresh Data** | Full data update (events + weather) | Weekly updates, manual refresh needed |
| **Load Test Events** | Creates sample data | Testing UI, when scraping fails |
| **Test APIs** | Verifies API connections | Setup verification, API troubleshooting |
| **View Refresh Log** | Shows refresh history | Monitoring background tasks |
| **Clear All Data** | Deletes all database content | Reset for testing (⚠️ USE WITH CAUTION) |

---

## Database Management

### Initial Setup

**First deployment:**

1. Open Admin panel
2. Click **Setup Database**
3. Wait for completion
4. Verify output shows all columns created:
   ```
   DATABASE SETUP COMPLETE
   Total tables: 4
   ✅ OK: 4
   📝 Columns created: 44
   ```

### Schema Verification

**Check database status without changes:**

1. Click **Check Status**
2. Review output for each table
3. Look for missing columns (if any)

**Sample output:**
```
DATABASE STATUS
📋 EVENTS
   Exists: ✅ Yes
   Columns: 17/17
   ✅ All columns present
```

### Data Cleanup

**Clear all data (for testing/reset):**

1. Click **Clear Data**
2. Confirm twice (irreversible action)
3. Re-run data refresh after clearing

⚠️ **Warning:** This deletes ALL events, weather data, and logs. Use only for testing or when resetting the system.

---

## Data Refresh Operations

### Full Data Refresh

**Complete update of all data:**

**Click:** `Refresh Data`

**Process:**
1. Cleans up old/past events
2. Fetches Memphis weather (3 days)
3. Scrapes events from ilovememphisblog.com
4. Parses event details
5. Analyzes with AI (categories, audience, cost)
6. Matches events with weather
7. Calculates recommendation scores

**Duration:** 2-5 minutes  
**Cost:** ~$0.30 (Firecrawl + OpenAI)  
**When to use:** Weekly updates, after clearing data

### Weather-Only Refresh

**Update weather and scores (no scraping/AI):**

This runs automatically via scheduled tasks daily. For manual updates, it's handled by the full refresh or scheduled task.

**Duration:** 10-30 seconds  
**Cost:** FREE  
**When to use:** Daily via scheduled task

### Test Data (Development)

**Load sample events for testing:**

**Click:** `Load Test Events`

**Creates:**
- 14 realistic sample events
- Variety of categories, costs, audiences
- Pre-calculated with weather scores

**Cost:** FREE  
**When to use:** 
- Initial development/testing
- UI/UX testing
- When Firecrawl is failing
- Demonstrations

**Cleanup:** Click `Clear Test Events` to remove test data only.

---

## API Testing & Monitoring

### Test All API Keys

**Click:** `Test API Keys`

**Verifies:**
- All 4 API keys are configured in Anvil Secrets
- Shows masked preview of each key
- Does NOT validate if keys are actually valid

**When to use:** After setup, when rotating API keys

### Individual API Tests

#### OpenWeather API Test

**Click:** `Test OpenWeather`

**What it tests:**
- Live API call to OpenWeather
- Fetches Memphis weather for Fri/Sat/Sun
- Displays full forecast data

**Success output:**
```
OPENWEATHER API TEST
✅ SUCCESS! Fetched weather for 3 days

Friday (2025-11-02):
  High: 72°F, Low: 58°F
  Conditions: partly cloudy
  Rain chance: 20%
  Wind: 8 mph
  Hourly forecasts: 24 hours
```

**Common failures:**
- Invalid API key
- No One Call API 3.0 access
- Billing issue

#### Firecrawl API Test

**Click:** `Test Firecrawl`

**What it tests:**
- Runs 3 comprehensive tests
- Test 1: Known-good URL (firecrawl.dev)
- Test 2: Target URL without stealth
- Test 3: Target URL with stealth

**Duration:** 30-60 seconds

**Success:** All 3 tests pass

**Common failures:**
- Invalid API key
- Plan doesn't support v2 API
- Target website blocking

#### OpenAI API Test

**Click:** `Test OpenAI`

**What it tests:**
- Sends sample event to ChatGPT
- Gets AI analysis back
- Verifies JSON response format

**Success output:**
```
OPENAI API TEST
✅ SUCCESS! ChatGPT API is working

AI Analysis Results:
  Indoor: True
  Outdoor: True
  Audience: all-ages
  Cost level: $$
  Categories: Music, Cultural Events
```

**Common failures:**
- Invalid API key
- Insufficient credits
- Rate limit exceeded

#### Test Scraping Only

**Click:** `Test Scraping Only`

**What it does:**
- Scrapes website and parses events
- **Does NOT use OpenAI** (saves money!)
- Perfect for debugging Firecrawl

**When to use:**
- Troubleshoot scraping without OpenAI costs
- Verify parser finds events
- Debug markdown extraction

---

## Troubleshooting Guide

### Database Issues

**Problem:** Missing columns error

**Solution:**
1. Click **Check Status** to see what's missing
2. Click **Setup Database**
3. Verify "Created X columns" in output

---

**Problem:** "Table does not exist" error

**Solution:**
1. In Anvil editor → Data Tables
2. Create missing table(s):
   - `events`
   - `weather_forecast`  
   - `hourly_weather`
   - `scrape_log`
3. Run **Setup Database**

---

### API Failures

**Problem:** OpenWeather test fails

**Common causes:**
- Invalid API key
- No One Call API 3.0 access
- Billing issue (paid plan required)

**Solution:**
1. Verify API key in OpenWeather dashboard
2. Check One Call 3.0 subscription active
3. Update key in Anvil Secrets if changed

---

**Problem:** Firecrawl test fails

**Common causes:**
- Invalid API key
- Free tier limitation
- Target website blocking
- Plan doesn't support v2 API

**Solution:**
1. Verify API key in Firecrawl dashboard
2. Check plan includes v2 API access
3. Review usage limits
4. Try **Test Scraping Only**

---

**Problem:** OpenAI test fails

**Common causes:**
- Invalid API key
- Insufficient credits/quota
- Rate limit exceeded

**Solution:**
1. Verify API key in OpenAI dashboard
2. Check billing and usage limits
3. Add credits if balance low

---

### Scraping Issues

**Problem:** "Found 0 events" after scraping

**Common causes:**
- Website structure changed
- Firecrawl returned empty content
- Cloudflare blocking

**Solution:**
1. Run **Test Scraping Only** to see debug output
2. Check markdown preview for content
3. Review parser stats in console
4. Use **Load Test Events** as temporary workaround

---

**Problem:** Scraping very slow (>2 minutes)

**Expected behavior:** Scraper fetches individual event pages

**Normal timing:** 
- ~3 seconds per event (Firecrawl rate limiting)
- 50 events = ~2.5 minutes total

**Not a bug** - This is intentional to get detailed event information.

---

### Data Refresh Failures

**Problem:** Background task shows "failed" status

**Solution:**
1. Click **View Refresh Log** to see error
2. Identify which step failed:
   - Weather → Check OpenWeather API
   - Scraping → Check Firecrawl API
   - AI Analysis → Check OpenAI API
3. Run individual API test
4. Fix underlying issue
5. Manually trigger **Refresh Data**

---

## Maintenance Schedule

### Daily (Automated)

✅ **Weather refresh via scheduled task**
- Runs automatically at 06:00 UTC
- Updates weather forecasts
- Recalculates recommendation scores
- Cost: FREE

### Weekly (Automated)

✅ **Full data refresh via scheduled task**
- Runs Monday at 06:00 UTC
- Scrapes new events
- AI analysis
- Weather matching
- Cost: ~$0.30

### Weekly (Manual)

📋 **Admin review:**
1. Click **Health Check** → Verify all ✅
2. Click **View Refresh Log** → Check task ran successfully
3. Review event count in system info
4. Spot-check event data quality

### Monthly

💰 **Cost review:**
1. Check OpenWeather usage
2. Check Firecrawl credits
3. Check OpenAI usage
4. Verify costs align with budget (~$1.20/month)

---

## Cost Optimization

### Best Practices

1. **Use scheduled tasks** (not manual refresh)
   - Weekly full refresh
   - Daily weather update
   - Total: $1.20/month

2. **Use test data for development**
   - Click **Load Test Events**
   - No API costs
   - Perfect for UI testing

3. **Use "Test Scraping Only" for debugging**
   - Skips OpenAI ($0 cost)
   - Tests Firecrawl only
   - Perfect for troubleshooting

4. **Monitor API usage**
   - OpenWeather dashboard
   - Firecrawl dashboard
   - OpenAI dashboard

### Cost Breakdown

| Operation | Firecrawl | OpenAI | OpenWeather | Total |
|-----------|-----------|--------|-------------|-------|
| Full Refresh | $0.10 | $0.20 | FREE | $0.30 |
| Weather Only | $0.00 | $0.00 | FREE | $0.00 |
| Test Events | $0.00 | $0.00 | $0.00 | $0.00 |
| Test Scraping | $0.10 | $0.00 | $0.00 | $0.10 |

**Monthly (Recommended Setup):**
- 4 full refreshes/month: $1.20
- 30 weather updates/month: $0.00
- **Total: $1.20/month**

---

## Health Check Details

### Overall Status Indicators

- **ok** - No issues detected
- **warning** - Minor issues, app functional
- **error** - Critical issues, needs fixing

### Checks Performed

1. **Database Tables**
   - All tables exist
   - All columns present
   - Schema matches expected

2. **API Keys**
   - All 4 keys configured
   - Not validating actual API access

3. **Data Freshness**
   - Last refresh time
   - Age of data
   - Warns if >7 days old

### Sample Health Check Output

```
SYSTEM HEALTH CHECK
Overall Status: OK
Issues Found: 0

✅ Database Tables: ok
✅ Api Keys: ok
✅ Data Freshness: ok

Last Refresh: 2025-11-01 06:00:00
Data Age: 0 days
```

---

## Refresh Log Details

View complete history of data refresh operations.

**Click:** `View Refresh Log`

**Information Shown:**
- Last run timestamp
- Success/failure status
- Events found and analyzed
- Duration in seconds
- Error message (if failed)
- Last 5 refresh runs

**Sample Output:**
```
DATA REFRESH STATUS
Last Run: 2025-11-01 06:00:15
Status: SUCCESS
Events Found: 42
Events Analyzed: 42
Duration: 187.3 seconds

Current Event Count: 42

RECENT RUNS
✅ 2025-11-01 06:00
   Status: success
   Events: 42
   Duration: 187.3s

✅ 2025-10-25 06:00
   Status: success
   Events: 38
   Duration: 192.1s
```

---

## Emergency Procedures

### App Not Showing Events

1. Check **System Info** → Event count should be > 0
2. If 0, run **Refresh Data** or **Load Test Events**
3. Check **App Logs** for errors

### Weather Not Showing

1. Run **Test OpenWeather**
2. If fails, check API key and One Call 3.0 access
3. Run **Refresh Data** to fetch fresh weather

### Admin Panel Not Accessible

1. Verify `ADMIN_PASSWORD` secret is set in Anvil
2. Try password reset (update secret in Anvil)
3. Check no syntax errors in `admin_auth.py`

### Scheduled Tasks Not Running

1. Verify app is published
2. Check you have paid Anvil plan
3. Verify "Run scheduled tasks" enabled in environment
4. Check task configuration in Anvil UI

---

## Status Output Icons

**Understanding the output panel:**

- ✅ - Success
- ⚠️ - Warning (non-critical)
- ❌ - Error (needs attention)
- ⏳ - In progress
- 🔍 - Diagnostic/testing
- 🌤️ - Weather-related
- 🤖 - AI-related
- 📋 - Database-related
- 🚀 - Background task
- 🗑️ - Data cleanup

---

## Additional Resources

- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Project Overview:** [README.md](README.md)
- **Server Logs:** Anvil editor → Tools → App Logs
- **Background Tasks:** Anvil editor → Tools → Background Tasks

---

**Questions or Issues?** Check the Anvil forum or open an issue in the GitHub repository.

