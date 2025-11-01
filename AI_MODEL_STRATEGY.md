# AI Model Strategy

## Overview

This Weekend app uses a **dual-model approach** with OpenAI to optimize for both cost and quality:

- **GPT-4.1-mini** for data analysis tasks
- **GPT-4.1** for user-facing text generation

## Model Usage

### GPT-4.1-mini (Analysis Model)

**Purpose:** Structured data extraction and event categorization

**Used in:**
- `analyze_event()` - Event categorization and analysis
- Returns structured JSON with event metadata

**Why GPT-4.1-mini:**
- ✅ Fast response times
- ✅ Cost-effective for bulk operations (50+ events/week)
- ✅ Excellent at structured JSON output
- ✅ Consistent categorization results

**Configuration:**
```python
config.OPENAI_ANALYSIS_MODEL = "gpt-4.1-mini"
config.OPENAI_TEMPERATURE = 0.3  # Lower for consistency
config.OPENAI_MAX_TOKENS = 500
```

**Output Format:**
```json
{
  "is_indoor": true/false,
  "is_outdoor": true/false,
  "audience_type": "adults|family-friendly|all-ages",
  "categories": ["Arts", "Music", ...],
  "cost_level": "Free|$|$$|$$$|$$$$"
}
```

### GPT-4.1 (Text Generation Model)

**Purpose:** Natural language recommendations for users

**Used in:**
- `generate_weather_aware_suggestions()` - Weekend event recommendations
- Returns friendly, conversational text

**Why GPT-4.1:**
- ✅ High-quality natural language output
- ✅ Better at creative, engaging recommendations
- ✅ More sophisticated weather/event matching
- ✅ Users only see this text (quality matters most)

**Configuration:**
```python
config.OPENAI_TEXT_MODEL = "gpt-4.1"
config.TEMPERATURE = 0.7  # Higher for creativity
config.MAX_TOKENS = 400
```

**Output Example:**
> "With sunny skies and temps in the 70s this weekend, I'd definitely check out the Overton Park Concert Series on Saturday - perfect for an outdoor evening with live music! Cooper-Young Festival is another great option if you're looking for food and local art. Don't miss the River Walk Art Market on Sunday, especially with this beautiful weather!"

## Cost Analysis

### Weekly Operation (50 events)

**Analysis Tasks (GPT-4.1-mini):**
- 50 event analyses per week
- ~500 tokens per analysis
- Cost: ~$0.15/week

**User-Facing Text (GPT-4.1):**
- 1 suggestion generation per week
- ~400 tokens output
- Cost: ~$0.15/week

**Total OpenAI Cost:** ~$0.30/week or ~$1.20/month

### Cost Comparison

| Model Strategy | Weekly Cost | Monthly Cost |
|---------------|-------------|--------------|
| GPT-3.5-turbo (old) | $0.05 | $0.20 |
| GPT-4 (all tasks) | $0.75 | $3.00 |
| **Dual Model (current)** | **$0.30** | **$1.20** |

**Benefits:**
- 6x cost increase from old approach BUT:
  - Much better quality (GPT-4.1 vs GPT-3.5)
  - GPT-4.1-mini is 60% cheaper than GPT-4
  - Optimized model selection for each task type

## Implementation

### Configuration (config.py)

```python
# OpenAI Configuration
# GPT-4.1-mini for data analysis (fast, cost-effective)
OPENAI_ANALYSIS_MODEL = "gpt-4.1-mini"
# GPT-4.1 for user-facing text generation (high quality)
OPENAI_TEXT_MODEL = "gpt-4.1"
```

### Usage in Code

**Event Analysis:**
```python
response = client.chat.completions.create(
    model=config.OPENAI_ANALYSIS_MODEL,  # GPT-4.1-mini
    messages=[...],
    response_format={"type": "json_object"}
)
```

**Text Generation:**
```python
response = client.chat.completions.create(
    model=config.OPENAI_TEXT_MODEL,  # GPT-4.1
    messages=[...],
    temperature=0.7
)
```

## Best Practices

### When to Use GPT-4.1-mini
- ✅ Structured data extraction
- ✅ Classification tasks
- ✅ Batch processing
- ✅ JSON output
- ✅ High-volume operations

### When to Use GPT-4.1
- ✅ User-facing text
- ✅ Creative writing
- ✅ Complex reasoning
- ✅ Nuanced recommendations
- ✅ Low-volume operations

## Migration Notes

### From GPT-3.5-turbo

**Changes Made:**
1. Split `OPENAI_MODEL` into two separate configs
2. Updated `analyze_event()` to use `OPENAI_ANALYSIS_MODEL`
3. Updated `generate_weather_aware_suggestions()` to use `OPENAI_TEXT_MODEL`
4. Added documentation and comments

**Backward Compatibility:**
- No API changes
- All function signatures remain the same
- Drop-in replacement

### Testing

After deployment, verify:
1. Event analysis returns valid JSON
2. Suggestions are high quality and relevant
3. No model-related errors in logs
4. Cost tracking shows expected usage

## Future Considerations

### Potential Optimizations
- Cache common event types to reduce analysis calls
- Batch event analysis requests
- Use function calling for even more structured outputs
- Add streaming for real-time suggestion generation

### Model Updates
OpenAI regularly releases new models. Consider evaluating:
- Newer GPT-4.x variants
- Specialized fine-tuned models
- Context length improvements

## References

- [OpenAI Models Documentation](https://platform.openai.com/docs/models)
- [GPT-4.1 Release Notes](https://openai.com/gpt-4)
- [OpenAI Pricing](https://openai.com/pricing)

---

**Last Updated:** November 1, 2025  
**Current Models:** GPT-4.1-mini (analysis) + GPT-4.1 (text)

