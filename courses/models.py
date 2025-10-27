from django.db import models
from django.conf import settings

class Folder(models.Model):
    """Model to store course folders for organization"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=255, verbose_name="Nom du dossier")
    description = models.TextField(blank=True, null=True, verbose_name="Description du dossier")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Couleur du dossier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        unique_together = ['user', 'name']  # Un nom unique par utilisateur
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    @property
    def course_count(self):
        """Retourne le nombre de cours dans ce dossier"""
        return self.courses.count()

class Course(models.Model):
    """Model to store AI-generated courses"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=255, verbose_name="Titre du cours")
    content = models.TextField(verbose_name="Contenu du cours", blank=True, null=True)
    language = models.CharField(max_length=10, default='fr', verbose_name="Langue du cours")
    is_generated = models.BooleanField(default=True, verbose_name="Généré par IA")
    pdf_file = models.FileField(upload_to='courses/pdfs/', blank=True, null=True, verbose_name="Fichier PDF")
    folders = models.ManyToManyField(Folder, related_name='courses', blank=True, verbose_name="Dossiers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
    
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
