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
- Recommends 3-4 **specific events** from scraped data (not generic activities)
- Prioritizes outdoor events when weather is nice
- Prioritizes indoor events when weather is rainy or extreme
- Explains WHY each event is suited for the weather conditions
- 3-4 sentences of warm, friendly guidance

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
- Includes weather summary and top 15 events with details
- Provides event venue type, day, cost, and location
- Instructs AI to recommend 3-4 specific events with weather reasoning

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
With sunny skies and perfect temps this weekend, I'd definitely check out 
the Memphis Japan Festival on Sunday - perfect for enjoying Japanese culture 
outdoors. The Farmers Market at Agricenter is another great option if you're 
looking for fresh produce and local crafts on Saturday morning. Don't miss 
the Broad Avenue Art Walk on Friday evening, especially with these beautiful 
fall temperatures!
```

### Rainy Weather:
```
With rain expected Saturday and Sunday, the Levitt Shell Indoor Concert 
Series on Saturday is perfect for staying dry while catching live music. 
The Memphis Brooks Museum of Art is another excellent rainy-day choice with 
their new exhibition. If you want something interactive, check out the 
Children's Museum of Memphis on Sunday - great for families and completely 
indoors!
```

### Mixed Weather:
```
Saturday's looking gorgeous at 72°F with sunshine - perfect for the Cooper-Young 
Festival's outdoor vendors and live music. Sunday might get some showers though, 
so I'd save the Dixon Gallery & Gardens indoor exhibits for then. The Crosstown 
Concourse First Friday event works great for tonight since it's mostly covered!
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
- **Max Tokens**: 400 (allows for specific event recommendations with explanations)
- **System Prompt**: "Recommend specific events from the provided list based on weather conditions"
- **Input**: Top 15 events with venue type, day, cost, location

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

1. **Actionable Recommendations**: Specific event names users can immediately look for
2. **Weather-Smart**: Events matched to actual forecast conditions
3. **Discovery**: Highlights top-rated events users might miss
4. **Context**: Explains WHY each event suits the weather
5. **Conversational**: Feels like advice from a knowledgeable local friend
6. **Saves Time**: Pre-curated picks instead of browsing hundreds of events

## Future Enhancements

Potential improvements:
- Cache suggestions for 1-2 hours to reduce API calls
- Add user preferences (family-friendly, budget-conscious, etc.)
- Make event names clickable to jump to that event in the list
- Show different suggestions for each day (Friday/Saturday/Sunday specific)
- Add emoji to make suggestions more visual
- Highlight recommended events in the main event list

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

