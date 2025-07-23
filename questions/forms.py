from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Question, Reponse, Tag

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label="Prénom", max_length=30, required=False)
    last_name = forms.CharField(label="Nom", max_length=30, required=False)
    username = forms.CharField(label="Nom d'utilisateur")
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

class QuestionForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control tag-autocomplete',
            'multiple': 'multiple',
        }),
        required=False,
        label="Tags associés"
    )

    class Meta:
        model = Question
        fields = ['titre', 'contenu', 'tags']
        labels = {
            'titre': "Titre de la question",
            'contenu': "Contenu",
            'tags': "Tags",
        }
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }

class ReponseForm(forms.ModelForm):
    class Meta:
        model = Reponse
        fields = ['contenu']
        labels = {'contenu': "Votre réponse"}
        widgets = {
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['nom']
        labels = {'nom': "Nom du tag"}
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: python, api, backend'})
        }
