from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'level', 'student_class')}),
    )
    list_display = ('username', 'email', 'user_type', 'level', 'student_class', 'is_active')

admin.site.register(User, CustomUserAdmin)
