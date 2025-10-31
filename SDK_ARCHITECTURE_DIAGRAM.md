# SDK Architecture - How It Works

## 🏗️ System Architecture with SDK Support

### Current Implementation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR CODE                                │
│                                                                   │
│  ┌────────────────────┐              ┌────────────────────┐     │
│  │ scraper_service.py │              │   ai_service.py    │     │
│  └────────────────────┘              └────────────────────┘     │
│           │                                    │                 │
│           ▼                                    ▼                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         SDK Available Check (on module load)            │    │
│  │                                                         │    │
│  │  try:                         try:                      │    │
│  │    from firecrawl import       from openai import      │    │
│  │      Firecrawl                   OpenAI                │    │
│  │    SDK_AVAILABLE = True        SDK_AVAILABLE = True    │    │
│  │  except ImportError:           except ImportError:      │    │
│  │    SDK_AVAILABLE = False       SDK_AVAILABLE = False   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Runtime Decision Tree                      │    │
│  │                                                         │    │
│  │  if SDK_AVAILABLE:                                     │    │
│  │    ┌─────────────────────────┐                         │    │
│  │    │  Try SDK Method         │                         │    │
│  │    │  - firecrawl.scrape()   │                         │    │
│  │    │  - client.chat.create() │                         │    │
│  │    └─────────────────────────┘                         │    │
│  │           │                                             │    │
│  │           ├── SUCCESS → Return Result ✅               │    │
│  │           │                                             │    │
│  │           └── FAILURE → Fall through to HTTP ↓         │    │
│  │                                                         │    │
│  │  ┌─────────────────────────┐                           │    │
│  │  │  HTTP Fallback Method   │                           │    │
│  │  │  - anvil.http.request() │                           │    │
│  │  │  - Manual JSON parsing  │                           │    │
│  │  └─────────────────────────┘                           │    │
│  │           │                                             │    │
│  │           └── SUCCESS → Return Result ✅               │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📊 SDK vs HTTP Comparison

### Firecrawl Integration

#### SDK Method (Recommended):
```python
from firecrawl import Firecrawl

# Simple, clean initialization
firecrawl = Firecrawl(api_key=api_key)

# Single method call with automatic error handling
result = firecrawl.scrape(
    url=TARGET_URL,
    formats=['markdown', 'html']
)

# Clean, typed response
markdown = result.markdown        # ✅ Type-safe
metadata = result.metadata        # ✅ Auto-parsed
```

#### HTTP Method (Fallback):
```python
import anvil.http
import json

# Manual setup
url = "https://api.firecrawl.dev/v2/scrape"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "url": TARGET_URL,
    "formats": ["markdown", "html"],
    "stealth": True,
    "timeout": 60000
}

# Manual request
response = anvil.http.request(url, method="POST", json=payload, headers=headers)

# Manual parsing
response_text = response.get_bytes().decode('utf-8')  # ⚠️ Manual
result = json.loads(response_text)                     # ⚠️ Manual
markdown = result["data"]["markdown"]                  # ⚠️ No types
```

**Lines of code:** SDK = 5 lines | HTTP = 15+ lines

---

### OpenAI Integration

#### SDK Method (Recommended):
```python
from openai import OpenAI

# Simple initialization
client = OpenAI(api_key=api_key)

# Clean API call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    temperature=0.7,
    response_format={"type": "json_object"}
)

# Type-safe response
content = response.choices[0].message.content  # ✅ Typed
```

#### HTTP Method (Fallback):
```python
import anvil.http
import json

# Manual setup
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "gpt-4o-mini",
    "messages": [...],
    "temperature": 0.7,
    "response_format": {"type": "json_object"}
}

# Manual request
response = anvil.http.request(url, method="POST", json=payload, headers=headers)

# Manual parsing
response_text = response.get_bytes().decode('utf-8')  # ⚠️ Manual
result = json.loads(response_text)                     # ⚠️ Manual
content = result["choices"][0]["message"]["content"]   # ⚠️ No types
```

**Lines of code:** SDK = 7 lines | HTTP = 14+ lines

---

## 🔄 Deployment Scenarios

### Scenario 1: Anvil Uplink (Local Development)

```
┌──────────────────┐         ┌──────────────────┐
│   Anvil Cloud    │         │  Your Computer   │
│                  │         │                  │
│  ┌────────────┐  │  WSS    │  ┌────────────┐  │
│  │   Forms    │  │ ◄─────► │  │   Python   │  │
│  │  (Client)  │  │ Uplink  │  │   Server   │  │
│  └────────────┘  │         │  └────────────┘  │
│                  │         │        │         │
└──────────────────┘         │        ▼         │
                             │  ┌────────────┐  │
                             │  │firecrawl-py│  │ ✅ Installed
                             │  └────────────┘  │
                             │  ┌────────────┐  │
                             │  │   openai   │  │ ✅ Installed
                             │  └────────────┘  │
                             └──────────────────┘

Result: ✅ FULL SDK SUPPORT
```

### Scenario 2: Anvil Hosted (With Approved Packages)

```
┌────────────────────────────────────────┐
│           Anvil Cloud                  │
│                                        │
│  ┌────────────┐    ┌────────────┐     │
│  │   Forms    │    │   Python   │     │
│  │  (Client)  │◄──►│   Server   │     │
│  └────────────┘    └────────────┘     │
│                          │             │
│                          ▼             │
│                    ┌────────────┐      │
│                    │firecrawl-py│ ✅   │ Approved by Anvil
│                    └────────────┘      │
│                    ┌────────────┐      │
│                    │   openai   │ ✅   │ Approved by Anvil
│                    └────────────┘      │
└────────────────────────────────────────┘

Result: ✅ FULL SDK SUPPORT
```

