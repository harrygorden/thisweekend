"""
API Testing Module for This Weekend App

Provides callable functions to test each API from client code.
"""

import anvil.server
from datetime import datetime


@anvil.server.callable
def test_openweather_api():
    """
    Test OpenWeather API connection and data retrieval.
    
    Returns:
        dict: Test results with weather data or error
    """
    from . import weather_service
    
    result = {
        'success': False,
        'timestamp': datetime.now()
    }
    
    try:
        print("Testing OpenWeather API...")
        weather_data = weather_service.fetch_weekend_weather()
        
        result['success'] = True
        result['days_count'] = len(weather_data)
        result['weather_data'] = weather_data
        
        print(f"✅ OpenWeather test passed! Got {len(weather_data)} days")
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        print(f"❌ OpenWeather test failed: {str(e)}")
    
    return result


@anvil.server.callable
def test_openai_api():
    """
    Test OpenAI API connection with a sample event analysis.
    
    Returns:
        dict: Test results with AI analysis or error
    """
    from . import ai_service
    
    result = {
        'success': False,
        'timestamp': datetime.now()
    }
    
    # Create test event
    test_event = {
        'title': 'Live Jazz Concert at Overton Park',
        'description': 'Outdoor jazz concert featuring local Memphis musicians. Bring blankets and chairs for lawn seating. Food trucks and beverages available.',
        'location': 'Overton Park Shell',
        'cost_raw': '$15 advance tickets, $20 at door'
    }
    
    try:
        print("Testing OpenAI API...")
        analysis = ai_service.analyze_event(test_event)
        
        result['success'] = True
        result['test_event'] = test_event
        result['analysis'] = analysis
        
        print(f"✅ OpenAI test passed! Event analyzed")
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        print(f"❌ OpenAI test failed: {str(e)}")
    
    return result

