# Admin Tools Guide - This Weekend App

## 🚀 Quick Start: Automatic Database Setup

You no longer need to manually create columns! The new admin tools will do it automatically.

### Step 1: Create Empty Tables in Anvil UI

Go to **Data Tables** tab and create these 3 empty tables:
- `events`
- `weather_forecast`
- `scrape_log`

That's it for manual work! The rest is automatic.

### Step 2: Run the Automatic Setup

**Option A: From a Test Form (Recommended)**

1. Add a button to any form in Anvil
2. Add this code to the button's click event:

```python
def setup_button_click(self, **event_args):
    from anvil import alert
    result = anvil.server.call('run_database_setup')
    
    summary = result['summary']
    if summary['tables_error'] > 0:
        alert(f"❌ Setup failed!\n{summary['tables_error']} tables have errors.\nCheck server logs for details.")
    elif summary['tables_fixed'] > 0:
        alert(f"✅ Setup complete!\nCreated {summary['total_columns_created']} columns across {summary['tables_fixed']} tables.")
    else:
        alert("✅ All tables already configured correctly!")
```

3. Click the button
4. Watch the server logs for detailed progress

**Option B: From Server Console**

In the Anvil server console:

```python
import server_code.setup_schema as setup
setup.setup_and_verify_all_tables()
```

### What It Does

The setup script will:
1. ✅ Check if all 3 tables exist
2. ✅ Detect which columns are missing
3. ✅ Automatically create missing columns with correct types
4. ✅ Report exactly what was created

**Expected output:**
```
THIS WEEKEND - AUTOMATIC SCHEMA SETUP
======================================

Checking table: events
  Table is empty - will create all 17 columns
  Creating columns: event_id, title, description, date, ...
  ✓ Successfully created 17 columns in 'events'

Checking table: weather_forecast
  ✓ Successfully created 9 columns

Checking table: scrape_log
  ✓ Successfully created 7 columns

SUMMARY
=======
Total tables checked: 3
  ✓ Tables OK: 0
  🔧 Tables fixed: 3
  ✗ Tables with errors: 0
  📝 Columns created: 33

✅ SETUP COMPLETE!
Successfully created 33 missing columns.
All tables are now ready to use.
```

---

## 📋 Available Admin Functions

All of these can be called from client code using `anvil.server.call()`:

### 1. `run_database_setup()`
**Purpose:** Automatically verify and create all required tables and columns

**Usage:**
```python
result = anvil.server.call('run_database_setup')
print(f"Created {result['summary']['total_columns_created']} columns")
```

**Returns:**
```python
{
    'timestamp': datetime,
    'tables': {
        'events': {
            'exists': True,
            'columns_expected': 17,
            'columns_found': 0,
            'columns_created': 17,
            'missing_columns': [],
            'status': 'fixed',
            'message': 'Created 17 missing columns'
        },
        # ... same for weather_forecast and scrape_log
    },
    'summary': {
        'total_tables': 3,
        'tables_ok': 0,
        'tables_fixed': 3,
        'tables_error': 0,
        'total_columns_created': 33
    }
}
```

---

### 2. `check_database_status()`
**Purpose:** Check database status without making any changes (read-only)

**Usage:**
```python
status = anvil.server.call('check_database_status')
for table_name, info in status['tables'].items():
    print(f"{table_name}: {len(info['existing_columns'])} columns")
    if info['missing_columns']:
        print(f"  Missing: {', '.join(info['missing_columns'])}")
```

**Returns:**
```python
{
    'timestamp': datetime,
    'tables': {
        'events': {
            'exists': True,
            'expected_columns': 17,
            'existing_columns': ['event_id', 'title', ...],
            'missing_columns': []  # or list of missing columns
        },
        # ... same for other tables
    }
}
```

---

### 3. `test_api_keys()`
**Purpose:** Verify that all required API keys are configured

**Usage:**
```python
keys = anvil.server.call('test_api_keys')
if keys['all_configured']:
    print("✅ All API keys are configured!")
else:
    for key, info in keys['keys'].items():
        if not info['configured']:
            print(f"❌ {key} is not configured")
```

**Returns:**
```python
{
    'timestamp': datetime,
    'all_configured': True,
    'keys': {
        'OPENWEATHER_API_KEY': {
            'configured': True,
            'masked_value': 'abc1...xyz9'
        },
        'FIRECRAWL_API_KEY': {
            'configured': True,
            'masked_value': 'fc-a...b123'
        },
        'OPENAI_API_KEY': {
            'configured': True,
            'masked_value': 'sk-a...xyz'
        }
    }
}
```

---

### 4. `run_quick_health_check()`
**Purpose:** Comprehensive system health check

**Usage:**
```python
health = anvil.server.call('run_quick_health_check')
print(f"Status: {health['overall_status']}")
if health['issues']:
    print(f"Issues: {', '.join(health['issues'])}")
```

**Returns:**
```python
{
    'timestamp': datetime,
    'overall_status': 'ok',  # or 'warning' or 'error'
    'checks': {
        'database_tables': {
            'status': 'ok',
            'details': { ... }
        },
        'api_keys': {
            'status': 'ok',
            'details': { ... }
        },
        'data_freshness': {
            'status': 'ok',
            'last_refresh': datetime,
            'age_days': 2
        }
    },
    'issues': [],  # or list of issue strings
    'issue_count': 0
}
```

