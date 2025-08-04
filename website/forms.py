from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Equipment, Affectation, DemandeEquipement, DemandeIntervention

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-control'})
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('admin', 'Admin'), ('gestionnaire', 'Gestionnaire'), ('fonctionnaire', 'Fonctionnaire')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('admin', 'Admin'), ('gestionnaire', 'Gestionnaire'), ('fonctionnaire', 'Fonctionnaire')])
    password = forms.CharField(
        label='Mot de passe (optionnel)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['email', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre utilisateur.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['cab_number', 'designation', 'type', 'sous_type', 'year', 'emplacement', 'quantity']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        }

class AffectationForm(forms.ModelForm):
    quantity = forms.IntegerField(
        label='Quantité',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Affectation
        fields = ['equipement', 'fonctionnaire', 'service', 'quantity']
        widgets = {
            'equipement': forms.Select(attrs={'class': 'form-control'}),
            'fonctionnaire': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipement'].queryset = Equipment.objects.filter(affecte=False, quantity__gt=0)
        self.fields['fonctionnaire'].queryset = User.objects.filter(is_staff=False, is_superuser=False)

    def clean(self):
        cleaned_data = super().clean()
        equipement = cleaned_data.get('equipement')
        quantity = cleaned_data.get('quantity')
        if equipement and quantity:
            if quantity > equipement.quantity:
                raise forms.ValidationError(f"La quantité demandée ({quantity}) dépasse la quantité disponible ({equipement.quantity}) pour cet équipement.")
        return cleaned_data


class DemandeEquipementForm(forms.ModelForm):
    equipements = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.filter(affecte=False, quantity__gt=0),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'data-live-search': 'true'})
    )

    class Meta:
        model = DemandeEquipement
        fields = ['objet', 'equipements', 'quantity', 'motif', 'service']
        widgets = {
            'motif': forms.Textarea(attrs={'rows': 4}),
        }

class DemandeInterventionForm(forms.ModelForm):
    class Meta:
        model = DemandeIntervention
        fields = ['service', 'poste', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
