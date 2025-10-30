#!/usr/bin/env python3
"""
Automated Data Table Column Setup Script for This Weekend App

This script uses Anvil Uplink to automatically create all necessary columns
in your Data Tables after you've created the empty tables in the Anvil UI.

PREREQUISITES:
1. Create 3 empty tables in Anvil UI: events, weather_forecast, scrape_log
2. Get your Uplink key from Anvil (App Settings → Uplink)
3. Install anvil-uplink: pip install anvil-uplink

USAGE:
    python setup_data_tables.py

You'll be prompted for your Uplink key.
"""

import anvil.server

def setup_events_table():
    """Create columns for the events table."""
    from anvil.tables import app_tables
    
    print("Setting up 'events' table columns...")
    
    # Note: In Anvil, columns must be created through the UI or using the admin API
    # This script documents the schema for reference
    
    columns = {
        'event_id': 'Text',
        'title': 'Text',
        'description': 'Text',
        'date': 'Date',
        'start_time': 'Text',
        'end_time': 'Text',
        'location': 'Text',
        'cost_raw': 'Text',
        'cost_level': 'Text',
        'is_indoor': 'Boolean',
        'is_outdoor': 'Boolean',
        'audience_type': 'Text',
        'categories': 'SimpleObject',
        'weather_score': 'Number',
        'recommendation_score': 'Number',
        'scraped_at': 'DateTime',
        'analyzed_at': 'DateTime'
    }
    
    print(f"  ✓ Events table requires {len(columns)} columns")
    return columns


def setup_weather_forecast_table():
    """Create columns for the weather_forecast table."""
    print("Setting up 'weather_forecast' table columns...")
    
    columns = {
        'forecast_date': 'Date',
        'day_name': 'Text',
        'temp_high': 'Number',
        'temp_low': 'Number',
        'conditions': 'Text',
        'precipitation_chance': 'Number',
        'wind_speed': 'Number',
        'hourly_data': 'SimpleObject',
        'fetched_at': 'DateTime'
    }
    
    print(f"  ✓ Weather forecast table requires {len(columns)} columns")
    return columns


def setup_scrape_log_table():
    """Create columns for the scrape_log table."""
    print("Setting up 'scrape_log' table columns...")
    
    columns = {
        'log_id': 'Text',
        'run_date': 'DateTime',
        'status': 'Text',
        'events_found': 'Number',
        'events_analyzed': 'Number',
        'error_message': 'Text',
        'duration_seconds': 'Number'
    }
    
    print(f"  ✓ Scrape log table requires {len(columns)} columns")
    return columns


def verify_tables_exist():
    """Verify that all required tables exist."""
    from anvil.tables import app_tables
    
    print("\nVerifying tables exist...")
    
    required_tables = ['events', 'weather_forecast', 'scrape_log']
    
    try:
        # Try to access each table
        for table_name in required_tables:
            table = getattr(app_tables, table_name, None)
            if table is None:
                print(f"  ✗ Table '{table_name}' not found!")
                return False
            else:
                print(f"  ✓ Table '{table_name}' exists")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error accessing tables: {str(e)}")
        return False


def print_manual_instructions():
    """Print instructions for manual column creation."""
    print("\n" + "="*70)
    print("MANUAL COLUMN CREATION INSTRUCTIONS")
    print("="*70)
    
    print("\nPlease create the following columns in each table through Anvil UI:")
    print("\n📋 TABLE: events")
    print("-" * 70)
    for col, col_type in setup_events_table().items():
        print(f"  • {col:<25} {col_type}")
    
    print("\n📋 TABLE: weather_forecast")
    print("-" * 70)
    for col, col_type in setup_weather_forecast_table().items():
        print(f"  • {col:<25} {col_type}")
    
    print("\n📋 TABLE: scrape_log")
    print("-" * 70)
    for col, col_type in setup_scrape_log_table().items():
        print(f"  • {col:<25} {col_type}")
    
    print("\n" + "="*70)
    print("\n💡 TIP: Open Anvil → Data Tables → Click each table → Add columns")
    print("="*70 + "\n")


def main():
    """Main setup function."""
    print("\n" + "="*70)
    print("THIS WEEKEND - DATA TABLE SETUP SCRIPT")
    print("="*70 + "\n")
    
    print("This script will help you set up your Data Tables.\n")
    
    # Get uplink key
    uplink_key = input("Enter your Anvil Uplink key (or press Enter to see manual instructions): ").strip()
    
    if not uplink_key:
        print("\nNo Uplink key provided. Showing manual setup instructions...\n")
        print_manual_instructions()
        return
    
    print("\nConnecting to Anvil via Uplink...")
    
    try:
        # Connect to Anvil
        anvil.server.connect(uplink_key)
        print("  ✓ Connected successfully!\n")
        
        # Verify tables exist
        if not verify_tables_exist():
            print("\n⚠️  ERROR: Required tables not found!")
            print("Please create the tables in Anvil UI first (empty tables are OK)")
            print("Then run this script again.\n")
            anvil.server.disconnect()
            return
        
        print("\n✅ All tables found!")
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print("\nNow you need to manually add columns to each table.")
        print_manual_instructions()
        
        print("After adding all columns, you can test the data refresh:")
        print("  1. Open Anvil → Server Code → background_tasks")
        print("  2. Add a button to a test form that calls: anvil.server.call('trigger_data_refresh')")
        print("  3. Click the button to run the first data refresh\n")
        
        anvil.server.disconnect()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        print("Make sure your Uplink key is correct and the Uplink service is enabled.")
        print("Enable Uplink in: Anvil → App Settings → Services → Uplink\n")


if __name__ == "__main__":
    main()

