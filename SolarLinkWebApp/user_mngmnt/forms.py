from django import forms  
from django.contrib.auth.models import User  
from django.contrib.auth.forms import UserCreationForm  
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.contrib.auth import get_user_model
from django.forms.forms import Form  


class SignupForm(forms.Form):
    first_name = forms.CharField(label='Nombre:', max_length=32)
    last_name = forms.CharField(label='Apellido:', max_length=32)

    email = forms.EmailField(label='Email')
    username = forms.CharField(label='Username:', max_length=16)
    password1 = forms.CharField(label='Contraseña:', max_length=32, min_length=8, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirmar contraseña:', max_length=32, min_length=8, widget=forms.PasswordInput())

    # metodo de filtrado
    def clean(self):
        username = self.cleaned_data['username']
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        # si las contraseñas no concuerdan
        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no concuerdan")
        # si el usuario ya existe
        if User.objects.filter(username = username):
            raise forms.ValidationError("El usuario ya existe")
        
        return self.cleaned_data

class PasswordSetForm(forms.Form):
    password1 = forms.CharField(label='Contraseña nueva:', max_length=32, min_length=8, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirmar contraseña:', max_length=32, min_length=8, widget=forms.PasswordInput())

    def clean(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        # si las contraseñas no concuerdan
        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no concuerdan")
        
        return self.cleaned_data
        

