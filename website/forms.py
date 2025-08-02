from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Equipment, MaterialType, MaterialRequest

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''
        self.fields['username'].widget.attrs.update({'placeholder': 'Nom d’utilisateur', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Mot de passe', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirmer le mot de passe', 'class': 'form-control'})
        self.fields['password2'].help_text = None

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Nom d’utilisateur', 'class': 'form-control'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password')

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['nom', 'numero_serie', 'type_materiel', 'etat']
        widgets = {
            'etat': forms.Select(),
        }

class MaterialTypeForm(forms.ModelForm):
    class Meta:
        model = MaterialType
        fields = ['nom', 'description']

class MaterialRequestForm(forms.ModelForm):
    class Meta:
        model = MaterialRequest
        fields = ['equipements', 'commentaires', 'etat']
        widgets = {
            'equipements': forms.CheckboxSelectMultiple(),
            'etat': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['equipements'].queryset = Equipment.objects.filter(etat='Disponible')
        if user and user.is_staff:
            self.fields.pop('equipements')
            self.fields.pop('commentaires')
        elif not user or not user.is_staff:
            self.fields.pop('etat')

