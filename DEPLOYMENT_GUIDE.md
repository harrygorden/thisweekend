# This Weekend - Deployment Guide

Complete guide for deploying the This Weekend Memphis Event Planner application.

## Prerequisites

1. **Anvil Account** - Sign up at [anvil.works](https://anvil.works)
2. **GitHub Account** - For version control
3. **API Keys:**
   - OpenWeather API Key (One Call API 3.0)
   - Firecrawl API Key
   - OpenAI API Key

## Step 1: Create Anvil App

1. Log into Anvil
2. Click **"Create New App"**
3. Choose **"Blank App"**
4. Name it: `ThisWeekend`

## Step 2: Configure Git Integration

1. In Anvil editor, click **Settings** (gear icon)
2. Navigate to **"Version Control"** tab
3. Click **"Connect to GitHub"**
4. Authorize Anvil to access your GitHub
5. Create a new repository: `thisweekend`
6. Click **"Initialize with a single initial commit"**
7. Click **"Connect"**

## Step 3: Push Local Code to GitHub

In your local project directory:

```bash
# Initialize git if not already done
git init

# Add your GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/thisweekend.git

# Add all files
git add .

# Commit
git commit -m "Initial commit - This Weekend app"

# Push to GitHub
git push -u origin master
```

## Step 4: Pull Code into Anvil

1. In Anvil editor, go to **Version Control** panel (clock icon on left)
2. Click **"Pull from Git"**
3. Anvil will download all your server code and client forms
4. You should see:
   - `server_code/` folder with all Python modules
   - `client_code/AdminForm/` folder with admin interface

## Step 5: Install Python Dependencies

1. In Anvil editor, click **Settings** (gear icon)
2. Navigate to **"Python Environment"** tab
3. Add these packages:
   ```
   firecrawl-py
   openai
   ```
4. Click **"Add"** for each package
5. Wait for installation to complete

## Step 6: Configure API Keys

1. In Anvil editor, click **Settings** (gear icon)
2. Navigate to **"Secrets"** tab
3. Add these secrets:
   - **Name:** `OPENWEATHER_API_KEY`  
     **Value:** Your OpenWeather API key
   - **Name:** `FIRECRAWL_API_KEY`  
     **Value:** Your Firecrawl API key
   - **Name:** `OPENAI_API_KEY`  
     **Value:** Your OpenAI API key
4. Click **"Add"** for each secret

## Step 7: Create Data Tables

1. In Anvil editor, click **Data Tables** icon (database icon on left)
2. Click **"Add Table"**
3. Create three tables with these **exact names**:
   - `events`
   - `weather_forecast`
   - `scrape_log`
4. Leave all tables empty (no columns yet)

> **Note:** The AdminForm will automatically create all required columns when you run the setup.

## Step 8: Set Startup Form

1. In Anvil editor, in the **Forms** panel (left side)
2. Right-click on **AdminForm**
3. Select **"Set as Startup Form"**

## Step 9: Run Database Setup

1. Click the **Run** button (▶️ at top)
2. Your app will open in a new browser tab
3. You'll see the AdminForm interface
4. Click the **"Setup Database"** button
5. Wait for setup to complete (creates all 33 columns automatically)
6. You should see: "✅ Setup complete!"

## Step 10: Test API Connections

In the AdminForm interface:

1. Click **"Test API Keys"** - Verify all keys are configured
2. Click **"Test OpenWeather API"** - Verify weather API works
3. Click **"Test Firecrawl API"** - Verify scraping API works (3 tests)
4. Click **"Test OpenAI API"** - Verify AI analysis works

All tests should pass with ✅ green checkmarks.

## Step 11: Initial Data Load

Choose one of these options:

### Option A: Load Test Events (Recommended for Testing)
1. Click **"Load Test Events"** button
2. This creates 14 realistic sample events
3. Perfect for testing the UI without using API credits

### Option B: Run Full Data Refresh (Production)
1. Click **"Refresh Data"** button
2. This will:
   - Fetch real Memphis weather forecast
   - Scrape events from ilovememphisblog.com
   - Analyze events with AI
   - Calculate recommendations
3. Takes 2-5 minutes
4. Uses API credits

## Step 12: Schedule Automated Updates

1. In Anvil editor, click **Settings** (gear icon)
2. Navigate to **"Background Tasks"** tab
3. Click **"Add a new task"**
4. Configure:
   - **Function:** `server_code.background_tasks.scheduled_refresh_all_data`
   - **Schedule:** Weekly (e.g., every Thursday at 6 PM)
   - **Enabled:** ✅ Yes
5. Click **"Save"**

## Deployment Complete! 🎉

Your app is now running on Anvil's development server.

## Publishing (Optional)

To publish your app with a custom domain:

1. In Anvil editor, click **Publish** (top right)
2. Choose a deployment option:
   - **Free Anvil subdomain:** `yourapp.anvil.app`
   - **Custom domain:** Requires paid Anvil plan
3. Click **"Publish This App"**
4. Your app is now live!

## Monitoring & Maintenance

### Check Health
- Click **"Health Check"** in AdminForm regularly
- Review any warnings or errors

### View Logs
- Click **"View Refresh Log"** to see data refresh history
- Monitor for scraping or API failures

### Clear Old Data
- Data is automatically cleaned up (7-day retention by default)
- Manual cleanup: **"Clear All Data"** button (use carefully!)

## Troubleshooting

### API Key Issues
- Verify secrets are spelled exactly: `OPENWEATHER_API_KEY`, `FIRECRAWL_API_KEY`, `OPENAI_API_KEY`
- Check for trailing spaces in secret values
- Test each API individually using test buttons

### Scraping Failures
- Firecrawl may fail if website structure changes
- Fallback: Use **"Load Test Events"** button temporarily
- Check Firecrawl API dashboard for rate limits

### Database Issues
- Re-run **"Setup Database"** button if columns are missing
- Check **"Check Status"** button for missing columns

### Background Task Failures
- Check Anvil background task logs in Settings → Background Tasks
- Common cause: API rate limits or invalid keys
- Manually trigger: Click **"Refresh Data"** button in AdminForm

## Cost Management

### API Usage Per Week (approx.)
- **OpenWeather:** ~$0.02 (3 API calls)
- **Firecrawl:** Varies by plan (50-100 scrape calls)
- **OpenAI:** ~$0.05-$0.75 (50 event analyses)

### Optimization Tips
1. Use **"Test Scraping Only"** to debug without OpenAI costs
2. Schedule refreshes weekly, not daily
3. Monitor usage in each API provider's dashboard

## Support

For issues or questions:
1. Check the **USER_GUIDE.md** for usage instructions
2. Review error messages in AdminForm output
3. Check Anvil server logs (View → Server Logs)
4. Open an issue in the GitHub repository

---

**Ready to use!** Start by running a data refresh or loading test events, then explore the event display (Form1 - coming soon in Phase 6).

