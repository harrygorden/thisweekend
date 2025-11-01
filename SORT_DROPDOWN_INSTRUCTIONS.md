# Sort Dropdown UI Instructions

**Component:** Sort Order Dropdown for MainApp  
**Purpose:** Allow users to toggle between time and recommendation sorting

---

## Add to Anvil Designer

### 1. Open MainApp in Designer

In Anvil editor:
1. Click on `MainApp` in the file tree
2. Open in **Design** view

### 2. Add DropDown Component

**Location:** Near the top, next to or above the event list

**Component Type:** DropDown

**Properties:**
- **Name:** `sort_dropdown`
- **Placeholder:** "Sort by..."
- **Items:** `[('Soonest First', 'time'), ('Recommended', 'recommendation')]`
- **Selected Value:** `'time'` (default to chronological)
- **Include placeholder:** `False`

### 3. Add Change Event

**Event:** `change`  
**Handler:** `sort_dropdown_change`

This is already implemented in the code!

### 4. Optional: Add Label

Add a Label next to the dropdown:
- **Text:** "Sort:"
- **Font size:** 14
- **Bold:** True

---

## How It Works

### Code Implementation

```python
# In __init__
self.current_sort = 'time'  # Default to chronological

# Change handler
def sort_dropdown_change(self, **event_args):
    selected = self.sort_dropdown.selected_value
    
    if selected and selected != self.current_sort:
        self.current_sort = selected
        self.load_events()  # Reload with new sort

# Load events uses current sort
def load_events(self):
    self.all_events = anvil.server.call('get_all_events', sort_by=self.current_sort)
```

### Sort Options

**Option 1: Soonest First (time)**
- Value: `'time'`
- Behavior: Events sorted chronologically (earliest first)
- Best for: Planning your weekend in order

**Option 2: Recommended (recommendation)**
- Value: `'recommendation'`
- Behavior: Events sorted by weather + popularity score
- Best for: Finding the best events for the conditions

### User Flow

```
1. User opens app → Default: Soonest First
2. Events shown chronologically
3. User changes dropdown to "Recommended"
4. Events reload sorted by recommendation score
5. User changes back to "Soonest First"
6. Events reload chronologically
```

---

## UI Placement Suggestions

### Option 1: Above Event List

```
┌────────────────────────────────────┐
│  [Search box...]                   │
│                                    │
│  Sort: [Soonest First ▼]          │
│                                    │
│  Showing 10 events by time         │
├────────────────────────────────────┤
│  Event cards...                    │
```

### Option 2: Next to Search

```
┌────────────────────────────────────┐
│  [Search box...]  Sort: [▼]       │
│                                    │
│  Showing 10 events by time         │
├────────────────────────────────────┤
│  Event cards...                    │
```

### Option 3: Filter Section

```
┌─ Filters ─────────┐
│ Days:             │
│ ☐ Friday          │
│ ☐ Saturday        │
│ ☐ Sunday          │
│                   │
│ Sort By:          │
│ [Soonest First ▼] │
└───────────────────┘
```

---

## DropDown Configuration

### Items Property

**Format:** List of tuples `(display_text, value)`

```python
items = [
    ('Soonest First', 'time'),
    ('Recommended', 'recommendation')
]
```

**Optional third option:**
```python
items = [
    ('Soonest First', 'time'),
    ('Recommended', 'recommendation'),
    ('Lowest Cost', 'cost')
]
```

### Alternative: Simple Items

If you prefer simpler configuration:

```python
items = ['Soonest First', 'Recommended']

# Then update handler:
def sort_dropdown_change(self, **event_args):
    selected = self.sort_dropdown.selected_value
    
    # Map display text to sort value
    sort_map = {
        'Soonest First': 'time',
        'Recommended': 'recommendation',
        'Lowest Cost': 'cost'
    }
    
    sort_value = sort_map.get(selected, 'time')
    
    if sort_value != self.current_sort:
        self.current_sort = sort_value
        self.load_events()
```

---

## Testing

After adding the dropdown:

1. **Test Sort Change:**
   - Change from "Soonest First" to "Recommended"
   - Verify events reorder
   - Check event count updates with sort label

2. **Test Default:**
   - Reload page
   - Should default to "Soonest First"

3. **Test with Filters:**
   - Apply some filters
   - Change sort order
   - Verify filtered events resort correctly

---

## Expected Behavior

### Soonest First (time)

```
Events displayed:
1. Friday 10:00 AM - Farmers Market
2. Friday 7:00 PM - Jazz Concert
3. Saturday 9:00 AM - Morning Yoga
4. Saturday 3:00 PM - Food Festival
5. Sunday 11:00 AM - Brunch Event
```

### Recommended (recommendation)

```
Events displayed:
1. Friday 7:00 PM - Jazz Concert (score: 95)
2. Saturday 9:00 AM - Morning Yoga (score: 92)
3. Sunday 11:00 AM - Brunch Event (score: 88)
4. Friday 10:00 AM - Farmers Market (score: 85)
5. Saturday 3:00 PM - Food Festival (score: 55)
```

---

## Quick Add Steps

1. Open MainApp in Anvil Designer
2. Drag **DropDown** component from toolbox
3. Name it `sort_dropdown`
4. Set items: `[('Soonest First', 'time'), ('Recommended', 'recommendation')]`
5. Set selected_value: `'time'`
6. Add event: `change` → `sort_dropdown_change`
7. Save and test!

**All handler code is already implemented - just add the UI component!** ✅


