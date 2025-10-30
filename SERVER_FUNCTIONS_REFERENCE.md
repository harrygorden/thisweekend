# Server Functions Reference

This document lists all callable server functions available to the client-side code.

## Background Tasks

### `trigger_data_refresh()`
Manually trigger a complete data refresh.

**Returns:** Task object for monitoring progress

**Example:**
```python
task = anvil.server.call('trigger_data_refresh')
```

---

### `get_last_refresh_time()`
Get the timestamp of the last successful data refresh.

**Returns:** datetime or None

**Example:**
```python
last_refresh = anvil.server.call('get_last_refresh_time')
```

---

### `get_refresh_status()`
Get detailed status of recent data refresh operations.

**Returns:** dict with status information:
- `last_run`: datetime
- `status`: "success" | "failed" | "never_run"
- `events_found`: int
- `events_analyzed`: int
- `duration_seconds`: float
- `error_message`: str (if failed)
- `events_count`: int (current total)
- `recent_logs`: list of recent runs

**Example:**
```python
status = anvil.server.call('get_refresh_status')
print(f"Last run: {status['last_run']}")
print(f"Status: {status['status']}")
print(f"Events in database: {status['events_count']}")
```

---

## Weather Data

### `get_weather_data()`
Get all weather forecasts from the database.

**Returns:** list of weather forecast dictionaries

**Example:**
```python
forecasts = anvil.server.call('get_weather_data')
for forecast in forecasts:
    print(f"{forecast['day_name']}: {forecast['conditions']}")
```

**Response Format:**
```python
{
  'date': datetime.date,
  'day_name': str,  # "Friday", "Saturday", "Sunday"
  'temp_high': int,
  'temp_low': int,
  'conditions': str,
  'precipitation_chance': int,  # 0-100
  'wind_speed': int,
  'hourly_data': list,
  'fetched_at': datetime
}
```

---

## Event Data

### `get_all_events(sort_by="recommendation")`
Get all events from the database.

**Parameters:**
- `sort_by` (optional): "recommendation" | "time" | "cost"

**Returns:** list of event dictionaries

**Example:**
```python
# Get events sorted by recommendation score
events = anvil.server.call('get_all_events')

# Get events sorted by time
events = anvil.server.call('get_all_events', sort_by='time')
```

---

### `get_filtered_events(filters)`
Get events filtered by various criteria.

**Parameters:**
- `filters`: dict with filter criteria (all optional):
  - `days`: list of day names (e.g., `["Friday", "Saturday"]`)
  - `cost_levels`: list of cost levels (e.g., `["Free", "$"]`)
  - `categories`: list of categories
  - `audience_types`: list of audience types
  - `indoor`: bool - include indoor events
  - `outdoor`: bool - include outdoor events

**Returns:** list of filtered event dictionaries

**Example:**
```python
filters = {
    'days': ['Friday', 'Saturday'],
    'cost_levels': ['Free', '$'],
    'categories': ['Music', 'Food & Drink'],
    'outdoor': True
}
events = anvil.server.call('get_filtered_events', filters)
```

---

### `search_events(search_text, filters=None)`
Search events by text and optionally apply filters.

**Parameters:**
- `search_text`: str - text to search in title, description, location
- `filters` (optional): same format as `get_filtered_events`

**Returns:** list of matching event dictionaries

**Example:**
```python
# Simple search
results = anvil.server.call('search_events', 'concert')

# Search with filters
filters = {'days': ['Saturday']}
results = anvil.server.call('search_events', 'live music', filters)
```

---

## Event Object Format

All event functions return dictionaries with this structure:

```python
{
  'event_id': str,
  'title': str,
  'description': str,
  'date': datetime.date,
  'day_name': str,  # "Friday", "Saturday", "Sunday"
  'start_time': str,  # "3:00 PM"
  'end_time': str or None,
  'location': str,
  'cost_raw': str,  # Original cost text
  'cost_level': str,  # "Free", "$", "$$", "$$$", "$$$$"
  'is_indoor': bool,
  'is_outdoor': bool,
  'audience_type': str,  # "adults", "family-friendly", "all-ages"
  'categories': list,  # e.g., ["Music", "Food & Drink"]
  'weather_score': int,  # 0-100
  'recommendation_score': int,  # 0-100
  'weather_warning': str or None  # e.g., "High chance of rain (80%)"
}
```

---

## Usage Examples

### Display Weekend Weather

```python
def show_weather(self):
    forecasts = anvil.server.call('get_weather_data')
    
    for forecast in forecasts:
        print(f"{forecast['day_name']}, {forecast['date']}")
        print(f"  High: {forecast['temp_high']}°F, Low: {forecast['temp_low']}°F")
        print(f"  {forecast['conditions']}")
        print(f"  Rain chance: {forecast['precipitation_chance']}%")
```

### Display Recommended Events

```python
def show_top_events(self):
    # Get events sorted by recommendation
    events = anvil.server.call('get_all_events', sort_by='recommendation')
    
    # Show top 10
    for event in events[:10]:
        print(f"{event['title']} - Score: {event['recommendation_score']}")
        if event['weather_warning']:
            print(f"  ⚠️ {event['weather_warning']}")
```

### Build a Filter Interface

```python
def apply_filters_click(self, **event_args):
    # Collect filter selections from UI
    filters = {
        'days': self.get_selected_days(),  # Your method to get checkboxes
        'cost_levels': self.get_selected_costs(),
        'categories': self.get_selected_categories(),
        'indoor': self.indoor_checkbox.checked,
        'outdoor': self.outdoor_checkbox.checked
    }
    
    # Get filtered events
    events = anvil.server.call('get_filtered_events', filters)
    
    # Update UI
    self.events_panel.items = events
```

### Search Events

```python
def search_box_change(self, **event_args):
    search_text = self.search_box.text
    
    if search_text:
        results = anvil.server.call('search_events', search_text)
        self.results_label.text = f"Found {len(results)} events"
        self.events_panel.items = results
    else:
        # Show all events
        self.events_panel.items = anvil.server.call('get_all_events')
```

### Monitor Data Refresh

```python
def refresh_button_click(self, **event_args):
    # Start refresh
    task = anvil.server.call('trigger_data_refresh')
    
    # Show loading state
    self.refresh_button.enabled = False
    self.status_label.text = "Refreshing data..."
    
    # Note: In production, you'd poll the task status or use task.wait()
```

---

## Available Categories

The AI can assign events to these categories:
- Arts
- Music
- Sports
- Food & Drink
- Outdoor Activities
- Cultural Events
- Theater/Performance
- Family/Kids
- Nightlife
- Shopping
- Educational
- Community Events
- Other

---

## Cost Levels

Events are categorized into these cost levels:
- `Free` - No cost
- `$` - Under $20
- `$$` - $20-50
- `$$$` - $50-100
- `$$$$` - Over $100

---

## Audience Types

Events are categorized for these audiences:
- `adults` - 21+ or adult-oriented content
- `family-friendly` - Suitable for families with children
- `all-ages` - Everyone welcome

