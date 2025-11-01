# Scheduled Tasks Guide

Automated background tasks for keeping your This Weekend app fresh and current.

## Overview

Your app has **3 background tasks** available for Anvil Scheduled Tasks:

| Task | Purpose | Duration | Cost | Schedule |
|------|---------|----------|------|----------|
| `scheduled_refresh_all_data` | Full refresh with scraping | 2-5 min | $0.30 | Weekly |
| `scheduled_refresh_weather_and_scores` | Update weather only | 10-30 sec | FREE | Daily |
| `scheduled_clear_all_data` | Clear all data | < 30 sec | FREE | Manual |

---

## Quick Setup (3 minutes)

### Prerequisites

- ✅ Anvil app is **published**
- ✅ You have a **paid Anvil plan** (Hobby or above)
- ✅ All API keys configured

### Add Scheduled Tasks

1. **In Anvil Editor:**
   - Click **+** in sidebar
   - Select **Scheduled Tasks** service
   - Click **Add**

2. **Add Weekly Full Refresh:**
   - Click **+ Add task**
   - Task: `scheduled_refresh_all_data`
   - Every: `1 week`
   - Day: `Monday`
   - Time: `06:00 UTC`
   - Click **Add**

3. **Add Daily Weather Update:**
   - Click **+ Add task**
   - Task: `scheduled_refresh_weather_and_scores`
   - Every: `1 day`
   - Time: `06:00 UTC`
   - Click **Add**

**Done!** Your app will auto-update weekly (events) and daily (weather).

---

## Task Details

### Task 1: `scheduled_refresh_all_data`

**Full comprehensive refresh**

**What it does:**
1. Cleans up old/past events
2. Fetches Memphis weather forecast (3 days)
3. Scrapes ilovememphisblog.com/weekend (Firecrawl)
4. Parses event details
5. Filters out past events
6. Saves events to database
7. Analyzes events with AI (OpenAI) - categories, audience, indoor/outdoor
8. Matches events with weather
9. Calculates recommendation scores
10. Logs completion

**When to use:** Weekly event updates

**Output example:**
```
🚀 BACKGROUND TASK STARTED
[1/10] Cleanup...
  ✓ Done
[2/10] Weather...
  ✓ 3 days
...
[10/10] Calculate scores...
  ✓ Done

✅ Data refresh completed successfully!
Duration: 187.3 seconds
Events found: 38
Events analyzed: 38
```

### Task 2: `scheduled_refresh_weather_and_scores`

**Lightweight weather-only refresh**

**What it does:**
1. Deletes old weather data
2. Fetches fresh weather forecast (OpenWeather)
3. Saves weather to database
4. Re-matches all events with updated weather
5. Recalculates recommendation scores

**When to use:** Daily weather updates (forecasts change frequently)

**Output example:**
```
🌤️ SCHEDULED WEATHER & SCORES REFRESH - STARTING
[1/5] Clearing old weather data...
  ✓ Deleted 3 old weather forecasts
[2/5] Fetching fresh weather forecast...
  ✓ Retrieved 3 days of weather
...
[5/5] Recalculating recommendation scores...
  ✓ Updated 42 recommendation scores

✅ WEATHER & SCORES REFRESH - COMPLETED
Duration: 12.3 seconds
```

### Task 3: `scheduled_clear_all_data`

**Database cleanup (use with caution)**

**What it does:**
1. Deletes all events
2. Deletes all weather forecasts
3. Deletes all scrape logs

**When to use:** Manual cleanup only (not recommended for scheduling)

---

## Recommended Schedules

### Option 1: Weekly + Daily (Recommended) ⭐

**Best for:** Fresh data, minimal cost

```
Weekly Full Refresh:
  Task: scheduled_refresh_all_data
  Every: 1 week on Monday at 06:00 UTC
  Cost: $1.20/month

Daily Weather Update:
  Task: scheduled_refresh_weather_and_scores
  Every: 1 day at 06:00 UTC
  Cost: FREE

Total: $1.20/month
Weather freshness: < 1 day old
```

**Why this works:**
- Events don't change often → weekly is fine
- Weather changes daily → daily updates needed
- Same cost as weekly-only, but fresher data!

### Option 2: Weekly Only (Budget)

```
Task: scheduled_refresh_all_data
Every: 1 week on Monday at 06:00 UTC
Cost: $1.20/month
Weather freshness: Up to 7 days old
```

**Trade-off:** Lower cost, but stale weather forecasts

### Option 3: Frequent Weather (Aggressive)

```
Full Refresh: Weekly (Monday 06:00 UTC)
Weather Refresh: Every 6 hours
Total Cost: $1.20/month (same!)
Weather freshness: < 6 hours old
```

**Best for:** Maximum accuracy with frequently changing weather

---

## Cost Breakdown

### Per-Task Costs

| Task | Firecrawl | OpenAI | OpenWeather | Total |
|------|-----------|--------|-------------|-------|
| Full Refresh | $0.10 | $0.20 | FREE | $0.30 |
| Weather Only | $0.00 | $0.00 | FREE | $0.00 |
| Clear Data | $0.00 | $0.00 | $0.00 | $0.00 |

### Monthly Costs (Recommended Setup)

```
Weekly Full Refresh:
  4 runs/month × $0.30 = $1.20

Daily Weather Refresh:
  30 runs/month × $0.00 = $0.00

Total: $1.20/month
```

