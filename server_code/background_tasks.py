"""
Background task orchestration module for This Weekend app.
Coordinates the complete data refresh workflow.
"""

import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta
import re

from . import config
from . import weather_service
from . import scraper_service
from . import ai_service
from . import data_processor
from . import api_helpers


@anvil.server.background_task
def scheduled_refresh_all_data():
    """
    Main background task that orchestrates the complete data refresh workflow.
    This function is called by Anvil Scheduler on a weekly basis.
    
    Steps:
    1. Clean up old data
    2. Fetch weather forecast
    3. Scrape events
    4. Parse events
    5. Save events to database
    6. Analyze events with AI
    7. Match events with weather
    8. Calculate recommendation scores
    9. Log completion
    """
    log_id = api_helpers.generate_unique_id("log")
    start_time = datetime.now()
    
    print("\n" + "=" * 60)
    print("🚀 BACKGROUND TASK STARTED")
    print(f"Starting scheduled data refresh at {start_time}")
    print(f"Log ID: {log_id}")
    print("=" * 60 + "\n")
    
    # Create initial log entry
    log_entry = app_tables.scrape_log.add_row(
        log_id=log_id,
        run_date=start_time,
        status="running",
        events_found=0,
        events_analyzed=0,
        error_message=None,
        duration_seconds=0
    )
    
    try:
        # Step 1: Clean up old data
        print("[1/10] Cleanup...")
        cleanup_old_data()
        print("  ✓ Done")
        
        # Step 2: Fetch weather forecast
        print("[2/10] Weather...")
        weather_data = weather_service.fetch_weekend_weather()
        print(f"  ✓ {len(weather_data)} days")
        
        # Step 3: Save weather to database
        print("[3/10] Save weather...")
        weather_service.save_weather_to_db(weather_data)
        print("  ✓ Done")
        
        # Step 4: Scrape weekend events
        print("[4/10] Scrape events...")
        markdown_content = scraper_service.scrape_weekend_events()
        
        # Step 5: Parse events from markdown
        print("[5/10] Parse events...")
        events = scraper_service.parse_events_from_markdown(markdown_content)
        log_entry["events_found"] = len(events)
        print(f"  ✓ Found {len(events)} events")
        
        # Step 6: Save events to database
        print("[6/10] Save to DB...")
        saved_count = scraper_service.save_events_to_db(events)
        
        # Step 7: Analyze events with AI
        print("[7/10] AI analysis...")
        db_events = list(app_tables.events.search())
        analyses = ai_service.analyze_all_events(db_events)
        
        # Step 8: Update events with AI analysis
        print("[8/10] Update DB with AI results...")
        analyzed_count = ai_service.update_events_with_analysis(analyses)
        log_entry["events_analyzed"] = analyzed_count
        print(f"  ✓ Analyzed {analyzed_count} events")
        
        # Step 9: Match events with weather
        print("[9/10] Match with weather...")
        data_processor.match_events_with_weather()
        print("  ✓ Done")
        
        # Step 10: Calculate recommendation scores
        print("[10/10] Calculate scores...")
        data_processor.update_all_recommendation_scores()
        print("  ✓ Done")
        
        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Update log with success
        log_entry["status"] = "success"
        log_entry["duration_seconds"] = duration
        
        print("\n" + "=" * 60)
        print(f"Data refresh completed successfully!")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Events found: {saved_count}")
        print(f"Events analyzed: {analyzed_count}")
        print("=" * 60)
        
        return {
            "status": "success",
            "events_found": saved_count,
            "events_analyzed": analyzed_count,
            "duration_seconds": duration
        }
        
    except Exception as e:
        # Log the error
        error_message = str(e)
        print(f"\n❌ ERROR during data refresh: {error_message}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        log_entry["status"] = "failed"
        log_entry["error_message"] = error_message
        log_entry["duration_seconds"] = duration
        
        print("=" * 60)
        print(f"Data refresh failed after {duration:.1f} seconds")
        print("=" * 60)
        
        # Re-raise exception so Anvil logs it
        raise


@anvil.server.callable
def trigger_data_refresh():
    """
    Manually trigger a data refresh.
    Callable from client-side code for testing/admin purposes.
    
    Returns:
        Task object for monitoring progress
    """
    print("Manual data refresh triggered by client")
    print("Launching background task: scheduled_refresh_all_data")
    task = anvil.server.launch_background_task('scheduled_refresh_all_data')
    print(f"Background task launched: {task}")
    return task


@anvil.server.callable
def get_last_refresh_time():
    """
    Get the timestamp of the last successful data refresh.
    Callable from client-side code.
    
    Returns:
        datetime or None
    """
    from anvil.tables import query as q
    
    # Get most recent successful log entry
    log_entry = app_tables.scrape_log.get(
        status="success"
    )
    
    if log_entry:
        return log_entry["run_date"]
    
    return None


@anvil.server.callable
def get_refresh_status():
    """
    Get the status of recent data refresh operations.
    Callable from client-side code.
    
    Returns:
        dict: Status information
    """
    from anvil.tables import query as q
    
    # Get most recent log entry
    recent_logs = list(app_tables.scrape_log.search(
        q.order_by("run_date", ascending=False)
    ))[:5]  # Get last 5 runs
    
    if not recent_logs:
        return {
            "last_run": None,
            "status": "never_run",
            "events_count": 0
        }
    
    last_log = recent_logs[0]
    events_count = len(list(app_tables.events.search()))
    
    return {
        "last_run": last_log["run_date"],
        "status": last_log["status"],
        "events_found": last_log["events_found"],
        "events_analyzed": last_log["events_analyzed"],
        "duration_seconds": last_log["duration_seconds"],
        "error_message": last_log["error_message"],
        "events_count": events_count,
        "recent_logs": [
            {
                "run_date": log["run_date"],
                "status": log["status"],
                "events_found": log["events_found"],
                "duration": log["duration_seconds"]
            }
            for log in recent_logs
        ]
    }


def cleanup_old_data():
    """
    Clean up old data from database tables.
    - Delete events older than configured retention period
    - Delete old weather forecasts
    - Delete old scrape logs
    """
    print("Cleaning up old data...")
    
    try:
        # Calculate retention cutoff dates
        now = datetime.now()
        event_cutoff = now - timedelta(days=config.DATA_RETENTION["events"])
        weather_cutoff = now - timedelta(days=config.DATA_RETENTION["weather"])
        log_cutoff = now - timedelta(days=config.DATA_RETENTION["scrape_log"])
        
        # First, delete junk events (Reply links, comment links, etc.)
        all_events = list(app_tables.events.search())
        deleted_junk = 0
        for event in all_events:
            try:
                title = event["title"] or ""
                # Check if title contains junk patterns
                junk_patterns = [
                    r'^reply$',
                    r'^- \[reply\]',
                    r'comment/reply',
                    r'^submit here',
                    r'^click here',
                ]
                if any(re.search(pattern, title, re.IGNORECASE) for pattern in junk_patterns):
                    event.delete()
                    deleted_junk += 1
            except Exception:
                pass
        
        if deleted_junk > 0:
            print(f"Deleted {deleted_junk} junk events (Reply links, etc.)")
        
        # Delete old events
        old_events = app_tables.events.search()
        deleted_events = 0
        for event in old_events:
            try:
                # Handle both timezone-aware and naive datetimes
                scraped_at = event["scraped_at"]
                if scraped_at:
                    # Remove timezone info for comparison if present
                    if hasattr(scraped_at, 'replace') and scraped_at.tzinfo is not None:
                        scraped_at = scraped_at.replace(tzinfo=None)
                    if scraped_at < event_cutoff:
                        event.delete()
                        deleted_events += 1
            except (TypeError, AttributeError):
                # Skip if datetime comparison fails
                pass
        
        if deleted_events > 0:
            print(f"Deleted {deleted_events} old events")
        
        # Delete old weather forecasts
        old_weather = app_tables.weather_forecast.search()
        deleted_weather = 0
        for forecast in old_weather:
            try:
                fetched_at = forecast["fetched_at"]
                if fetched_at:
                    if hasattr(fetched_at, 'replace') and fetched_at.tzinfo is not None:
                        fetched_at = fetched_at.replace(tzinfo=None)
                    if fetched_at < weather_cutoff:
                        forecast.delete()
                        deleted_weather += 1
            except (TypeError, AttributeError):
                pass
        
        if deleted_weather > 0:
            print(f"Deleted {deleted_weather} old weather forecasts")
        
        # Delete old scrape logs
        old_logs = app_tables.scrape_log.search()
        deleted_logs = 0
        for log in old_logs:
            try:
                run_date = log["run_date"]
                if run_date:
                    if hasattr(run_date, 'replace') and run_date.tzinfo is not None:
                        run_date = run_date.replace(tzinfo=None)
                    if run_date < log_cutoff:
                        log.delete()
                        deleted_logs += 1
            except (TypeError, AttributeError):
                pass
        
        if deleted_logs > 0:
            print(f"Deleted {deleted_logs} old scrape logs")
        
        print("Data cleanup completed")
        
    except Exception as e:
        print(f"Error during data cleanup: {str(e)}")
        # Don't raise - cleanup failure shouldn't stop the refresh


@anvil.server.callable
def search_events(search_text, filters=None):
    """
    Search events by text and apply filters.
    Callable from client-side code.
    
    Args:
        search_text: Text to search in title, description, location
        filters: Optional filter criteria (same as get_filtered_events)
        
    Returns:
        list: List of matching event dictionaries
    """
    # First apply filters if provided
    if filters:
        events = data_processor.get_filtered_events(filters)
    else:
        events = data_processor.get_all_events()
    
    # If no search text, return filtered results
    if not search_text or not search_text.strip():
        return events
    
    # Search within results
    search_text = search_text.lower().strip()
    matching_events = []
    
    for event in events:
        # Search in title, description, and location
        if (search_text in event.get("title", "").lower() or
            search_text in event.get("description", "").lower() or
            search_text in event.get("location", "").lower()):
            matching_events.append(event)
    
    return matching_events

