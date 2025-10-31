# MainApp - User-Facing Form

## Overview
The **MainApp** form is the primary user interface for the "This Weekend" application. It provides a clean, intuitive interface for browsing weekend events with powerful filtering capabilities.

## Layout Structure

### 1. Header Section
- **App Title**: "🎉 This Weekend"
- **Refresh Button**: Reloads weather and event data from the server
- **My Itinerary Button**: Shows saved events, displays count when events are selected

### 2. Weather Forecast Section
Displays a 3-day weather forecast (Friday, Saturday, Sunday) using the **WeatherCard** component.

Each weather card shows:
- Day name
- High/Low temperatures
- Weather icon (emoji)
- Conditions description
- Precipitation chance with color coding
- Wind speed

### 3. Main Content (Two-Column Layout)

#### Left Column - Filter Panel
Comprehensive filtering options organized by category:

**Day Filters:**
- Friday
- Saturday  
- Sunday

**Cost Filters:**
- Free
- $ (Under $20)
- $$ ($20-50)
- $$$ ($50-100)
- $$$$ ($100+)

**Category Filters:**
- Arts
- Music
- Sports
- Food & Drink
- Outdoor Activities
- Cultural Events
- Theater/Performance
- Family/Kids
- Nightlife

**Audience Filters:**
- Adults
- Family-Friendly
- All Ages

**Venue Type Filters:**
- Indoor (checked by default)
- Outdoor (checked by default)

**Additional Features:**
- Search box for text search
- "Clear All Filters" button

#### Right Column - Events Panel
- Displays filtered events using the **EventCard** component
- Shows event count ("Showing X of Y events")
- Automatically updates when filters change
- Empty state message when no events match filters

## Usage

### To Set as Startup Form
In your Anvil app, set MainApp as the startup form:

```python
# In anvil.yaml or App settings
startup: {type: form, module: MainApp}
```

### To Open Programmatically
```python
from anvil import open_form
from .MainApp import MainApp

open_form(MainApp())
```

## Features

### Search Functionality
- Type in the search box to filter events by title, description, or location
- Searches are case-insensitive
- Combines with other active filters

### Filtering
- Multiple filters can be active simultaneously
- Filters are applied using AND logic within categories and OR logic across filter values
- Example: Selecting "Music" AND "Arts" shows events that have EITHER category
- Filter combinations narrow down results progressively

### Itinerary Management
1. Click "Add to Itinerary" on any event card
2. Button changes to "In Itinerary" with a red heart icon
3. Itinerary button in header shows count: "My Itinerary (3)"
4. Click "My Itinerary" button to view your saved events organized by day

### Weather Integration
- Weather cards automatically update based on server data
- Events show weather warnings for outdoor activities
- Weather summary provides quick weekend outlook

## Server Dependencies

The form requires these server functions (already implemented):
- `get_weather_data()` - Returns weather forecast data
- `get_all_events(sort_by='recommendation')` - Returns sorted event list

## Components Used

- **WeatherCard** (`client_code/WeatherCard/`) - Custom component for weather display
- **EventCard** (`client_code/EventCard/`) - Custom component for event display

## Responsive Design

The form uses Anvil's GridPanel for responsive layout:
- On desktop (sm+): Two-column layout with filters on left (4 cols) and events on right (8 cols)
- On mobile (xs): Single column stacked layout

## Customization

### Colors
- Primary blue: `#1976D2`
- Success green: `#4CAF50`
- Warning orange: `#FF9800`
- Error red: `#F44336`

### Modify Filters
To add/remove categories, update:
1. Filter checkboxes in `form_template.yaml`
2. Event handlers in `__init__.py`
3. Category list in `server_code/config.py`

## Best Practices

1. **Initial Load**: The form loads data automatically on initialization
2. **Refresh**: Users can manually refresh using the refresh button
3. **Performance**: Events are filtered client-side for fast response
4. **Error Handling**: Shows user-friendly messages if data loading fails

