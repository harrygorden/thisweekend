# This Weekend - User Guide

Complete guide for using and administering the This Weekend Memphis Event Planner.

## Table of Contents

1. [AdminForm Overview](#adminform-overview)
2. [Database Management](#database-management)
3. [Testing & Monitoring](#testing--monitoring)
4. [Data Refresh](#data-refresh)
5. [API Configuration](#api-configuration)
6. [Troubleshooting](#troubleshooting)

---

## AdminForm Overview

The AdminForm is your control center for managing the This Weekend app. It provides:

- **Database Setup & Status** - Automatic schema management
- **Health Checks** - System-wide diagnostics
- **API Testing** - Individual API verification
- **Data Refresh** - Manual and automated data updates
- **Monitoring** - Status dashboards and logs

### Accessing AdminForm

1. Open your Anvil app
2. AdminForm should be the startup form (set during deployment)
3. If not, navigate to AdminForm from the app menu

---

## Database Management

### Setup Database

**Button:** `Setup Database`

**What it does:**
- Verifies all required tables exist
- Creates any missing columns automatically
- Updates schema to match latest version

**When to use:**
- First deployment (creates all 33 columns)
- After pulling code updates that change schema
- If columns are missing or corrupted

**Expected output:**
```
DATABASE SETUP COMPLETE
Total tables: 3
  ✅ OK: 3
  🔧 Fixed: 0
  ❌ Errors: 0
  📝 Columns created: 33
```

### Check Status

**Button:** `Check Status`

**What it does:**
- Read-only check of database schema
- Lists all columns in each table
- Identifies missing columns (if any)

**When to use:**
- Before running setup (to see what needs fixing)
- After updates to verify schema
- When troubleshooting database issues

### Clear All Data

**Button:** `Clear Data` ⚠️ **DANGER**

**What it does:**
- Deletes ALL rows from all tables:
  - Events
  - Weather forecasts
  - Scrape logs

**When to use:**
- Testing fresh data loads
- Clearing corrupted data
- Resetting for development

**Warning:** This cannot be undone! You'll need to re-run data refresh.

---

## Testing & Monitoring

### Health Check

**Button:** `Health Check`

**What it does:**
- Comprehensive system health scan
- Checks:
  - Database tables and columns
  - API key configuration
  - Data freshness (last refresh time)

**When to use:**
- Weekly maintenance check
- Before important events/demos
- After deployment or updates
- When troubleshooting issues

**Expected output:**
```
SYSTEM HEALTH CHECK
Overall Status: OK
Issues Found: 0

✅ Database Tables: ok
✅ Api Keys: ok
✅ Data Freshness: ok
```

### Test API Keys

**Button:** `Test API Keys`

**What it does:**
- Verifies all 3 API keys are configured in Anvil Secrets
- Shows masked preview of each key
- Does NOT test if keys are valid (just checks they exist)

**When to use:**
- After initial setup
- If API calls are failing
- When rotating API keys

### Individual API Tests

#### Test OpenWeather API

**Button:** `Test OpenWeather`

**What it does:**
- Makes a live API call to OpenWeather
- Fetches Memphis weather for Fri/Sat/Sun
- Displays full forecast data

**When to use:**
- Verify OpenWeather API key works
- Check weather data format
- Troubleshoot weather integration

#### Test Firecrawl API

**Button:** `Test Firecrawl`

**What it does:**
- Runs 3 comprehensive tests:
  1. Known-good URL (firecrawl.dev)
  2. Target URL without stealth mode
  3. Target URL with stealth mode
- Takes 30-60 seconds to complete

**When to use:**
- Verify Firecrawl API key and access
- Troubleshoot scraping failures
- Test stealth mode capability

#### Test OpenAI API

**Button:** `Test OpenAI`

**What it does:**
- Sends a sample event to ChatGPT
- Gets AI analysis back
- Verifies JSON response format

**When to use:**
- Verify OpenAI API key works
- Check AI categorization quality
- Troubleshoot analysis failures

### Test Scraping Only

**Button:** `Test Scraping Only`

**What it does:**
- Scrapes website and parses events
- **Does NOT use OpenAI** (saves API costs!)
- Perfect for debugging Firecrawl integration

**When to use:**
- Troubleshoot scraping without spending OpenAI credits
- Verify parser is finding events
- Debug markdown extraction issues

---

## Data Refresh

### Refresh Data

**Button:** `Refresh Data`

**What it does:**
Complete data refresh workflow:
1. Clean up old data
2. Fetch Memphis weather forecast
3. Scrape events from ilovememphisblog.com
4. Parse event details
5. Analyze events with AI (categorization)
6. Match events with weather
7. Calculate recommendation scores

**Duration:** 2-5 minutes

**When to use:**
- Weekly (automated via background task)
- Manual updates before checking weekend plans
- After clearing data

**Limitations:**
- Uses Firecrawl API credits
- Uses OpenAI API credits
- May fail if source website structure changes

### Load Test Events

**Button:** `Load Test Events`

**What it does:**
- Creates 14 realistic sample events
- Perfect for testing UI without API costs
- Events include variety of:
  - Categories (arts, music, sports, food)
  - Audience types (adults, family, all-ages)
  - Cost levels (free to $$$$)
  - Indoor/outdoor settings

**When to use:**
- Initial development and testing
- UI/UX testing without live data
- When Firecrawl is failing
- Demonstrations

### Clear Test Events

**Button:** `Clear Test Events`

**What it does:**
- Removes only test events (marked with special ID pattern)
- Keeps real scraped events

**When to use:**
- After testing, before production use
- Switching from test to live data

### View Refresh Log

**Button:** `View Refresh Log`

**What it does:**
- Shows history of data refresh runs
- Displays:
  - Last run timestamp
  - Success/failure status
  - Events found and analyzed
  - Duration
  - Error messages (if any)
- Shows last 5 refresh runs

**When to use:**
- Monitor background task execution
- Troubleshoot refresh failures
- Verify automated updates are running

---

## API Configuration

### Required API Keys

Configure these in Anvil Settings → Secrets:

#### 1. OPENWEATHER_API_KEY

**Provider:** OpenWeather  
**Plan Required:** One Call API 3.0 access  
**Free Tier:** No (requires paid subscription ~$0.02/call)  
**Usage:** 3 calls per week (Fri/Sat/Sun forecasts)

**How to get:**
1. Sign up at [openweathermap.org](https://openweathermap.org)
2. Subscribe to One Call API 3.0 plan
3. Copy API key from dashboard
4. Add to Anvil Secrets as `OPENWEATHER_API_KEY`

#### 2. FIRECRAWL_API_KEY

**Provider:** Firecrawl  
**Plan Required:** Any plan with v2 API access  
**Free Tier:** Varies (check firecrawl.dev pricing)  
**Usage:** ~50-100 calls per week (scraping events)

**How to get:**
1. Sign up at [firecrawl.dev](https://firecrawl.dev)
2. Choose a plan
3. Copy API key from dashboard
4. Add to Anvil Secrets as `FIRECRAWL_API_KEY`

#### 3. OPENAI_API_KEY

**Provider:** OpenAI  
**Plan Required:** Pay-as-you-go API access  
**Free Tier:** New accounts get free credits  
**Usage:** ~50 calls per week (event analysis)  
**Cost:** ~$0.05/week (GPT-3.5) or ~$0.75/week (GPT-4)

**How to get:**
1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Add billing information
3. Create API key
4. Add to Anvil Secrets as `OPENAI_API_KEY`

### Changing API Keys

1. In Anvil editor: Settings → Secrets
2. Click the **Edit** button next to the secret
3. Update the value
4. Click **Save**
5. Run **Test API Keys** to verify

---

## Troubleshooting

### Database Issues

**Symptom:** Missing columns error

**Solution:**
1. Click **"Check Status"** to see what's missing
2. Click **"Setup Database"** to auto-create columns
3. Verify in output: "Created X columns"

---

**Symptom:** "Table does not exist" error

**Solution:**
1. In Anvil editor → Data Tables
2. Manually create missing table(s): `events`, `weather_forecast`, `scrape_log`
3. Run **"Setup Database"** to add columns

---

### API Failures

**Symptom:** OpenWeather test fails

**Common causes:**
- Invalid API key
- API key doesn't have One Call API 3.0 access
- Billing issue (requires paid plan)

**Solution:**
1. Verify API key in OpenWeather dashboard
2. Check One Call 3.0 subscription is active
3. Update key in Anvil Secrets if changed

---

**Symptom:** Firecrawl test fails

**Common causes:**
- Invalid API key
- Free tier limitation
- Target website blocking
- Plan doesn't support v2 API or stealth mode

**Solution:**
1. Verify API key in Firecrawl dashboard
2. Check plan includes v2 API access
3. Review usage limits
4. Try **"Test Scraping Only"** button

---

**Symptom:** OpenAI test fails

**Common causes:**
- Invalid API key
- Insufficient credits/quota
- Rate limit exceeded

**Solution:**
1. Verify API key in OpenAI dashboard
2. Check billing and usage limits
3. Add credits if balance is low

---

### Scraping Issues

**Symptom:** "Found 0 events" after scraping

**Common causes:**
- Website structure changed (parser doesn't recognize events)
- Firecrawl returned empty content
- Cloudflare blocking (needs stealth mode)

**Solution:**
1. Run **"Test Scraping Only"** to see debug output
2. Check markdown preview for content
3. Review parser stats in console
4. Temporarily use **"Load Test Events"** while investigating

---

**Symptom:** Scraping very slow (>2 minutes)

**Cause:** Scraper fetches individual event pages for details

**Expected:** ~3 seconds per event (Firecrawl rate limiting)

**Normal:** 50 events = ~2.5 minutes total

---

### Data Refresh Failures

**Symptom:** Background task shows "failed" status

**Solution:**
1. Click **"View Refresh Log"** to see error message
2. Identify which step failed:
   - Weather → Check OpenWeather API
   - Scraping → Check Firecrawl API  
   - AI Analysis → Check OpenAI API
3. Run individual test for that API
4. Fix the underlying issue
5. Manually trigger refresh with **"Refresh Data"** button

---

### Health Check Warnings

**Warning:** "Data is X days old"

**Cause:** Background task hasn't run recently

**Solution:**
1. Verify background task is enabled (Settings → Background Tasks)
2. Check task schedule is correct
3. Manually run **"Refresh Data"**

---

**Warning:** "Some API keys are not configured"

**Cause:** Missing or incorrectly named secrets

**Solution:**
1. Click **"Test API Keys"** to see which are missing
2. In Anvil: Settings → Secrets
3. Add missing keys with exact names:
   - `OPENWEATHER_API_KEY`
   - `FIRECRAWL_API_KEY`
   - `OPENAI_API_KEY`

---

## Best Practices

### Weekly Maintenance
1. Run **"Health Check"** - verify system is healthy
2. Review **"View Refresh Log"** - check automated updates ran
3. Spot-check event data quality in database

### Before Important Use
1. Run **"Health Check"** - catch issues early
2. If data is stale, manually **"Refresh Data"**
3. Verify weather forecast is current

### Cost Optimization
1. Schedule background task weekly (not daily)
2. Use **"Test Scraping Only"** for debugging (free)
3. Use **"Load Test Events"** for development (free)
4. Monitor API usage in provider dashboards

### Backup & Recovery
1. Regular health checks prevent issues
2. If data corrupted: **"Clear All Data"** → **"Refresh Data"**
3. Use **"Load Test Events"** as emergency fallback

---

## Status Indicators

### Output Panel Icons

- **✅** - Success
- **⚠️** - Warning (non-critical)
- **❌** - Error (needs attention)
- **⏳** - In progress
- **🔍** - Diagnostic/testing
- **🌤️** - Weather-related
- **🤖** - AI-related
- **📋** - Database-related

### Health Check Statuses

- **ok** - No issues detected
- **warning** - Minor issues, app functional
- **error** - Critical issues, needs fixing

---

## Additional Resources

- **DEPLOYMENT_GUIDE.md** - Initial setup and deployment
- **README.md** - Project overview and architecture
- **Server Logs** - Anvil editor → View → Server Logs (detailed debugging)

---

**Questions or issues?** Open an issue in the GitHub repository or contact support.

