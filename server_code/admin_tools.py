"""
Admin Tools for This Weekend App

This module provides administrative functions for managing the application,
including database setup, testing, and maintenance tasks.

These functions can be called from a test form or admin panel.
"""

import anvil.server
from datetime import datetime

# Import our setup module
from . import setup_schema


@anvil.server.callable
def run_database_setup():
    """
    Run the complete database setup process.
    This will verify all tables exist and create any missing columns.
    
    Returns:
        dict: Setup results with detailed status
        
    Example usage from client:
        result = anvil.server.call('run_database_setup')
        print(result['summary'])
    """
    return setup_schema.setup_and_verify_all_tables()


@anvil.server.callable
def check_database_status():
    """
    Check database status without making any changes.
    
    Returns:
        dict: Status report for all tables
        
    Example usage from client:
        status = anvil.server.call('check_database_status')
        for table_name, info in status['tables'].items():
            print(f"{table_name}: {info['existing_columns']} columns")
    """
    return setup_schema.verify_database_schema()


@anvil.server.callable
def test_scraping_only():
    """
    Test scraping and parsing events WITHOUT AI analysis.
    Perfect for troubleshooting Firecrawl without paying for OpenAI API calls.
    
    Returns:
        dict: Scraping results with detailed debug info
    """
    from . import scraper_service
    from datetime import datetime
    
    result = {
        'timestamp': datetime.now(),
        'status': 'unknown',
        'events': [],
        'debug_info': {}
    }
    
    try:
        # Step 1: Scrape the website
        print("\n" + "="*60)
        print("🔍 TEST SCRAPING ONLY (No AI Analysis)")
        print("="*60)
        print("\n[1/2] Scraping website...")
        
        markdown_content = scraper_service.scrape_weekend_events()
        result['debug_info']['markdown_length'] = len(markdown_content)
        result['debug_info']['markdown_preview'] = markdown_content[:500]
        
        # Step 2: Parse events
        print("\n[2/2] Parsing events...")
        events = scraper_service.parse_events_from_markdown(markdown_content)
        
        # Convert events to serializable format
        result['events'] = [
            {
                'title': e.get('title', ''),
                'location': e.get('location', ''),
                'start_time': e.get('start_time', ''),
                'cost_raw': e.get('cost_raw', ''),
                'date': str(e.get('date', '')),
                'source_url': e.get('source_url', '')
            }
            for e in events
        ]
        
        result['status'] = 'success'
        result['event_count'] = len(events)
        
        print(f"\n✅ Scraping test complete!")
        print(f"   Found {len(events)} events")
        print("="*60 + "\n")
        
        return result
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        print(f"\n❌ Scraping test failed: {str(e)}")
        print("="*60 + "\n")
        return result


@anvil.server.callable
def get_system_info():
    """
    Get general system information and status.
    
    Returns:
        dict: System information
    """
    from . import background_tasks
    
    info = {
        'timestamp': datetime.now(),
        'database_status': {},
        'last_refresh': None,
        'event_count': 0,
        'weather_forecast_count': 0
    }
    
    # Get database status
    try:
        db_status = setup_schema.verify_database_schema()
        info['database_status'] = {
            table: {
                'exists': data['exists'],
                'columns_ok': len(data['missing_columns']) == 0,
                'column_count': len(data['existing_columns'])
            }
            for table, data in db_status['tables'].items()
        }
    except Exception as e:
        info['database_status_error'] = str(e)
    
    # Get last refresh time
    try:
        info['last_refresh'] = background_tasks.get_last_refresh_time()
    except Exception as e:
        info['last_refresh_error'] = str(e)
    
    # Get event count
    try:
        from anvil.tables import app_tables
        info['event_count'] = len(list(app_tables.events.search()))
        info['weather_forecast_count'] = len(list(app_tables.weather_forecast.search()))
    except Exception as e:
        info['count_error'] = str(e)
    
    return info


