from django import forms
from django.forms import ModelForm, fields, widgets
from .models import User


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User

        help_texts = {
            'username': None,
            'email': None,
        }

        fields = ('username', 'email', 'password')

        labels = {
            'username': ('Username (ID No.)'),
            'email': ('Email (GSFE)'),
            'password': ('Password'),
        }

        widgets = {
            # 'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg mb-3',  'autocomplete': 'off', 'style': "text-transform: capitalize;", 'required': 'on'}),
            # 'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg mb-3',  'autocomplete': 'off', 'style': "text-transform: capitalize;", 'required': 'on'}),
            # 'course': forms.ChoiceField(choices  = course),
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg mb-3',  'autocomplete': 'off', 'name': 'usernameForm', 'required': 'on', 'placeholder': 'TUPC-XX-XXXX', 'onkeyup': "this.value = this.value.toUpperCase();"}),
            'email': forms.EmailInput(attrs={'type': 'email', 'class': 'form-control form-control-lg mb-3', 'name': 'email_address', 'autocomplete': 'off', 'required': 'on'}),
            'password': forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control form-control-lg', 'name': 'passwordForm', 'autocomplete': 'off', 'required': 'on'}),
        }
