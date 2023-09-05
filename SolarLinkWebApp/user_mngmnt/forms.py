from django import forms  
from django.contrib.auth.models import User  
from django.contrib.auth.forms import UserCreationForm  
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form  

class SignupForm(forms.Form):
    first_name = forms.CharField(label='Nombre:', max_length=32)
    last_name = forms.CharField(label='Apellido:', max_length=32)

    email = forms.EmailField(label='Email')
    username = forms.CharField(label='Username:', max_length=16)
    password1 = forms.CharField(label='Contraseña:', max_length=32, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirmar contraseña:', max_length=32, widget=forms.PasswordInput())



    