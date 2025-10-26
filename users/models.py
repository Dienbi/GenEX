from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )

    LEVEL_CHOICES = (
        ('weak', 'Weak'),
        ('medium', 'Medium'),
        ('advanced', 'Advanced'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, blank=True, null=True)
    student_class = models.CharField(max_length=50, blank=True, null=True)
    
    # Quiz Streak Fields
    current_streak = models.IntegerField(default=0, help_text="Current consecutive days with quiz completion")
    longest_streak = models.IntegerField(default=0, help_text="Longest streak ever achieved")
    last_quiz_date = models.DateTimeField(null=True, blank=True, help_text="Last time user completed a quiz")
    
    # Theme preference
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    )
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='auto', help_text="User's theme preference")

    def __str__(self):
        return f"{self.username} ({self.user_type})"