### Scenario 3: Anvil Hosted (No Extra Packages)

```
┌────────────────────────────────────────┐
│           Anvil Cloud                  │
│                                        │
│  ┌────────────┐    ┌────────────┐     │
│  │   Forms    │    │   Python   │     │
│  │  (Client)  │◄──►│   Server   │     │
│  └────────────┘    └────────────┘     │
│                          │             │
│                          ▼             │
│                    ┌────────────┐      │
│                    │anvil.http  │ ⚠️   │ Built-in
│                    └────────────┘      │
│                    ┌────────────┐      │
│                    │   json     │ ⚠️   │ Built-in
│                    └────────────┘      │
└────────────────────────────────────────┘

Result: ⚠️ HTTP FALLBACK MODE
```

---

## 🎯 Decision Tree: Which Mode Gets Used?

```
START: Module loads
    │
    ▼
Check: Can import firecrawl?
    │
    ├─► YES → Set FIRECRAWL_SDK_AVAILABLE = True
    │         Print: "✅ Firecrawl Python SDK available"
    │
    └─► NO  → Set FIRECRAWL_SDK_AVAILABLE = False
              Print: "⚠️ Firecrawl SDK not installed"
    │
    ▼
Check: Can import openai?
    │
    ├─► YES → Set OPENAI_SDK_AVAILABLE = True
    │         Print: "✅ OpenAI Python SDK available"
    │
    └─► NO  → Set OPENAI_SDK_AVAILABLE = False
              Print: "⚠️ OpenAI SDK not installed"

─────────────────────────────────────────────

RUNTIME: User calls scrape_weekend_events()
    │
    ▼
Check: FIRECRAWL_SDK_AVAILABLE?
    │
    ├─► YES → Try: scrape_with_firecrawl_sdk()
    │         │
    │         ├─► SUCCESS → Return result ✅
    │         │             Print: "🚀 Using Firecrawl Python SDK"
    │         │
    │         └─► FAILURE → Print: "⚠️ SDK failed, falling back"
    │                       Continue to HTTP ↓
    │
    └─► NO  → Skip to HTTP ↓
    │
    ▼
Try: scrape_with_firecrawl_http()
    │
    └─► SUCCESS → Return result ✅
                  Print: "📡 Using raw HTTP method"

─────────────────────────────────────────────

RUNTIME: User calls analyze_event()
    │
    ▼
Check: OPENAI_SDK_AVAILABLE?
    │
    ├─► YES → Try: analyze_event_with_sdk()
    │         │
    │         ├─► SUCCESS → Return result ✅
    │         │             Print: "🚀 Using OpenAI SDK"
    │         │
    │         └─► FAILURE → Print: "⚠️ SDK failed, falling back"
    │                       Continue to HTTP ↓
    │
    └─► NO  → Skip to HTTP ↓
    │
    ▼
Try: analyze_event_with_http()
    │
    └─► SUCCESS → Return result ✅
                  Print: "📡 Using raw HTTP method"
```

---

## 📈 Reliability Comparison

### Error Handling

| Scenario | SDK Behavior | HTTP Behavior |
|----------|-------------|---------------|
| **Rate Limit** | ✅ Auto-retry with backoff | ❌ Immediate failure |
| **Timeout** | ✅ Configurable with retry | ⚠️ Manual timeout handling |
| **Auth Error** | ✅ Clear error message | ⚠️ Generic 401/403 |
| **Invalid Response** | ✅ Type validation | ❌ JSON parse error |
| **Network Error** | ✅ Automatic retry | ❌ Immediate failure |
| **API Change** | ✅ SDK update handles it | ❌ Code breaks |

---

## 🔧 Maintenance Impact

### When Firecrawl API Changes:

**With SDK:**
```bash
# Just update the package
pip install --upgrade firecrawl-py

# Code keeps working! ✅
```

**Without SDK:**
```python
# Must manually update:
# - API endpoints
# - Request payloads
# - Response parsing
# - Error handling
# All by hand! ❌
```

### When OpenAI API Changes:

**With SDK:**
```bash
# Just update the package
pip install --upgrade openai

# Code keeps working! ✅
```

**Without SDK:**
```python
# Must manually update:
# - API endpoints
# - Request structure
# - Response parsing
# All by hand! ❌
```

---

## 💡 Best Practices

### ✅ DO:
- Use Anvil Uplink for development
- Request packages for production deployment
- Let the code choose SDK automatically
- Monitor console for which mode is active

### ❌ DON'T:
- Force HTTP mode when SDK available
- Ignore SDK import warnings
- Skip testing after package updates
- Deploy to production without SDK support

---

## 🚀 Performance Comparison

| Operation | SDK Time | HTTP Time | Difference |
|-----------|----------|-----------|------------|
| **Firecrawl Scrape** | ~3-5 sec | ~3-5 sec | Same (network bound) |
| **OpenAI Analysis** | ~2-4 sec | ~2-4 sec | Same (API bound) |
| **Error Recovery** | Instant | Manual | ⚠️ SDK faster |
| **Code Maintenance** | Minutes | Hours | ⚠️ SDK much faster |

**Note:** Network-bound operations have similar speed, but **development speed** is much faster with SDKs!

---

## 📚 Summary

Your code now has **three layers of reliability**:

1. **🥇 First Choice:** Python SDKs (when available)
2. **🥈 Second Choice:** Raw HTTP (automatic fallback)
3. **🥉 Third Choice:** Direct scraper (for Firecrawl only)

**Result:** Your app works in ANY environment! 🎉

