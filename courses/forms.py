"""
Formulaires pour les cours
"""
from django import forms
from .models import Course, Folder
import re

class CourseForm(forms.ModelForm):
    """Formulaire pour créer et modifier un cours"""
    
    class Meta:
        model = Course
        fields = ['title', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre du cours',
                'maxlength': '255'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le champ PDF optionnel
        self.fields['pdf_file'].required = False
        self.fields['pdf_file'].help_text = "Fichier PDF optionnel (max 10MB)"
    
    def clean_title(self):
        """Validation du titre avec messages personnalisés"""
        title = self.cleaned_data.get('title')
        
        if not title:
            raise forms.ValidationError("📝 Veuillez saisir un titre pour votre cours")
        
        # Nettoyer le titre
        title = title.strip()
        
        if len(title) < 3:
            raise forms.ValidationError("📏 Le titre doit contenir au moins 3 caractères")
        
        if len(title) > 255:
            raise forms.ValidationError("📏 Le titre ne doit pas dépasser 255 caractères")
        
        # Vérifier les caractères interdits
        forbidden_chars = ['<', '>', '&', '"', "'", '\\', '/', '|', '?', '*']
        for char in forbidden_chars:
            if char in title:
                raise forms.ValidationError(f"🚫 Le caractère '{char}' n'est pas autorisé dans le titre")
        
        # Vérifier que le titre ne commence pas par un espace ou un point
        if title.startswith(' ') or title.startswith('.'):
            raise forms.ValidationError("⚠️ Le titre ne peut pas commencer par un espace ou un point")
        
        # Vérifier que le titre ne se termine pas par un espace ou un point
        if title.endswith(' ') or title.endswith('.'):
            raise forms.ValidationError("⚠️ Le titre ne peut pas se terminer par un espace ou un point")
        
        # Vérifier qu'il n'y a pas d'espaces multiples
        if '  ' in title:
            raise forms.ValidationError("⚠️ Veuillez éviter les espaces multiples dans le titre")
        
        return title
    
    def clean_pdf_file(self):
        """Validation du fichier PDF avec messages personnalisés"""
        pdf_file = self.cleaned_data.get('pdf_file')
        
        if pdf_file:
            # Vérifier l'extension
            if not pdf_file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("📄 Veuillez sélectionner un fichier PDF valide")
            
            # Vérifier la taille (max 10MB)
            if pdf_file.size > 10 * 1024 * 1024:  # 10MB en bytes
                raise forms.ValidationError("📦 Le fichier PDF ne doit pas dépasser 10MB")
            
            # Vérifier le nom du fichier
            if len(pdf_file.name) > 100:
                raise forms.ValidationError("📏 Le nom du fichier ne doit pas dépasser 100 caractères")
            
            # Vérifier les caractères interdits dans le nom du fichier
            forbidden_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
            for char in forbidden_chars:
                if char in pdf_file.name:
                    raise forms.ValidationError(f"🚫 Le caractère '{char}' n'est pas autorisé dans le nom du fichier")
        
        return pdf_file

class CourseCreateForm(CourseForm):
    """Formulaire spécifique pour la création de cours"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Ex: Introduction à la Programmation Python'
        })

class CourseEditForm(CourseForm):
    """Formulaire spécifique pour la modification de cours"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Ex: Introduction à la Programmation Python'
        })
        # Afficher le nom du fichier actuel
        if self.instance and self.instance.pdf_file:
            self.fields['pdf_file'].help_text = f"Fichier actuel: {self.instance.pdf_file.name} (max 10MB)"


class FolderForm(forms.ModelForm):
    """Formulaire pour créer et modifier un dossier"""
    
    class Meta:
        model = Folder
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du dossier',
                'maxlength': '100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description du dossier (optionnel)',
                'rows': 3,
                'maxlength': '500'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control color-input',
                'title': 'Choisissez une couleur pour le dossier'
            })
        }
    
    def clean_name(self):
        """Validation du nom du dossier avec messages personnalisés"""
        name = self.cleaned_data.get('name')
        
        if not name:
            raise forms.ValidationError("📁 Veuillez saisir un nom pour votre dossier")
        
        # Nettoyer le nom
        name = name.strip()
        
        if len(name) < 2:
            raise forms.ValidationError("📏 Le nom du dossier doit contenir au moins 2 caractères")
        
        if len(name) > 100:
            raise forms.ValidationError("📏 Le nom du dossier ne doit pas dépasser 100 caractères")
        
        # Vérifier les caractères interdits
        forbidden_chars = ['<', '>', '&', '"', "'", '\\', '/', '|', '?', '*']
        for char in forbidden_chars:
            if char in name:
                raise forms.ValidationError(f"🚫 Le caractère '{char}' n'est pas autorisé dans le nom du dossier")
        
        return name
    
    def clean_description(self):
        """Validation de la description avec messages personnalisés"""
        description = self.cleaned_data.get('description')
        
        if description:
            description = description.strip()
            
            if len(description) > 500:
                raise forms.ValidationError("📏 La description ne doit pas dépasser 500 caractères")
        
        return description
    
    def clean_color(self):
        """Validation de la couleur avec messages personnalisés"""
        color = self.cleaned_data.get('color')
        
        if not color:
            # Valeur par défaut si aucune couleur n'est fournie
            return '#007bff'
        
        # Nettoyer la couleur
        color = color.strip().lower()
        
        # Vérifier le format hexadécimal
        if not re.match(r'^#[0-9a-f]{6}$', color):
            raise forms.ValidationError("🎨 Veuillez sélectionner une couleur valide (format hexadécimal)")
        
        return color