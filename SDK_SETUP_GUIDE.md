# SDK Setup Guide - Using Firecrawl & OpenAI Python SDKs

## 🎯 Overview

This project now **supports both Python SDKs and raw HTTP** for API interactions:
- **Firecrawl Python SDK** (`firecrawl-py`) - More reliable for web scraping
- **OpenAI Python SDK** (`openai`) - More reliable for AI analysis

The code **automatically detects** which method is available and uses the best option.

---

## ✅ Benefits of Using SDKs

### Why Use SDKs Instead of Raw HTTP?

| Feature | Python SDK | Raw HTTP |
|---------|-----------|----------|
| **Reliability** | ✅ Handles retries, errors | ❌ Manual handling |
| **Type Safety** | ✅ Type hints, validation | ❌ Manual parsing |
| **Maintainability** | ✅ Auto-updates with API changes | ❌ Manual updates needed |
| **Error Messages** | ✅ Clear, helpful errors | ❌ Generic HTTP errors |
| **Rate Limiting** | ✅ Automatic handling | ❌ Manual implementation |
| **Authentication** | ✅ Simplified | ❌ Manual headers |
| **Features** | ✅ All latest features | ❌ May miss new features |

**Recommendation:** Use SDKs when possible, especially for development/testing.

---

## 🚀 Setup Options

You have **3 options** for running this project:

### Option 1: Anvil Uplink (Local Development) - **RECOMMENDED**

**Best for:** Development, testing, full SDK support

#### Setup Steps:

1. **Install dependencies locally:**
   ```bash
   pip install -r server_code/requirements.txt
   ```

   This installs:
   - `firecrawl-py` - Firecrawl Python SDK
   - `openai` - OpenAI Python SDK
   - `anvil-uplink` - Anvil local server

2. **Get your Uplink URL from Anvil:**
   - Open your Anvil app
   - Go to **Settings** → **Uplink**
   - Copy the server URL (looks like: `wss://anvil.works/uplink/...`)

3. **Run Anvil Uplink:**
   ```bash
   python -m anvil.uplink --server-url wss://anvil.works/uplink/YOUR-KEY-HERE
   ```

4. **Run your app:**
   - Your local Python environment handles all server calls
   - Full access to `firecrawl-py` and `openai` packages
   - Changes to server code apply immediately (no deployment needed)

#### How It Works:
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ ◄─────► │ Anvil Cloud  │ ◄─────► │ Your Local  │
│  (Client)   │         │   (Forms)    │         │   Python    │
└─────────────┘         └──────────────┘         └─────────────┘
                                                   ↓
                                              firecrawl-py
                                              openai SDK
                                              ✅ Full access!
```

---

### Option 2: Anvil Hosted with Third-Party Packages

**Best for:** Production, if Anvil approves your packages

#### Setup Steps:

1. **Request third-party packages in Anvil:**
   - Open your Anvil app
   - Go to **Settings** → **Dependencies**
   - Click **"Add a Third-Party Package"**
   - Request:
     - `firecrawl-py` (version: latest)
     - `openai` (version: latest)

2. **Wait for approval:**
   - Anvil team reviews package requests
   - May take 1-3 business days
   - Not all packages are approved

3. **Deploy your app:**
   - Once approved, packages are available in hosted environment
   - Code automatically uses SDK mode

#### How It Works:
```
┌─────────────┐         ┌──────────────────────────┐
│   Browser   │ ◄─────► │   Anvil Cloud (All)      │
│  (Client)   │         │   - Forms                │
└─────────────┘         │   - Server Code          │
                        │   - firecrawl-py ✅      │
                        │   - openai ✅            │
                        └──────────────────────────┘
```

---

### Option 3: Anvil Hosted with Fallback HTTP (Current State)

**Best for:** Quick deployment without waiting for package approval

#### Setup Steps:

1. **No additional setup needed!**
   - Code already includes HTTP fallback
   - Works immediately in Anvil hosted environment

2. **What happens:**
   - SDKs not available → automatic fallback to raw HTTP
   - Less reliable, but functional
   - See console for warnings about missing SDKs

#### How It Works:
```
┌─────────────┐         ┌──────────────────────────┐
│   Browser   │ ◄─────► │   Anvil Cloud (All)      │
│  (Client)   │         │   - Forms                │
└─────────────┘         │   - Server Code          │
                        │   - Raw HTTP calls ⚠️    │
                        │   (fallback mode)        │
                        └──────────────────────────┘
