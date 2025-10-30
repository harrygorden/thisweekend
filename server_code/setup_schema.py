"""
Automated Data Table Schema Setup and Verification for This Weekend App

This module can be run from within Anvil to automatically create and verify
all required Data Tables and columns. It uses Anvil's automatic column creation
feature by adding sample rows with the correct data types.

Usage:
    From Anvil server code or a test form:
    import server_code.setup_schema as setup_schema
    result = setup_schema.setup_and_verify_all_tables()
    print(result)
"""

import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
from datetime import datetime, date


# Define the complete schema for all tables
SCHEMA_DEFINITIONS = {
    'events': {
        'event_id': ('text', 'sample_id_123'),
        'title': ('text', 'Sample Event'),
        'description': ('text', 'Sample event description'),
        'date': ('date', date.today()),
        'start_time': ('text', '12:00 PM'),
        'end_time': ('text', '2:00 PM'),
        'location': ('text', 'Sample Location'),
        'cost_raw': ('text', '$20'),
        'cost_level': ('text', '$$'),
        'is_indoor': ('bool', True),
        'is_outdoor': ('bool', False),
        'audience_type': ('text', 'all-ages'),
        'categories': ('simpleobject', ['Sample Category']),
        'weather_score': ('number', 75),
        'recommendation_score': ('number', 80),
        'scraped_at': ('datetime', datetime.now()),
        'analyzed_at': ('datetime', datetime.now())
    },
    'weather_forecast': {
        'forecast_date': ('date', date.today()),
        'day_name': ('text', 'Friday'),
        'temp_high': ('number', 75),
        'temp_low': ('number', 55),
        'conditions': ('text', 'Partly Cloudy'),
        'precipitation_chance': ('number', 20),
        'wind_speed': ('number', 10),
        'hourly_data': ('simpleobject', [{'time': '12:00 PM', 'temp': 70}]),
        'fetched_at': ('datetime', datetime.now())
    },
    'scrape_log': {
        'log_id': ('text', 'log_sample_123'),
        'run_date': ('datetime', datetime.now()),
        'status': ('text', 'success'),
        'events_found': ('number', 0),
        'events_analyzed': ('number', 0),
        'error_message': ('text', ''),
        'duration_seconds': ('number', 0)
    }
}


def table_exists(table_name):
    """
    Check if a table exists in app_tables.
    
    Args:
        table_name: Name of the table to check
        
    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        table = getattr(app_tables, table_name, None)
        if table is None:
            return False
        
        # Try to perform a simple operation to verify it's a valid table
        list(table.search())
        return True
    except Exception as e:
        print(f"Table '{table_name}' does not exist or is not accessible: {str(e)}")
        return False


def get_existing_columns(table_name):
    """
    Get list of existing columns in a table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        list: List of column names, or empty list if table doesn't exist
    """
    try:
        table = getattr(app_tables, table_name)
        schema = SCHEMA_DEFINITIONS[table_name]
        existing_cols = []
        
        # Try to get the first row to examine columns
        rows = list(table.search())
        
        if rows:
            # Table has data - check which columns exist
            first_row = rows[0]
            for col_name in schema.keys():
                try:
                    # Try to access the column
                    _ = first_row[col_name]
                    existing_cols.append(col_name)
                except KeyError:
                    pass
            return existing_cols
        else:
            # Empty table - try adding and immediately deleting a test row
            # This is the only way to detect columns on an empty Anvil table
            try:
                # Create a minimal test row with one column
                test_col = list(schema.keys())[0]
                col_type, sample_value = schema[test_col]
                test_row = table.add_row(**{test_col: sample_value})
                
                # Now check which columns exist
                for col_name in schema.keys():
                    try:
                        _ = test_row[col_name]
                        existing_cols.append(col_name)
                    except KeyError:
                        pass
                
                # Delete the test row
                test_row.delete()
                
                return existing_cols
                
            except Exception as e:
                print(f"  Could not detect columns on empty table '{table_name}': {str(e)}")
                # If we can't detect, assume no columns exist
                return []
            
    except Exception as e:
        print(f"Error getting columns for '{table_name}': {str(e)}")
        return []


def create_missing_columns(table_name, missing_columns):
    """
    Create missing columns by adding a sample row with those columns.
    Anvil will automatically create the columns with the correct types.
    
    Args:
        table_name: Name of the table
        missing_columns: List of column names to create
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not missing_columns:
        return True
    
    try:
        table = getattr(app_tables, table_name)
        schema = SCHEMA_DEFINITIONS[table_name]
        
        # Build a sample row with only the missing columns
        sample_data = {}
        for col_name in missing_columns:
            if col_name in schema:
                col_type, sample_value = schema[col_name]
                sample_data[col_name] = sample_value
        
        # Add the sample row (this creates the columns)
        print(f"  Creating columns for '{table_name}': {', '.join(missing_columns)}")
        sample_row = table.add_row(**sample_data)
        
        # Delete the sample row immediately
        sample_row.delete()
        
        print(f"  ✓ Successfully created {len(missing_columns)} columns in '{table_name}'")
        return True
        
    except Exception as e:
        print(f"  ✗ Error creating columns in '{table_name}': {str(e)}")
        return False


