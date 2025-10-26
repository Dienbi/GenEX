# 🔥 Quiz Streak Feature - Documentation

## 📋 Overview
The Quiz Streak feature gamifies the learning experience by tracking consecutive days of quiz completion, encouraging daily engagement.

## ✨ Features Implemented

### 🎯 Streak Tracking
- **Current Streak**: Days in a row the user has completed quizzes
- **Longest Streak**: Personal best streak ever achieved
- **Last Quiz Date**: Timestamp of most recent quiz completion

### 📏 Streak Rules

#### 1. Starting a Streak
- Complete your first quiz → Streak = 1
- The clock starts ticking!

#### 2. Maintaining a Streak
- Complete a quiz **within 30 hours** of the last one
- Must be on a **different day** (date, not just 24h)
- Streak continues ✅

#### 3. Incrementing a Streak
- Complete a quiz on the **next day**
- Must be within **30 hours** window
- Example:
  - Monday 2 PM: Quiz → Streak = 1
  - Tuesday 3 PM: Quiz → Streak = 2 ✅
  - Tuesday 8 PM: Another quiz → Streak still 2 (same day)

#### 4. Streak Reset
- **Automatic**: Visit `/quizzes/` after 30+ hours → Streak = 0
- **After Break**: Complete quiz after 30+ hours → New streak = 1

### ⏰ 30-Hour Window
Why 30 hours instead of 24?
- Gives flexibility for different schedules
- Monday 10 PM + 30h = Wednesday 4 AM (grace period)
- Prevents midnight deadline stress
- Still requires next-day completion

## 🎨 UI/UX

### Quiz Hub Display
Two beautiful cards showing:

