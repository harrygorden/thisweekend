# This Weekend - Setup & Deployment Guide

Complete guide for setting up and deploying the This Weekend Memphis Event Planner.

## Prerequisites

- **Anvil Account:** Sign up at [anvil.works](https://anvil.works)
- **GitHub Account:** For version control
- **API Keys:**
  - [OpenWeather API](https://openweathermap.org/api) (One Call API 3.0)
  - [Firecrawl API](https://firecrawl.dev)
  - [OpenAI API](https://openai.com)

---

## Quick Setup (15 minutes)

### Step 1: Create Anvil App

1. Log into [Anvil](https://anvil.works)
2. Click **"Create New App"**
3. Choose **"Blank App"**
4. Name it: `ThisWeekend`

### Step 2: Connect to GitHub

1. Click **Settings** (gear icon) → **Version Control**
2. Click **"Connect to GitHub"**
3. Authorize Anvil
4. Create repository: `thisweekend`
5. Click **"Connect"**

### Step 3: Push Your Code

```bash
cd thisweekend
git init
git remote add origin https://github.com/YOUR_USERNAME/thisweekend.git
git add .
git commit -m "Initial commit"
git push -u origin master
```

### Step 4: Pull into Anvil

1. In Anvil editor: **Version Control** panel (clock icon)
2. Click **"Pull from Git"**
3. Code appears in Anvil

### Step 5: Install Dependencies

1. **Settings** → **Python Environment**
2. Add packages:
   - `firecrawl-py`
   - `openai`

### Step 6: Configure API Keys

1. **Settings** → **Secrets**
2. Add three secrets:
   - `OPENWEATHER_API_KEY`
   - `FIRECRAWL_API_KEY`
   - `OPENAI_API_KEY`

### Step 7: Create Data Tables

1. Click **"Data Tables"** in left sidebar (database icon)
2. Create 3 tables with **ANY** column (we'll auto-create the rest):
   - `events`
   - `weather_forecast`
   - `scrape_log`

### Step 8: Set Startup Form

1. Click **Settings** → **Startup Form**
2. Select `AdminForm`

### Step 9: Run & Setup Database

1. Click **Run** ▶️
2. AdminForm loads
3. Click **"Setup Database"** button
4. All 33 columns created automatically! ✅

**Done!** Your app is ready to use.

---

## Admin Access (Optional)

If you want to protect the admin panel:

### Add Simple Authentication

1. In Anvil: **Services** → **+** → **Users**
2. **Settings** → Enable email/password
3. Click **"View Users"** → **Add User**
4. Create admin account

### Update AdminForm

At the top of `AdminForm/__init__.py`:

```python
def __init__(self, **properties):
    # Check if user is logged in
    if not anvil.users.get_user():
        alert("Please log in to access admin panel")
        anvil.users.login_with_form()
        if not anvil.users.get_user():
            return  # User cancelled login
    
    # Rest of initialization...
```

Now users must log in to access admin panel.

---

## Testing Your Setup

### Test 1: API Keys

1. In AdminForm, click **"Test API Keys"**
2. All three should show as configured ✅

### Test 2: OpenWeather

1. Click **"Test OpenWeather"**
2. Should return 3 days of weather ✅

### Test 3: OpenAI

1. Click **"Test OpenAI"**
2. Should analyze a sample event ✅

### Test 4: Firecrawl

1. Click **"Test Firecrawl"**
2. Should successfully connect ✅

### Test 5: Full Refresh

1. Click **"Refresh Data"**
2. Wait 2-5 minutes
3. Should scrape events, analyze with AI, and calculate scores ✅

---

## Troubleshooting

### "Module not found" errors

**Solution:** Install dependencies in Settings → Python Environment

### "Secret not found" errors

**Solution:** Add API keys in Settings → Secrets

### Designer files missing

**Solution:** Open each form in visual designer:
1. Click on `AdminForm` in sidebar
2. Click on `MainApp` in sidebar
3. Click on `EventCard` in sidebar
4. Click on `WeatherCard` in sidebar

Anvil will auto-generate `_anvil_designer.py` files.

### Database columns missing

**Solution:** Click "Setup Database" button in AdminForm

### "Table not found" errors

**Solution:** Create the 3 tables in Data Tables section

---

## Deployment to Production

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

## Environment Setup

### Development Environment

1. **Settings** → **Environments**
2. Create "Development" environment
3. Use for testing (won't run scheduled tasks)

### Production Environment

1. Create "Production" environment
2. Enable "Run scheduled tasks"
3. Use for live app

---

## Next Steps

After setup:

1. ✅ **Set up scheduled tasks** (see [SCHEDULED_TASKS.md](SCHEDULED_TASKS.md))
2. ✅ **Test data refresh** from AdminForm
3. ✅ **Check user interface** (open MainApp)
4. ✅ **Monitor App Logs** (Tools → App Logs)

---

## File Structure

```
thisweekend/
├── server_code/           # Backend Python modules
│   ├── background_tasks.py  # Scheduled tasks
│   ├── weather_service.py   # Weather API
│   ├── scraper_service.py   # Event scraping
│   ├── ai_service.py        # OpenAI integration
│   ├── data_processor.py    # Recommendation engine
│   ├── admin_tools.py       # Admin utilities
│   ├── setup_schema.py      # Database setup
│   └── requirements.txt     # Dependencies
├── client_code/           # Frontend Anvil forms
│   ├── AdminForm/          # Admin panel
│   ├── MainApp/            # Main user interface
│   ├── EventCard/          # Event component
│   └── WeatherCard/        # Weather component
└── *.md                   # Documentation
```

---

## Database Schema

### `events` Table (17 columns)
Stores scraped and AI-analyzed events.

### `weather_forecast` Table (9 columns)
Caches weekend weather forecasts.

### `scrape_log` Table (7 columns)
Tracks background task execution.

**Setup:** Click "Setup Database" in AdminForm to create all columns automatically.

---

## API Requirements

### OpenWeather API
- **Plan:** One Call API 3.0 (subscription required)
- **Cost:** ~$0.02/week
- **Calls:** 1 per data refresh

### Firecrawl API
- **Plan:** Paid (starts at $10/month for 500 credits)
- **Cost:** ~1 credit per scrape
- **Calls:** 1 per data refresh

### OpenAI API
- **Plan:** Pay-as-you-go
- **Cost:** ~$0.20-0.40 per refresh (depends on event count)
- **Models:** GPT-4.1-mini (analysis) + GPT-4.1 (user-facing text)

**Total:** ~$0.50 per full refresh, ~$2.00/month with weekly schedule

---

## Support

- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Scheduled Tasks:** [SCHEDULED_TASKS.md](SCHEDULED_TASKS.md)
- **Anvil Docs:** https://anvil.works/docs
- **Forum:** https://anvil.works/forum

---

**Setup complete! 🎉 Your app is ready to plan weekends!**

