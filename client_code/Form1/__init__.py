from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Form1(Form1Template):
    """
    Main application form for This Weekend
    
    Displays weather forecasts and weekend events with filtering,
    search, and itinerary building capabilities.
    """
    
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

        # Initialize state
        self.all_events = []
        self.filtered_events = []
        self.selected_event_ids = set()
        self.active_filters = {
            'days': [],
            'cost_levels': [],
            'categories': [],
            'audience_types': [],
            'indoor': True,
            'outdoor': True
        }
        
        # Load initial data
        self.load_data()
    
    
    def load_data(self):
        """Load weather and events from server"""
        try:
            # Show loading indicator
            self.status_label.text = "Loading data..."
            self.status_label.visible = True
            
            # Load weather
            self.load_weather()
            
            # Load events
            self.load_events()
            
            # Update last refresh time
            self.update_last_refresh()
            
            # Hide loading indicator
            self.status_label.visible = False
            
        except Exception as e:
            self.status_label.text = f"Error loading data: {str(e)}"
            self.status_label.foreground = "red"
            print(f"Error in load_data: {e}")
    
    
    def load_weather(self):
        """Load and display weather forecasts"""
        try:
            weather_data = anvil.server.call('get_weather_data')
            
            if weather_data:
                # Sort by date
                weather_data.sort(key=lambda w: w['date'])
                
                # Display weather cards (we'll bind to repeating panel)
                self.weather_panel.items = weather_data
                
                # Update header weather summary
                if len(weather_data) >= 3:
                    self.weekend_summary_label.text = (
                        f"This Weekend: {weather_data[0]['conditions']} to {weather_data[2]['conditions']}, "
                        f"{weather_data[0]['temp_low']}-{weather_data[2]['temp_high']}°F"
                    )
            else:
                self.weekend_summary_label.text = "No weather data available"
                
        except Exception as e:
            print(f"Error loading weather: {e}")
            self.weekend_summary_label.text = "Weather unavailable"
    
    
    def load_events(self):
        """Load events from server"""
        try:
            # Get all events, sorted by recommendation score
            self.all_events = anvil.server.call('get_all_events', sort_by='recommendation')
            
            # Apply current filters
            self.apply_filters()
            
            # Update event count
            self.update_event_count()
            
        except Exception as e:
            print(f"Error loading events: {e}")
            alert(f"Error loading events: {str(e)}")
    
    
    def apply_filters(self):
        """Apply current filters to events"""
        # Start with all events
        filtered = self.all_events
        
        # Apply search if active
        search_text = self.search_box.text
        if search_text and search_text.strip():
            search_lower = search_text.lower().strip()
            filtered = [
                e for e in filtered
                if (search_lower in e['title'].lower() or
                    search_lower in e.get('description', '').lower() or
                    search_lower in e.get('location', '').lower())
            ]
        
        # Apply day filter
        if self.active_filters['days']:
            filtered = [e for e in filtered if e['day_name'] in self.active_filters['days']]
        
        # Apply cost filter
        if self.active_filters['cost_levels']:
            filtered = [e for e in filtered if e['cost_level'] in self.active_filters['cost_levels']]
        
        # Apply category filter
        if self.active_filters['categories']:
            filtered = [
                e for e in filtered
                if any(cat in e.get('categories', []) for cat in self.active_filters['categories'])
            ]
        
        # Apply audience filter
        if self.active_filters['audience_types']:
            filtered = [e for e in filtered if e['audience_type'] in self.active_filters['audience_types']]
        
        # Apply indoor/outdoor filter
        if not self.active_filters['indoor']:
            filtered = [e for e in filtered if not e.get('is_indoor')]
        if not self.active_filters['outdoor']:
            filtered = [e for e in filtered if not e.get('is_outdoor')]
        
        # Update filtered events
        self.filtered_events = filtered
        
        # Update display
        self.events_panel.items = self.filtered_events
        self.update_event_count()
    
    
    def update_event_count(self):
        """Update the event count display"""
        total = len(self.all_events)
        shown = len(self.filtered_events)
        
        if shown == total:
            self.event_count_label.text = f"Showing all {total} events"
        else:
            self.event_count_label.text = f"Showing {shown} of {total} events"
    
    
    def update_last_refresh(self):
        """Update the last refresh timestamp"""
        try:
            last_refresh = anvil.server.call('get_last_refresh_time')
            if last_refresh:
                self.last_refresh_label.text = f"Updated: {last_refresh.strftime('%b %d, %I:%M %p')}"
            else:
                self.last_refresh_label.text = "No data yet"
        except:
            self.last_refresh_label.text = ""
    
    
    # Search functionality
    def search_box_change(self, **event_args):
        """Handle search box text change"""
        self.apply_filters()
    
    
    def search_box_pressed_enter(self, **event_args):
        """Handle enter key in search box"""
        self.apply_filters()
    
    
    # Filter panel - Days
    def friday_checkbox_change(self, **event_args):
        """Friday filter changed"""
        if self.friday_checkbox.checked:
            self.active_filters['days'].append('Friday')
        else:
            self.active_filters['days'].remove('Friday')
        self.apply_filters()
    
    
    def saturday_checkbox_change(self, **event_args):
        """Saturday filter changed"""
        if self.saturday_checkbox.checked:
            self.active_filters['days'].append('Saturday')
        else:
            self.active_filters['days'].remove('Saturday')
        self.apply_filters()
    
    
    def sunday_checkbox_change(self, **event_args):
        """Sunday filter changed"""
        if self.sunday_checkbox.checked:
            self.active_filters['days'].append('Sunday')
        else:
            self.active_filters['days'].remove('Sunday')
        self.apply_filters()
    
    
    # Filter panel - Cost
    def cost_free_checkbox_change(self, **event_args):
        """Free events filter"""
        self.update_cost_filter('Free', self.cost_free_checkbox.checked)
    
    
    def cost_1_checkbox_change(self, **event_args):
        """$ events filter"""
        self.update_cost_filter('$', self.cost_1_checkbox.checked)
    
    
    def cost_2_checkbox_change(self, **event_args):
        """$$ events filter"""
        self.update_cost_filter('$$', self.cost_2_checkbox.checked)
    
    
    def cost_3_checkbox_change(self, **event_args):
        """$$$ events filter"""
        self.update_cost_filter('$$$', self.cost_3_checkbox.checked)
    
    
    def cost_4_checkbox_change(self, **event_args):
        """$$$$ events filter"""
        self.update_cost_filter('$$$$', self.cost_4_checkbox.checked)
    
    
    def update_cost_filter(self, cost_level, is_checked):
        """Update cost filter list"""
        if is_checked:
            if cost_level not in self.active_filters['cost_levels']:
                self.active_filters['cost_levels'].append(cost_level)
        else:
            if cost_level in self.active_filters['cost_levels']:
                self.active_filters['cost_levels'].remove(cost_level)
        self.apply_filters()
    
    
    # Filter panel - Indoor/Outdoor
    def indoor_checkbox_change(self, **event_args):
        """Indoor events filter"""
        self.active_filters['indoor'] = self.indoor_checkbox.checked
        self.apply_filters()
    
    
    def outdoor_checkbox_change(self, **event_args):
        """Outdoor events filter"""
        self.active_filters['outdoor'] = self.outdoor_checkbox.checked
        self.apply_filters()
    
    
    # Filter controls
    def clear_filters_button_click(self, **event_args):
        """Clear all filters"""
        # Reset all filter checkboxes
        self.friday_checkbox.checked = False
        self.saturday_checkbox.checked = False
        self.sunday_checkbox.checked = False
        
        self.cost_free_checkbox.checked = False
        self.cost_1_checkbox.checked = False
        self.cost_2_checkbox.checked = False
        self.cost_3_checkbox.checked = False
        self.cost_4_checkbox.checked = False
        
        self.indoor_checkbox.checked = True
        self.outdoor_checkbox.checked = True
        
        # Clear search
        self.search_box.text = ""
        
        # Reset filter state
        self.active_filters = {
            'days': [],
            'cost_levels': [],
            'categories': [],
            'audience_types': [],
            'indoor': True,
            'outdoor': True
        }
        
        # Reapply (will show all events)
        self.apply_filters()
    
    
    # Sorting
    def sort_dropdown_change(self, **event_args):
        """Handle sort option change"""
        sort_by = self.sort_dropdown.selected_value
        
        if sort_by == 'recommendation':
            self.filtered_events.sort(key=lambda e: e.get('recommendation_score', 0), reverse=True)
        elif sort_by == 'time':
            self.filtered_events.sort(key=lambda e: (e.get('date'), e.get('start_time', '')))
        elif sort_by == 'cost':
            cost_order = {'Free': 0, '$': 1, '$$': 2, '$$$': 3, '$$$$': 4}
            self.filtered_events.sort(key=lambda e: cost_order.get(e.get('cost_level', '$'), 5))
        
        # Update display
        self.events_panel.items = self.filtered_events
    
    
    # Itinerary management
    def toggle_event_in_itinerary(self, event_id):
        """Add or remove event from itinerary"""
        if event_id in self.selected_event_ids:
            self.selected_event_ids.remove(event_id)
        else:
            self.selected_event_ids.add(event_id)
        
        # Update itinerary count
        self.update_itinerary_count()
    
    
    def update_itinerary_count(self):
        """Update itinerary badge count"""
        count = len(self.selected_event_ids)
        if count > 0:
            self.itinerary_button.text = f"My Itinerary ({count})"
            self.itinerary_button.icon = "fa:calendar-check-o"
        else:
            self.itinerary_button.text = "My Itinerary"
            self.itinerary_button.icon = "fa:calendar-o"
    
    
    def itinerary_button_click(self, **event_args):
        """Show itinerary view"""
        if len(self.selected_event_ids) == 0:
            alert("Your itinerary is empty.\n\nClick the ❤️ on events to add them!")
            return
        
        # Get selected events
        selected_events = [e for e in self.all_events if e['event_id'] in self.selected_event_ids]
        
        # Sort by date and time
        selected_events.sort(key=lambda e: (e.get('date'), e.get('start_time', '')))
        
        # Build itinerary text
        itinerary_text = self.build_itinerary_text(selected_events)
        
        # Show in alert (or could create a custom form)
        alert(
            content=itinerary_text,
            title=f"My Weekend Itinerary ({len(selected_events)} events)",
            large=True
        )
    
    
    def build_itinerary_text(self, events):
        """Build formatted itinerary text"""
        # Group by day
        by_day = {'Friday': [], 'Saturday': [], 'Sunday': []}
        
        for event in events:
            day = event.get('day_name', 'Unknown')
            if day in by_day:
                by_day[day].append(event)
        
        # Build text
        lines = []
        
        for day in ['Friday', 'Saturday', 'Sunday']:
            day_events = by_day[day]
            if day_events:
                lines.append(f"\n{'='*40}")
                lines.append(f"{day.upper()}")
                lines.append(f"{'='*40}\n")
                
                for event in day_events:
                    lines.append(f"⏰ {event.get('start_time', 'TBD')}")
                    lines.append(f"📍 {event['title']}")
                    lines.append(f"   {event.get('location', 'Location TBD')}")
                    
                    if event.get('weather_warning'):
                        lines.append(f"   ⚠️ {event['weather_warning']}")
                    
                    lines.append("")  # Blank line
        
        return '\n'.join(lines)
    
    
    def clear_itinerary_button_click(self, **event_args):
        """Clear the itinerary"""
        if len(self.selected_event_ids) == 0:
            return
        
        if confirm(f"Clear all {len(self.selected_event_ids)} events from your itinerary?"):
            self.selected_event_ids.clear()
            self.update_itinerary_count()
            # Refresh event display to update heart icons
            self.events_panel.items = self.filtered_events
    
    
    # Refresh data
    def refresh_button_click(self, **event_args):
        """Refresh data from server"""
        self.load_data()
        alert("Data refreshed!")
