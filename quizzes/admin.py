from django.contrib import admin
from .models import Quiz, Question, QuizAttempt, GameRoom, GameAnswer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['order', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
    ordering = ['order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'subject']
    search_fields = ['title', 'subject', 'user_prompt', 'created_by__username']
    readonly_fields = ['created_at']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Quiz Information', {
            'fields': ('title', 'subject', 'is_active')
        }),
        ('Details', {
            'fields': ('user_prompt', 'created_by', 'created_at')
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'order', 'question_text_short', 'correct_answer']
    list_filter = ['quiz', 'correct_answer']
    search_fields = ['question_text', 'quiz__title']
    ordering = ['quiz', 'order']
    
    fieldsets = (
        ('Question', {
            'fields': ('quiz', 'order', 'question_text')
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d')
        }),
        ('Answer', {
            'fields': ('correct_answer',)
        }),
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'total_questions', 'percentage', 'completed_at']
    list_filter = ['completed_at', 'quiz']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['completed_at', 'answers']
    ordering = ['-completed_at']
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('quiz', 'user', 'completed_at')
        }),
        ('Results', {
            'fields': ('score', 'total_questions', 'percentage')
        }),
        ('Answers', {
            'fields': ('answers',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of attempts through admin
        return False


class GameAnswerInline(admin.TabularInline):
    model = GameAnswer
    extra = 0
    fields = ['player', 'question', 'answer', 'is_correct', 'time_taken', 'points_earned']
    readonly_fields = ['player', 'question', 'answer', 'is_correct', 'time_taken', 'points_earned', 'answered_at']


@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ['room_code', 'quiz', 'player1', 'player2', 'status', 'player1_score', 'player2_score', 'winner', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['room_code', 'quiz__title', 'player1__username', 'player2__username']
    readonly_fields = ['room_code', 'created_at', 'started_at', 'finished_at']
    ordering = ['-created_at']
    inlines = [GameAnswerInline]
    
    fieldsets = (
        ('Room Information', {
            'fields': ('room_code', 'quiz', 'status')
        }),
        ('Players', {
            'fields': ('player1', 'player2')
        }),
        ('Game Progress', {
            'fields': ('current_question', 'player1_score', 'player2_score', 'winner')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'finished_at')
        }),
    )


@admin.register(GameAnswer)
class GameAnswerAdmin(admin.ModelAdmin):
    list_display = ['game_room', 'player', 'question', 'answer', 'is_correct', 'points_earned', 'time_taken', 'answered_at']
    list_filter = ['is_correct', 'answered_at', 'game_room']
    search_fields = ['game_room__room_code', 'player__username', 'question__question_text']
    readonly_fields = ['answered_at']
    ordering = ['-answered_at']
    
    fieldsets = (
        ('Answer Information', {
            'fields': ('game_room', 'player', 'question')
        }),
        ('Response', {
            'fields': ('answer', 'is_correct', 'time_taken', 'points_earned')
        }),
        ('Timestamp', {
            'fields': ('answered_at',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of game answers through admin
        return False
