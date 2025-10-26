from django import forms
from .models import Folder

class FolderForm(forms.ModelForm):
    """Formulaire pour créer et modifier des dossiers"""
    
    class Meta:
        model = Folder
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du dossier (ex: Spring, Python, Web Development)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description optionnelle du dossier'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'title': 'Couleur du dossier'
            })
        }
        labels = {
            'name': 'Nom du dossier',
            'description': 'Description',
            'color': 'Couleur'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes CSS pour le style
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
