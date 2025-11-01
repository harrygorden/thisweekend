from ._anvil_designer import MainAppTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# Import our custom components
from ..WeatherCard import WeatherCard
from ..EventCard import EventCard
from ..AdminForm import AdminForm


class MainApp(MainAppTemplate):
    """
    Main user-facing application form for This Weekend
    
    Features:
    - 3-day weather forecast at the top
    - Filter panel on the left (cost, category, audience, venue type)
    - Event list on the right
    - Search functionality
    - Itinerary management
    """
    
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Initialize state
        self.all_events = []
        self.filtered_events = []
        self.selected_event_ids = set()
        
        # Active filters
        self.active_filters = {
            'days': [],
            'cost_levels': [],
            'categories': [],
            'audience_types': [],
            'indoor': True,
            'outdoor': True
        }
        
        # Load initial data
        self.load_initial_data()
    
    
    def load_initial_data(self):
        """Load weather and events from server"""
        try:
            # Show loading
            self.loading_label.visible = True
            self.loading_label.text = "Loading weekend data..."
            
            # Load weather
            self.load_weather_forecast()
            
            # Load weekend suggestions
            self.load_weekend_suggestions()
            
            # Load events
            self.load_events()
            
            # Hide loading
            self.loading_label.visible = False
            
        except Exception as e:
            self.loading_label.text = f"Error loading data: {str(e)}"
            self.loading_label.foreground = "red"
            print(f"Error in load_initial_data: {e}")
    
    
    def load_weather_forecast(self):
        """Load and display 3-day weather forecast"""
        try:
            weather_data = anvil.server.call('get_weather_data')
            
            if weather_data:
                # Sort by date
                weather_data.sort(key=lambda w: w['date'])
                
                # Clear existing weather cards
                self.weather_container.clear()
                
                # Create weather cards for first 3 days (Friday, Saturday, Sunday)
                for i, day_weather in enumerate(weather_data[:3]):
                    try:
                        weather_card = WeatherCard()
                        weather_card.set_weather_data(day_weather)
                        self.weather_container.add_component(weather_card)
                    except Exception as card_error:
                        print(f"Error creating WeatherCard: {card_error}")
                        # Show fallback text if WeatherCard component isn't ready
                        fallback_label = Label(
                            text=f"{day_weather.get('day_name', 'Unknown')}: {int(day_weather.get('temp_high', 0))}°F / {int(day_weather.get('temp_low', 0))}°F - {day_weather.get('conditions', 'Unknown')}",
                            font_size=14,
                            spacing_above="small",
                            spacing_below="small"
                        )
                        self.weather_container.add_component(fallback_label)
                
                # Update summary text
                if len(weather_data) >= 3:
                    self.weather_summary_label.text = (
                        f"Weekend Outlook: {weather_data[0]['conditions']} to {weather_data[2]['conditions']}, "
                        f"{int(weather_data[0]['temp_low'])}-{int(weather_data[2]['temp_high'])}°F"
                    )
            else:
                self.weather_summary_label.text = "No weather data available"
                
        except Exception as e:
            print(f"Error loading weather: {e}")
            self.weather_summary_label.text = "Weather forecast unavailable"
    
    
    def load_weekend_suggestions(self):
        """Load AI-generated weekend suggestions"""
        try:
            # Set loading state
            self.suggestions_text.text = "Generating personalized suggestions..."
            self.suggestions_text.italic = True
            
            # Get suggestions from server
            suggestions = anvil.server.call('get_weekend_suggestions')
            
            if suggestions:
                self.suggestions_text.text = suggestions
                self.suggestions_text.italic = False
            else:
                # Hide the section if no suggestions
                self.suggestions_section.visible = False
                
        except Exception as e:
            print(f"Error loading suggestions: {e}")
            # Show a friendly fallback message
            self.suggestions_text.text = "Explore the events below to find your perfect weekend activities!"
            self.suggestions_text.italic = False
    
    
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
        self.display_events()
        self.update_event_count()
    
    
    def display_events(self):
        """Display events in the events panel"""
        # Clear existing events
        self.events_container.clear()
        
        if not self.filtered_events:
            # Show "no events" message
            no_events_label = Label(
                text="No events match your filters. Try adjusting your criteria.",
                align="center",
                foreground="#999999",
                font_size=16,
                spacing_above="large",
                spacing_below="large"
            )
            self.events_container.add_component(no_events_label)
            return
        
        # Create event cards
        for event in self.filtered_events:
            try:
                event_card = EventCard()
                event_card.set_event_data(event)
                
                # Check if event is in itinerary
                if event['event_id'] in self.selected_event_ids:
                    event_card.is_selected = True
                    event_card.update_favorite_button()
                
                self.events_container.add_component(event_card)
            except Exception as card_error:
                print(f"Error creating EventCard: {card_error}")
                # Show fallback simple event display
                fallback_label = Label(
                    text=f"📅 {event.get('title', 'Event')} - {event.get('day_name', 'TBD')} @ {event.get('start_time', 'TBD')}",
                    font_size=14,
                    spacing_above="small",
                    spacing_below="small",
                    bold=True
                )
                self.events_container.add_component(fallback_label)
    
    
    def update_event_count(self):
        """Update the event count display"""
        total = len(self.all_events)
        shown = len(self.filtered_events)
        
        if shown == total:
            self.event_count_label.text = f"Showing all {total} events"
        else:
            self.event_count_label.text = f"Showing {shown} of {total} events"
    
    
    # Search functionality
    def search_box_change(self, **event_args):
        """Handle search box text change"""
        self.apply_filters()
    
    
    def search_box_pressed_enter(self, **event_args):
        """Handle enter key in search box"""
        self.apply_filters()
    
    
    # Filter handlers - Days
    def day_filter_changed(self, day_name, is_checked):
        """Generic handler for day filter changes"""
        if is_checked:
            if day_name not in self.active_filters['days']:
                self.active_filters['days'].append(day_name)
        else:
            if day_name in self.active_filters['days']:
                self.active_filters['days'].remove(day_name)
        self.apply_filters()
    
    def friday_check_change(self, **event_args):
        self.day_filter_changed('Friday', self.friday_check.checked)
    
    def saturday_check_change(self, **event_args):
        self.day_filter_changed('Saturday', self.saturday_check.checked)
    
    def sunday_check_change(self, **event_args):
        self.day_filter_changed('Sunday', self.sunday_check.checked)
    
    
    # Filter handlers - Cost
    def cost_filter_changed(self, cost_level, is_checked):
        """Generic handler for cost filter changes"""
        if is_checked:
            if cost_level not in self.active_filters['cost_levels']:
                self.active_filters['cost_levels'].append(cost_level)
        else:
            if cost_level in self.active_filters['cost_levels']:
                self.active_filters['cost_levels'].remove(cost_level)
        self.apply_filters()
    
    def cost_free_check_change(self, **event_args):
        self.cost_filter_changed('Free', self.cost_free_check.checked)
    
    def cost_1_check_change(self, **event_args):
        self.cost_filter_changed('$', self.cost_1_check.checked)
    
    def cost_2_check_change(self, **event_args):
        self.cost_filter_changed('$$', self.cost_2_check.checked)
    
    def cost_3_check_change(self, **event_args):
        self.cost_filter_changed('$$$', self.cost_3_check.checked)
    
    def cost_4_check_change(self, **event_args):
        self.cost_filter_changed('$$$$', self.cost_4_check.checked)
    
    
    # Filter handlers - Categories
    def category_filter_changed(self, category, is_checked):
        """Generic handler for category filter changes"""
        if is_checked:
            if category not in self.active_filters['categories']:
                self.active_filters['categories'].append(category)
        else:
            if category in self.active_filters['categories']:
                self.active_filters['categories'].remove(category)
        self.apply_filters()
    
    def cat_arts_check_change(self, **event_args):
        self.category_filter_changed('Arts', self.cat_arts_check.checked)
    
    def cat_music_check_change(self, **event_args):
        self.category_filter_changed('Music', self.cat_music_check.checked)
    
    def cat_sports_check_change(self, **event_args):
        self.category_filter_changed('Sports', self.cat_sports_check.checked)
    
    def cat_food_check_change(self, **event_args):
        self.category_filter_changed('Food & Drink', self.cat_food_check.checked)
    
    def cat_outdoor_check_change(self, **event_args):
        self.category_filter_changed('Outdoor Activities', self.cat_outdoor_check.checked)
    
    def cat_cultural_check_change(self, **event_args):
        self.category_filter_changed('Cultural Events', self.cat_cultural_check.checked)
    
    def cat_theater_check_change(self, **event_args):
        self.category_filter_changed('Theater/Performance', self.cat_theater_check.checked)
    
    def cat_family_check_change(self, **event_args):
        self.category_filter_changed('Family/Kids', self.cat_family_check.checked)
    
    def cat_nightlife_check_change(self, **event_args):
        self.category_filter_changed('Nightlife', self.cat_nightlife_check.checked)
    
    
    # Filter handlers - Audience
    def audience_filter_changed(self, audience_type, is_checked):
        """Generic handler for audience filter changes"""
        if is_checked:
            if audience_type not in self.active_filters['audience_types']:
                self.active_filters['audience_types'].append(audience_type)
        else:
            if audience_type in self.active_filters['audience_types']:
                self.active_filters['audience_types'].remove(audience_type)
        self.apply_filters()
    
    def aud_adults_check_change(self, **event_args):
        self.audience_filter_changed('adults', self.aud_adults_check.checked)
    
    def aud_family_check_change(self, **event_args):
        self.audience_filter_changed('family-friendly', self.aud_family_check.checked)
    
    def aud_all_check_change(self, **event_args):
        self.audience_filter_changed('all-ages', self.aud_all_check.checked)
    
    
    # Filter handlers - Venue Type
    def indoor_check_change(self, **event_args):
        self.active_filters['indoor'] = self.indoor_check.checked
        self.apply_filters()
    
    def outdoor_check_change(self, **event_args):
        self.active_filters['outdoor'] = self.outdoor_check.checked
        self.apply_filters()
    
    
    # Clear filters
    def clear_filters_button_click(self, **event_args):
        """Clear all filters"""
        # Reset day filters
        self.friday_check.checked = False
        self.saturday_check.checked = False
        self.sunday_check.checked = False
        
        # Reset cost filters
        self.cost_free_check.checked = False
        self.cost_1_check.checked = False
        self.cost_2_check.checked = False
        self.cost_3_check.checked = False
        self.cost_4_check.checked = False
        
        # Reset category filters
        self.cat_arts_check.checked = False
        self.cat_music_check.checked = False
        self.cat_sports_check.checked = False
        self.cat_food_check.checked = False
        self.cat_outdoor_check.checked = False
        self.cat_cultural_check.checked = False
        self.cat_theater_check.checked = False
        self.cat_family_check.checked = False
        self.cat_nightlife_check.checked = False
        
        # Reset audience filters
        self.aud_adults_check.checked = False
        self.aud_family_check.checked = False
        self.aud_all_check.checked = False
        
        # Reset venue type filters
        self.indoor_check.checked = True
        self.outdoor_check.checked = True
        
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
    
    
    # Itinerary management
    def toggle_event_in_itinerary(self, event_id):
        """Add or remove event from itinerary (called by EventCard)"""
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
            self.itinerary_button.icon = "fa:calendar-check"
        else:
            self.itinerary_button.text = "My Itinerary"
            self.itinerary_button.icon = "fa:calendar-o"
    
    
    def itinerary_button_click(self, **event_args):
        """Show itinerary view"""
        if len(self.selected_event_ids) == 0:
            alert("Your itinerary is empty.\n\nClick 'Add to Itinerary' on events to save them!")
            return
        
        # Get selected events
        selected_events = [e for e in self.all_events if e['event_id'] in self.selected_event_ids]
        
        # Sort by date and time
        selected_events.sort(key=lambda e: (e.get('date'), e.get('start_time', '')))
        
        # Build itinerary text
        itinerary_text = self.build_itinerary_text(selected_events)
        
        # Show in alert
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
                    lines.append(f"   💰 {event.get('cost_level', 'Unknown')}")
                    
                    if event.get('weather_warning'):
                        lines.append(f"   ⚠️ {event['weather_warning']}")
                    
                    lines.append("")  # Blank line
        
        return '\n'.join(lines)
    
    
    def refresh_button_click(self, **event_args):
        """Refresh data from server"""
        self.load_initial_data()
        alert("Data refreshed!", title="Success")
    
    
    def admin_link_click(self, **event_args):
        """Handle admin link click - prompt for password"""
        # Create a password textbox
        password_box = TextBox(
            placeholder="Enter admin password",
            type="password",
            spacing_above="small",
            spacing_below="small"
        )
        
        # Show password prompt
        result = alert(
            content=password_box,
            title="🔒 Admin Access",
            buttons=[("Login", True), ("Cancel", False)]
        )
        
        # If user clicked Login
        if result:
            password = password_box.text
            
            if not password:
                alert("Please enter a password", title="Error")
                return
            
            # Check password with server
            try:
                is_valid = anvil.server.call('check_admin_password', password)
                
                if is_valid:
                    # Password correct - open AdminForm
                    open_form(AdminForm())
                else:
                    alert("Incorrect password", title="Access Denied")
            
            except Exception as e:
                alert(f"Error checking password: {str(e)}", title="Error")

