# 🧪 Local Scraping Test Guide

## Purpose

Test if `https://ilovememphisblog.com/weekend` can be scraped from your local computer to determine if the website is blocking Anvil's servers.

## Quick Start

### Step 1: Install Dependencies

```bash
pip install requests beautifulsoup4
```

### Step 2: Run Test Script

```bash
python test_scraping_local.py
```

### Step 3: Check Results

The script will:
- ✅ Test HTTP access to the website
- ✅ Download the HTML
- ✅ Extract text content
- ✅ Detect possible events
- ✅ Save 4 files for inspection
- ✅ Test with different user agents

## 📊 What to Expect

### If Scraping WORKS Locally:

```
✅ SUCCESS! Website is accessible from your computer.
  ✅ Downloaded 45000 characters
  ✅ Found 42 potential event entries
  
Files Created:
  • scraped_page.html - Raw HTML
  • scraped_text.txt - Extracted text
  • possible_events.txt - Detected events
```

**Interpretation:**
- Website is NOT blocking general access
- Anvil's direct scraper should work
- If Anvil still fails → Anvil servers are blocked
- Solution: Use proxy or cloud function

### If Scraping FAILS Locally:

```
❌ ERROR: Connection failed
  → Website might be down
  OR
❌ ERROR: Request timed out
  → Website is very slow or blocking
```

**Interpretation:**
- Website has anti-scraping protection
- Might require JavaScript rendering
- Solution: Use Firecrawl with stealth mode or Selenium

## 🔍 Diagnostic Flow

```
Run test_scraping_local.py
        ↓
    SUCCESS?
        ↓
    ┌────┴────┐
  YES         NO
    ↓         ↓
  Works!    Blocked!
    ↓         ↓
  Check     Website
  Anvil     has anti-
  scraper   scraping
    ↓         ↓
  Still     Need JS
  fails?    renderer
    ↓         or proxy
  Anvil
  servers
  blocked
```

## 📁 Files Created

### 1. `scraped_page.html`
Raw HTML from the website. Open in browser to see the page structure.

### 2. `scraped_page_pretty.html`
Formatted HTML with proper indentation. Easier to read and analyze structure.

### 3. `scraped_text.txt`
Plain text extracted from HTML. Shows what content is available.

### 4. `possible_events.txt`
Lines that look like they might be events. Helps identify parsing patterns.

## 🔧 What To Do With Results

### Scenario 1: Local Test WORKS

**Files show good content with events:**

```
possible_events.txt contains:
  • Live Music at Railgarten - Friday 7PM
  • Food Truck Friday at Overton Square - Friday 5PM
  • Cooper-Young Farmers Market - Saturday 8AM
  ... 40 more events
```

**Action:**
1. ✅ Direct scraper should work from Anvil
2. ✅ Push the code and test
3. ✅ If Anvil scraper fails, website blocks Anvil IPs
4. → Use a proxy service or cloud function

### Scenario 2: Local Test FAILS

**Connection errors or no content:**

**Action:**
1. Check if website is down (visit in browser)
2. Website might have aggressive anti-bot protection
3. Try with different user agents (script tests this)
4. Might need:
   - Selenium/Playwright for JS rendering
   - Proxy service
   - Alternative data source

### Scenario 3: Local Works, Anvil Fails

**This means: Website blocks Anvil's server IPs**

**Solutions:**
1. **Use a proxy service:**
   - Bright Data
   - ScraperAPI
   - ProxyMesh

2. **Use a cloud function:**
   - AWS Lambda with requests
   - Google Cloud Function
   - Calls back to Anvil

3. **Use different scraping service:**
   - ScrapeOwl
   - ScrapingBee
   - WebScraper.io

## 💡 Recommended Approach

Based on the Firecrawl error (`URL must have a valid top-level domain`), this is likely a **Firecrawl limitation**, not website blocking.

**Most Likely Scenario:**
- ✅ Local scraping will work
- ✅ Anvil direct scraping will work
- ⚠️ Firecrawl rejects the URL due to their validation rules

**Recommendation:**
- Skip Firecrawl entirely
- Use direct HTTP scraping
- Already implemented and ready!

## 🚀 Next Steps

### After Running Local Test:

1. **Check the saved files** to see content structure
2. **Share results** with me:
   - Did it work?
   - How many events detected?
   - Sample from possible_events.txt

3. **Based on results, I'll:**
   - Improve the parser if needed
   - Add better event detection
   - Optimize for the actual HTML structure

## 🧪 Advanced Testing

### Test from Python Console:

```python
import requests
from bs4 import BeautifulSoup

# Quick test
url = "https://ilovememphisblog.com/weekend"
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Length: {len(response.text)}")

# Look for events
soup = BeautifulSoup(response.text, 'html.parser')
text = soup.get_text()
print(f"Friday count: {text.lower().count('friday')}")
print(f"Saturday count: {text.lower().count('saturday')}")
```

### Test Specific Sections:

```python
# Find article or event containers
articles = soup.find_all('article')
print(f"Articles found: {len(articles)}")

# Find headings (often event titles)
headings = soup.find_all(['h1', 'h2', 'h3'])
print(f"Headings found: {len(headings)}")
for h in headings[:10]:
    print(f"  • {h.get_text().strip()}")
```

## 📚 Dependencies

```bash
pip install requests beautifulsoup4
```

**What they do:**
- `requests` - HTTP library for making web requests
- `beautifulsoup4` - HTML parser for extracting content

---

## 🎯 Expected Outcome

**Most likely:** Local scraping will work perfectly, showing that:
- ✅ Website is accessible
- ✅ Content is scrapable  
- ✅ Direct scraping is viable
- ✅ Firecrawl rejection is their URL validation, not website blocking

Then you can confidently use the direct scraper in Anvil! 🚀

---

**Run the test and send me the results!** I'll optimize the parser based on what you find.

