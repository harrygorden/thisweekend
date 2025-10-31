# MainApp Quick Start Guide

## What Was Created

I've created a complete user-facing form for your "This Weekend" application with the following components:

### 1. **WeatherCard Component** (`client_code/WeatherCard/`)
A reusable component that displays a single day's weather forecast with:
- Day name and temperature (high/low)
- Weather icon (emoji-based)
- Conditions description
- Precipitation percentage (color-coded)
- Wind speed
- Smart background coloring based on weather conditions

### 2. **MainApp Form** (`client_code/MainApp/`)
The main user interface featuring:

**Header:**
- App branding ("🎉 This Weekend")
- Refresh button
- My Itinerary button (shows count of saved events)

**Weather Section:**
- 3-day forecast (Friday, Saturday, Sunday)
- Weather summary text

**Two-Column Layout:**
- **Left Column**: Comprehensive filter panel with:
  - Search box
  - Day filters (Fri/Sat/Sun)
  - Cost filters (Free, $, $$, $$$, $$$$)
  - Category filters (Arts, Music, Sports, Food & Drink, etc.)
  - Audience filters (Adults, Family-Friendly, All Ages)
  - Venue type filters (Indoor/Outdoor)
  - Clear all filters button
  
- **Right Column**: Event display area
  - Event count indicator
  - Dynamic event cards (uses existing EventCard component)
  - Empty state messaging

## How to Use It

### Option 1: Set as Startup Form (Recommended)
1. Open your Anvil app in the editor
2. Click on the **App** dropdown in the left sidebar
3. Find "MainApp" in the list of forms
4. Right-click and select **"Set as startup form"**
5. Run your app!

### Option 2: Navigate to MainApp Programmatically
If you want to navigate from another form:

```python
from anvil import open_form
from .MainApp import MainApp

# Replace current form with MainApp
open_form('MainApp')
```

### Option 3: Test in a Button Click
Add this to any existing form:

```python
def button_click(self, **event_args):
    from .MainApp import MainApp
    open_form(MainApp())
```

## Features Overview

### 🌤️ Weather Forecast
- Automatically loads 3-day weather forecast from your weather_forecast table
- Color-coded cards based on conditions and precipitation
- Quick weekend outlook summary

### 🎭 Event Browsing
- All events displayed by default, sorted by recommendation score
- Real-time filtering as you check/uncheck options
- Combines multiple filters intelligently
- Search across title, description, and location

### 🔍 Smart Filtering
- **Day Filter**: Show only Friday, Saturday, or Sunday events
- **Cost Filter**: Filter by price range
- **Category Filter**: Multiple categories (Music, Arts, Sports, etc.)
- **Audience Filter**: Adults-only, family-friendly, or all-ages
- **Venue Filter**: Indoor vs Outdoor events
- **Search**: Free-text search across event details

### ❤️ Itinerary Management
1. Click "Add to Itinerary" on any event
2. Button turns red with heart icon
3. Header shows count: "My Itinerary (3)"
4. Click "My Itinerary" to view organized by day
5. Includes weather warnings for outdoor events

### 🔄 Data Refresh
- Click the refresh button (🔄) in the header to reload data
- Shows a loading indicator while fetching
- Updates both weather and events

## Testing Checklist

Before showing to users, verify:

- [ ] Weather data loads correctly (check weather_forecast table has data)
- [ ] Events display properly (check events table has data)
- [ ] All filter checkboxes work
- [ ] Search box filters events
- [ ] "Clear All Filters" button resets everything
- [ ] Adding events to itinerary works
- [ ] "My Itinerary" button shows saved events
- [ ] Refresh button updates data
- [ ] Mobile/tablet responsive layout works

## Troubleshooting

### No Weather Data Shows
- Run `anvil.server.call('run_database_setup')` to ensure tables exist
- Run background task to fetch weather data
- Check that `OPENWEATHER_API_KEY` secret is configured

### No Events Show  
- Verify events table has data
- Check that events have required fields (title, date, categories, etc.)
- Try creating test events: `anvil.server.call('create_test_events')`

### Filters Don't Work
- Ensure events have proper field values (cost_level, audience_type, categories)
- Check browser console for JavaScript errors
- Verify event data structure matches what the form expects

### Layout Looks Wrong
- Clear browser cache and reload
- Check that both WeatherCard and EventCard components exist
- Verify form_template.yaml loaded correctly

## Next Steps

1. **Populate Data**: 
   - Run your scraper to populate events
   - Ensure weather forecast is up to date
   - Create test data if needed

2. **Customize Branding**:
   - Update header color in form_template.yaml (currently `#1976D2`)
   - Change app title if desired
   - Adjust fonts and spacing to match your style

3. **Add Features**:
   - Export itinerary to calendar
   - Share itinerary via email/link
   - User accounts and saved preferences
   - Map view of event locations

4. **Deploy**:
   - Test thoroughly with real data
   - Set MainApp as startup form
   - Publish your app!

## File Structure

```
client_code/
├── MainApp/
│   ├── __init__.py          # Main form logic
│   ├── form_template.yaml   # UI layout definition
│   └── README.md            # Component documentation
├── WeatherCard/
│   ├── __init__.py          # Weather card logic
│   └── form_template.yaml   # Weather card layout
└── EventCard/
    ├── __init__.py          # Event card logic (existing)
    └── form_template.yaml   # Event card layout (existing)
```

## Support

The form integrates seamlessly with your existing server code:
- Uses `get_weather_data()` for weather
- Uses `get_all_events()` for events  
- Compatible with existing EventCard component
- No database changes required

Enjoy your new user-facing form! 🎉

