from ._anvil_designer import EventCardTemplate
from anvil import *
import anvil.server


class EventCard(EventCardTemplate):
    """
    Event card component for displaying individual events
    
    Used in RepeatingPanel to show event details with:
    - Title, date, time, location
    - Cost, categories, audience type
    - Weather warning for outdoor events
    - Add to itinerary button
    """
    
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Store event data
        self.event_data = None
        self.is_selected = False
    
    
    def set_event_data(self, event):
        """Set the event data and update display"""
        self.event_data = event
        self.update_display()
    
    
    def update_display(self):
        """Update all UI elements with event data"""
        if not self.event_data:
            return
        
        event = self.event_data
        
        # Title
        self.title_label.text = event.get('title', 'Untitled Event')
        
        # Date and time
        date_str = event.get('date').strftime('%A, %B %d') if event.get('date') else 'Date TBD'
        time_str = event.get('start_time', 'Time TBD')
        self.datetime_label.text = f"{date_str} • {time_str}"
        
        # Location
        self.location_label.text = f"📍 {event.get('location', 'Location TBD')}"
        
        # Description (truncated)
        description = event.get('description', '')
        if len(description) > 200:
            description = description[:197] + "..."
        self.description_label.text = description
        
        # Cost
        cost_level = event.get('cost_level', '$')
        self.cost_label.text = cost_level
        self.cost_label.foreground = self.get_cost_color(cost_level)
        
        # Indoor/Outdoor indicator
        if event.get('is_indoor') and event.get('is_outdoor'):
            self.indoor_outdoor_label.text = "🏠🌳 Indoor & Outdoor"
        elif event.get('is_indoor'):
            self.indoor_outdoor_label.text = "🏠 Indoor"
        elif event.get('is_outdoor'):
            self.indoor_outdoor_label.text = "🌳 Outdoor"
        else:
            self.indoor_outdoor_label.text = ""
        
        # Audience type
        audience = event.get('audience_type', 'all-ages')
        audience_icons = {
            'adults': '🍷 Adults',
            'family-friendly': '👨‍👩‍👧‍👦 Family-Friendly',
            'all-ages': '✨ All Ages'
        }
        self.audience_label.text = audience_icons.get(audience, audience)
        
        # Categories
        categories = event.get('categories', [])
        if categories:
            # Show up to 3 categories
            cats_to_show = categories[:3]
            self.categories_label.text = " • ".join(cats_to_show)
        else:
            self.categories_label.text = ""
        
        # Weather warning (for outdoor events)
        warning = event.get('weather_warning')
        if warning:
            self.weather_warning_label.text = f"⚠️ {warning}"
            self.weather_warning_label.visible = True
            self.weather_warning_label.foreground = "#ff6600"
        else:
            self.weather_warning_label.visible = False
        
        # Recommendation score (show as stars or badge)
        score = event.get('recommendation_score', 0)
        if score >= 90:
            self.recommendation_badge.text = "⭐ Highly Recommended"
            self.recommendation_badge.background = "#4CAF50"
        elif score >= 75:
            self.recommendation_badge.text = "👍 Recommended"
            self.recommendation_badge.background = "#2196F3"
        elif score >= 50:
            self.recommendation_badge.text = "✓ Good Option"
            self.recommendation_badge.background = "#9E9E9E"
        else:
            self.recommendation_badge.visible = False
        
        # Update favorite button state
        self.update_favorite_button()
    
    
    def get_cost_color(self, cost_level):
        """Get color for cost level"""
        colors = {
            'Free': '#4CAF50',  # Green
            '$': '#8BC34A',      # Light green
            '$$': '#FFC107',     # Amber
            '$$$': '#FF9800',    # Orange
            '$$$$': '#F44336'    # Red
        }
        return colors.get(cost_level, '#000000')
    
    
    def favorite_button_click(self, **event_args):
        """Toggle favorite/itinerary status"""
        if not self.event_data:
            return
        
        # Toggle selection
        self.is_selected = not self.is_selected
        
        # Notify parent form
        parent_form = self.parent.parent  # RepeatingPanel -> Form1
        if hasattr(parent_form, 'toggle_event_in_itinerary'):
            parent_form.toggle_event_in_itinerary(self.event_data['event_id'])
        
        # Update button display
        self.update_favorite_button()
    
    
    def update_favorite_button(self):
        """Update the favorite button appearance"""
        if self.is_selected:
            self.favorite_button.icon = "fa:heart"
            self.favorite_button.foreground = "#F44336"
            self.favorite_button.text = "In Itinerary"
        else:
            self.favorite_button.icon = "fa:heart-o"
            self.favorite_button.foreground = "#666666"
            self.favorite_button.text = "Add to Itinerary"
    
    
    def expand_button_click(self, **event_args):
        """Show full event details"""
        if not self.event_data:
            return
        
        event = self.event_data
        
        # Build detailed info
        details = []
        details.append(f"📅 {event.get('title', 'Event')}")
        details.append("=" * 50)
        details.append(f"\n🗓️ Date: {event.get('date').strftime('%A, %B %d, %Y') if event.get('date') else 'TBD'}")
        details.append(f"⏰ Time: {event.get('start_time', 'TBD')}")
        if event.get('end_time'):
            details.append(f"   Ends: {event['end_time']}")
        details.append(f"📍 Location: {event.get('location', 'TBD')}")
        details.append(f"💰 Cost: {event.get('cost_level', 'Unknown')}")
        
        if event.get('cost_raw'):
            details.append(f"   ({event['cost_raw']})")
        
        details.append(f"\n👥 Audience: {event.get('audience_type', 'Unknown')}")
        
        if event.get('is_indoor') or event.get('is_outdoor'):
            indoor_outdoor = []
            if event.get('is_indoor'):
                indoor_outdoor.append("Indoor")
            if event.get('is_outdoor'):
                indoor_outdoor.append("Outdoor")
            details.append(f"🏠 Venue Type: {' & '.join(indoor_outdoor)}")
        
        categories = event.get('categories', [])
        if categories:
            details.append(f"🏷️ Categories: {', '.join(categories)}")
        
        details.append(f"\n📝 Description:")
        details.append(event.get('description', 'No description available'))
        
        if event.get('weather_warning'):
            details.append(f"\n⚠️ Weather Warning:")
            details.append(event['weather_warning'])
        
        # Show in alert
        alert(
            content='\n'.join(details),
            title="Event Details",
            large=True
        )