---

### 5. `get_system_info()`
**Purpose:** Get general system information and statistics

**Usage:**
```python
info = anvil.server.call('get_system_info')
print(f"Events in database: {info['event_count']}")
print(f"Last refresh: {info['last_refresh']}")
```

**Returns:**
```python
{
    'timestamp': datetime,
    'database_status': {
        'events': {
            'exists': True,
            'columns_ok': True,
            'column_count': 17
        },
        # ... other tables
    },
    'last_refresh': datetime,
    'event_count': 42,
    'weather_forecast_count': 3
}
```

---

### 6. `clear_all_data()`
**Purpose:** ⚠️ **DANGER:** Delete all data from all tables (for testing)

**Usage:**
```python
if confirm("Are you sure you want to delete ALL data?"):
    result = anvil.server.call('clear_all_data')
    alert(f"Deleted {result['deleted']} rows")
```

**Returns:**
```python
{
    'timestamp': datetime,
    'deleted': {
        'events': 42,
        'weather_forecast': 3,
        'scrape_log': 5
    }
}
```

---

## 🎨 Example Admin Form

Here's a complete example of an admin form with all the tools:

```python
from anvil import *
import anvil.server

class AdminForm(AdminFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
    
    def setup_database_button_click(self, **event_args):
        """Run database setup"""
        self.status_label.text = "Setting up database..."
        
        result = anvil.server.call('run_database_setup')
        
        summary = result['summary']
        if summary['tables_error'] > 0:
            self.status_label.text = f"❌ Setup failed! {summary['tables_error']} tables have errors."
            self.status_label.foreground = "red"
        elif summary['tables_fixed'] > 0:
            self.status_label.text = f"✅ Setup complete! Created {summary['total_columns_created']} columns."
            self.status_label.foreground = "green"
        else:
            self.status_label.text = "✅ All tables already configured!"
            self.status_label.foreground = "green"
    
    def health_check_button_click(self, **event_args):
        """Run health check"""
        health = anvil.server.call('run_quick_health_check')
        
        if health['overall_status'] == 'ok':
            alert("✅ System is healthy!\n\nAll checks passed.")
        else:
            issues = '\n'.join(f"• {issue}" for issue in health['issues'])
            alert(f"⚠️ Issues found:\n\n{issues}")
    
    def refresh_data_button_click(self, **event_args):
        """Trigger data refresh"""
        self.status_label.text = "Starting data refresh..."
        
        task = anvil.server.call('trigger_data_refresh')
        
        self.status_label.text = "Data refresh started! Check server logs for progress."
        self.status_label.foreground = "blue"
    
    def test_keys_button_click(self, **event_args):
        """Test API keys"""
        keys = anvil.server.call('test_api_keys')
        
        if keys['all_configured']:
            alert("✅ All API keys are configured!")
        else:
            missing = [k for k, v in keys['keys'].items() if not v['configured']]
            alert(f"❌ Missing API keys:\n\n" + '\n'.join(f"• {k}" for k in missing))
    
    def clear_data_button_click(self, **event_args):
        """Clear all data"""
        if confirm("⚠️ WARNING: This will DELETE ALL DATA!\n\nAre you absolutely sure?"):
            result = anvil.server.call('clear_all_data')
            total = sum(v for v in result['deleted'].values() if isinstance(v, int))
            alert(f"Deleted {total} total rows:\n" + 
                  '\n'.join(f"• {table}: {count}" for table, count in result['deleted'].items()))
```

---

## 🔍 Troubleshooting

### "Table does not exist"
**Solution:** Create the empty table in Anvil UI first:
1. Go to **Data Tables** tab
2. Click **Add Table**
3. Name it exactly: `events`, `weather_forecast`, or `scrape_log`
4. Run setup again

### "Failed to create columns"
**Possible causes:**
1. Anvil app is not synced with GitHub
2. Permissions issue
3. Table name mismatch

**Solution:**
- Check server logs for detailed error message
- Verify table names are exactly: `events`, `weather_forecast`, `scrape_log`
- Try creating one column manually first

### Want to verify without changes?
Use `check_database_status()` instead of `run_database_setup()`

---

## 📚 Related Documentation

- **NEXT_STEPS.md** - Original manual setup instructions
- **SERVER_FUNCTIONS_REFERENCE.md** - All callable server functions
- **IMPLEMENTATION_SUMMARY.md** - What's been built

---

## ✅ Recommended Workflow

**First-time setup:**
1. Create 3 empty tables in Anvil UI
2. Run `run_database_setup()` - creates all columns automatically
3. Run `test_api_keys()` - verify API keys configured
4. Run `trigger_data_refresh()` - populate with real data
5. Run `run_quick_health_check()` - confirm everything works

**Ongoing maintenance:**
- Run `run_quick_health_check()` weekly
- Run `trigger_data_refresh()` as needed
- Use `get_system_info()` to monitor data freshness

---

**Happy coding! 🎉**

