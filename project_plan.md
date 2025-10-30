# This Weekend - Project Plan

## Table of Contents
1. [Project Overview](#project-overview)
2. [Manual Configuration Checklist](#manual-configuration-checklist) ⚠️ **START HERE**
3. [Phase 1: Project Setup & Configuration](#phase-1-project-setup--configuration)
4. [Phase 2: Weather Data Integration](#phase-2-weather-data-integration-background-task)
5. [Phase 3: Event Data Collection](#phase-3-event-data-collection-background-task)
6. [Phase 4: AI-Powered Event Analysis](#phase-4-ai-powered-event-analysis-background-task)
7. [Phase 5: Data Combination & Recommendation Engine](#phase-5-data-combination--recommendation-engine-background-task)
8. [Phase 5.5: Background Task Orchestration](#phase-55-background-task-orchestration)
9. [Phase 6: Anvil UI Development](#phase-6-anvil-ui-development)
10. [Phase 7: Filtering & Search Functionality](#phase-7-filtering--search-functionality)
11. [Phase 8: Itinerary Builder](#phase-8-itinerary-builder)
12. [Phase 9: Data Refresh & Caching](#phase-9-data-refresh--caching)
13. [Phase 10: Testing & Quality Assurance](#phase-10-testing--quality-assurance)
14. [Phase 11: Error Handling & Edge Cases](#phase-11-error-handling--edge-cases)
15. [Phase 12: Deployment & Launch](#phase-12-deployment--launch)
16. [Future Enhancements](#future-enhancements-optional)
17. [Development Timeline Estimate](#development-timeline-estimate)
18. [Success Criteria](#success-criteria)
19. [Quick Reference](#quick-reference)

---

## 🚀 Quick Start Guide

**New to this project? Follow these steps:**

1. **Read the [ANVIL_SETUP_INSTRUCTIONS.md](ANVIL_SETUP_INSTRUCTIONS.md)** - Detailed step-by-step setup guide
2. **Obtain your API keys:**
   - OpenWeather One Call API 3.0 (paid, ~$3/1000 calls)
   - Firecrawl API
   - OpenAI API
3. **Configure Anvil (MANUAL):**
   - Enable Data Tables and Background Tasks services
   - Add the 3 API keys to Anvil Secrets
   - Create 3 **empty** Data Tables (`events`, `weather_forecast`, `scrape_log`)
4. **Run the automated setup script:**
   - `pip install anvil-uplink`
   - `python setup_data_tables.py`
   - This auto-creates all table columns for you!
5. **Start with Phase 1** - Set up the server module structure
6. **Work through Phases 2-5.5** - Build the data pipeline and background task
7. **Build the UI in Phases 6-8** - Create forms and components in Anvil
8. **Test, polish, and deploy** - Phases 9-12

**Estimated Timeline:** 20-32 days for full build, 17-27 days for MVP

---

## Project Overview
An Anvil web application to help users plan their weekend activities by combining weather forecasts with local event data, AI-powered categorization, and intelligent filtering.

### Core Features
- Weather forecast integration (OpenWeather One Call API 3.0)
- Event scraping from ilovememphisblog.com/weekend (Firecrawl)
- AI-powered event analysis (ChatGPT)
- Weather-aware event recommendations
- Multi-criteria filtering (cost, category, audience)
- Custom itinerary builder

### Architecture Notes
- **Background Processing:** Anvil Scheduler will run a single scheduled background task to scrape events, fetch weather, and perform AI analysis
- **Data Storage:** Anvil Data Tables will cache processed events to avoid repeated API calls
- **GitHub Integration:** App is synced with GitHub for version control
- **Manual Configuration:** Some setup required in Anvil UI (see Manual Configuration section)

### Anvil Project Structure
```
thisweekend/
├── client_code/              # Client-side (browser) Python code
│   ├── Form1/               # Main form
│   │   ├── __init__.py
│   │   └── form_template.yaml
│   ├── EventCard/           # Event card component (repeating panel item)
│   │   ├── __init__.py
│   │   └── form_template.yaml
│   └── ItineraryView/       # Itinerary display component
│       ├── __init__.py
│       └── form_template.yaml
├── server_code/              # Server-side Python code
│   ├── config.py            # Configuration constants
│   ├── weather_service.py   # OpenWeather API integration
│   ├── scraper_service.py   # Firecrawl integration
│   ├── ai_service.py        # OpenAI/ChatGPT integration
│   ├── data_processor.py    # Data combination & scoring
│   ├── background_tasks.py  # Scheduled task orchestrator
│   └── api_helpers.py       # Common utilities
├── theme/                    # Anvil theme/styling
└── anvil.yaml               # Anvil app configuration
```

**Note:** When working with GitHub-synced Anvil apps:
- Server code changes can be made in this repo and pushed to GitHub
- Anvil will automatically pull changes from GitHub
- UI/Form changes MUST be made in Anvil's visual editor
- Data Table schemas MUST be created in Anvil UI
- Secrets MUST be configured in Anvil UI
- After editing server code locally, commit and push, then pull in Anvil

---

## Manual Configuration Checklist

> 📖 **Detailed step-by-step instructions available in:** [ANVIL_SETUP_INSTRUCTIONS.md](ANVIL_SETUP_INSTRUCTIONS.md)
> 
> 🤖 **Automated column setup script:** `setup_data_tables.py` (run after creating empty tables)

### Anvil Secrets (App Settings → Secrets)
The following secrets must be configured in your Anvil app:

1. **`OPENWEATHER_API_KEY`**
   - Description: API key for OpenWeather One Call API 3.0
   - How to obtain: Sign up at https://openweathermap.org/api
   - Required subscription: One Call API 3.0 (paid, ~$3/1000 calls)
   - Note: Free tier API does NOT include One Call 3.0

2. **`FIRECRAWL_API_KEY`**
   - Description: API key for Firecrawl web scraping service
   - How to obtain: Sign up at https://firecrawl.dev
   - Note: Check pricing for scraping frequency needs

3. **`OPENAI_API_KEY`**
   - Description: API key for OpenAI ChatGPT API
   - How to obtain: Sign up at https://platform.openai.com
   - Recommended model: GPT-4 or GPT-3.5-turbo
   - Note: Monitor token usage costs

### Anvil App Services to Enable

1. **Data Tables**
   - Enable in: App Settings → Services → Data Tables
   - Required for caching events and weather data

2. **Background Tasks (Uplink/Scheduler)**
   - Enable in: App Settings → Services → Uplink
   - OR use Anvil's built-in Scheduled Tasks if available on your plan
   - Required for automated data refresh

### Anvil Data Tables to Create

Navigate to **Data Tables** tab and create the following tables:

#### Table 1: `events`
| Column Name | Type | Description |
|------------|------|-------------|
| `event_id` | Text | Unique identifier (auto-generated) |
| `title` | Text | Event name |
| `description` | Text | Event description (long text) |
| `date` | Date | Event date |
| `start_time` | Text | Start time (formatted string) |
| `end_time` | Text | End time (formatted string, optional) |
| `location` | Text | Event location/venue |
| `cost_raw` | Text | Original cost text from website |
| `cost_level` | Text | Standardized: "Free", "$", "$$", "$$$", "$$$$" |
| `is_indoor` | Boolean | True if indoor, False if outdoor |
| `is_outdoor` | Boolean | True if outdoor, False if indoor |
| `audience_type` | Text | "adults", "family-friendly", or "all-ages" |
| `categories` | SimpleObject | List of categories (JSON) |
| `weather_score` | Number | Weather suitability score (0-100) |
| `recommendation_score` | Number | Overall recommendation score (0-100) |
| `scraped_at` | DateTime | When event was scraped |
| `analyzed_at` | DateTime | When AI analysis completed |

#### Table 2: `weather_forecast`
| Column Name | Type | Description |
|------------|------|-------------|
| `forecast_date` | Date | Date of forecast |
| `day_name` | Text | "Friday", "Saturday", or "Sunday" |
| `temp_high` | Number | High temperature (°F) |
| `temp_low` | Number | Low temperature (°F) |
| `conditions` | Text | Weather description |
| `precipitation_chance` | Number | Chance of rain (0-100%) |
| `wind_speed` | Number | Wind speed (mph) |
| `hourly_data` | SimpleObject | Hourly forecast (JSON) |
| `fetched_at` | DateTime | When forecast was retrieved |

#### Table 3: `scrape_log`
| Column Name | Type | Description |
|------------|------|-------------|
| `log_id` | Text | Unique log ID |
| `run_date` | DateTime | When background task ran |
| `status` | Text | "success", "partial", "failed" |
| `events_found` | Number | Number of events scraped |
| `events_analyzed` | Number | Number of events analyzed by AI |
| `error_message` | Text | Error details if failed |
| `duration_seconds` | Number | How long the task took |

### Anvil Scheduled Task Setup

1. Navigate to **Server Code** → **Background Tasks**
2. Create new scheduled task:
   - **Name:** `refresh_weekend_data`
   - **Function:** `scheduled_refresh_all_data` (in `background_tasks.py`)
   - **Schedule:** Weekly on Monday at 6:00 AM (or your preferred time)
   - **Timeout:** 10 minutes (may need adjustment based on event count)

### Memphis, TN Coordinates
- **Latitude:** 35.1495
- **Longitude:** -90.0490
- (Hardcode these in your weather service module)

### Additional Manual Steps

1. **Test API Keys:**
   - After adding secrets, run test functions to verify connectivity
   - Create a test form/button to manually trigger data refresh during development

2. **Initial Data Load:**
   - First run may take several minutes
   - Manually trigger background task initially to populate data

3. **GitHub Sync Settings:**
   - Ensure `.gitignore` excludes any local config files
   - Never commit API keys to repository

---

## Phase 1: Project Setup & Configuration

### 1.1 Manual Anvil Configuration ⚠️ MANUAL STEPS
- [ ] Enable Data Tables service (App Settings → Services)
- [ ] Enable Background Tasks/Uplink service (App Settings → Services)
- [ ] Configure Anvil Secrets (see Manual Configuration Checklist above):
  - [ ] Add `OPENWEATHER_API_KEY`
  - [ ] Add `FIRECRAWL_API_KEY`
  - [ ] Add `OPENAI_API_KEY`

### 1.2 Anvil Data Tables Creation ⚠️ MANUAL + AUTOMATED
- [ ] **MANUAL:** Create 3 empty tables in Anvil UI:
  - [ ] Create `events` table (empty, no columns yet)
  - [ ] Create `weather_forecast` table (empty)
  - [ ] Create `scrape_log` table (empty)
- [ ] **AUTOMATED:** Run `setup_data_tables.py` script locally to auto-create all columns
  - [ ] Install anvil-uplink: `pip install anvil-uplink`
  - [ ] Run: `python setup_data_tables.py`
  - [ ] Enter Uplink key when prompted
- [ ] **MANUAL:** Verify table schemas in Anvil UI (see ANVIL_SETUP_INSTRUCTIONS.md)
- [ ] **MANUAL:** Set table permissions (server = full access, client = read-only or none)

### 1.3 Server Module Structure (CODE)
- [ ] Create `server_code/config.py` - Constants and configuration
- [ ] Create `server_code/weather_service.py` - OpenWeather API integration
- [ ] Create `server_code/scraper_service.py` - Firecrawl integration
- [ ] Create `server_code/ai_service.py` - OpenAI/ChatGPT integration
- [ ] Create `server_code/data_processor.py` - Data combination and scoring
- [ ] Create `server_code/background_tasks.py` - Scheduled task orchestrator
- [ ] Create `server_code/api_helpers.py` - Common API utility functions

### 1.4 API Keys Acquisition ⚠️ MANUAL STEPS
- [ ] Obtain OpenWeather API key (One Call API 3.0) - https://openweathermap.org/api
- [ ] Obtain Firecrawl API key - https://firecrawl.dev
- [ ] Obtain OpenAI API key - https://platform.openai.com
- [ ] Test each API key before adding to Anvil Secrets

---

## Phase 2: Weather Data Integration (Background Task)

### 2.1 OpenWeather API Integration (`weather_service.py`)
- [ ] Create `fetch_weekend_weather()` function
- [ ] Implement One Call API 3.0 request (lat: 35.1495, lon: -90.0490)
- [ ] Parse API response for upcoming Friday, Saturday, Sunday forecasts
- [ ] Extract relevant weather data (temperature, conditions, precipitation, wind)
- [ ] Handle API errors and rate limiting gracefully
- [ ] Return structured weather data dictionary

### 2.2 Weather Data Storage
- [ ] Create `save_weather_to_db()` function
- [ ] Clear old weather data from `weather_forecast` table
- [ ] Insert new forecasts for Friday, Saturday, Sunday
- [ ] Store hourly data as SimpleObject/JSON
- [ ] Set `fetched_at` timestamp

### 2.3 Weather Data Processing
- [ ] Create `calculate_weather_score()` function for events
- [ ] Determine weather suitability scores (0-100) based on:
  - Precipitation chance (outdoor events penalized)
  - Temperature extremes
  - Wind speed
- [ ] Create `get_weather_for_datetime()` helper function
- [ ] Handle timezone conversions for Memphis, TN (Central Time)
- [ ] Create hourly weather breakdown for each day

---

## Phase 3: Event Data Collection (Background Task)

### 3.1 Web Scraping with Firecrawl (`scraper_service.py`)
- [ ] Create `scrape_weekend_events()` function
- [ ] Implement Firecrawl API integration
- [ ] Configure scraping parameters for https://ilovememphisblog.com/weekend
- [ ] Use Firecrawl's markdown extraction format
- [ ] Handle scraping errors and implement retry logic
- [ ] Return raw scraped content (markdown/text)

### 3.2 Event Data Parsing (`scraper_service.py`)
- [ ] Create `parse_events_from_markdown()` function
- [ ] Use regex/patterns to identify event sections
- [ ] Extract event details (title, date, time, location, description, cost)
- [ ] Parse date and time information (handle various formats)
- [ ] Extract cost information (preserve raw text)
- [ ] Extract location details
- [ ] Clean and normalize event descriptions
- [ ] Handle missing or incomplete event data
- [ ] Return list of event dictionaries

### 3.3 Event Data Storage (Initial)
- [ ] Create `save_events_to_db()` function
- [ ] Clear old events from `events` table (events older than current week)
- [ ] Insert new events with initial data (before AI analysis)
- [ ] Set `scraped_at` timestamp
- [ ] Generate unique `event_id` for each event

---

## Phase 4: AI-Powered Event Analysis (Background Task)

### 4.1 ChatGPT Integration (`ai_service.py`)
- [ ] Create `analyze_event()` function (single event analysis)
- [ ] Design comprehensive prompt for multi-faceted analysis:
  - Indoor/outdoor classification
  - Audience type (adults, family-friendly, all-ages)
  - Category assignment (arts, music, sports, food & drink, outdoor activities, cultural events, etc.)
  - Cost level standardization (Free, $, $$, $$$, $$$$) if ambiguous
- [ ] Implement OpenAI API call using GPT-3.5-turbo or GPT-4
- [ ] Request JSON response format for structured output
- [ ] Handle API errors and rate limiting
- [ ] Implement retry logic with exponential backoff

### 4.2 Batch Event Analysis (`ai_service.py`)
- [ ] Create `analyze_all_events()` function
- [ ] Loop through all scraped events
- [ ] Call `analyze_event()` for each event
- [ ] Add rate limiting/delays to avoid API throttling
- [ ] Track analysis progress
- [ ] Return analyzed event data

### 4.3 AI Response Processing (`ai_service.py`)
- [ ] Create `parse_ai_response()` function
- [ ] Parse JSON response from ChatGPT
- [ ] Extract and validate:
  - `is_indoor` (boolean)
  - `is_outdoor` (boolean)
  - `audience_type` (string)
  - `cost_level` (string)
  - `categories` (list)
- [ ] Create fallback logic for AI failures (use defaults)
- [ ] Log AI decisions for debugging

### 4.4 Update Events with AI Analysis
- [ ] Create `update_events_with_analysis()` function
- [ ] Update each event in `events` table with AI results
- [ ] Set `analyzed_at` timestamp
- [ ] Preserve original scraped data

---

## Phase 5: Data Combination & Recommendation Engine (Background Task)

### 5.1 Weather-Event Matching (`data_processor.py`)
- [ ] Create `match_events_with_weather()` function
- [ ] For each event, find corresponding weather forecast by date
- [ ] Get hourly weather for event time (if available)
- [ ] Calculate weather suitability scores using `calculate_weather_score()`
- [ ] Handle events without specific times (use daily average)

### 5.2 Event Scoring System (`data_processor.py`)
- [ ] Create `calculate_recommendation_score()` function
- [ ] Develop composite scoring algorithm (0-100):
  - **Outdoor Events:**
    - Weather score (70% weight): High temps, low rain = high score
    - Time of day (30% weight): Evening outdoor events score higher
  - **Indoor Events:**
    - Baseline score of 80 (weather-independent)
    - Bad weather increases indoor event scores slightly
- [ ] Create weather warnings for outdoor events with poor conditions
- [ ] Update events table with `weather_score` and `recommendation_score`

### 5.3 Final Data Update
- [ ] Update all events in database with final scores
- [ ] Ensure all data is ready for UI consumption
- [ ] Log completion status

---

## Phase 5.5: Background Task Orchestration

### 5.5.1 Master Background Task (`background_tasks.py`)
- [ ] Create `scheduled_refresh_all_data()` function (entry point for scheduler)
- [ ] Implement complete workflow:
  1. Log task start in `scrape_log` table
  2. Call `fetch_weekend_weather()` - get weather data
  3. Call `save_weather_to_db()` - store weather
  4. Call `scrape_weekend_events()` - scrape events
  5. Call `parse_events_from_markdown()` - parse events
  6. Call `save_events_to_db()` - store initial events
  7. Call `analyze_all_events()` - AI analysis
  8. Call `update_events_with_analysis()` - update with AI results
  9. Call `match_events_with_weather()` - match weather to events
  10. Call `calculate_recommendation_score()` - score events
  11. Log task completion in `scrape_log` table
- [ ] Wrap each step in try/except for error handling
- [ ] Continue on partial failures when possible
- [ ] Return detailed status report

### 5.5.2 Manual Trigger Function
- [ ] Create `@anvil.server.callable` wrapper for manual triggering
- [ ] Create `trigger_data_refresh()` callable function
- [ ] Allow admin/test form to trigger refresh manually
- [ ] Return progress updates to client

### 5.5.3 Progress Logging
- [ ] Create logging utility functions
- [ ] Track progress at each step
- [ ] Store comprehensive logs in `scrape_log` table
- [ ] Calculate and store task duration

### 5.5.4 Scheduled Task Setup ⚠️ MANUAL STEPS
- [ ] In Anvil UI, navigate to Server Code → Background Tasks
- [ ] Register `scheduled_refresh_all_data` as scheduled task
- [ ] Set schedule: Weekly on Monday at 6:00 AM (or preferred time)
- [ ] Set timeout: 10-15 minutes (adjust based on testing)
- [ ] Test manual execution before scheduling

---

## Phase 6: Anvil UI Development

### 6.1 Server-Side Data Access Functions
- [ ] Create `@anvil.server.callable` functions in server code:
  - [ ] `get_weather_data()` - returns weather forecast from `weather_forecast` table
  - [ ] `get_all_events()` - returns all events from `events` table
  - [ ] `get_filtered_events(filters)` - returns filtered events
  - [ ] `get_last_refresh_time()` - returns last scrape timestamp
  - [ ] `trigger_data_refresh()` - manually trigger background task (for testing)

### 6.2 Main Form Layout (`Form1` or `MainForm`)
- [ ] Design app header with title "This Weekend in Memphis"
- [ ] Add last updated timestamp display
- [ ] Create responsive column layout (mobile and desktop)
- [ ] Add loading indicators for data fetch
- [ ] Create error message display areas
- [ ] Add manual refresh button (for testing/admin)

### 6.3 Weather Display Component
- [ ] Create weather card panel/component
- [ ] Display 3 cards for Friday, Saturday, Sunday
- [ ] Show for each day:
  - Day name and date
  - High/Low temperature
  - Weather conditions (text description)
  - Precipitation chance
  - Weather icon (emoji or image)
- [ ] Create expandable hourly forecast view (optional)
- [ ] Style weather cards with Material Design

### 6.4 Events List Component
- [ ] Create repeating panel for events (`RepeatingPanel`)
- [ ] Create event card template (`EventCard` component):
  - Event title (bold, large)
  - Date and time
  - Location
  - Description (truncated with "read more")
  - Cost indicator (Free/$/$$/$$$/$$$$)
  - Category tags (colored labels)
  - Audience type badge (adults/family-friendly/all-ages)
  - Indoor/outdoor indicator (icon)
  - Weather recommendation badge (good/fair/poor for outdoor events)
  - "Add to Itinerary" checkbox/button
- [ ] Implement expandable event details (click to expand)
- [ ] Sort events by recommendation score (default) or by time
- [ ] Style event cards with consistent spacing and colors

### 6.5 Filter Panel Component
- [ ] Create filter sidebar/panel
- [ ] Add filter sections:
  - **Day Filter:** Checkboxes for Friday, Saturday, Sunday, All
  - **Cost Filter:** Checkboxes for Free, $, $$, $$$, $$$$
  - **Category Filter:** Checkboxes for:
    - Arts
    - Music
    - Sports
    - Food & Drink
    - Outdoor Activities
    - Cultural Events
    - Theater/Performance
    - Family/Kids
    - Nightlife
    - (Others as discovered from AI analysis)
  - **Audience Filter:** Radio buttons or checkboxes for Adults, Family-Friendly, All
  - **Indoor/Outdoor:** Checkboxes for Indoor, Outdoor
- [ ] Add "Clear All Filters" button
- [ ] Add "Apply Filters" button (or auto-apply on change)
- [ ] Style filter panel for usability (collapsible on mobile)

---

## Phase 7: Filtering & Search Functionality

### 7.1 Server-Side Filter Logic
- [ ] Create `apply_filters()` function in server code
- [ ] Implement filter logic for:
  - Day filter (match event date)
  - Cost filter (match cost_level)
  - Category filter (check if event categories include selected)
  - Audience filter (match audience_type)
  - Indoor/outdoor filter (check is_indoor/is_outdoor flags)
- [ ] Combine multiple filter criteria (AND logic across types, OR within types)
- [ ] Return filtered event list

### 7.2 Client-Side Filter UI Logic
- [ ] Track filter state in form (checkboxes/radio buttons)
- [ ] Create `apply_filters_click()` event handler
- [ ] Collect all selected filters
- [ ] Call server `get_filtered_events(filters)`
- [ ] Update events repeating panel with filtered results
- [ ] Update result count display
- [ ] Show "no results" message when appropriate

### 7.3 Search Functionality
- [ ] Add search text box to UI
- [ ] Create `search_events()` function (server-side)
- [ ] Search by title, description, location (case-insensitive)
- [ ] Combine search with active filters
- [ ] Update display in real-time (on text change or button click)

### 7.4 Sort Options
- [ ] Add sort dropdown to UI (Recommended, Time, Cost)
- [ ] Implement sort logic:
  - **Recommended:** Sort by recommendation_score (desc)
  - **Time:** Sort by date, then start_time
  - **Cost:** Sort by cost_level (Free first)
- [ ] Apply sort to filtered results
- [ ] Update display when sort changes

---

## Phase 8: Itinerary Builder

### 8.1 Selection Management (Client-Side)
- [ ] Add checkbox to each event card for selection
- [ ] Track selected events in form property (list of event_ids)
- [ ] Create `event_selected_change()` event handler
- [ ] Add/remove event from selected list on checkbox change
- [ ] Visual indicator for selected events (highlight/border)
- [ ] Display selected event count badge
- [ ] Add "Clear Itinerary" button

### 8.2 Itinerary Display Panel
- [ ] Create separate itinerary panel/section (collapsible or separate page)
- [ ] Create "View My Itinerary" button
- [ ] Display selected events grouped by day:
  - **Friday** section
  - **Saturday** section
  - **Sunday** section
- [ ] Sort events by time within each day
- [ ] Show simplified event info:
  - Time
  - Title
  - Location
  - Weather forecast for that time
- [ ] Add "Remove" button for each event in itinerary
- [ ] Show total event count

### 8.3 Itinerary Enhancements
- [ ] Time conflict detection:
  - Check for overlapping event times
  - Highlight conflicts in red
  - Show warning message
- [ ] Calculate total time commitment
- [ ] Show weather summary for each day in itinerary
- [ ] Add notes field for user (optional future feature)

### 8.4 Itinerary Export
- [ ] Create "Export Itinerary" button
- [ ] Generate formatted text itinerary:
  - Include weather summary
  - List events by day and time
  - Include locations
- [ ] Create print-friendly dialog/view (using Anvil alert or custom form)
- [ ] Add "Copy to Clipboard" functionality
- [ ] Optional: Email itinerary (requires email integration)

---

## Phase 9: Data Refresh & Caching

### 9.1 Data Lifecycle Management
- [ ] Scheduled refresh already implemented via background task (Phase 5.5)
- [ ] Implement data cleanup:
  - [ ] Delete events older than 1 week
  - [ ] Delete weather forecasts older than 3 days
  - [ ] Keep scrape_log entries for 30 days (for history)
- [ ] Create `cleanup_old_data()` function in background tasks
- [ ] Call cleanup at start of scheduled refresh

### 9.2 Manual Refresh UI
- [ ] Add "Refresh Data" button to admin/test form
- [ ] Show loading indicator during refresh
- [ ] Display refresh progress (if possible with background tasks)
- [ ] Show success/error message after completion
- [ ] Disable button during refresh to prevent multiple triggers

### 9.3 Data Freshness Indicators
- [ ] Display last update timestamp on main form
- [ ] Show "data is fresh" vs "data is stale" indicator
- [ ] Calculate time since last refresh
- [ ] Show next scheduled refresh time

### 9.4 Performance Optimization
- [ ] Cache event list in client-side form property (reduce server calls)
- [ ] Only re-fetch data when filters change
- [ ] Optimize Data Table queries (use indexes if needed)
- [ ] Minimize server roundtrips for filtering (do client-side when possible)
- [ ] Implement lazy loading for event descriptions (expand on demand)

---

## Phase 10: Testing & Quality Assurance

### 10.1 Component Testing
- [ ] Test weather API integration:
  - [ ] Test with valid API key
  - [ ] Test with invalid API key (error handling)
  - [ ] Test with different weather conditions
  - [ ] Verify date calculations for Friday/Saturday/Sunday
- [ ] Test scraping functionality:
  - [ ] Test successful scrape
  - [ ] Test failed scrape (error handling)
  - [ ] Test with different event formats
  - [ ] Verify event parsing accuracy
- [ ] Test AI analysis:
  - [ ] Test with various event types
  - [ ] Test error handling for API failures
  - [ ] Verify categorization accuracy
  - [ ] Test with edge cases (ambiguous events)
- [ ] Test filtering logic:
  - [ ] Test each filter type independently
  - [ ] Test combined filters
  - [ ] Test with no results
  - [ ] Test "clear filters" functionality

### 10.2 Integration Testing
- [ ] Test complete background task workflow:
  - [ ] Run scheduled_refresh_all_data manually
  - [ ] Verify all data is collected and stored
  - [ ] Check scrape_log entries
  - [ ] Verify event and weather data in tables
- [ ] Test UI data flow:
  - [ ] Load events from database
  - [ ] Apply filters and verify results
  - [ ] Build itinerary and verify display
  - [ ] Test export functionality
- [ ] Test error scenarios:
  - [ ] API failures (each service)
  - [ ] Database errors
  - [ ] No events found
  - [ ] No weather data

### 10.3 User Experience Testing
- [ ] Test on mobile devices:
  - [ ] iOS Safari
  - [ ] Android Chrome
  - [ ] Verify responsive layout
  - [ ] Check filter panel (collapsible on mobile)
- [ ] Test on desktop browsers:
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Edge
- [ ] Performance testing:
  - [ ] Measure page load time
  - [ ] Test with 50+ events
  - [ ] Test filter response time
  - [ ] Test background task duration
- [ ] Usability testing:
  - [ ] Verify intuitive navigation
  - [ ] Check button labels and placement
  - [ ] Verify color contrast and accessibility
  - [ ] Test workflow from viewing events to building itinerary

---

## Phase 11: Error Handling & Edge Cases

### 11.1 API Error Handling
- [ ] OpenWeather API:
  - [ ] Handle invalid API key
  - [ ] Handle rate limiting (429 errors)
  - [ ] Handle network timeouts
  - [ ] Fallback: Show "Weather unavailable" message
- [ ] Firecrawl API:
  - [ ] Handle scraping failures
  - [ ] Handle malformed HTML/content
  - [ ] Fallback: Use cached events from previous week
- [ ] OpenAI API:
  - [ ] Handle rate limiting
  - [ ] Handle token limit errors
  - [ ] Handle invalid responses
  - [ ] Fallback: Use default categorizations

### 11.2 Data Edge Cases
- [ ] No events found:
  - [ ] Display friendly message
  - [ ] Show previous week's events as backup (optional)
  - [ ] Suggest checking back later
- [ ] Events with missing data:
  - [ ] Handle missing times (show "TBD" or "All Day")
  - [ ] Handle missing location (show "See event details")
  - [ ] Handle missing cost (show "Varies" or "Free")
  - [ ] Handle missing description (show title only)
- [ ] Weather edge cases:
  - [ ] Handle extreme temperatures (show warnings)
  - [ ] Handle severe weather (storms, etc.) - highlight prominently
  - [ ] Handle API outages (show cached weather or "unavailable")
- [ ] Date/time edge cases:
  - [ ] Handle events spanning multiple days
  - [ ] Handle all-day events
  - [ ] Handle midnight boundary events
  - [ ] Verify correct timezone (Central Time for Memphis)

### 11.3 User Error Handling
- [ ] No filters selected (show all events)
- [ ] Conflicting filters (no results) - show helpful message
- [ ] Empty itinerary - show prompt to select events
- [ ] Network errors - show retry button

### 11.4 Logging & Monitoring
- [ ] Log all API errors to scrape_log table
- [ ] Track success/failure rates
- [ ] Monitor API costs (especially OpenAI)
- [ ] Create admin view to check logs (optional)

---

## Phase 12: Deployment & Launch

### 12.1 Pre-Launch Checklist ⚠️ MANUAL STEPS
- [ ] Verify all Anvil Secrets are configured:
  - [ ] OPENWEATHER_API_KEY
  - [ ] FIRECRAWL_API_KEY
  - [ ] OPENAI_API_KEY
- [ ] Verify all Data Tables are created and configured
- [ ] Verify background task is scheduled
- [ ] Run manual data refresh to populate initial data
- [ ] Test app thoroughly on Anvil platform
- [ ] Check mobile responsiveness on real devices
- [ ] Verify all filters work correctly
- [ ] Test itinerary builder end-to-end
- [ ] Review error handling for all scenarios

### 12.2 Documentation
- [ ] Add in-app help text/tooltips
- [ ] Create brief user guide (optional)
- [ ] Document API costs and limits
- [ ] Document scheduled task settings
- [ ] Create maintenance/admin guide

### 12.3 Launch
- [ ] App is already deployed to Anvil (synced with GitHub)
- [ ] Make app public or share link with users
- [ ] Monitor first scheduled background task run
- [ ] Check scrape_log for errors
- [ ] Verify events and weather data are displayed correctly

### 12.4 Post-Launch Monitoring
- [ ] Monitor API usage and costs:
  - [ ] OpenWeather API calls (pay-per-use)
  - [ ] Firecrawl API calls (check quota)
  - [ ] OpenAI API token usage ($$)
- [ ] Check scrape_log table weekly for errors
- [ ] Monitor background task execution
- [ ] Gather user feedback
- [ ] Fix critical bugs as discovered
- [ ] Create issue tracker for enhancement requests

### 12.5 Ongoing Maintenance
- [ ] Weekly check of background task logs
- [ ] Monthly review of API costs
- [ ] Update scraping logic if website changes
- [ ] Adjust AI prompts if categorization needs improvement
- [ ] Update category list based on event types discovered

---

## Future Enhancements (Optional)

### Potential V2 Features
- [ ] Multiple city support
- [ ] User accounts and saved preferences
- [ ] Historical weather correlation
- [ ] Social sharing features
- [ ] Map integration for event locations
- [ ] Traffic/drive time estimates
- [ ] Event reminders
- [ ] User reviews and ratings
- [ ] Integration with calendar apps (Google Calendar, Outlook)
- [ ] Machine learning for personalized recommendations

---

## Technical Stack Summary

**Frontend:** Anvil (Python-based web framework)
**Weather API:** OpenWeather One Call API 3.0
**Web Scraping:** Firecrawl API
**AI Analysis:** OpenAI ChatGPT API
**Language:** Python (Anvil server modules)
**Storage:** Anvil Data Tables (optional, for caching)

---

## Dependencies & Resources

### Required APIs
1. OpenWeather One Call API 3.0 - https://openweathermap.org/api/one-call-3
2. Firecrawl API - https://firecrawl.dev
3. OpenAI API - https://platform.openai.com

### Python Libraries (Anvil Compatible)
- `requests` - HTTP requests
- `openai` - OpenAI API client
- `firecrawl-py` - Firecrawl client (or requests-based alternative)
- `datetime` - Date/time handling
- `json` - JSON parsing

### Target Website
- https://ilovememphisblog.com/weekend

---

## Development Timeline Estimate

- **Phase 1:** 1-2 days (Manual configuration + Server module structure)
- **Phase 2:** 2-3 days (Weather API integration + storage)
- **Phase 3:** 2-3 days (Web scraping + event parsing)
- **Phase 4:** 2-3 days (AI analysis integration)
- **Phase 5:** 1-2 days (Recommendation engine + scoring)
- **Phase 5.5:** 1-2 days (Background task orchestration)
- **Phase 6:** 3-4 days (Anvil UI development - forms, components)
- **Phase 7:** 2-3 days (Filtering & search functionality)
- **Phase 8:** 2-3 days (Itinerary builder)
- **Phase 9:** 1-2 days (Data refresh & caching optimization)
- **Phase 10:** 2-3 days (Testing & QA)
- **Phase 11:** 2-3 days (Error handling & edge cases)
- **Phase 12:** 1-2 days (Final deployment & documentation)

**Total Estimated Time:** 20-32 days

### Accelerated Timeline (MVP)
Focus on core functionality first:
- **Phases 1-5.5:** Get data pipeline working (10-15 days)
- **Phase 6:** Basic UI to display events (2-3 days)
- **Phase 7:** Basic filtering (1-2 days)
- **Phase 8:** Simple itinerary (1-2 days)
- **Phase 10-12:** Testing & deployment (3-5 days)

**MVP Timeline:** 17-27 days

---

## Success Criteria

✅ Successfully retrieves and displays weather for Friday, Saturday, Sunday
✅ Successfully scrapes events from ilovememphisblog.com/weekend
✅ AI correctly categorizes events (indoor/outdoor, audience, categories, cost)
✅ Weather recommendations are logical and helpful
✅ Filters work correctly and in combination
✅ Itinerary builder creates chronological, conflict-free plans
✅ UI is intuitive and mobile-responsive
✅ App handles errors gracefully
✅ Performance is acceptable (< 5 second initial load)

---

## Quick Reference

### API Documentation Links
- **OpenWeather One Call API 3.0:** https://openweathermap.org/api/one-call-3
  - Pricing: ~$3 per 1,000 calls (no free tier for One Call 3.0)
  - Rate limit: 1,000 calls/day on basic plan
- **Firecrawl API:** https://docs.firecrawl.dev
  - Pricing: Check current pricing at https://firecrawl.dev/pricing
  - Rate limits: Varies by plan
- **OpenAI API:** https://platform.openai.com/docs
  - Pricing: ~$0.002 per 1K tokens (GPT-3.5-turbo), ~$0.03 per 1K tokens (GPT-4)
  - Rate limits: Varies by account tier
- **Anvil Documentation:** https://anvil.works/docs
  - Scheduled Tasks: https://anvil.works/docs/background-tasks
  - Data Tables: https://anvil.works/docs/data-tables

### Cost Estimates (Weekly Operation)
Assuming 50 events per week:
- **OpenWeather:** ~7 API calls/week (3 days × 1-2 calls) = ~$0.02/week
- **Firecrawl:** 1-2 scrapes/week = varies by plan
- **OpenAI:** 50 events × ~500 tokens each = ~25K tokens = ~$0.05/week (GPT-3.5) or ~$0.75/week (GPT-4)
- **Total:** ~$0.07-$0.80/week depending on model choice

**Recommendation:** Start with GPT-3.5-turbo for cost efficiency, upgrade to GPT-4 if categorization accuracy needs improvement.

### Memphis, TN Information
- **Coordinates:** Latitude 35.1495, Longitude -90.0490
- **Timezone:** America/Chicago (Central Time, UTC-6 or UTC-5 during DST)
- **Weekend Blog:** https://ilovememphisblog.com/weekend

### Important Notes
- Weekly data refresh recommended (Monday or Tuesday before next weekend)
- AI token costs should be monitored (each event requires ~500 tokens for analysis)
- OpenWeather One Call 3.0 requires paid subscription (no free tier)
- Firecrawl rate limits - plan scraping frequency accordingly
- Test all APIs with small datasets before full deployment
- Consider implementing daily rate limit checks to avoid unexpected charges

