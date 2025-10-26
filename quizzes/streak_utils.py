"""
Utility functions for managing quiz streak logic
"""
from django.utils import timezone
from datetime import timedelta


def check_and_update_streak(user):
    """
    Check if user's streak should be reset based on 30-hour rule.
    Called when user visits the quizzes page.
    
    Args:
        user: User instance
        
    Returns:
        dict: Current streak info
    """
    if not user.last_quiz_date:
        # No quiz history, streak is 0
        return {
            'current_streak': 0,
            'longest_streak': user.longest_streak,
            'status': 'no_history'
        }
    
    now = timezone.now()
    time_since_last_quiz = now - user.last_quiz_date
    hours_since_last_quiz = time_since_last_quiz.total_seconds() / 3600
    
    # If more than 30 hours have passed, reset streak
    if hours_since_last_quiz > 30:
        user.current_streak = 0
        user.save(update_fields=['current_streak'])
        return {
            'current_streak': 0,
            'longest_streak': user.longest_streak,
            'status': 'reset',
            'hours_since_last': hours_since_last_quiz
        }
    
    # Streak is still valid
    return {
        'current_streak': user.current_streak,
        'longest_streak': user.longest_streak,
        'status': 'active',
        'hours_since_last': hours_since_last_quiz
    }


def update_streak_on_quiz_completion(user):
    """
    Update user's streak when they complete a quiz.
    
    Rules:
    - If same day: Don't increment, just update timestamp
    - If next day AND within 30h: Increment streak
    - If > 30h: Reset to 1 (new streak)
    
    Args:
        user: User instance
        
    Returns:
        dict: Updated streak info with increment status
    """
    now = timezone.now()
    
    # First quiz ever
    if not user.last_quiz_date:
        user.current_streak = 1
        user.longest_streak = max(user.longest_streak, 1)
        user.last_quiz_date = now
        user.save(update_fields=['current_streak', 'longest_streak', 'last_quiz_date'])
        return {
            'current_streak': 1,
            'longest_streak': user.longest_streak,
            'incremented': True,
            'reason': 'first_quiz'
        }
    
    time_since_last_quiz = now - user.last_quiz_date
    hours_since_last_quiz = time_since_last_quiz.total_seconds() / 3600
    
    # Get dates (ignore time) for day comparison
    last_quiz_date = user.last_quiz_date.date()
    current_date = now.date()
    
    # Same day - don't increment streak
    if last_quiz_date == current_date:
        user.last_quiz_date = now
        user.save(update_fields=['last_quiz_date'])
        return {
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'incremented': False,
            'reason': 'same_day'
        }
    
    # More than 30 hours - reset to 1
    if hours_since_last_quiz > 30:
        user.current_streak = 1
        user.longest_streak = max(user.longest_streak, 1)
        user.last_quiz_date = now
        user.save(update_fields=['current_streak', 'longest_streak', 'last_quiz_date'])
        return {
            'current_streak': 1,
            'longest_streak': user.longest_streak,
            'incremented': False,
            'reason': 'streak_broken',
            'hours_passed': hours_since_last_quiz
        }
    
    # Different day AND within 30 hours - increment streak!
    user.current_streak += 1
    user.longest_streak = max(user.longest_streak, user.current_streak)
    user.last_quiz_date = now
    user.save(update_fields=['current_streak', 'longest_streak', 'last_quiz_date'])
    
    return {
        'current_streak': user.current_streak,
        'longest_streak': user.longest_streak,
        'incremented': True,
        'reason': 'new_day',
        'hours_passed': hours_since_last_quiz
    }


def get_streak_status_message(streak_info):
    """
    Get a user-friendly message based on streak info.
    
    Args:
        streak_info: dict returned from update_streak_on_quiz_completion
        
    Returns:
        str: Message to display to user
    """
    if streak_info['incremented']:
        if streak_info['reason'] == 'first_quiz':
            return "🔥 Streak started! Come back tomorrow to keep it going!"
        elif streak_info['reason'] == 'new_day':
            return f"🔥 Streak increased to {streak_info['current_streak']} days! Keep it up!"
    else:
        if streak_info['reason'] == 'same_day':
            return f"✅ Quiz completed! Current streak: {streak_info['current_streak']} days (Complete a quiz tomorrow to increase!)"
        elif streak_info['reason'] == 'streak_broken':
            return "💔 Streak was broken, but you're starting fresh! New streak: 1 day!"
    
    return "Quiz completed!"


def get_time_until_streak_expires(user):
    """
    Calculate how much time is left before streak expires.
    
    Args:
        user: User instance
        
    Returns:
        dict: Time remaining info
    """
    if not user.last_quiz_date:
        return {
            'expired': True,
            'hours_remaining': 0,
            'message': 'No active streak'
        }
    
    now = timezone.now()
    time_since_last_quiz = now - user.last_quiz_date
    hours_since_last_quiz = time_since_last_quiz.total_seconds() / 3600
    hours_remaining = 30 - hours_since_last_quiz
    
    if hours_remaining <= 0:
        return {
            'expired': True,
            'hours_remaining': 0,
            'message': 'Streak has expired'
        }
    
    return {
        'expired': False,
        'hours_remaining': hours_remaining,
        'message': f'{int(hours_remaining)} hours remaining to maintain streak'
    }