```

---

## 📊 Feature Comparison

| Feature | Option 1 (Uplink) | Option 2 (Hosted + Pkgs) | Option 3 (Fallback) |
|---------|-------------------|--------------------------|---------------------|
| **Setup Time** | 5 minutes | 1-3 days | 0 minutes |
| **SDK Support** | ✅ Full | ✅ Full (after approval) | ❌ None |
| **Reliability** | ✅✅✅ Best | ✅✅✅ Best | ⚠️ Good |
| **Development** | ✅ Instant updates | ❌ Requires deployment | ❌ Requires deployment |
| **Production** | ❌ Not recommended | ✅ Best for production | ⚠️ Works, less reliable |
| **Cost** | Free (local) | Free tier available | Free tier available |
| **Internet Required** | ✅ Yes (for APIs) | ✅ Yes | ✅ Yes |

---

## 🔍 How to Check Which Mode You're Using

### Check Console Output

When your server code runs, look for these messages:

#### SDK Mode (Good):
```
✅ Firecrawl Python SDK available - using SDK mode
✅ OpenAI Python SDK available - using SDK mode
```

#### Fallback Mode (Working, but not ideal):
```
⚠️ Firecrawl SDK not installed - using fallback HTTP mode
   Install with: pip install firecrawl-py
   See server_code/requirements.txt for instructions
⚠️ OpenAI SDK not installed - using fallback HTTP mode
   Install with: pip install openai
   See server_code/requirements.txt for instructions
```

### During Execution

The code also logs which method it's using for each API call:

**SDK Mode:**
```
  🚀 Using Firecrawl Python SDK (recommended)
  ✅ SDK scrape successful: 15234 characters
```

**Fallback Mode:**
```
  📡 Using raw HTTP method (fallback)
  Received 15234 bytes
```

---

## 🛠️ Troubleshooting

### Issue: "Firecrawl SDK not installed"

**Solution:**
- If using Uplink: Run `pip install firecrawl-py`
- If using hosted: Request package in Anvil Settings → Dependencies
- If quick fix needed: Code will automatically use HTTP fallback

### Issue: "OpenAI SDK not installed"

**Solution:**
- If using Uplink: Run `pip install openai`
- If using hosted: Request package in Anvil Settings → Dependencies
- If quick fix needed: Code will automatically use HTTP fallback

### Issue: Uplink won't connect

**Solution:**
```bash
# Make sure you have the correct uplink URL
python -m anvil.uplink --server-url wss://anvil.works/uplink/YOUR-KEY-HERE

# Check firewall/network settings
# Uplink needs WebSocket (wss://) access
```

### Issue: "SDK method failed" but HTTP works

This is normal! Possible causes:
- API version mismatch
- SDK authentication issue
- Network configuration

The code automatically falls back to HTTP, so your app keeps working.

---

## 📝 Updating `requirements.txt`

The `requirements.txt` file is now **uncommented** and ready to use:

```txt
# Required third-party packages:
firecrawl-py>=1.0.0        # Firecrawl Python SDK
openai>=1.0.0              # OpenAI Python SDK

# For local testing with Anvil Uplink:
anvil-uplink
```

**To install:**
```bash
pip install -r server_code/requirements.txt
```

---

## 🎓 Recommendations

### For Development:
✅ **Use Option 1 (Anvil Uplink)**
- Fastest setup
- Best development experience
- Full SDK support
- Instant code updates

### For Production:
✅ **Use Option 2 (Hosted + Packages)**
- Most reliable
- No local server needed
- Auto-scaling
- Better error handling

### For Quick Testing:
✅ **Use Option 3 (Fallback HTTP)**
- Works immediately
- No setup needed
- Good enough for proof-of-concept

---

## 🔗 Resources

- **Firecrawl SDK Docs:** https://docs.firecrawl.dev/sdks/python
- **OpenAI SDK Docs:** https://platform.openai.com/docs/libraries/python-library
- **Anvil Uplink Guide:** https://anvil.works/docs/uplink
- **Anvil Third-Party Packages:** https://anvil.works/docs/server/third-party-packages

---

## 💡 Next Steps

1. **Choose your option** based on your needs (see recommendations above)
2. **Follow the setup steps** for your chosen option
3. **Verify SDK availability** by checking console output
4. **Test your app** - it will work either way!

Your code now has **automatic fallback**, so it works in all environments. Using the SDKs just makes it more reliable! 🚀

