from ._anvil_designer import AdminFormTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class AdminForm(AdminFormTemplate):
    """
    Admin/Test Form for This Weekend App
    
    This form provides easy access to all administrative functions:
    - Database setup
    - Health checks
    - Data refresh
    - API key verification
    - System monitoring
    """
    
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Load initial status
        self.refresh_status()
    
    
    def refresh_status(self):
        """Refresh all status displays"""
        try:
            # Get system info
            info = anvil.server.call('get_system_info')
            
            # Update status labels
            if info.get('last_refresh'):
                self.last_refresh_label.text = f"Last Refresh: {info['last_refresh'].strftime('%Y-%m-%d %H:%M')}"
            else:
                self.last_refresh_label.text = "Last Refresh: Never"
            
            self.event_count_label.text = f"Events in DB: {info.get('event_count', 0)}"
            self.weather_count_label.text = f"Weather Forecasts: {info.get('weather_forecast_count', 0)}"
            
            # Database status
            db_status = info.get('database_status', {})
            status_parts = []
            for table, status in db_status.items():
                icon = "✅" if status.get('columns_ok') else "⚠️"
                status_parts.append(f"{icon} {table}: {status.get('column_count', 0)} cols")
            self.db_status_label.text = " | ".join(status_parts) if status_parts else "Unknown"
            
        except Exception as e:
            self.status_output.text = f"Error refreshing status: {str(e)}\n"
            print(f"Status refresh error: {e}")
    
    
    def setup_database_button_click(self, **event_args):
        """Run automatic database setup"""
        self.status_output.text = "⏳ Running database setup...\n"
        self.setup_database_button.enabled = False
        
        try:
            result = anvil.server.call('run_database_setup')
            
            summary = result['summary']
            
            # Build status message
            status_msg = "="*50 + "\n"
            status_msg += "DATABASE SETUP COMPLETE\n"
            status_msg += "="*50 + "\n\n"
            status_msg += f"Total tables: {summary['total_tables']}\n"
            status_msg += f"  ✅ OK: {summary['tables_ok']}\n"
            status_msg += f"  🔧 Fixed: {summary['tables_fixed']}\n"
            status_msg += f"  ❌ Errors: {summary['tables_error']}\n"
            status_msg += f"  📝 Columns created: {summary['total_columns_created']}\n\n"
            
            # Details for each table
            for table_name, table_result in result['tables'].items():
                status_msg += f"\n{table_name}:\n"
                status_msg += f"  Status: {table_result['status']}\n"
                status_msg += f"  Message: {table_result['message']}\n"
                if table_result.get('missing_columns'):
                    status_msg += f"  Created: {', '.join(table_result['missing_columns'])}\n"
            
            self.status_output.text = status_msg
            
            # Show alert
            if summary['tables_error'] > 0:
                alert(f"❌ Setup failed!\n{summary['tables_error']} tables have errors.\nCheck output for details.", title="Setup Failed")
            elif summary['tables_fixed'] > 0:
                alert(f"✅ Setup complete!\n\nCreated {summary['total_columns_created']} columns across {summary['tables_fixed']} tables.", title="Setup Successful")
            else:
                alert("✅ All tables already configured correctly!", title="Setup Complete")
            
            # Refresh status
            self.refresh_status()
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}\n"
            self.status_output.text = error_msg
            alert(f"Setup failed:\n{str(e)}", title="Error")
            
        finally:
            self.setup_database_button.enabled = True
    
    
    def health_check_button_click(self, **event_args):
        """Run comprehensive health check"""
        self.status_output.text = "⏳ Running health check...\n"
        
        try:
            health = anvil.server.call('run_quick_health_check')
            
            # Build health report
            report = "="*50 + "\n"
            report += "SYSTEM HEALTH CHECK\n"
            report += "="*50 + "\n\n"
            report += f"Overall Status: {health['overall_status'].upper()}\n"
            report += f"Issues Found: {health['issue_count']}\n\n"
            
            # Individual checks
            for check_name, check_result in health['checks'].items():
                status_icon = {"ok": "✅", "warning": "⚠️", "error": "❌"}.get(check_result['status'], "❓")
                report += f"{status_icon} {check_name.replace('_', ' ').title()}: {check_result['status']}\n"
                
                if check_result.get('error'):
                    report += f"   Error: {check_result['error']}\n"
                elif check_result.get('message'):
                    report += f"   {check_result['message']}\n"
            
            # Issues summary
            if health['issues']:
                report += "\n⚠️ ISSUES:\n"
                for issue in health['issues']:
                    report += f"  • {issue}\n"
            else:
                report += "\n✅ No issues detected!\n"
            
            self.status_output.text = report
            
            # Show alert
            if health['overall_status'] == 'ok':
                alert("✅ System is healthy!\n\nAll checks passed.", title="Health Check")
            else:
                issues_text = '\n'.join(f"• {issue}" for issue in health['issues'])
                alert(f"⚠️ Issues found:\n\n{issues_text}", title="Health Check")
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}\n"
            self.status_output.text = error_msg
            alert(f"Health check failed:\n{str(e)}", title="Error")
    
    
    def refresh_data_button_click(self, **event_args):
        """Trigger data refresh"""
        confirm_msg = (
            "This will:\n"
            "1. Fetch Memphis weather ✅\n"
            "2. Scrape events from website (may fail)\n"
            "3. Analyze with AI\n"
            "4. Calculate recommendations\n\n"
            "This may take 2-5 minutes.\n\n"
            "Note: If scraping fails, use 'Load Test Events' instead.\n\n"
            "Continue?"
        )
        
        if not confirm(confirm_msg):
            return
        
        self.status_output.text = "⏳ Starting data refresh...\n"
        self.refresh_data_button.enabled = False
        
        try:
            task = anvil.server.call('trigger_data_refresh')
            
            self.status_output.text = (
                "✅ Data refresh started!\n\n"
                "Background task is running...\n"
                "Check server logs for detailed progress.\n\n"
                "This will take 2-5 minutes.\n"
                "You can close this form and come back later.\n\n"
                "If it fails at scraping, try 'Load Test Events' instead.\n"
            )
            
            alert("✅ Data refresh started!\n\nCheck server logs for progress.\nThis will take 2-5 minutes.", title="Refresh Started")
            
            # Refresh status after a delay
            self.refresh_status()
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}\n"
            self.status_output.text = error_msg
            alert(f"Failed to start refresh:\n{str(e)}", title="Error")
            
        finally:
            self.refresh_data_button.enabled = True
    
    
    def load_test_events_button_click(self, **event_args):
        """Load test events for development/testing"""
        confirm_msg = (
            "This will create 14 realistic sample events for testing.\n\n"
            "Perfect for testing the UI while debugging Firecrawl!\n\n"
            "Continue?"
        )
        
        if not confirm(confirm_msg):
            return
        
        self.status_output.text = "⏳ Creating test events...\n"
        
        try:
            count = anvil.server.call('create_test_events')
            
            self.status_output.text = (
                f"✅ Created {count} test events!\n\n"
                "Events have been:\n"
                "  • Added to database\n"
                "  • Matched with weather\n"
                "  • Scored and ready to display\n\n"
                "You can now test the UI with real-looking data!\n"
            )
            
            alert(f"✅ Created {count} test events!\n\nYou can now test the UI.", title="Test Events Loaded")
            
            # Refresh status
            self.refresh_status()
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}\n"
            self.status_output.text = error_msg
            alert(f"Failed to create test events:\n{str(e)}", title="Error")
    
    
    def clear_test_events_button_click(self, **event_args):
        """Clear test events only"""
        if not confirm("Clear all test events?"):
            return
        
        try:
            count = anvil.server.call('clear_test_events')
            alert(f"✅ Deleted {count} test events", title="Test Events Cleared")
            self.refresh_status()
        except Exception as e:
            alert(f"Error: {str(e)}", title="Error")
    
    
    def test_openweather_button_click(self, **event_args):
        """Test OpenWeather API"""
        self.status_output.text = "🌤️ Testing OpenWeather API...\n\n"
        
        try:
            import server_code.weather_service as weather
            
            self.status_output.text += "Fetching Memphis weather forecast...\n"
            
            # Fetch weather
            weather_data = weather.fetch_weekend_weather()
            
            # Build output
            output = "="*50 + "\n"
            output += "OPENWEATHER API TEST\n"
            output += "="*50 + "\n\n"
            output += f"✅ SUCCESS! Fetched weather for {len(weather_data)} days\n\n"
            
            for day_name, forecast in weather_data.items():
                output += f"{forecast['day_name']} ({forecast['date']}):\n"
                output += f"  High: {forecast['temp_high']}°F, Low: {forecast['temp_low']}°F\n"
                output += f"  Conditions: {forecast['conditions']}\n"
                output += f"  Rain chance: {forecast['precipitation_chance']}%\n"
                output += f"  Wind: {forecast['wind_speed']} mph\n"
                output += f"  Hourly forecasts: {len(forecast['hourly_data'])} hours\n\n"
            
            self.status_output.text = output
            alert("✅ OpenWeather API is working!", title="API Test")
            
        except Exception as e:
            output = "="*50 + "\n"
            output += "OPENWEATHER API TEST\n"
            output += "="*50 + "\n\n"
            output += f"❌ FAILED!\n\n"
            output += f"Error: {str(e)}\n\n"
            output += "Possible causes:\n"
            output += "  • Invalid API key\n"
            output += "  • API key doesn't have One Call API 3.0 access\n"
            output += "  • Network connection issue\n"
            output += "  • Rate limit exceeded\n"
            
            self.status_output.text = output
            alert(f"❌ OpenWeather API failed:\n\n{str(e)}", title="API Test Failed")
    
    
    def test_firecrawl_button_click(self, **event_args):
        """Test Firecrawl API connectivity"""
        self.status_output.text = "🔍 Testing Firecrawl API...\n\n"
        self.status_output.text += "Running 3 tests (this may take 30-60 seconds)...\n\n"
        
        try:
            result = anvil.server.call('test_firecrawl_connection')
            
            # Build output
            output = "="*50 + "\n"
            output += "FIRECRAWL API CONNECTION TEST\n"
            output += "="*50 + "\n\n"
            
            output += f"API Key Configured: {result['api_key_configured']}\n"
            if result.get('api_key_preview'):
                output += f"API Key: {result['api_key_preview']}\n\n"
            
            output += "TEST RESULTS:\n"
            output += "-"*50 + "\n\n"
            
            for test_name, test_result in result['tests'].items():
                status = "✅ PASS" if test_result['success'] else "❌ FAIL"
                output += f"{test_name.upper()}:\n"
                output += f"  Status: {status}\n"
                output += f"  URL: {test_result['url']}\n"
                output += f"  Stealth: {test_result['stealth']}\n"
                
                if test_result['success']:
                    output += f"  ✅ Markdown size: {test_result.get('markdown_size', 0)} chars\n"
                    if test_result.get('metadata'):
                        output += f"  ✅ Page title: {test_result['metadata'].get('title', 'Unknown')}\n"
                else:
                    output += f"  ❌ Error: {test_result.get('error', 'Unknown')}\n"
                    if test_result.get('error_code'):
                        output += f"  ❌ Error code: {test_result['error_code']}\n"
                
                output += "\n"
            
            # Summary
            success_count = sum(1 for t in result['tests'].values() if t['success'])
            total_count = len(result['tests'])
            
            output += "="*50 + "\n"
            output += f"SUMMARY: {success_count}/{total_count} tests passed\n"
            output += "="*50 + "\n"
            
            self.status_output.text = output
            
            if success_count == total_count:
                alert("✅ All Firecrawl tests passed!", title="API Test")
            elif success_count > 0:
                alert(f"⚠️ Partial success: {success_count}/{total_count} tests passed\n\nCheck output for details.", title="API Test")
            else:
                alert("❌ All Firecrawl tests failed\n\nCheck output for error details.", title="API Test Failed")
            
        except Exception as e:
            self.status_output.text = f"❌ Test failed: {str(e)}\n\n{traceback.format_exc()}"
            alert(f"❌ Test failed:\n{str(e)}", title="Error")
    
    
    def test_openai_button_click(self, **event_args):
        """Test OpenAI API"""
        self.status_output.text = "🤖 Testing OpenAI API...\n\n"
        
        try:
            import server_code.ai_service as ai
            
            self.status_output.text += "Sending test event to ChatGPT for analysis...\n\n"
            
            # Create a test event
            test_event = {
                'title': 'Live Jazz Concert at Overton Park',
                'description': 'Outdoor jazz concert featuring local Memphis musicians. Bring blankets and chairs for lawn seating. Food trucks and beverages available.',
                'location': 'Overton Park Shell',
                'cost_raw': '$15 advance tickets, $20 at door'
            }
            
            # Analyze with AI
            analysis = ai.analyze_event(test_event)
            
            # Build output
            output = "="*50 + "\n"
            output += "OPENAI API TEST\n"
            output += "="*50 + "\n\n"
            output += "✅ SUCCESS! ChatGPT API is working\n\n"
            output += "Test Event:\n"
            output += f"  Title: {test_event['title']}\n\n"
            output += "AI Analysis Results:\n"
            output += f"  Indoor: {analysis.get('is_indoor', 'unknown')}\n"
            output += f"  Outdoor: {analysis.get('is_outdoor', 'unknown')}\n"
            output += f"  Audience: {analysis.get('audience_type', 'unknown')}\n"
            output += f"  Cost level: {analysis.get('cost_level', 'unknown')}\n"
            output += f"  Categories: {', '.join(analysis.get('categories', []))}\n\n"
            output += "="*50 + "\n"
            output += "OpenAI API is configured correctly!\n"
            output += "="*50 + "\n"
            
            self.status_output.text = output
            alert("✅ OpenAI API is working!\n\nChatGPT successfully analyzed the test event.", title="API Test")
            
        except Exception as e:
            output = "="*50 + "\n"
            output += "OPENAI API TEST\n"
            output += "="*50 + "\n\n"
            output += f"❌ FAILED!\n\n"
            output += f"Error: {str(e)}\n\n"
            output += "Possible causes:\n"
            output += "  • Invalid API key\n"
            output += "  • Insufficient credits/quota\n"
            output += "  • Network connection issue\n"
            output += "  • Rate limit exceeded\n"
            
            self.status_output.text = output
            alert(f"❌ OpenAI API failed:\n\n{str(e)}", title="API Test Failed")
    
    
    def test_api_keys_button_click(self, **event_args):
        """Test API key configuration"""
        self.status_output.text = "⏳ Testing API keys...\n"
        
        try:
            keys = anvil.server.call('test_api_keys')
            
            # Build report
            report = "="*50 + "\n"
            report += "API KEY VERIFICATION\n"
            report += "="*50 + "\n\n"
            
            for key_name, key_info in keys['keys'].items():
                if key_info['configured']:
                    report += f"✅ {key_name}\n"
                    report += f"   Value: {key_info['masked_value']}\n"
                else:
                    report += f"❌ {key_name}\n"
                    report += f"   Error: {key_info.get('error', 'Not configured')}\n"
                report += "\n"
            
            report += f"\nAll Configured: {'✅ YES' if keys['all_configured'] else '❌ NO'}\n"
            
            self.status_output.text = report
            
            # Show alert
            if keys['all_configured']:
                alert("✅ All API keys are configured!", title="API Keys")
            else:
                missing = [k for k, v in keys['keys'].items() if not v['configured']]
                alert(f"❌ Missing API keys:\n\n" + '\n'.join(f"• {k}" for k in missing), title="API Keys")
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}\n"
            self.status_output.text = error_msg
            alert(f"API key test failed:\n{str(e)}", title="Error")
    
    
    def check_status_button_click(self, **event_args):
        """Check database status (read-only)"""
        self.status_output.text = "⏳ Checking database status...\n"
        
        try:
            status = anvil.server.call('check_database_status')
            
            # Build report
            report = "="*50 + "\n"
            report += "DATABASE STATUS\n"
            report += "="*50 + "\n\n"
            
            for table_name, table_info in status['tables'].items():
                report += f"\n📋 {table_name.upper()}\n"
                report += f"   Exists: {'✅ Yes' if table_info['exists'] else '❌ No'}\n"
                
                if table_info['exists']:
                    col_count = len(table_info['existing_columns'])
                    expected = table_info['expected_columns']
                    report += f"   Columns: {col_count}/{expected}\n"
                    
                    if table_info['existing_columns']:
                        report += f"   Found: {', '.join(sorted(table_info['existing_columns']))}\n"
                    
                    if table_info['missing_columns']:
                        report += f"   ⚠️ Missing: {', '.join(sorted(table_info['missing_columns']))}\n"
                    else:
                        report += f"   ✅ All columns present\n"
            
            self.status_output.text = report
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}\n"
            self.status_output.text = error_msg
            alert(f"Status check failed:\n{str(e)}", title="Error")
    
    
    def view_refresh_log_button_click(self, **event_args):
        """View refresh status and logs"""
        self.status_output.text = "⏳ Loading refresh status...\n"
        
        try:
            refresh_status = anvil.server.call('get_refresh_status')
            
            # Build report
            report = "="*50 + "\n"
            report += "DATA REFRESH STATUS\n"
            report += "="*50 + "\n\n"
            
            if refresh_status['last_run']:
                report += f"Last Run: {refresh_status['last_run'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                report += f"Status: {refresh_status['status'].upper()}\n"
                report += f"Events Found: {refresh_status.get('events_found', 0)}\n"
                report += f"Events Analyzed: {refresh_status.get('events_analyzed', 0)}\n"
                report += f"Duration: {refresh_status.get('duration_seconds', 0):.1f} seconds\n"
                
                if refresh_status.get('error_message'):
                    report += f"\n❌ Error: {refresh_status['error_message']}\n"
            else:
                report += "No refresh has been run yet.\n"
            
            report += f"\nCurrent Event Count: {refresh_status.get('events_count', 0)}\n"
            
            # Recent logs
            if refresh_status.get('recent_logs'):
                report += "\n" + "="*50 + "\n"
                report += "RECENT RUNS\n"
                report += "="*50 + "\n\n"
                
                for log in refresh_status['recent_logs']:
                    status_icon = {"success": "✅", "partial": "⚠️", "failed": "❌"}.get(log['status'], "❓")
                    report += f"{status_icon} {log['run_date'].strftime('%Y-%m-%d %H:%M')}\n"
                    report += f"   Status: {log['status']}\n"
                    report += f"   Events: {log['events_found']}\n"
                    report += f"   Duration: {log['duration']:.1f}s\n\n"
            
            self.status_output.text = report
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}\n"
            self.status_output.text = error_msg
            alert(f"Failed to load refresh status:\n{str(e)}", title="Error")
    
    
    def clear_data_button_click(self, **event_args):
        """Clear all data (DANGER!)"""
        confirm_msg = (
            "⚠️ WARNING ⚠️\n\n"
            "This will DELETE ALL DATA from:\n"
            "• Events table\n"
            "• Weather forecast table\n"
            "• Scrape log table\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you ABSOLUTELY SURE?"
        )
        
        if not confirm(confirm_msg):
            return
        
        # Double confirmation
        if not confirm("Last chance! Really delete ALL data?"):
            return
        
        self.status_output.text = "⏳ Deleting all data...\n"
        
        try:
            result = anvil.server.call('clear_all_data')
            
            total_deleted = sum(v for v in result['deleted'].values() if isinstance(v, int))
            
            report = "="*50 + "\n"
            report += "DATA CLEARED\n"
            report += "="*50 + "\n\n"
            report += f"Total rows deleted: {total_deleted}\n\n"
            
            for table, count in result['deleted'].items():
                if isinstance(count, int):
                    report += f"  • {table}: {count} rows\n"
                else:
                    report += f"  • {table}: {count}\n"
            
            self.status_output.text = report
            
            alert(f"✅ Deleted {total_deleted} rows", title="Data Cleared")
            
            # Refresh status
            self.refresh_status()
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}\n"
            self.status_output.text = error_msg
            alert(f"Failed to clear data:\n{str(e)}", title="Error")
    
    
    def refresh_status_button_click(self, **event_args):
        """Refresh the status display"""
        self.refresh_status()
        self.status_output.text = "✅ Status refreshed\n"

