from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def __str__(self):
        return f"{self.username} ({self.user_type})"
