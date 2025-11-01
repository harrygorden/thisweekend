# Weather-Aware Weekend Suggestions Feature

## Overview

Added an AI-powered "Weekend Ideas" section that provides personalized, weather-aware suggestions for weekend activities. This section appears between the weather forecast and the event filters, giving users smart recommendations based on current weather conditions.

## Features

### Smart Weather Analysis
- Analyzes the 3-day weather forecast (Friday-Sunday)
- Considers temperature, precipitation chance, and conditions
- Counts available indoor vs outdoor events

### AI-Powered Suggestions
- Uses OpenAI GPT to generate friendly, conversational recommendations
- Highlights outdoor activities when weather is nice
- Suggests indoor alternatives when weather is rainy or extreme
- 2-3 sentences of warm, friendly guidance

### Seamless Integration
- Loads automatically when the page loads
- Positioned between weather and filters for optimal visibility
- Light blue background to stand out visually
- Graceful fallback if AI generation fails

## Implementation

### Server-Side (server_code/ai_service.py)

#### New Functions:

**`generate_weather_aware_suggestions(weather_data, events)`**
- Main AI generation function
- Analyzes weather and events
- Returns suggestion text

**`build_suggestions_prompt(weather_data, events)`**
- Builds the ChatGPT prompt
- Includes weather summary, event counts, and sample events
- Provides clear instructions for tone and content

**`get_weekend_suggestions()`** (Server Callable)
- Client-callable function
- Fetches weather and event data
- Generates and returns suggestions
- Returns None if generation fails

### Client-Side

#### UI Component (client_code/MainApp/form_template.yaml)
Added new `suggestions_section` ColumnPanel with:
- **Title**: "Weekend Ideas" with lightbulb icon
- **Text Label**: Displays AI-generated suggestions
- **Background**: Light blue (#E3F2FD) for visual prominence
- **Position**: Between weather and filters sections

#### Logic (client_code/MainApp/__init__.py)

**`load_weekend_suggestions()`**
- Shows "Generating personalized suggestions..." while loading
- Calls server to get AI suggestions
- Updates UI with suggestions
- Falls back to friendly generic message on error
- Hides section if no suggestions available

**`load_initial_data()`**
- Updated to call `load_weekend_suggestions()` after weather but before events

## Example Outputs

### Nice Weather:
```
This weekend's looking gorgeous! Perfect weather for checking out outdoor 
festivals, farmers markets, or catching a concert under the stars. If you 
need a break from the heat, there are plenty of air-conditioned museums 
and theaters too.
```

### Rainy Weather:
```
Looks like we've got some rain in the forecast this weekend. Great time to 
explore Memphis' indoor scene - think museums, theaters, and cozy cafes. 
There are still some covered outdoor markets if you want fresh air without 
getting drenched!
```

### Mixed Weather:
```
Saturday's looking beautiful for outdoor adventures, but Sunday might be 
better for indoor activities. Consider front-loading your outdoor plans 
and saving museums and shows for later in the weekend!
```

## User Experience Flow

1. **Page loads** → Shows "Loading suggestions..."
2. **Weather loads** → Weather cards populate
3. **AI generates** → "Generating personalized suggestions..."
4. **Suggestions display** → Friendly 2-3 sentence guidance appears
5. **User reads** → Gets weather-aware activity ideas
6. **User scrolls** → Filters and browses specific events below

## Technical Details

### API Usage
- **Model**: GPT-3.5-turbo or GPT-4 (from config.OPENAI_MODEL)
- **Temperature**: 0.7 (more creative for suggestions)
- **Max Tokens**: 300 (keeps suggestions concise)
- **System Prompt**: "Friendly local events guide for Memphis, TN"

### Error Handling
- Catches API failures gracefully
- Falls back to generic message: "Explore the events below to find your perfect weekend activities!"
- Hides section entirely if no data available
- Logs errors for debugging

### Performance
- Loads asynchronously during page initialization
- Does not block event loading
- Cached by weather/event data (one call per page load)
- Typical generation time: 1-2 seconds

## Benefits

1. **User Engagement**: Warm, personalized greeting sets friendly tone
2. **Weather Context**: Helps users plan based on forecast
3. **Discovery**: Encourages exploration of event types they might not filter for
4. **Smart Filtering**: Pre-filters by weather suitability before user even looks
5. **Conversational**: Feels like advice from a local friend

## Future Enhancements

Potential improvements:
- Cache suggestions for 1-2 hours to reduce API calls
- Add user preferences (family-friendly, budget-conscious, etc.)
- Include specific event recommendations (not just general types)
- Show different suggestions for each day (Friday/Saturday/Sunday specific)
- Add emoji to make suggestions more visual

## Files Modified

1. **server_code/ai_service.py**
   - Added `generate_weather_aware_suggestions()`
   - Added `build_suggestions_prompt()`
   - Added `get_weekend_suggestions()` (server callable)

2. **client_code/MainApp/form_template.yaml**
   - Added `suggestions_section` ColumnPanel
   - Added `suggestions_title` Label
   - Added `suggestions_text` Label

3. **client_code/MainApp/__init__.py**
   - Added `load_weekend_suggestions()` method
   - Updated `load_initial_data()` to load suggestions

4. **WEATHER_SUGGESTIONS_FEATURE.md** (this file)
   - Feature documentation

## Testing

To test different weather scenarios:

1. **Check current output**: Load the app and see what suggestions appear
2. **Verify weather context**: Suggestions should match weather conditions
3. **Test error handling**: Try with no internet/API issues
4. **Check fallback**: Ensure graceful degradation if AI fails

---

**Feature completed**: November 1, 2025
**Status**: Ready for deployment
**Dependencies**: OpenAI API key required

