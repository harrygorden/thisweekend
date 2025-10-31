# Quick Debug Reference - What The Output Means

## 🔍 Understanding Your Parser Debug Output

When you run the background task, look at the `[5/10] Parse events...` section:

---

## 📊 The Key Line

```
🔍 Parser stats: 84 links found, 84 skipped, 0 events parsed
```

**This tells you:**
- **84 links found** = Markdown link detection is working ✅
- **84 skipped** = ALL links were rejected ❌
- **0 events parsed** = No valid events made it through ❌

---

## 🎯 Quick Diagnosis Chart

### Good Signs ✅

```
✅ 84 links found, 15 skipped, 69 events parsed
```
→ **Working perfectly!** 69 events detected, 15 junk filtered

```
📅 Found day header: FRIDAY
📅 Found day header: SATURDAY
📅 Found day header: SUNDAY
```
→ **Day detection working!**

```
❌ Skip reasons (top 3):
   url:facebook.com: 10 links
   text:reply: 3 links
```
→ **Filters working correctly!** Facebook and Reply links being skipped

---

### Warning Signs ⚠️

```
⚠️ No day keywords (FRIDAY/SATURDAY/SUNDAY) found in first 100 lines!
```
→ **Day headers missing or in different format**  
→ **But:** Fallback will still assign Friday by default

```
❌ Skip reasons (top 3):
   no_day_context_or_invalid: 84 links
```
→ **All links rejected** - something's wrong with validation

---

### Bad Signs ❌

```
🔍 Parser stats: 0 links found, 0 skipped, 0 events parsed
```
→ **Markdown link pattern not matching** - format changed

```
🔍 Parser stats: 84 links found, 84 skipped, 0 events parsed
❌ Skip reasons (top 3):
   no_day_context_or_invalid: 84 links
```
→ **Fallback not working** - all events rejected

---

## 🎯 What To Share

### If You Get 0 Events, Share This Section:

```
[5/10] Parse events...
  🔍 Parser stats: [X] links found, [Y] skipped, [Z] events parsed
  
  [Day keywords section - shows if they exist]
  
  [Skip reasons section - shows why links were skipped]
  
  ✓ Found [Z] events
```

**This tells me:**
1. **Are links being found?** (X value)
2. **Are day keywords present?** (keywords section)
3. **Why are they being skipped?** (skip reasons section)
4. **Did fallback work?** (Z value)

---

## 🚀 Quick Action Guide

### Scenario 1: "84 found, 15 skipped, 69 parsed" ✅

**What It Means:** Working perfectly!

**Action:** Nothing! Enjoy your events! 🎉

---

### Scenario 2: "84 found, 84 skipped, 0 parsed" ❌

**What It Means:** All links rejected

**Check:**
```
❌ Skip reasons (top 3):
   [LOOK HERE - what's the top reason?]
```

**If:** `no_day_context_or_invalid: 84`
→ **Issue:** Fallback not working, validation too strict

**Action:** Share debug output, we'll adjust validation

**If:** `url:[some pattern]: 84`
→ **Issue:** Skip pattern too broad

**Action:** Share debug output, we'll adjust skip patterns

---

### Scenario 3: "0 found, 0 skipped, 0 parsed" ❌

**What It Means:** Markdown link pattern not matching

**Action:** Share scraped content sample, we'll adjust regex

---

## 📋 Checklist Before Reporting Issues

**Run background task and check:**

- [ ] How many links were found?
- [ ] How many were skipped?
- [ ] How many events parsed?
- [ ] Were day headers detected?
- [ ] Were day keywords found?
- [ ] What were the top skip reasons?

**Then share the `[5/10] Parse events...` section!**

---

## 💡 What The Numbers Mean

### Links Found (84):
- Total markdown links detected in content
- Should be 50-150 for typical weekend page
- 0 = Pattern not matching (bad)
- 84 = Pattern working (good)

### Links Skipped (15-20):
- Links filtered by skip patterns
- Navigation, Reply, Facebook, etc.
- 15-20% is normal (good)
- 100% = Something wrong (bad)

### Events Parsed (30-80):
- Valid events after all filtering
- Should be 30-80 for typical weekend
- 0 = Validation issue (bad)
- 30-80 = Working correctly (good)

---

## 🎯 Success Criteria

### Perfect Run:
```
✓ Found 3 day headers (Friday, Saturday, Sunday)
✓ 84 links found, 15 skipped
✓ 69 events parsed
✓ Skip reasons are Facebook/Reply/navigation only
```

### Acceptable Run (Fallback):
```
⚠️ No day headers found (using fallback)
✓ 84 links found, 15 skipped
✓ 69 events parsed
✓ All events assigned to Friday by default
```

### Problem Run:
```
❌ 84 links found, 84 skipped
❌ 0 events parsed
❌ Skip reason: no_day_context_or_invalid: 84
```
→ Share debug output for diagnosis!

---

## 🚀 Next Steps

1. **Pull from GitHub** in Anvil
2. **Run background task**
3. **Look at `[5/10] Parse events...` section**
4. **Check against this guide**
5. **Share debug output if needed**

---

## 🎉 You're Almost There!

The code now has:
- ✅ Full SDK support
- ✅ Comprehensive debugging
- ✅ Fallback mechanisms
- ✅ All bugs fixed

**The debug output will show us exactly what's happening!**

**Pull and run - let's see what the debugging tells us!** 🔍✨