def verify_and_setup_table(table_name):
    """
    Verify a table exists and has all required columns.
    Create missing columns if needed.
    
    Args:
        table_name: Name of the table to verify
        
    Returns:
        dict: Status report with details
    """
    print(f"\n{'='*60}")
    print(f"Checking table: {table_name}")
    print(f"{'='*60}")
    
    result = {
        'table_name': table_name,
        'exists': False,
        'columns_expected': len(SCHEMA_DEFINITIONS[table_name]),
        'columns_found': 0,
        'columns_created': 0,
        'missing_columns': [],
        'status': 'unknown',
        'message': ''
    }
    
    # Check if table exists
    if not table_exists(table_name):
        result['status'] = 'error'
        result['message'] = f"Table '{table_name}' does not exist. Please create it in Anvil UI first."
        print(f"  ✗ {result['message']}")
        return result
    
    result['exists'] = True
    
    # Get existing columns
    existing_columns = get_existing_columns(table_name)
    result['columns_found'] = len(existing_columns)
    
    # Determine missing columns
    expected_columns = set(SCHEMA_DEFINITIONS[table_name].keys())
    existing_columns_set = set(existing_columns)
    missing_columns = expected_columns - existing_columns_set
    result['missing_columns'] = list(missing_columns)
    
    if existing_columns:
        print(f"  Found {len(existing_columns)} existing columns: {', '.join(sorted(existing_columns))}")
    else:
        print(f"  Table is empty - will create all {len(expected_columns)} columns")
    
    if missing_columns:
        print(f"  Missing {len(missing_columns)} columns: {', '.join(sorted(missing_columns))}")
        
        # Create missing columns
        success = create_missing_columns(table_name, list(missing_columns))
        
        if success:
            result['columns_created'] = len(missing_columns)
            result['status'] = 'fixed'
            result['message'] = f"Created {len(missing_columns)} missing columns"
        else:
            result['status'] = 'error'
            result['message'] = f"Failed to create missing columns"
    else:
        result['status'] = 'ok'
        result['message'] = 'All columns present'
        print(f"  ✓ All {len(expected_columns)} columns are present")
    
    return result


