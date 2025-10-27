from django import forms
from .models import Exercise, ExerciseCategory, ExerciseType, DifficultyLevel
import json


class ExerciseForm(forms.ModelForm):
    """Formulaire pour créer et modifier des exercices"""
    
    # Redéfinir les champs JSON comme des champs texte simples
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Write the exercise statement here'
        }),
        help_text='Write the exercise statement here'
    )
    solution = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Provide the correct answer'
        }),
        help_text='Provide the correct answer'
    )
    hints = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Optional hints to help users'
        }),
        required=False,
        help_text='Optional hints to help users'
    )
    
    class Meta:
        model = Exercise
        fields = [
            'title', 'description', 'content', 'solution', 'hints',
            'category', 'difficulty', 'exercise_type', 'estimated_time', 'points',
            'is_public', 'explanation_video_url', 'explanation_video_type'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Exercise title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Short description of the exercise'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'exercise_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estimated_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Estimated time in minutes'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Points awarded'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'explanation_video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL of explanation video (YouTube, Vimeo, etc.)'
            }),
            'explanation_video_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rendre certains champs optionnels
        self.fields['hints'].required = False
        self.fields['explanation_video_url'].required = False
        
        # Ajouter des labels personnalisés
        self.fields['is_public'].label = 'Public Exercise'
        self.fields['explanation_video_url'].label = 'Explanation Video URL'
        self.fields['explanation_video_type'].label = 'Video Type'
        
        # Si on édite un exercice existant, convertir les JSON en texte
        if self.instance and self.instance.pk:
            if isinstance(self.instance.content, dict):
                self.initial['content'] = json.dumps(self.instance.content, indent=2, ensure_ascii=False)
            if isinstance(self.instance.solution, dict):
                self.initial['solution'] = json.dumps(self.instance.solution, indent=2, ensure_ascii=False)
            if isinstance(self.instance.hints, list):
                self.initial['hints'] = json.dumps(self.instance.hints, indent=2, ensure_ascii=False)
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            try:
                # Essayer de parser comme JSON
                return json.loads(content)
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON valide, le traiter comme du texte simple
                return {"text": content, "type": "text"}
        return {}
    
    def clean_solution(self):
        solution = self.cleaned_data.get('solution')
        if solution:
            try:
                # Essayer de parser comme JSON
                return json.loads(solution)
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON valide, le traiter comme du texte simple
                return {"text": solution, "type": "text"}
        return {}
    
    def clean_hints(self):
        hints = self.cleaned_data.get('hints')
        if hints:
            try:
                # Essayer de parser comme JSON
                return json.loads(hints)
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON valide, le traiter comme une liste de texte
                return [hints] if hints.strip() else []
        return []