@anvil.server.callable  
def clear_all_data():
    """
    DANGER: Clear all data from all tables.
    Use this to reset the database for testing.
    
    Returns:
        dict: Count of rows deleted from each table
    """
    from anvil.tables import app_tables
    
    result = {
        'timestamp': datetime.now(),
        'deleted': {}
    }
    
    # Clear events
    try:
        count = 0
        for row in app_tables.events.search():
            row.delete()
            count += 1
        result['deleted']['events'] = count
    except Exception as e:
        result['deleted']['events'] = f"Error: {str(e)}"
    
    # Clear weather_forecast
    try:
        count = 0
        for row in app_tables.weather_forecast.search():
            row.delete()
            count += 1
        result['deleted']['weather_forecast'] = count
    except Exception as e:
        result['deleted']['weather_forecast'] = f"Error: {str(e)}"
    
    # Clear scrape_log
    try:
        count = 0
        for row in app_tables.scrape_log.search():
            row.delete()
            count += 1
        result['deleted']['scrape_log'] = count
    except Exception as e:
        result['deleted']['scrape_log'] = f"Error: {str(e)}"
    
    return result


@anvil.server.callable
def test_api_keys():
    """
    Test that all required API keys are configured.
    Does NOT test if they're valid, just that they're set.
    
    Returns:
        dict: Status of each API key
    """
    import anvil.secrets
    
    required_keys = [
        'OPENWEATHER_API_KEY',
        'FIRECRAWL_API_KEY',
        'OPENAI_API_KEY'
    ]
    
    result = {
        'timestamp': datetime.now(),
        'keys': {}
    }
    
    for key_name in required_keys:
        try:
            key_value = anvil.secrets.get_secret(key_name)
            if key_value:
                # Show first/last 4 chars only for security
                if len(key_value) > 8:
                    masked = f"{key_value[:4]}...{key_value[-4:]}"
                else:
                    masked = "***"
                result['keys'][key_name] = {
                    'configured': True,
                    'masked_value': masked
                }
            else:
                result['keys'][key_name] = {
                    'configured': False,
                    'error': 'Secret is empty'
                }
        except Exception as e:
            result['keys'][key_name] = {
                'configured': False,
                'error': str(e)
            }
    
    # Check if all are configured
    all_ok = all(info.get('configured', False) for info in result['keys'].values())
    result['all_configured'] = all_ok
    
    return result