**Note:** OpenWeather free tier includes 1,000 calls/day - more than enough!

---

## Manual Testing

Test tasks before scheduling:

### From Admin Panel

**Full Refresh:**
1. Open AdminForm
2. Click "Refresh Data"
3. Wait 2-5 minutes
4. Check results

**Weather Only:**
Add a "Refresh Weather" button that calls:
```python
anvil.server.call('trigger_weather_refresh')
```

### From Python

```python
# Full refresh
anvil.server.launch_background_task('scheduled_refresh_all_data')

# Weather only
anvil.server.launch_background_task('scheduled_refresh_weather_and_scores')

# Clear data (careful!)
anvil.server.launch_background_task('scheduled_clear_all_data')
```

---

## Monitoring

### In Anvil Editor

**Background Tasks:**
- Tools → Background Tasks
- See all running/completed tasks
- Click task for details

**App Logs:**
- Tools → App Logs
- Filter by date
- Look for emoji indicators:
  - 🚀 = Full refresh
  - 🌤️ = Weather refresh
  - 🗑️ = Clear data
  - ✅ = Success
  - ❌ = Error

### In Your App

**Admin Panel:**
- "View Refresh Log" - See history
- "System Info" - Check last refresh time
- Status output - Real-time progress

---

## Troubleshooting

### Tasks don't appear in dropdown

**Check:**
- [ ] App is published (not in development)
- [ ] Scheduled Tasks service is added
- [ ] No syntax errors in `background_tasks.py`
- [ ] Refresh browser

### Task doesn't run on schedule

**Check:**
- [ ] App is published
- [ ] You have paid Anvil plan
- [ ] Environment has "Run scheduled tasks" enabled
- [ ] Time is in UTC (not local time)
- [ ] Task configuration is saved

### Full refresh fails

**Check:**
- [ ] Firecrawl API key is valid and has credits
- [ ] OpenAI API key is valid
- [ ] OpenWeather API key is valid
- [ ] Website (ilovememphisblog.com) is accessible

### Weather refresh fails

**Check:**
- [ ] OpenWeather API key is valid
- [ ] Events exist in database (run full refresh first)
- [ ] Database tables are set up correctly

### Scores don't update

**Check:**
- [ ] Events have valid dates
- [ ] Weather data was fetched successfully
- [ ] Task completed without errors in App Logs

---

## Environment Configuration

### Production Environment

1. **Settings** → **Environments**
2. Select **Production**
3. Click **Show advanced settings**
4. Enable ✓ **Run scheduled tasks**

### Development Environment

1. Select **Development**
2. **Disable** "Run scheduled tasks"
3. Use manual refresh for testing

This prevents double-runs and wasted API credits.

---

## Task Comparison Table

| Feature | Full Refresh | Weather Only | Clear Data |
|---------|--------------|--------------|------------|
| Scrapes Events | ✅ | ❌ | ❌ |
| Uses AI | ✅ | ❌ | ❌ |
| Updates Weather | ✅ | ✅ | ❌ |
| Updates Scores | ✅ | ✅ | ❌ |
| Updates Events | ✅ | ❌ | ❌ |
| Deletes Data | Old only | Old weather | Everything |
| Safe for Daily Use | ❌ ($$$) | ✅ (FREE) | ❌ |

---

## Best Practices

1. **Start conservative:** Weekly full + daily weather
2. **Monitor costs:** Check API usage dashboards monthly
3. **Test manually first:** Verify tasks work before scheduling
4. **Environment-specific:**
   - Production: Enable scheduled tasks
   - Development: Manual only
5. **Review logs:** Check weekly for failures
6. **Adjust as needed:** Change frequency based on event calendar updates

---

## Quick Reference

### Task Names (Copy-Paste)

```
scheduled_refresh_all_data
scheduled_refresh_weather_and_scores
scheduled_clear_all_data
```

### Recommended Configuration

```yaml
Production Environment:
  Task 1: scheduled_refresh_all_data
    - Every 1 week on Monday at 06:00 UTC
  
  Task 2: scheduled_refresh_weather_and_scores
    - Every 1 day at 06:00 UTC
```

---

## FAQs

**Q: Why not scrape daily?**  
A: Events don't change that often. Weekly is sufficient and saves $6-9/month.

**Q: Why update weather daily?**  
A: Weather forecasts change frequently. Daily updates keep recommendations accurate at zero cost.

**Q: Can I run weather updates more than daily?**  
A: Yes! OpenWeather free tier supports up to 1,000 calls/day. Update every 6 hours if you want.

**Q: What happens if a task fails?**  
A: Check App Logs for error details. Task will retry next scheduled time. Fix the issue (usually API key/credits).

**Q: Can I pause scheduled tasks?**  
A: Yes. In Scheduled Tasks tab, click task and delete it. You can re-add later.

**Q: Will tasks run in development?**  
A: Only if you enable "Run scheduled tasks" for development environment. Not recommended.

---

## Support

- **Setup Guide:** [SETUP.md](SETUP.md)
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Anvil Docs:** https://anvil.works/docs/background-tasks
- **Forum:** https://anvil.works/forum

---

**Ready to automate? Add your scheduled tasks and enjoy always-fresh weekend plans! 🎉**

