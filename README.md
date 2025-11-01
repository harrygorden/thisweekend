# This Weekend - Memphis Event Planner

An intelligent Anvil web application that combines real-time weather forecasts with local Memphis events, powered by AI for smart categorization and weather-aware recommendations.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Anvil](https://img.shields.io/badge/Platform-Anvil-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

- **🌤️ Weather Integration** - Live forecasts for Friday, Saturday, and Sunday using OpenWeather One Call API 3.0
- **📅 Event Scraping** - Automatic collection of Memphis weekend events from ilovememphisblog.com
- **🤖 AI-Powered Analysis** - GPT-4.1-mini categorizes events (indoor/outdoor, audience type, cost, categories)
- **🎯 Smart Recommendations** - Weather-aware suggestions that match outdoor events with good weather
- **🔍 Advanced Filtering** - Multi-criteria search by cost, category, audience type, day, and more
- **📋 Itinerary Builder** - Create personalized weekend plans with conflict detection
- **⏰ Automated Updates** - Scheduled background tasks refresh data weekly

## 🏗️ Architecture

**Platform:** [Anvil](https://anvil.works) - Python-based web framework  
**Backend:** Anvil Server Modules (Python 3.10+)  
**Database:** Anvil Data Tables (PostgreSQL-backed)  
**APIs:**
- OpenWeather One Call API 3.0 (weather forecasts)
- Firecrawl API (web scraping)
- OpenAI API (GPT-4.1-mini for analysis, GPT-4.1 for suggestions)

## 📂 Project Structure

```
thisweekend/
├── server_code/              # Backend Python modules
│   ├── background_tasks.py   # Scheduled task orchestration
│   ├── weather_service.py    # OpenWeather API integration
│   ├── scraper_service.py    # Firecrawl web scraping
│   ├── ai_service.py         # OpenAI event analysis
│   ├── data_processor.py     # Recommendation engine
│   ├── admin_tools.py        # Admin utilities
│   ├── config.py             # Configuration constants
│   ├── api_helpers.py        # Common utilities
│   └── requirements.txt      # Python dependencies
├── client_code/              # Frontend Anvil forms
│   ├── MainApp/              # Main user interface
│   ├── AdminForm/            # Admin panel
│   ├── EventCard/            # Event display component
│   └── WeatherCard/          # Weather display component
├── theme/                    # Anvil theme/styling
├── README.md                 # This file
├── DEPLOYMENT.md             # Setup & deployment guide
└── ADMIN_GUIDE.md            # Administrator operations guide
```

## 🚀 Quick Start

### Prerequisites

- Anvil account ([sign up](https://anvil.works))
- GitHub account
- API keys:
  - [OpenWeather API](https://openweathermap.org/api) - One Call API 3.0 access
  - [Firecrawl API](https://firecrawl.dev)
  - [OpenAI API](https://openai.com)

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete setup instructions.

**Quick overview:**
1. Create Anvil app and connect to GitHub
2. Install Python dependencies (`firecrawl-py`, `openai`, `pytz`)
3. Configure API keys in Anvil Secrets
4. Create Data Tables in Anvil UI
5. Pull code from GitHub
6. Run admin setup to auto-create database schema
7. Configure scheduled tasks (optional, requires paid plan)

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete setup and deployment guide
- **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** - Administrator operations and troubleshooting
- **[server_code/requirements.txt](server_code/requirements.txt)** - Python dependencies

## 🗄️ Database Schema

### `events` Table (17 columns)
Stores scraped events with AI analysis (category, audience, indoor/outdoor, cost).

### `weather_forecast` Table (9 columns)
Caches weather forecasts for the upcoming weekend (daily summaries).

### `hourly_weather` Table (11 columns)
Stores hourly weather data for precise event-time forecasts.

###`scrape_log` Table (7 columns)
Tracks background task execution and errors.

**Setup:** All columns created automatically via admin panel's "Setup Database" button.

## 🔧 Development

### Server Code Changes

1. Edit Python files in `server_code/` locally
2. Commit and push to GitHub
3. Pull changes in Anvil editor

### UI Changes

- Must be made in Anvil's visual editor
- Forms, components, and styling done in Anvil UI
- Changes automatically synced to GitHub

### Data Table Changes

- Schema changes must be made in Anvil UI
- Use setup script for initial column creation
- Modifications require admin panel "Setup Database"

## 💰 Operating Costs

Weekly operation (assuming 50 events/week):
- **OpenWeather:** FREE (within free tier limits)
- **Firecrawl:** ~$0.10/week (varies by plan)
- **OpenAI:** ~$0.20-$0.40/week (GPT-4.1-mini + GPT-4.1)
- **Total:** ~$0.30-$0.50/week or ~$1.20-$2.00/month

## 🔑 Required API Configuration

Configure in Anvil App Settings → Secrets:

1. `OPENWEATHER_API_KEY` - OpenWeather One Call API 3.0
2. `FIRECRAWL_API_KEY` - Firecrawl web scraping
3. `OPENAI_API_KEY` - OpenAI ChatGPT API
4. `ADMIN_PASSWORD` - Password for admin panel access

## 📊 Features Status

✅ **Complete & Production-Ready**
- Weather API integration (OpenWeather One Call API 3.0)
- Event scraping & parsing (Firecrawl)
- AI event analysis (OpenAI GPT-4.1-mini)
- Weather-aware recommendation engine
- Advanced filtering (cost, category, audience, day, indoor/outdoor)
- Itinerary builder
- Admin panel with testing tools
- Scheduled background tasks
- Complete UI with weather cards, event cards, and filtering

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

This is a personal project, but suggestions and feedback are welcome! Open an issue or pull request.

## 📝 License

MIT License - feel free to use this as a template for your own projects.

## 🙏 Acknowledgments

- [Anvil](https://anvil.works) - Python web framework
- [OpenWeather](https://openweathermap.org) - Weather data
- [Firecrawl](https://firecrawl.dev) - Web scraping
- [OpenAI](https://openai.com) - AI analysis
- [I Love Memphis Blog](https://ilovememphisblog.com) - Event data source

## 📧 Contact

For questions or suggestions, please open an issue in this repository.

---

**Built with ❤️ for Memphis weekends**