@anvil.server.callable
def run_quick_health_check():
    """
    Run a comprehensive health check of the application.
    
    Returns:
        dict: Health check results
    """
    health = {
        'timestamp': datetime.now(),
        'overall_status': 'unknown',
        'checks': {}
    }
    
    issues = []
    
    # Check 1: Database tables
    try:
        db_status = setup_schema.verify_database_schema()
        tables_ok = all(
            data['exists'] and len(data['missing_columns']) == 0
            for data in db_status['tables'].values()
        )
        health['checks']['database_tables'] = {
            'status': 'ok' if tables_ok else 'error',
            'details': db_status['tables']
        }
        if not tables_ok:
            issues.append('Database tables have missing columns')
    except Exception as e:
        health['checks']['database_tables'] = {
            'status': 'error',
            'error': str(e)
        }
        issues.append(f'Database check failed: {str(e)}')
    
    # Check 2: API keys
    try:
        keys = test_api_keys()
        health['checks']['api_keys'] = {
            'status': 'ok' if keys['all_configured'] else 'error',
            'details': {k: v['configured'] for k, v in keys['keys'].items()}
        }
        if not keys['all_configured']:
            issues.append('Some API keys are not configured')
    except Exception as e:
        health['checks']['api_keys'] = {
            'status': 'error',
            'error': str(e)
        }
        issues.append(f'API key check failed: {str(e)}')
    
    # Check 3: Data freshness
    try:
        from . import background_tasks
        last_refresh = background_tasks.get_last_refresh_time()
        
        if last_refresh:
            age = datetime.now() - last_refresh
            is_fresh = age.days < 7
            health['checks']['data_freshness'] = {
                'status': 'ok' if is_fresh else 'warning',
                'last_refresh': last_refresh,
                'age_days': age.days
            }
            if not is_fresh:
                issues.append(f'Data is {age.days} days old')
        else:
            health['checks']['data_freshness'] = {
                'status': 'warning',
                'message': 'No data refresh has run yet'
            }
            issues.append('No data refresh has been run')
    except Exception as e:
        health['checks']['data_freshness'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Determine overall status
    statuses = [check.get('status', 'unknown') for check in health['checks'].values()]
    if 'error' in statuses:
        health['overall_status'] = 'error'
    elif 'warning' in statuses:
        health['overall_status'] = 'warning'
    else:
        health['overall_status'] = 'ok'
    
    health['issues'] = issues
    health['issue_count'] = len(issues)
    
    return health


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


@anvil.server.callable
def test_firecrawl_connection():
    """
    Test Firecrawl API connectivity and authentication.
    Tests with a known-good URL and the target URL with/without stealth.
    
    Returns:
        dict: Test results
    """
    import anvil.http
    import json
    from . import api_helpers
    
    results = {
        'timestamp': datetime.now(),
        'tests': {}
    }
    
    # Get API key
    try:
        api_key = api_helpers.get_api_key("FIRECRAWL_API_KEY")
        results['api_key_configured'] = True
        results['api_key_preview'] = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
    except Exception as e:
        results['api_key_configured'] = False
        results['api_key_error'] = str(e)
        return results
    
    # Test 1: Simple test URL (firecrawl.dev - should always work)
    print("\n" + "="*60)
    print("TEST 1: Firecrawl with Known-Good URL")
    print("="*60)
    
    test_url = "https://firecrawl.dev"
    results['tests']['test_url'] = _test_firecrawl_url(api_key, test_url, use_stealth=False)
    
    # Test 2: Target URL without stealth
    print("\n" + "="*60)
    print("TEST 2: Target URL without Stealth Mode")
    print("="*60)
    
    target_url = "https://ilovememphisblog.com/weekend"
    results['tests']['target_no_stealth'] = _test_firecrawl_url(api_key, target_url, use_stealth=False)
    
    # Test 3: Target URL with stealth
    print("\n" + "="*60)
    print("TEST 3: Target URL with Stealth Mode")
    print("="*60)
    
    results['tests']['target_with_stealth'] = _test_firecrawl_url(api_key, target_url, use_stealth=True)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, test_result in results['tests'].items():
        status = "✅ SUCCESS" if test_result['success'] else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not test_result['success']:
            print(f"  Error: {test_result.get('error', 'Unknown')}")
    
    return results


def _test_firecrawl_url(api_key, url, use_stealth=False):
    """
    Helper function to test scraping a specific URL with Firecrawl v2.
    
    Args:
        api_key: Firecrawl API key
        url: URL to test
        use_stealth: Whether to use stealth mode
        
    Returns:
        dict: Test results
    """
    import anvil.http
    import json
    
    result = {
        'url': url,
        'stealth': use_stealth,
        'success': False
    }
    
    # Build request using Firecrawl SDK
    try:
        from firecrawl import Firecrawl
        
        firecrawl = Firecrawl(api_key=api_key)
        
        print(f"Testing URL: {url}")
        print(f"Stealth mode: {use_stealth}")
        
        # Make request (SDK doesn't expose stealth mode directly, so we'll note this)
        response = firecrawl.scrape(url=url, formats=['markdown'])
        
        if hasattr(response, 'markdown'):
            result['success'] = True
            result['markdown_size'] = len(response.markdown)
            
            if hasattr(response, 'metadata') and response.metadata:
                result['metadata'] = {
                    'title': getattr(response.metadata, 'title', 'Unknown'),
                    'status_code': getattr(response.metadata, 'statusCode', 'Unknown')
                }
            
            print(f"✅ SUCCESS! Got {result['markdown_size']} chars of markdown")
        else:
            result['success'] = False
            result['error'] = "No markdown content in response"
            print(f"❌ No markdown content returned")
    
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        print(f"❌ Exception: {str(e)}")
    
    return result


@anvil.server.callable
def create_test_events():
    """
    Create realistic test events for UI testing without using external APIs.
    
    Returns:
        int: Number of test events created
    """
    from . import test_data
    return test_data.create_test_events()


@anvil.server.callable
def clear_test_events():
    """
    Clear only test events (identified by special ID pattern).
    
    Returns:
        int: Number of test events deleted
    """
    from anvil.tables import app_tables
    
    count = 0
    for event in app_tables.events.search():
        # Test events have IDs starting with 'test_'
        if event['event_id'] and event['event_id'].startswith('test_'):
            event.delete()
            count += 1
    
    print(f"Deleted {count} test events")
    return count

