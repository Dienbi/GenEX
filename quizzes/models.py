from django.db import models
from django.conf import settings
from django.utils import timezone
import random
import string


class Quiz(models.Model):
    """Model to store generated quizzes"""
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    user_prompt = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.subject}"


class Question(models.Model):
    """Model to store individual questions"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class QuizAttempt(models.Model):
    """Model to store user attempts and results"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=10)
    percentage = models.FloatField(default=0.0)
    answers = models.JSONField(default=dict)  # Store user's answers as JSON
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}/{self.total_questions}"
    
    def calculate_score(self):
        """Calculate score based on answers"""
        correct_count = 0
        for question in self.quiz.questions.all():
            user_answer = self.answers.get(str(question.id))
            if user_answer and user_answer.upper() == question.correct_answer:
                correct_count += 1
        
        self.score = correct_count
        self.total_questions = self.quiz.questions.count()
        self.percentage = (correct_count / self.total_questions * 100) if self.total_questions > 0 else 0
        self.save()
        return self.score


def generate_room_code():
    """Generate a unique 6-character room code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class GameRoom(models.Model):
    """Model for 1vs1 game rooms"""
    
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Player 2'),
        ('ready', 'Both Players Ready'),
        ('playing', 'Game in Progress'),
        ('finished', 'Game Finished'),
        ('cancelled', 'Game Cancelled'),
    ]
    
    room_code = models.CharField(max_length=6, unique=True, default=generate_room_code)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='game_rooms')
    
    # Players
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_rooms_as_player1')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='game_rooms_as_player2')
    
    # Game state
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    current_question = models.IntegerField(default=0)  # 0 = not started, 1-10 = question number
    
    # Scores
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    # Winner
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')
    
    class Meta:
        verbose_name = 'Game Room'
        verbose_name_plural = 'Game Rooms'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Room {self.room_code} - {self.get_status_display()}"
    
    def is_full(self):
        """Check if room has both players"""
        return self.player2 is not None
    
    def get_opponent(self, user):
        """Get the opponent for a given user"""
        if self.player1 == user:
            return self.player2
        return self.player1
    
    def get_player_number(self, user):
        """Get player number (1 or 2) for a user"""
        if self.player1 == user:
            return 1
        elif self.player2 == user:
            return 2
        return None
    
    def get_player_score(self, user):
        """Get score for a player"""
        if self.player1 == user:
            return self.player1_score
        elif self.player2 == user:
            return self.player2_score
        return 0
    
    def update_score(self, user, points):
        """Update score for a player"""
        if self.player1 == user:
            self.player1_score += points
        elif self.player2 == user:
            self.player2_score += points
        self.save()
    
    def determine_winner(self):
        """Determine and set the winner"""
        if self.player1_score > self.player2_score:
            self.winner = self.player1
        elif self.player2_score > self.player1_score:
            self.winner = self.player2
        # else: it's a tie, winner stays None
        self.status = 'finished'
        self.finished_at = timezone.now()
        self.save()


class GameAnswer(models.Model):
    """Model to store player answers in a game"""
    game_room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name='answers')
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1)  # A, B, C, or D
    is_correct = models.BooleanField()
    time_taken = models.FloatField()  # seconds
    points_earned = models.IntegerField(default=0)
    answered_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Game Answer'
        verbose_name_plural = 'Game Answers'
        unique_together = ['game_room', 'player', 'question']
    
    def __str__(self):
        return f"{self.player.username} - Q{self.question.order} - {self.answer}"
