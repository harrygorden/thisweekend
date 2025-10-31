# This Weekend - Memphis Event Planner

An intelligent Anvil web application that helps you plan your weekend by combining real-time weather forecasts with local Memphis events, powered by AI for smart categorization and weather-aware recommendations.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Anvil](https://img.shields.io/badge/Platform-Anvil-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

- **🌤️ Weather Integration:** Live weather forecasts for Friday, Saturday, and Sunday using OpenWeather One Call API 3.0
- **📅 Event Scraping:** Automatic scraping of Memphis weekend events from ilovememphisblog.com
- **🤖 AI-Powered Analysis:** ChatGPT automatically categorizes events:
  - Indoor vs. Outdoor
  - Adult vs. Family-Friendly
  - Cost level (Free, $, $$, $$$, $$$$)
  - Categories (Arts, Music, Sports, Food & Drink, etc.)
- **🎯 Smart Recommendations:** Weather-aware suggestions that match outdoor events with good weather
- **🔍 Advanced Filtering:** Multi-criteria search by cost, category, audience type, day, and more
- **📋 Itinerary Builder:** Create personalized weekend plans with conflict detection
- **⏰ Automated Updates:** Scheduled background tasks refresh data weekly

## 🏗️ Architecture

**Frontend:** Anvil (Python-based web framework with drag-and-drop UI)  
**Backend:** Anvil Server Modules (Python)  
**Database:** Anvil Data Tables (PostgreSQL-backed)  
**APIs:**
- OpenWeather One Call API 3.0 (weather forecasts)
- Firecrawl API (web scraping)
- OpenAI API (event analysis)

## 📂 Project Structure

```
thisweekend/
├── README.md                          # This file - project overview
├── DEPLOYMENT_GUIDE.md                # Complete deployment instructions
├── USER_GUIDE.md                      # Admin interface user guide
├── project_plan.md                    # Comprehensive project plan
├── LICENSE.txt                        # MIT license
├── server_code/                       # Server-side Python modules
│   ├── config.py                      # Configuration constants
│   ├── weather_service.py             # OpenWeather API integration
│   ├── scraper_service.py             # Firecrawl SDK integration
│   ├── ai_service.py                  # OpenAI SDK integration
│   ├── data_processor.py              # Recommendation engine
│   ├── background_tasks.py            # Task orchestration
│   ├── admin_tools.py                 # Admin & testing functions
│   ├── api_helpers.py                 # Common utilities
│   └── requirements.txt               # Python dependencies
└── client_code/                       # Anvil client forms
    ├── AdminForm/                     # Admin control panel
    ├── EventCard/                     # Event card component
    └── Form1/                         # Main user interface (WIP)
```

## 🚀 Quick Start

### ✅ Phase 1 Complete!

All server-side code has been implemented. The complete data pipeline is ready to test!

### Where You Are Now

You've completed:
- ✅ Anvil app created
- ✅ API keys configured in Anvil Secrets
- ✅ Empty Data Tables created
- ✅ All 7 server modules built and ready

### ✨ Complete AdminForm Ready!

**No manual work in Anvil editor!** A complete admin panel is included.

**👉 See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step setup**

**Super quick setup:**
1. Push this code to GitHub
2. In Anvil: "Pull from Git"  
3. Set `AdminForm` as startup form
4. Click **Run** ▶️
5. Click **"Setup Database"** button
6. All 33 columns created automatically! ✨

**What you get:**
- 🎛️ Complete admin panel with testing functions
- ⚙️ One-click database setup
- 🔍 Health checks and monitoring
- 📊 Data refresh controls
- 📝 Real-time status output

**See:** [USER_GUIDE.md](USER_GUIDE.md) for complete admin interface documentation

## 📖 Documentation

### Essential Guides
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** ⚡ - Complete deployment walkthrough
- **[USER_GUIDE.md](USER_GUIDE.md)** 📚 - Admin interface documentation
- **[project_plan.md](project_plan.md)** 📋 - Complete 12-phase development plan
- **[server_code/requirements.txt](server_code/requirements.txt)** 📦 - Python dependencies

## 🗄️ Database Schema

### `events` Table (17 columns)
Stores all scraped and analyzed event data.

### `weather_forecast` Table (9 columns)
Caches weather forecasts for the upcoming weekend.

### `scrape_log` Table (7 columns)
Tracks background task execution and errors.

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for setup instructions.

## 🔧 Development Workflow

1. **Server Code Changes:**
   - Edit Python files in `server_code/` locally
   - Commit and push to GitHub
   - Pull changes in Anvil editor

2. **UI Changes:**
   - Must be made in Anvil's visual editor
   - Forms, components, and styling done in Anvil UI

3. **Data Table Changes:**
   - Schema changes must be made in Anvil UI
   - Use the setup script for initial column creation

## 📅 Development Timeline

- **Full Build:** 20-32 days
- **MVP:** 17-27 days

See [project_plan.md](project_plan.md) for detailed phase breakdown.

## 💰 Cost Estimates

Weekly operation (assuming 50 events/week):
- **OpenWeather:** ~$0.02/week
- **Firecrawl:** Varies by plan
- **OpenAI:** ~$0.05/week (GPT-3.5-turbo) or ~$0.75/week (GPT-4)
- **Total:** ~$0.07-$0.80/week

## 🔑 Required Anvil Secrets

Configure these in Anvil App Settings → Secrets:

1. `OPENWEATHER_API_KEY` - OpenWeather One Call API 3.0
2. `FIRECRAWL_API_KEY` - Firecrawl web scraping
3. `OPENAI_API_KEY` - OpenAI ChatGPT API

## 📊 Project Status

### ✅ Completed
- **Phase 1.1-1.3:** Server architecture complete (7 modules)
- **Phase 2:** Weather API integration ✅
- **Phase 3:** Event scraping & parsing ✅
- **Phase 4:** AI event analysis ✅
- **Phase 5:** Recommendation engine ✅
- **Phase 5.5:** Background task orchestration ✅

### ⏳ Current
- **Phase 1.2:** Add columns to Data Tables ← **YOU ARE HERE**

### 🔜 Next
- **Phase 2-5:** Test complete data pipeline
- **Phase 6:** Build Anvil UI (weather display, event cards)
- **Phase 7:** Implement filtering & search
- **Phase 8:** Build itinerary builder
- **Phase 9-12:** Testing, polish, deployment

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for detailed status.

## 🎯 Success Criteria

✅ Successfully retrieves weather for Friday, Saturday, Sunday  
✅ Scrapes events from ilovememphisblog.com/weekend  
✅ AI correctly categorizes events  
✅ Weather recommendations are helpful  
✅ Filters work correctly  
✅ Itinerary builder creates chronological plans  
✅ UI is intuitive and mobile-responsive  
✅ Handles errors gracefully  
✅ Performance < 5 second initial load  

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

## 📝 License

MIT License - feel free to use this as a template for your own projects.

## 🙏 Acknowledgments

- [Anvil](https://anvil.works) - Python web framework
- [OpenWeather](https://openweathermap.org) - Weather data
- [Firecrawl](https://firecrawl.dev) - Web scraping
- [OpenAI](https://openai.com) - AI analysis
- [I Love Memphis Blog](https://ilovememphisblog.com) - Event data source

## 📧 Contact

For questions or suggestions, please open an issue in the repository.

---

**Built with ❤️ in Memphis, TN**
