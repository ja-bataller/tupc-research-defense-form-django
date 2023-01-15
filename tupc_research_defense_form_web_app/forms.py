from django import forms
from django.forms import ModelForm, fields, widgets
from .models import User
from django.utils.safestring import mark_safe


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User

        help_texts = {
            'username': None,
            'email': None,
        }

        fields = ('username', 'email', 'password')

        labels ={
            'username': mark_safe('<sup class='"text-danger>*</sup>"'Username (ID no.)'),
            'email': mark_safe('<sup class='"text-danger>*</sup>"'Email (GSFE)'),
            'password': mark_safe('<sup class='"text-danger>*</sup>"'Password'),
        }

        widgets = {
            # 'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg mb-3',  'autocomplete': 'off', 'style': "text-transform: capitalize;", 'required': 'on'}),
            # 'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg mb-3',  'autocomplete': 'off', 'style': "text-transform: capitalize;", 'required': 'on'}),
            # 'course': forms.ChoiceField(choices  = course),
            'username': forms.TextInput(attrs={'id':'username_input','class': 'form-control mb-3',  'autocomplete': 'off', 'name': 'usernameForm', 'required': 'on', 'placeholder': 'TUPC-XX-XXXX', 'onkeyup': "this.value = this.value.toUpperCase();"}),
            'email': forms.EmailInput(attrs={'id':'email_input', 'type': 'email', 'class': 'form-control mb-3', 'name': 'email_address', 'autocomplete': 'off', 'required': 'on'}),
            'password': forms.PasswordInput(attrs={'id':'password_input', 'type': 'password', 'class': 'form-control', 'name': 'passwordForm', 'autocomplete': 'off', 'required': 'on'}),
        }

