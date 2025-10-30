# 🧪 API Test Buttons - User Guide

## ✨ What I Just Added

**3 new API test buttons** to AdminForm with full diagnostic capabilities!

### New Buttons Section: "API Testing"

Located between the main action buttons and secondary buttons:

```
┌─────────────────────────────────────────┐
│ API Testing 🔌                          │
├─────────────────────────────────────────┤
│ [Test Weather API] [Test Firecrawl API] │
│ [Test OpenAI API]                        │
└─────────────────────────────────────────┘
```

## 🚀 How to Use

### Step 1: Pull from Git

1. Open Anvil
2. Click **"Pull from Git"**
3. AdminForm will update with new buttons

### Step 2: Test Each API

#### Test 1: OpenWeather API ☁️

**Button:** "Test Weather API"

**What it does:**
- Fetches Memphis weather for Friday, Saturday, Sunday
- Shows temperatures, conditions, rain chance
- Displays hourly forecast count

**Expected output:**
```
==================================================
OPENWEATHER API TEST
==================================================

✅ SUCCESS! Fetched weather for 3 days

Friday (2025-11-01):
  High: 75°F, Low: 55°F
  Conditions: Partly cloudy
  Rain chance: 20%
  Wind: 10 mph
  Hourly forecasts: 24 hours

(Saturday and Sunday follow...)
```

#### Test 2: Firecrawl API 🐛

**Button:** "Test Firecrawl API"

**What it does:**
- Tests 3 different scenarios
- Tests known-good URL (firecrawl.dev)
- Tests target URL without stealth
- Tests target URL WITH stealth mode
- Takes 30-60 seconds to run

**Expected output:**
```
==================================================
FIRECRAWL API CONNECTION TEST
==================================================

API Key Configured: True
API Key: fc-c4dfba3...b123

TEST RESULTS:
--------------------------------------------------

TEST_URL:
  Status: ✅ PASS
  URL: https://firecrawl.dev
  Stealth: False
  ✅ Markdown size: 15000 chars
  ✅ Page title: Firecrawl

TARGET_NO_STEALTH:
  Status: ❌ FAIL
  URL: https://ilovememphisblog.com/weekend
  Stealth: False
  ❌ Error: URL must have a valid top-level domain
  ❌ Error code: BAD_REQUEST

TARGET_WITH_STEALTH:
  Status: ✅ PASS or ❌ FAIL
  URL: https://ilovememphisblog.com/weekend
  Stealth: True
  (Results show if stealth mode works!)

==================================================
SUMMARY: 1/3 or 2/3 or 3/3 tests passed
==================================================
```

**This tells us:**
- If API key is valid (test 1)
- If stealth mode works (test 3)
- What the exact error is

#### Test 3: OpenAI API 🤖

**Button:** "Test OpenAI API"

**What it does:**
- Sends a test event to ChatGPT
- Asks it to categorize the event
- Shows AI analysis results

**Expected output:**
```
==================================================
OPENAI API TEST
==================================================

✅ SUCCESS! ChatGPT API is working

Test Event:
  Title: Live Jazz Concert at Overton Park

AI Analysis Results:
  Indoor: False
  Outdoor: True
  Audience: all-ages
  Cost level: $$
  Categories: Music, Outdoor Activities

==================================================
OpenAI API is configured correctly!
==================================================
```

## 📊 Interpreting Results

### All 3 APIs Work ✅
```
✅ OpenWeather: Working
✅ Firecrawl: Working (with stealth)
✅ OpenAI: Working
```
**Action:** Run full data refresh - everything should work!

### Weather + OpenAI Work, Firecrawl Fails ⚠️
```
✅ OpenWeather: Working
❌ Firecrawl: All tests failed
✅ OpenAI: Working
```
**Action:** 
- Check Firecrawl API key
- Verify plan supports v1/v2
- Use test events or direct scraper

### Only Some APIs Work 🔧
```
✅ OpenWeather: Working
❌ Firecrawl: Stealth mode not available
✅ OpenAI: Working
```
**Action:**
- Upgrade Firecrawl plan for stealth
- Or use alternative scraping

## 🎯 Common Error Messages

### OpenWeather Errors

**"Invalid API key"**
→ Get new key from openweathermap.org

**"API key doesn't have One Call API 3.0 access"**
→ Subscribe to One Call API 3.0 (~$3/1000 calls)

**"Rate limit exceeded"**
→ Wait or upgrade plan

### Firecrawl Errors

**"Invalid API key"**
→ Get new key from firecrawl.dev

**"URL must have a valid top-level domain"**
→ Your plan doesn't allow this URL (we saw this!)

**"Stealth mode requires paid plan"**
→ Upgrade Firecrawl or use alternative

**"Rate limit exceeded"**
→ Wait or upgrade plan

### OpenAI Errors

**"Invalid API key"**
→ Get new key from platform.openai.com

**"Insufficient quota"**
→ Add credits to your OpenAI account

**"Rate limit exceeded"**
→ Wait or upgrade tier

## 🚀 Next Steps

### After Pulling from Git:

**Your AdminForm will have:**

**Main Actions:**
1. Setup Database
2. Test API Keys (shows if keys exist)
3. Health Check
4. Refresh Data

**API Testing:** (NEW!)
- Test Weather API
- Test Firecrawl API
- Test OpenAI API

**Secondary:**
- Check DB Status
- View Refresh Log
- Refresh Status
- Clear All Data

## 💡 Test Workflow

**Do this in order:**

1. **"Test Weather API"** 
   - Should work (we know it does!)
   - Confirms OpenWeather is good

2. **"Test OpenAI API"**
   - Should work if key is valid
   - Confirms ChatGPT access

3. **"Test Firecrawl API"**
   - Shows exactly what works/doesn't
   - Takes 30-60 seconds
   - Gives detailed error info

4. **Based on results:**
   - All pass → Run "Refresh Data"
   - Some fail → Fix those APIs
   - Firecrawl fails → Use test events or alternative

## 📋 What to Share With Me

After clicking **"Test Firecrawl API"**, send me:

1. **Summary line:**
   - "SUMMARY: X/3 tests passed"

2. **For each failed test:**
   - Error message
   - Error code
   - Which test failed

Example:
```
TEST_URL: ✅ PASS
TARGET_NO_STEALTH: ❌ FAIL - URL must have a valid top-level domain
TARGET_WITH_STEALTH: ❌ FAIL - Stealth mode requires paid plan
```

Then I'll know exactly what solution to implement!

---

## 🎉 Ready to Test!

**In Anvil:**
1. **"Pull from Git"**
2. You'll see the new "API Testing" section
3. Click each test button
4. See immediate results!

**This will definitively show us:**
- ✅ Which APIs work
- ❌ Which APIs have issues
- 🔧 Exact errors to fix

---

**Pull from Git now and test the APIs!** The buttons are ready and will give you complete diagnostic information. 🔍

