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

