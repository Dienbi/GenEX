from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatSession(models.Model):
    """Représente une session de chat entre un utilisateur et le chatbot"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default="Nouvelle conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    """Représente un message dans une conversation"""
    MESSAGE_TYPES = [
        ('user', 'Utilisateur'),
        ('assistant', 'Assistant'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Métadonnées pour l'analyse
    subject_detected = models.CharField(max_length=100, blank=True, null=True)  # mathématiques, physique, etc.
    response_time = models.FloatField(null=True, blank=True)  # temps de réponse en secondes
    
    # Champs pour la modification des messages
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    original_content = models.TextField(blank=True, null=True)  # Contenu original avant modification

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.session.title} - {self.message_type}: {self.content[:50]}..."


class EducationalSubject(models.Model):
    """Sujets éducatifs supportés par le chatbot"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(help_text="Mots-clés séparés par des virgules")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def keyword_list(self):
        return [keyword.strip() for keyword in self.keywords.split(',') if keyword.strip()]


class UploadedFile(models.Model):
    """Représente un fichier uploadé par l'utilisateur"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files')
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='uploaded_files', null=True, blank=True)
    file = models.FileField(upload_to='chatbot_files/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=[
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('other', 'Other')
    ])
    file_size = models.IntegerField()  # Taille en bytes
    content_text = models.TextField(blank=True)  # Contenu extrait du fichier
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} ({self.file_type})"
    
    def get_file_size_display(self):
        """Retourne la taille du fichier formatée"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"