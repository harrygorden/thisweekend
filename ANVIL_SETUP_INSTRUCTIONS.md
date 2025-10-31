# Anvil Setup Instructions - Final Steps

## Issues Fixed in Code ✅

I've fixed the following issues and pushed them to GitHub:

1. ✅ **Duplicate callable warnings** - Removed `@anvil.server.callable` decorators from `admin_tools.py` (they're already in `test_data.py`)
2. ✅ **Notification error** - Changed `Notification().show()` to `alert()` in MainApp refresh button
3. ✅ **Safety check** - Added component initialization check in WeatherCard

## Remaining Issue: Missing _anvil_designer Files

The error `'WeatherCard' object has no attribute 'day_label'` indicates that Anvil hasn't generated the `_anvil_designer.py` files for the new components yet.

## 🔧 How to Fix in Anvil Editor

### Step 1: Pull Latest Code from GitHub

1. In Anvil editor, click the **Version History** icon (clock) in the top-right
2. Click **"Pull from origin"** or **"Sync"** button
3. This will pull the latest code including all fixes

### Step 2: Force Anvil to Generate Designer Files

Anvil auto-generates `_anvil_designer.py` files when you open a form in the designer. You need to do this for each new component:

**For WeatherCard:**
1. In the left sidebar, find **WeatherCard** under "Forms"
2. Click on it to open in the designer
3. You should see the weather card layout appear
4. Anvil will automatically generate `WeatherCard/_anvil_designer.py`
5. You might see the layout adjust - this is normal

**For MainApp:**
1. Find **MainApp** under "Forms"
2. Click on it to open in the designer
3. The layout will load with all the filters and event panels
4. Anvil will automatically generate `MainApp/_anvil_designer.py`

**For EventCard:**
1. Find **EventCard** under "Forms"
2. Click on it to open in the designer
3. Anvil will generate `EventCard/_anvil_designer.py`

### Step 3: Verify Components Are Initialized

After opening each form in the designer:

1. Check that no errors appear in the **Output Panel** at the bottom
2. The forms should display properly in the designer view
3. You might see some component names or layouts adjust - Anvil reformats YAML files

### Step 4: Test the App

1. Make sure **MainApp** is set as the startup form:
   - Right-click on **MainApp** in the forms list
   - Select **"Set as startup form"**
   - You should see a small home icon next to MainApp

2. Click the **Run** button (top right)

3. The app should now load successfully!

## 🎯 What Should Happen

When the app runs successfully, you should see:

✅ **Header** with "🎉 This Weekend" title  
✅ **3 Weather Cards** showing Friday, Saturday, Sunday forecasts  
✅ **Filter Panel** on the left with all filter options  
✅ **Events List** on the right  

## 🐛 If You Still Get Errors

### Error: "Error loading weather"

**Cause**: No weather data in database yet

**Fix**:
```python
# In Anvil console or from a test form
anvil.server.call('scheduled_refresh_all_data')
```
This will fetch weather and events from APIs.

**OR** use test data:
```python
anvil.server.call('create_test_events')
```

### Error: "Error loading events: get"

**Cause**: Missing server function or database table

**Fix**:
1. Check that `events` table exists in Data Tables
2. Verify `get_all_events` function exists in `server_code/data_processor.py`
3. Run database setup:
```python
anvil.server.call('run_database_setup')
```

### Error: "AttributeError: module 'anvil' has no attribute 'Card'"

**Cause**: This error should be gone after pulling the latest code and regenerating designer files

**If it persists**:
1. Make sure you pulled from GitHub (Step 1)
2. Reload the Anvil editor page (Ctrl+F5 or Cmd+Shift+R)
3. Open each form in the designer again (Step 2)

## 📝 Quick Checklist

Before running the app, verify:

- [ ] Pulled latest code from GitHub
- [ ] Opened **WeatherCard** in designer (to generate `_anvil_designer.py`)
- [ ] Opened **MainApp** in designer (to generate `_anvil_designer.py`)
- [ ] Opened **EventCard** in designer (to generate `_anvil_designer.py`)
- [ ] Set **MainApp** as startup form (home icon visible)
- [ ] Have weather data OR test data in database
- [ ] No errors in Output Panel

## 💡 Why This Happens

Anvil uses a "designer-first" approach where:

1. **You edit forms** in the visual designer
2. **Anvil generates** `_anvil_designer.py` files automatically
3. **Your Python code** imports from these generated files

When files are created/modified outside Anvil (like we did), Anvil needs to "see" them in the designer to generate the bridge files.

This is a one-time setup - once the designer files are generated, they'll stay generated even when you make code changes.

## 🚀 After Setup

Once everything is working:

1. **Test all filters** - click various checkboxes to ensure filtering works
2. **Test search** - type in the search box
3. **Test itinerary** - add events to itinerary, view them
4. **Test weather cards** - verify they display correctly
5. **Test on mobile** - the layout should be responsive

## Need More Help?

If you're still having issues after following these steps, let me know:
- What error message you're seeing
- Which step you're on
- What you see in the Output Panel

The code is all fixed and pushed to GitHub - it's just a matter of getting Anvil to recognize and generate the designer files! 🎉

