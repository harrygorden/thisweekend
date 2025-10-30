# 🚨 Firecrawl API Key Issue Detected

## Critical Finding

**ALL 3 Firecrawl tests failed** - even the known-good URL (`firecrawl.dev`)!

```
TEST_URL (firecrawl.dev): ❌ FAIL - HTTP 400
TARGET_NO_STEALTH: ❌ FAIL - HTTP 400
TARGET_WITH_STEALTH: ❌ FAIL - HTTP 400
```

## What This Means

Since even `https://firecrawl.dev` (Firecrawl's own website) fails, the problem is NOT:
- ❌ Not the target URL
- ❌ Not Cloudflare protection
- ❌ Not stealth mode availability

The problem IS most likely:
- ⚠️ **API key is invalid or inactive**
- ⚠️ **API key is for v0 only** (not v1/v2)
- ⚠️ **API key format is wrong**
- ⚠️ **No Firecrawl subscription**

## 🔍 Diagnosis

Your API key: `fc-c4dfba3...a8c2`

### Possible Issues:

**1. API Key Invalid/Revoked**
- Key was deleted or expired
- Account suspended
- Wrong key copied

**2. API Key is v0 Only**
- Old Firecrawl accounts use v0 endpoint
- v1/v2 weren't available on older plans
- Need to regenerate key or upgrade

**3. No Active Subscription**
- Free trial ended
- Payment failed
- Account not activated

## ✅ How to Fix

### Step 1: Verify API Key

1. Log into **https://firecrawl.dev**
2. Go to **API Keys** section
3. Check if the key is **active**
4. Check which **API version** it supports
5. Note if it says "v0 only" or "v1/v2 compatible"

### Step 2: Generate New Key (If Needed)

1. In Firecrawl dashboard
2. Click **"Generate New API Key"**
3. Copy the new key
4. Update in Anvil Secrets

### Step 3: Check Your Plan

1. In Firecrawl dashboard → **Billing**
2. Check if you have an **active subscription**
3. Check which **features** are included
4. Verify **API version access** (v0 vs v1/v2)

### Step 4: Test with cURL (Outside Anvil)

Test your API key directly:

```bash
curl -X POST https://api.firecrawl.dev/v2/scrape \
  -H 'Authorization: Bearer YOUR_ACTUAL_KEY_HERE' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://firecrawl.dev",
    "formats": ["markdown"]
  }'
```

**If this works:** Anvil is doing something wrong  
**If this fails:** API key issue confirmed

## 🔄 Alternative: Try v0 Endpoint

Your API key might only work with the older v0 endpoint.

I've created a test for this: `test_firecrawl_v0_endpoint()`

### Test v0 in Anvil Console:

```python
import server_code.firecrawl_diagnostics as diag
result = diag.test_firecrawl_v0_endpoint()
print(result)
```

**If v0 works:**
- Update main scraper to use v0
- Or request v1/v2 access from Firecrawl

## 💡 Most Likely Scenario

Based on all 3 tests failing identically:

**Your Firecrawl API key is either:**
1. **Invalid/inactive** (most likely)
2. **v0 only** (common for older accounts)
3. **Free trial expired** (check billing)

## 🎯 Immediate Actions

### Action 1: Check Firecrawl Dashboard

Log into firecrawl.dev and verify:
- ✅ API key is active
- ✅ Subscription is active  
- ✅ Which API versions you have access to

### Action 2: Regenerate API Key

If key looks suspicious:
1. Delete old key
2. Generate new key
3. Update in Anvil Secrets (`FIRECRAWL_API_KEY`)
4. Test again

### Action 3: Test v0 Endpoint

Run in Anvil console:
```python
import server_code.firecrawl_diagnostics as diag
diag.test_firecrawl_v0_endpoint()
```

### Action 4: Contact Firecrawl Support

If nothing works:
- Email support@firecrawl.dev
- Include: "All API calls return HTTP 400, even for firecrawl.dev"
- They can check your account status

## 🔄 Meanwhile: Alternative Solutions

While debugging Firecrawl, you can:

### Option A: Use Test Events (Immediate)
```python
# In AdminForm, add button:
anvil.server.call('create_test_events')
```
- ✅ 14 realistic events
- ✅ Works immediately
- ✅ Test complete app

### Option B: Switch to Different Service

I can integrate:
- **ScraperAPI** ($30/mo, handles Cloudflare)
- **Bright Data** (enterprise)
- **ScrapingBee** (Cloudflare bypass built-in)

### Option C: Build Manual Entry Form

I can create a quick admin form to manually enter events:
- Takes 10-15 minutes weekly
- Full control
- No API needed
- Free forever

## 📋 Summary

**Issue:** Firecrawl API key appears invalid or incompatible  
**Evidence:** Even firecrawl.dev fails (should always work)  
**Action Needed:** Check Firecrawl dashboard, regenerate key, or use alternative  

**Workarounds Available:**
1. ✅ Test events (ready now)
2. ✅ Alternative scraping service (I can integrate)
3. ✅ Manual entry form (I can build)

---

**Check your Firecrawl dashboard and send me what you find!** Meanwhile, the app works with test events or other APIs.