**Current Streak Card** 🔥
- Large fire emoji
- Orange accent (#ff6b35)
- Shows hours remaining when active
- Warning (red) when < 5 hours left
- Motivational messages

**Longest Streak Card** 🏆
- Trophy emoji
- Gold accent (#f7b731)
- Shows personal best
- "Personal Best!" celebration message

### Messages on Quiz Completion
- 🔥 "Streak increased to X days! Keep it up!"
- ✅ "Quiz completed! Current streak: X days (Complete a quiz tomorrow to increase!)"
- 💔 "Streak was broken, but you're starting fresh! New streak: 1 day!"
- 🔥 "Streak started! Come back tomorrow to keep it going!"

## 🛠️ Technical Implementation

### Database Schema (User Model)
```python
current_streak = IntegerField(default=0)
longest_streak = IntegerField(default=0)
last_quiz_date = DateTimeField(null=True, blank=True)
```

### Key Functions (`quizzes/streak_utils.py`)

#### `check_and_update_streak(user)`
- Called when user visits `/quizzes/`
- Checks if 30 hours passed
- Resets streak if needed
- Returns streak info

#### `update_streak_on_quiz_completion(user)`
- Called after quiz submission
- Determines if streak should increment
- Updates current and longest streaks
- Returns increment status

#### `get_streak_status_message(streak_info)`
- Generates user-friendly messages
- Based on streak status and reason

#### `get_time_until_streak_expires(user)`
- Calculates remaining time
- Shows countdown on UI

### View Integration

**quiz_home view:**
```python
streak_info = check_and_update_streak(request.user)
time_info = get_time_until_streak_expires(request.user)
# Pass to template
```

**submit_quiz_view:**
```python
streak_info = update_streak_on_quiz_completion(request.user)
streak_message = get_streak_status_message(streak_info)
messages.success(request, streak_message)
```

## 📊 Examples & Edge Cases

### Scenario 1: Perfect Daily Streak
```
Monday 3 PM: Quiz 1 → Streak = 1
Tuesday 3 PM: Quiz 2 → Streak = 2 ✅
Wednesday 3 PM: Quiz 3 → Streak = 3 ✅
Thursday 3 PM: Quiz 4 → Streak = 4 ✅
```

### Scenario 2: Multiple Quizzes Same Day
```
Monday 10 AM: Quiz 1 → Streak = 1
Monday 2 PM: Quiz 2 → Streak = 1 (no increment)
Monday 8 PM: Quiz 3 → Streak = 1 (still no increment)
Tuesday 11 AM: Quiz 4 → Streak = 2 ✅ (next day!)
```

### Scenario 3: Using the 30-Hour Window
```
Monday 11 PM: Quiz 1 → Streak = 1
Wednesday 4 AM: Quiz 2 → Streak = 2 ✅ (29 hours later, different day)
Thursday 9 AM: Quiz 3 → Streak = 3 ✅
```

### Scenario 4: Streak Break
```
Monday 3 PM: Quiz 1 → Streak = 1
[33 hours pass - no quiz]
Wednesday 12 AM: Visit /quizzes/ → Streak = 0 (reset)
Wednesday 1 PM: Quiz 2 → Streak = 1 (new streak)
```

### Scenario 5: Just Under 30 Hours
```
Monday 10 AM: Quiz 1 → Streak = 1
Tuesday 3:59 PM: Quiz 2 → Streak = 2 ✅ (29h 59m, safe!)
Tuesday 4:01 PM: Visit page → Still Streak = 2
```

### Scenario 6: Just Over 30 Hours
```
Monday 10 AM: Quiz 1 → Streak = 1
Tuesday 4:01 PM: Visit /quizzes/ → Streak = 0 (30h 1m, reset)
Tuesday 5 PM: Quiz 2 → Streak = 1 (new streak starts)
```

## 🎮 User Experience Flow

### First Time User
1. Visit `/quizzes/` → Sees "Start your streak today!" (0 days)
2. Completes first quiz → "Streak started! Come back tomorrow!"
3. Returns next day → Sees "X hours remaining" countdown
4. Completes quiz → Streak increases! 🔥

### Active User
1. Visits daily → Sees current streak and countdown
2. When < 5 hours left → Red warning ⚠️
3. Completes quiz → Success message + streak increment
4. Longest streak automatically tracked

### Returning User (After Break)
1. Visits after 30+ hours → Streak auto-reset to 0
2. No penalty message (gentle)
3. Complete quiz → "Starting fresh! New streak: 1"
4. Longest streak preserved (shows what they achieved)

## 🚀 Future Enhancements (Ideas)

- 📧 Email reminders when streak about to expire
- 🏅 Badges for milestone streaks (7, 30, 100 days)
- 📊 Streak graph/calendar visualization
- 🎁 Rewards for maintaining streaks
- 👥 Leaderboard of longest streaks
- 📱 Push notifications
- 🔔 In-app streak expiration warnings
- 📈 Streak analytics and insights

## 🔧 Configuration

### Adjusting the 30-Hour Window
Edit `quizzes/streak_utils.py`:
```python
hours_since_last_quiz > 30  # Change 30 to desired hours
```

### Changing Streak Colors
Edit `templates/quizzes/home.html`:
```css
.streak-card.current {
    border-left: 5px solid #ff6b35;  /* Current streak color */
}
.streak-card.longest {
    border-left: 5px solid #f7b731;  /* Longest streak color */
}
```

## 📁 Files Modified/Created

### New Files
- `quizzes/streak_utils.py` - Streak logic functions

### Modified Files
- `users/models.py` - Added streak fields
- `users/migrations/0002_*.py` - Database migration
- `quizzes/views.py` - Integrated streak checks
- `templates/quizzes/home.html` - Streak display

## ✅ Testing Checklist

- [x] First quiz starts streak at 1
- [x] Same day multiple quizzes don't increment
- [x] Next day quiz increments (within 30h)
- [x] 30+ hours auto-resets streak
- [x] Longest streak updates correctly
- [x] Timer shows hours remaining
- [x] Warning appears < 5 hours
- [x] Messages display correctly
- [x] UI displays properly

## 🎯 Success Metrics

Track these to measure engagement:
- Average streak length
- % users with active streaks
- Longest streak achieved
- Daily quiz completion rate
- Streak retention rate

## 🎊 Conclusion

The streak feature successfully gamifies the quiz experience, encouraging daily engagement while being flexible enough to accommodate different schedules. The 30-hour window provides a safety net while still requiring next-day participation.

**Keep that streak alive! 🔥**

