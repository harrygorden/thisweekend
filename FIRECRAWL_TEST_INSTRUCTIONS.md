# 🧪 Firecrawl Testing Instructions

## What We Discovered

**The website uses Cloudflare protection** (HTTP 403) which blocks:
- ❌ Direct HTTP requests
- ❌ Simple scrapers
- ✅ Need Firecrawl stealth mode OR browser automation

## 🔬 Diagnostic Tests Available

I've created comprehensive Firecrawl testing functions:

### Test 1: Connection Test

**Function:** `test_firecrawl_connection()`

Tests 3 scenarios:
1. Known-good URL (firecrawl.dev) without stealth
2. Target URL without stealth
3. Target URL with stealth mode

**Use in AdminForm:**
```python
def test_firecrawl_button_click(self, **event_args):
    self.status_output.text = "Testing Firecrawl API...\n"
    
    result = anvil.server.call('test_firecrawl_connection')
    
    # Display results
    output = "FIRECRAWL CONNECTION TEST\n"
    output += "="*50 + "\n\n"
    
    for test_name, test_result in result['tests'].items():
        status = "✅" if test_result['success'] else "❌"
        output += f"{status} {test_name}\n"
        if not test_result['success']:
            output += f"  Error: {test_result.get('error', 'Unknown')}\n"
        output += "\n"
    
    self.status_output.text = output
```

### Test 2: v0 Endpoint Test

**Function:** `test_firecrawl_v0_endpoint()`

Tests the older v0 API which might work differently.

**Use in AdminForm:**
```python
def test_v0_button_click(self, **event_args):
    result = anvil.server.call('test_firecrawl_v0_endpoint')
    
    if result['success']:
        alert(f"✅ v0 API works!\nContent: {result['content_size']} chars")
    else:
        alert(f"❌ v0 API failed: {result['error']}")
```

## 🚀 How to Add Test Buttons

### In AdminForm:

1. Open AdminForm in Anvil visual editor
2. Add two new buttons:

**Button 1:**
- Name: `test_firecrawl_button`
- Text: "Test Firecrawl API"
- Icon: `fa:bug`
- Click handler already exists in the code!

**Button 2:**
- Name: `test_v0_button`
- Text: "Test v0 Endpoint"
- Icon: `fa:flask`

### Or Add to Existing Code:

Add these handlers to `client_code/AdminForm/__init__.py`:

```python
def test_firecrawl_button_click(self, **event_args):
    """Test Firecrawl API connectivity"""
    self.status_output.text = "🔍 Testing Firecrawl API...\n\n"
    
    try:
        result = anvil.server.call('test_firecrawl_connection')
        
        # Build output
        output = "="*50 + "\n"
        output += "FIRECRAWL API CONNECTION TEST\n"
        output += "="*50 + "\n\n"
        
        output += f"API Key Configured: {result['api_key_configured']}\n"
        if result.get('api_key_preview'):
            output += f"API Key: {result['api_key_preview']}\n\n"
        
        output += "TEST RESULTS:\n\n"
        
        for test_name, test_result in result['tests'].items():
            status = "✅ PASS" if test_result['success'] else "❌ FAIL"
            output += f"{test_name}:\n"
            output += f"  Status: {status}\n"
            output += f"  URL: {test_result['url']}\n"
            output += f"  Stealth: {test_result['stealth']}\n"
            
            if test_result['success']:
                output += f"  Markdown size: {test_result.get('markdown_size', 0)} chars\n"
                if test_result.get('metadata'):
                    output += f"  Page title: {test_result['metadata'].get('title', 'Unknown')}\n"
            else:
                output += f"  Error: {test_result.get('error', 'Unknown')}\n"
                if test_result.get('error_code'):
                    output += f"  Error code: {test_result['error_code']}\n"
            
            output += "\n"
        
        self.status_output.text = output
        
    except Exception as e:
        self.status_output.text = f"❌ Test failed: {str(e)}"
```

## 📊 What These Tests Will Show

### If API Key is Wrong:
```
❌ test_url: FAILED
  Error: Invalid API key
  Error code: UNAUTHORIZED
```
**Solution:** Get new API key from firecrawl.dev

### If Plan Doesn't Support v1/v2:
```
✅ test_url (v0): SUCCESS
❌ target_url (v1): FAILED
  Error: Endpoint not available for your plan
```
**Solution:** Use v0 endpoint or upgrade plan

### If URL Validation is the Issue:
```
✅ test_url: SUCCESS (firecrawl.dev works)
❌ target_url: FAILED
  Error: URL must have a valid top-level domain
```
**Solution:** Firecrawl doesn't allow this specific URL

### If Stealth Mode Not Available:
```
✅ test_url: SUCCESS
❌ target_with_stealth: FAILED
  Error: Stealth mode requires paid plan
```
**Solution:** Upgrade plan or use alternative

### If Nothing Works:
```
❌ All tests: FAILED
  Error: Connection timeout / Network error
```
**Solution:** Firewall or network issue

## 🎯 Immediate Action

### Step 1: Push Diagnostic Code

```bash
git add server_code/firecrawl_diagnostics.py
git commit -m "Add Firecrawl diagnostic tests"
git push origin master
```

### Step 2: Pull in Anvil

Open Anvil → "Pull from Git"

### Step 3: Run Diagnostic

**Option A: From Python Console in Anvil**

```python
import server_code.firecrawl_diagnostics as diag
result = diag.test_firecrawl_connection()
print(result)
```

**Option B: Add Test Button to AdminForm**

Add the handler code above and a button to trigger it.

### Step 4: Share Results

Send me the output from the diagnostic test. It will show:
- Whether API key is valid
- Which endpoints work
- Exact error messages
- What features are available

## 💡 Quick Alternative

Since you don't see activity in Firecrawl's dashboard, **the API key might be incorrect or inactive**.

**Quick check:**
1. Log into firecrawl.dev
2. Go to API Keys page
3. Copy the API key
4. Verify it matches what's in Anvil Secrets
5. Check if it's active/not revoked

## 🔧 Files Created

- `server_code/firecrawl_diagnostics.py` - Diagnostic tests
- `FIRECRAWL_TEST_INSTRUCTIONS.md` - This guide

---

**Push the diagnostic code and run the tests.** They'll tell us exactly what's wrong with the Firecrawl connection! 🔍

