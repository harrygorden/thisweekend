# 🔍 Firecrawl Debugging Guide

## What We Know

✅ **Weather API:** Working perfectly  
⚠️ **Firecrawl API:** Getting HTTP 400 error  
❓ **Cause:** Unknown (need error details)

## 🔧 What I Just Fixed

### Enhanced Error Reporting

The scraper now captures the **full error response** from Firecrawl, including:
- Exact error message
- Error code
- Request details
- API key verification

**Reference:** According to [Firecrawl documentation](https://docs.firecrawl.dev/features/scrape), the v2 endpoint format is:

```json
{
  "url": "https://example.com",
  "formats": ["markdown", "html"]
}
```

Which is what we're using, so the error must be something else.

## 🚀 Next Steps

### Step 1: Push the Enhanced Error Handler

```bash
git add server_code/
git commit -m "Add detailed Firecrawl error reporting and direct scraper backup"
git push origin main
```

### Step 2: Pull and Test

1. In Anvil: **"Pull from Git"**
2. Click **"4. Refresh Data"**
3. **Watch Server Logs carefully**

### Step 3: Look for This in Logs

```
Making request to https://api.firecrawl.dev/v2/scrape
Payload: {'url': '...', 'formats': ['markdown', 'html']}
API Key (first 10 chars): fc-1234567...

Firecrawl error response: {
  "success": false,
  "error": "ACTUAL ERROR MESSAGE HERE",  ← THIS IS WHAT WE NEED!
  "code": "error_code"
}
```

### Step 4: Send Me the Error

Once you see the actual error message, send me:
- The error message
- The error code
- Any other details in the response

Then I can fix it precisely!

## 🔄 Alternative: Direct Scraper (Backup Ready!)

I've also created **`server_code/scraper_direct.py`** as a backup option.

This scraper:
- ✅ No API needed (free!)
- ✅ Direct HTTP to website
- ✅ Simple HTML parsing
- ✅ Ready to use immediately

### Test Direct Scraper

Add this test button to AdminForm:

```python
def test_direct_scraper_button_click(self, **event_args):
    import server_code.scraper_direct as direct
    
    try:
        result = anvil.server.call('test_direct_scraping')
        
        if result['success']:
            self.status_output.text = (
                f"✅ Direct scraping works!\n\n"
                f"Text extracted: {result['text_length']} chars\n"
                f"Events found: {result['events_found']}\n\n"
                f"Sample events:\n"
                f"{result['sample_events']}"
            )
        else:
            self.status_output.text = f"❌ Error: {result['error']}"
            
    except Exception as e:
        self.status_output.text = f"❌ {str(e)}"
```

## 📊 Comparison: Firecrawl vs Direct

| Feature | Firecrawl API | Direct Scraper |
|---------|---------------|----------------|
| Cost | Paid API | Free |
| Reliability | High (when working) | Medium |
| Clean markdown | ✅ Excellent | ⚠️ Basic |
| JS rendering | ✅ Yes | ❌ No |
| Rate limits | API limits | None |
| Dependencies | API key needed | None |
| Setup | Complex | Simple |
| Maintenance | Low | Medium (fragile) |

## 🎯 Decision Tree

```
Is Firecrawl API accessible?
    ├─ YES → Fix the 400 error (we'll see details soon)
    │         └─ Keep using Firecrawl (best option)
    │
    └─ NO → Use direct scraper
              ├─ Works well enough? → Use it!
              ├─ Not good enough? → Try alternative API
              └─ Want both? → Use direct as fallback
```

## 🔍 Common 400 Error Causes

Based on the [Firecrawl API documentation](https://docs.firecrawl.dev/features/scrape):

### 1. API Key Issues (Most Common)
- Key doesn't have v2 access
- Free tier limitation
- Key expired or revoked

**Check:**
- Log into firecrawl.dev dashboard
- Verify plan includes v2 API
- Check usage limits

### 2. Request Format
- Missing required fields
- Wrong parameter types
- Invalid URL format

**Our payload looks correct:**
```python
{
  "url": "https://ilovememphisblog.com/weekend",
  "formats": ["markdown", "html"]
}
```

### 3. URL Restrictions
- Some URLs require stealth mode
- Anti-scraping protection
- Geographic restrictions

**Solution:** Try with `stealth: true` parameter

### 4. Plan Limitations
- Free tier might not support all URLs
- Need paid plan for certain features
- Monthly quota exceeded

**Check:** Firecrawl dashboard usage page

## 🛠️ Fixes to Try (In Order)

### Fix 1: Add Stealth Mode

```python
payload = {
    "url": config.TARGET_WEBSITE_URL,
    "formats": ["markdown", "html"],
    "stealth": True  # Enable anti-bot bypass
}
```

### Fix 2: Add Location

```python
payload = {
    "url": config.TARGET_WEBSITE_URL,
    "formats": ["markdown"],
    "location": {
        "country": "US"
    }
}
```

### Fix 3: Try Simpler Formats

```python
payload = {
    "url": config.TARGET_WEBSITE_URL,
    "formats": ["markdown"]  # Just one format
}
```

### Fix 4: Use Direct Scraper

```python
# In scraper_service.py
from . import scraper_direct

def scrape_weekend_events():
    try:
        # Try Firecrawl first
        return scrape_firecrawl()
    except:
        # Fall back to direct scraping
        return scraper_direct.scrape_weekend_events_direct()
```

## 📝 Action Plan

**Right Now:**
1. Push the enhanced error handler
2. Run refresh again
3. Send me the **actual error message**
4. I'll create a precise fix

**Backup Plan:**
1. Test direct scraper
2. If it works, use it as fallback
3. Keep trying to fix Firecrawl

**Ultimate Goal:**
- Get events into database (by any means)
- Firecrawl is preferred but not required
- Direct scraper works as backup

## 🎯 What We Need

**To fix Firecrawl:** The actual error response  
**To use direct scraper:** Test if website allows it  
**To proceed:** Either one working is fine!

---

**Push the code and run the test.** We'll see the exact Firecrawl error and fix it immediately! 🚀

If Firecrawl's error suggests we need a different plan or the website blocks it, we'll switch to the direct scraper which is already built and waiting.

