from django.contrib.auth.models import User
from django import forms

class RegisterForm(forms.Form):
    first_name = forms.CharField(label='Nombre:', max_length=32)
    last_name = forms.CharField(label='Apellido', max_length=32)

    email = forms.EmailField(label='email')
    username = forms.CharField(label='username', max_length=16)
    password = forms.CharField(label='password', max_length=32, widget=forms.PasswordInput())
    password_confirmation = forms.CharField(label='password', max_length=32, widget=forms.PasswordInput())


    



    