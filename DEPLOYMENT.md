# This Weekend - Deployment Guide

Complete guide for deploying and configuring the This Weekend Memphis Event Planner.

## Prerequisites

- **Anvil Account:** [anvil.works](https://anvil.works)
- **GitHub Account:** For version control
- **API Keys:**
  - [OpenWeather API](https://openweathermap.org/api) - One Call API 3.0 access required
  - [Firecrawl API](https://firecrawl.dev) - Paid plan for web scraping
  - [OpenAI API](https://openai.com) - Pay-as-you-go access

---

## Quick Deployment (20 minutes)

### 1. Create Anvil App

1. Log into [Anvil](https://anvil.works)
2. Click **Create New App** → **Blank App**
3. Name it: `ThisWeekend`

### 2. Connect to GitHub

1. **Settings** (gear icon) → **Version Control**
2. Click **Connect to GitHub**
3. Authorize Anvil
4. Create repository: `thisweekend`
5. Click **Connect**

### 3. Push Code to GitHub

```bash
cd thisweekend
git init
git remote add origin https://github.com/YOUR_USERNAME/thisweekend.git
git add .
git commit -m "Initial commit"
git push -u origin master
```

### 4. Pull into Anvil

1. In Anvil editor: **Version Control** panel (clock icon)
2. Click **Pull from Git**
3. All code appears in Anvil

### 5. Install Python Dependencies

1. **Settings** → **Python Environment**
2. Add packages:
   - `firecrawl-py`
   - `openai`
   - `pytz`

### 6. Configure API Keys

1. **Settings** → **Secrets**
2. Add secrets:
   - `OPENWEATHER_API_KEY` - Your OpenWeather One Call API 3.0 key
   - `FIRECRAWL_API_KEY` - Your Firecrawl API key
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `ADMIN_PASSWORD` - Password for admin access (create your own)

### 7. Create Data Tables

1. Click **Data Tables** in left sidebar
2. Create 4 empty tables (we'll auto-create columns):
   - `events`
   - `weather_forecast`
   - `hourly_weather`
   - `scrape_log`

**Important:** Just create the tables with any single column - our setup script will create all the proper columns automatically.

### 8. Set Startup Form

1. **Settings** → **Startup Form**
2. Select `MainApp`

### 9. Run Admin Setup

1. Click **Run** ▶️
2. Access the Admin panel via the admin link
3. Enter your `ADMIN_PASSWORD`
4. Click **Setup Database** button
5. All 44 columns created automatically! ✅

**Setup Complete!** Your app is ready to use.

---

## Configure Scheduled Tasks

Anvil Scheduled Tasks automate data refreshes. **Requires paid Anvil plan.**

### Add Tasks

1. **Settings** → **Scheduled Tasks** → **+**
2. Configure two tasks:

**Task 1: Weekly Full Refresh**
- Task: `scheduled_refresh_all_data`
- Every: `1 week on Monday at 06:00 UTC`
- Fetches events, weather, runs AI analysis (~$0.30/run)

**Task 2: Daily Weather Update**
- Task: `scheduled_refresh_weather_and_scores`
- Every: `1 day at 06:00 UTC`
- Updates weather and scores only (FREE)

**Total Cost:** ~$1.20/month

---

## Production Deployment

### Option 1: Anvil Subdomain (Free)

1. Click **Publish** in top-right
2. Choose subdomain: `your-app.anvil.app`
3. Click **Publish**

**URL:** `https://your-app.anvil.app`

### Option 2: Custom Domain (Paid Plans)

1. Upgrade to paid Anvil plan
2. **Settings** → **Custom Domains**
3. Add your domain
4. Update DNS records as instructed
5. Click **Publish**

---

## Testing Your Deployment

### 1. Test API Keys

1. Open app → Admin panel
2. Click **Test API Keys**
3. All three should show ✅

### 2. Test Individual APIs

1. **Test OpenWeather** → Should return 3 days of weather
2. **Test Firecrawl** → Should connect successfully
3. **Test OpenAI** → Should analyze sample event

### 3. Test Data Refresh

**Option A: Using Test Data (Recommended First)**
1. Click **Load Test Events**
2. Creates 14 realistic sample events
3. No API costs, instant results
4. Perfect for testing UI

**Option B: Full Refresh (Uses API Credits)**
1. Click **Refresh Data**
2. Wait 2-5 minutes
3. Scrapes real events, uses AI analysis
4. Cost: ~$0.30 per run

---

## Troubleshooting

### "Module not found" errors
**Solution:** Install dependencies in Settings → Python Environment

### "Secret not found" errors
**Solution:** Add API keys in Settings → Secrets with exact names

### Database columns missing
**Solution:** 
1. Open Admin panel
2. Click **Setup Database**
3. Columns auto-created

### "Table not found" errors
**Solution:** Create the 4 tables in Data Tables section

### Scheduled tasks don't run
**Check:**
- App is published
- You have paid Anvil plan
- Environment has "Run scheduled tasks" enabled

---

## Environment Setup

### Production Environment

1. **Settings** → **Environments** → **Production**
2. Enable **Run scheduled tasks**
3. Use for live app

### Development Environment

1. Create "Development" environment
2. **Disable** scheduled tasks
3. Use for testing

This prevents double-runs and wasted API credits.

---

## Database Schema

### `events` Table (17 columns)
Stores scraped and AI-analyzed events.

### `weather_forecast` Table (9 columns)
Caches weekend weather forecasts.

### `hourly_weather` Table (11 columns)
Stores hourly weather data for precise event-time forecasts.

### `scrape_log` Table (7 columns)
Tracks background task execution.

**Setup:** All columns created automatically via "Setup Database" button.

---

## API Requirements & Costs

### OpenWeather API
- **Plan:** One Call API 3.0 (paid subscription)
- **Cost:** ~$0.02/week
- **Usage:** 1 call per data refresh

### Firecrawl API
- **Plan:** Paid (starts at $10/month)
- **Cost:** ~1 credit per scrape
- **Usage:** 50-100 calls per event scrape

### OpenAI API
- **Plan:** Pay-as-you-go
- **Cost:** ~$0.20-$0.40 per refresh
- **Models:** GPT-4.1-mini (analysis) + GPT-4.1 (suggestions)
- **Usage:** 1 call per event + 1 for suggestions

**Total Operating Cost:** ~$0.50 per full refresh, ~$2.00/month with weekly schedule + daily weather

---

## File Structure

```
thisweekend/
├── server_code/              # Backend Python modules
│   ├── background_tasks.py   # Scheduled task orchestration
│   ├── weather_service.py    # OpenWeather API integration
│   ├── scraper_service.py    # Firecrawl web scraping
│   ├── ai_service.py         # OpenAI event analysis
│   ├── data_processor.py     # Recommendation engine
│   ├── admin_tools.py        # Admin utilities
│   ├── admin_auth.py         # Admin authentication
│   ├── config.py             # Configuration constants
│   ├── api_helpers.py        # API utility functions
│   ├── date_utils.py         # Timezone-aware date handling
│   ├── debug_tools.py        # Debugging utilities
│   ├── setup_schema.py       # Database schema setup
│   ├── test_data.py          # Test event generation
│   └── requirements.txt      # Python dependencies
├── client_code/              # Frontend Anvil forms
│   ├── MainApp/              # Main user interface
│   ├── AdminForm/            # Admin panel
│   ├── EventCard/            # Event component
│   └── WeatherCard/          # Weather component
├── theme/                    # Anvil theme/styling
├── README.md                 # Project overview
├── DEPLOYMENT.md             # This file
├── ADMIN_GUIDE.md            # Admin operations guide
└── anvil.yaml               # Anvil app configuration
```

---

## Post-Deployment Checklist

- [ ] App published to Anvil subdomain or custom domain
- [ ] All API keys configured and tested
- [ ] Database tables created and columns setup
- [ ] Scheduled tasks configured (if using paid plan)
- [ ] Test data loaded OR full refresh run successfully
- [ ] Admin password set and tested
- [ ] Main app displays weather and events correctly

---

## Support & Documentation

- **Admin Operations:** See [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- **Project Overview:** See [README.md](README.md)
- **Anvil Documentation:** https://anvil.works/docs
- **Anvil Forum:** https://anvil.works/forum

---

**Deployment Complete! 🎉 Your app is ready to help users plan their Memphis weekends!**

