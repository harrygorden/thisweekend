# Changelog

All notable changes to This Weekend Memphis Event Planner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed - 2025-11-01

#### AI Model Strategy Update

**Summary:** Implemented dual-model approach using GPT-4.1-mini for data analysis and GPT-4.1 for user-facing text generation.

**Changes:**

1. **Configuration (`config.py`)**
   - Replaced single `OPENAI_MODEL` with two separate model configurations:
     - `OPENAI_ANALYSIS_MODEL = "gpt-4.1-mini"` - For event categorization
     - `OPENAI_TEXT_MODEL = "gpt-4.1"` - For user-facing recommendations

2. **AI Service (`ai_service.py`)**
   - Updated `analyze_event()` to use GPT-4.1-mini for structured JSON analysis
   - Updated `generate_weather_aware_suggestions()` to use GPT-4.1 for natural language text
   - Enhanced module docstring with model strategy explanation

3. **Documentation Updates**
   - `README.md`: Updated features, cost estimates
   - `SETUP.md`: Updated API cost information
   - `AI_MODEL_STRATEGY.md`: New comprehensive guide on model selection rationale
   - `CHANGELOG.md`: Added this changelog

**Benefits:**
- 🚀 Better quality: GPT-4.1 models vs previous GPT-3.5-turbo
- 💰 Cost optimized: GPT-4.1-mini for bulk analysis (60% cheaper than full GPT-4.1)
- ✨ High quality: GPT-4.1 for user-facing text where quality matters most
- 📊 Strategic: Right model for the right task

**Cost Impact:**
- Previous (GPT-3.5-turbo): ~$0.05/week
- New (Dual model): ~$0.30/week
- 6x increase but with significantly better output quality

**Migration:**
- ✅ No breaking changes to API
- ✅ All function signatures remain the same
- ✅ Drop-in replacement - just update and deploy

**Files Modified:**
- `server_code/config.py`
- `server_code/ai_service.py`
- `README.md`
- `SETUP.md`

**Files Added:**
- `AI_MODEL_STRATEGY.md`
- `CHANGELOG.md`

---

## [1.0.0] - Initial Release

### Added
- Complete Memphis weekend event planner application
- OpenWeather API integration for weekend forecasts
- Firecrawl web scraping for event data
- OpenAI integration for event analysis
- Weather-aware recommendation engine
- Admin panel for testing and management
- Automated background tasks for data refresh
- Complete documentation suite