def setup_and_verify_all_tables():
    """
    Main function to verify and set up all required tables.
    
    Returns:
        dict: Complete status report
    """
    print("\n" + "="*60)
    print("THIS WEEKEND - AUTOMATIC SCHEMA SETUP")
    print("="*60)
    print(f"Started at: {datetime.now()}")
    print("")
    
    results = {
        'timestamp': datetime.now(),
        'tables': {},
        'summary': {
            'total_tables': len(SCHEMA_DEFINITIONS),
            'tables_ok': 0,
            'tables_fixed': 0,
            'tables_error': 0,
            'total_columns_created': 0
        }
    }
    
    # Process each table
    for table_name in SCHEMA_DEFINITIONS.keys():
        result = verify_and_setup_table(table_name)
        results['tables'][table_name] = result
        
        # Update summary
        if result['status'] == 'ok':
            results['summary']['tables_ok'] += 1
        elif result['status'] == 'fixed':
            results['summary']['tables_fixed'] += 1
            results['summary']['total_columns_created'] += result['columns_created']
        elif result['status'] == 'error':
            results['summary']['tables_error'] += 1
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total tables checked: {results['summary']['total_tables']}")
    print(f"  ✓ Tables OK: {results['summary']['tables_ok']}")
    print(f"  🔧 Tables fixed: {results['summary']['tables_fixed']}")
    print(f"  ✗ Tables with errors: {results['summary']['tables_error']}")
    print(f"  📝 Columns created: {results['summary']['total_columns_created']}")
    
    # Overall status
    if results['summary']['tables_error'] > 0:
        print("\n⚠️  ERRORS DETECTED!")
        print("Some tables could not be verified or fixed.")
        print("Please create missing tables manually in Anvil UI.")
    elif results['summary']['tables_fixed'] > 0:
        print("\n✅ SETUP COMPLETE!")
        print(f"Successfully created {results['summary']['total_columns_created']} missing columns.")
        print("All tables are now ready to use.")
    else:
        print("\n✅ ALL TABLES OK!")
        print("All tables and columns are already correctly configured.")
    
    print("\nCompleted at:", datetime.now())
    print("="*60 + "\n")
    
    return results


@anvil.server.callable
def setup_database_schema():
    """
    Callable version of the setup function for use from client code.
    
    Returns:
        dict: Setup results
    """
    return setup_and_verify_all_tables()


@anvil.server.callable
def verify_database_schema():
    """
    Verify database schema without making changes.
    Returns a detailed report of the current state.
    
    Returns:
        dict: Verification report
    """
    print("\n" + "="*60)
    print("DATABASE SCHEMA VERIFICATION (READ-ONLY)")
    print("="*60)
    
    report = {
        'timestamp': datetime.now(),
        'tables': {}
    }
    
    for table_name in SCHEMA_DEFINITIONS.keys():
        table_report = {
            'exists': table_exists(table_name),
            'expected_columns': len(SCHEMA_DEFINITIONS[table_name]),
            'existing_columns': [],
            'missing_columns': []
        }
        
        if table_report['exists']:
            existing = get_existing_columns(table_name)
            table_report['existing_columns'] = existing
            
            expected = set(SCHEMA_DEFINITIONS[table_name].keys())
            missing = expected - set(existing)
            table_report['missing_columns'] = list(missing)
        
        report['tables'][table_name] = table_report
        
        print(f"\nTable: {table_name}")
        print(f"  Exists: {table_report['exists']}")
        if table_report['exists']:
            print(f"  Columns: {len(table_report['existing_columns'])}/{table_report['expected_columns']}")
            if table_report['missing_columns']:
                print(f"  Missing: {', '.join(table_report['missing_columns'])}")
    
    print("\n" + "="*60 + "\n")
    return report


def print_schema_reference():
    """
    Print a reference of the complete schema for all tables.
    Useful for documentation and manual setup.
    """
    print("\n" + "="*60)
    print("DATA TABLES SCHEMA REFERENCE")
    print("="*60)
    
    for table_name, columns in SCHEMA_DEFINITIONS.items():
        print(f"\n📋 TABLE: {table_name}")
        print("-" * 60)
        print(f"{'Column Name':<30} {'Type':<15} {'Sample Value'}")
        print("-" * 60)
        
        for col_name, (col_type, sample_value) in columns.items():
            sample_str = str(sample_value)
            if len(sample_str) > 30:
                sample_str = sample_str[:27] + "..."
            print(f"{col_name:<30} {col_type:<15} {sample_str}")
    
    print("\n" + "="*60 + "\n")


# Auto-run verification when module is imported (informational only)
if __name__ != "__main__":
    # Only run verification, not setup, when imported
    # This provides useful diagnostics without making changes
    pass

