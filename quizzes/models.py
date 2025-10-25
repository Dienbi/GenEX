from django.db import models
from django.conf import settings
from django.utils import timezone


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
