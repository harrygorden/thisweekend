"""
Test data generation module for This Weekend app.

Provides realistic sample events for testing and development
when the scraping service is unavailable.
"""

import anvil.server
from anvil.tables import app_tables
from datetime import datetime, date, timedelta

from . import api_helpers


@anvil.server.callable
def create_test_events():
    """
    Create realistic test events for development and testing.
    
    Returns:
        int: Number of test events created
    """
    print("Creating test events...")
    
    # Get weekend dates
    weekend_dates = api_helpers.get_weekend_dates()
    
    # Sample events
    test_events = [
        # Friday Events
        {
            "title": "Live Jazz at Railgarten",
            "description": "Enjoy live jazz music in the outdoor beer garden with local food trucks. Features Memphis jazz legends performing classic and contemporary pieces.",
            "date": weekend_dates["friday"],
            "start_time": "7:00 PM",
            "end_time": "10:00 PM",
            "location": "Railgarten, Downtown",
            "cost_raw": "$10 cover",
            "cost_level": "$",
            "is_indoor": False,
            "is_outdoor": True,
            "audience_type": "adults",
            "categories": ["Music", "Nightlife", "Food & Drink"]
        },
        {
            "title": "Food Truck Friday at Overton Square",
            "description": "Over 20 food trucks gather for the weekly Food Truck Friday event. Live music, outdoor seating, and family-friendly atmosphere.",
            "date": weekend_dates["friday"],
            "start_time": "5:00 PM",
            "end_time": "9:00 PM",
            "location": "Overton Square",
            "cost_raw": "Free admission, food varies",
            "cost_level": "$$",
            "is_indoor": False,
            "is_outdoor": True,
            "audience_type": "family-friendly",
            "categories": ["Food & Drink", "Community Events"]
        },
        {
            "title": "Indie Film Night at Crosstown Theater",
            "description": "Independent film screening followed by director Q&A. This week featuring award-winning documentary about Memphis music history.",
            "date": weekend_dates["friday"],
            "start_time": "8:00 PM",
            "end_time": "10:30 PM",
            "location": "Crosstown Theater",
            "cost_raw": "$12 general admission",
            "cost_level": "$",
            "is_indoor": True,
            "is_outdoor": False,
            "audience_type": "adults",
            "categories": ["Arts", "Cultural Events"]
        },
        
        # Saturday Events
        {
            "title": "Cooper-Young Farmers Market",
            "description": "Weekly farmers market featuring local produce, artisan goods, live music, and food vendors. Pet-friendly and family-oriented.",
            "date": weekend_dates["saturday"],
            "start_time": "8:00 AM",
            "end_time": "1:00 PM",
            "location": "Cooper-Young Historic District",
            "cost_raw": "Free",
            "cost_level": "Free",
            "is_indoor": False,
            "is_outdoor": True,
            "audience_type": "family-friendly",
            "categories": ["Shopping", "Food & Drink", "Community Events"]
        },
        {
            "title": "Memphis Zoo - Wild Encounters",
            "description": "Special exhibit featuring rare animals from around the world. Includes keeper talks, feeding demonstrations, and interactive experiences.",
            "date": weekend_dates["saturday"],
            "start_time": "9:00 AM",
            "end_time": "5:00 PM",
            "location": "Memphis Zoo, Overton Park",
            "cost_raw": "$18 adults, $13 children",
            "cost_level": "$$",
            "is_indoor": True,
            "is_outdoor": True,
            "audience_type": "family-friendly",
            "categories": ["Family/Kids", "Educational", "Outdoor Activities"]
        },
        {
            "title": "Beale Street Music Festival Pre-Party",
            "description": "All-day music event featuring 15+ bands across 3 stages. Blues, rock, soul, and Memphis classics. Full bar and food vendors.",
            "date": weekend_dates["saturday"],
            "start_time": "2:00 PM",
            "end_time": "11:00 PM",
            "location": "Beale Street",
            "cost_raw": "$35 advance, $45 at door",
            "cost_level": "$$$",
            "is_indoor": False,
            "is_outdoor": True,
            "audience_type": "all-ages",
            "categories": ["Music", "Cultural Events"]
        },
        {
            "title": "Art Gallery Opening - Contemporary Memphis",
            "description": "Opening reception for new contemporary art exhibit featuring local Memphis artists. Wine, cheese, and artist talks throughout the evening.",
            "date": weekend_dates["saturday"],
            "start_time": "6:00 PM",
            "end_time": "9:00 PM",
            "location": "Metal Museum",
            "cost_raw": "Free",
            "cost_level": "Free",
            "is_indoor": True,
            "is_outdoor": False,
            "audience_type": "all-ages",
            "categories": ["Arts", "Cultural Events"]
        },
        {
            "title": "Kayaking on the Wolf River",
            "description": "Guided kayak tour through the scenic Wolf River wetlands. All equipment provided. No experience necessary. Meet at Ghost River State Natural Area.",
            "date": weekend_dates["saturday"],
            "start_time": "10:00 AM",
            "end_time": "2:00 PM",
            "location": "Ghost River State Natural Area",
            "cost_raw": "$45 per person",
            "cost_level": "$$",
            "is_indoor": False,
            "is_outdoor": True,
            "audience_type": "all-ages",
            "categories": ["Outdoor Activities", "Sports"]
        },
        
        # Sunday Events
        {
            "title": "Sunday Brunch & Blues at B.B. King's",
            "description": "Gospel brunch with live blues music. Southern buffet featuring Memphis BBQ, fried chicken, biscuits, and classic sides.",
            "date": weekend_dates["sunday"],
            "start_time": "11:00 AM",
            "end_time": "2:00 PM",
            "location": "B.B. King's Blues Club, Beale Street",
            "cost_raw": "$28 per person",
            "cost_level": "$$",
            "is_indoor": True,
            "is_outdoor": False,
            "audience_type": "all-ages",
            "categories": ["Music", "Food & Drink"]
        },
        {
            "title": "Memphis Botanic Garden - Fall Festival",
            "description": "Seasonal festival celebrating autumn with pumpkin patch, hayrides, live music, food vendors, and botanical workshops. Perfect for families.",
            "date": weekend_dates["sunday"],
            "start_time": "10:00 AM",
            "end_time": "4:00 PM",
            "location": "Memphis Botanic Garden",
            "cost_raw": "$15 adults, $10 children",
            "cost_level": "$$",
            "is_indoor": False,
            "is_outdoor": True,
            "audience_type": "family-friendly",
            "categories": ["Family/Kids", "Outdoor Activities"]
        },
        {
            "title": "Yoga in the Park",
            "description": "Free outdoor yoga session for all skill levels. Bring your own mat. Donation-based, all proceeds go to local park conservation.",
            "date": weekend_dates["sunday"],
            "start_time": "9:00 AM",
            "end_time": "10:30 AM",
            "location": "Shelby Farms Park",
            "cost_raw": "Free (donations welcome)",
            "cost_level": "Free",
            "is_indoor": False,
            "is_outdoor": True,
            "audience_type": "all-ages",
            "categories": ["Outdoor Activities", "Community Events"]
        },
        {
            "title": "Orpheum Theatre - Hamilton",
            "description": "Tony Award-winning musical Hamilton comes to Memphis! An American Musical that tells the story of founding father Alexander Hamilton through hip-hop, R&B, and Broadway.",
            "date": weekend_dates["sunday"],
            "start_time": "7:30 PM",
            "end_time": "10:00 PM",
            "location": "Orpheum Theatre, Downtown",
            "cost_raw": "$75-$200 depending on seating",
            "cost_level": "$$$$",
            "is_indoor": True,
            "is_outdoor": False,
            "audience_type": "all-ages",
            "categories": ["Theater/Performance", "Arts"]
        },
        {
            "title": "Memphis Tigers Football Watch Party",
            "description": "Watch the Memphis Tigers game on big screens with fellow fans. Drink specials, giveaways, and post-game analysis. Outdoor patio seating available.",
            "date": weekend_dates["sunday"],
            "start_time": "2:00 PM",
            "end_time": "6:00 PM",
            "location": "Wiseacre Brewing Co.",
            "cost_raw": "Free (food and drink purchase encouraged)",
            "cost_level": "$",
            "is_indoor": True,
            "is_outdoor": True,
            "audience_type": "adults",
            "categories": ["Sports", "Food & Drink"]
        },
        {
            "title": "Vintage Market at Central Station",
            "description": "Monthly vintage and antique market with 50+ vendors. Furniture, clothing, records, art, and collectibles. Live music and food trucks.",
            "date": weekend_dates["saturday"],
            "start_time": "10:00 AM",
            "end_time": "5:00 PM",
            "location": "Central Station Hotel",
            "cost_raw": "$5 admission",
            "cost_level": "$",
            "is_indoor": True,
            "is_outdoor": False,
            "audience_type": "all-ages",
            "categories": ["Shopping", "Arts"]
        }
    ]
    
    # Add events to database
    created_count = 0
    
    try:
        for event_data in test_events:
            # Generate unique ID
            event_id = api_helpers.generate_unique_id("test_evt")
            
            # Add to database
            app_tables.events.add_row(
                event_id=event_id,
                title=event_data["title"],
                description=event_data["description"],
                date=event_data["date"],
                start_time=event_data["start_time"],
                end_time=event_data.get("end_time"),
                location=event_data["location"],
                cost_raw=event_data["cost_raw"],
                cost_level=event_data["cost_level"],
                is_indoor=event_data["is_indoor"],
                is_outdoor=event_data["is_outdoor"],
                audience_type=event_data["audience_type"],
                categories=event_data["categories"],
                scraped_at=datetime.now(),
                analyzed_at=datetime.now(),
                weather_score=None,  # Will be calculated
                recommendation_score=None  # Will be calculated
            )
            
            created_count += 1
        
        print(f"Created {created_count} test events")
        
        # Now calculate weather scores and recommendations
        from . import data_processor
        
        print("Calculating weather scores...")
        data_processor.match_events_with_weather()
        
        print("Calculating recommendation scores...")
        data_processor.update_all_recommendation_scores()
        
        print(f"✅ Test data ready! {created_count} events with scores calculated")
        
        return created_count
        
    except Exception as e:
        print(f"Error creating test events: {str(e)}")
        raise


@anvil.server.callable
def clear_test_events():
    """
    Clear all test events (ones with event_id starting with 'test_evt').
    
    Returns:
        int: Number of events deleted
    """
    deleted = 0
    
    for event in app_tables.events.search():
        if event["event_id"] and event["event_id"].startswith("test_evt"):
            event.delete()
            deleted += 1
    
    print(f"Deleted {deleted} test events")
    return deleted

