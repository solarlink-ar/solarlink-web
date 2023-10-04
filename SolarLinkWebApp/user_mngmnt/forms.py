from django import forms  
from django.contrib import auth
from django.contrib.auth.models import User  
from django.contrib.auth.forms import UserCreationForm  
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.contrib.auth import get_user_model
from django.forms.forms import Form
import string


class SignupForm(forms.Form):
    first_name = forms.CharField(label='Nombre:', max_length=32)
    last_name = forms.CharField(label='Apellido:', max_length=32)

    email = forms.EmailField(label='Email')
    username = forms.CharField(label='Username:', max_length=16)
    password1 = forms.CharField(label='Contraseña:', max_length=32, min_length=8, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirmar contraseña:', max_length=32, min_length=8, widget=forms.PasswordInput())

    # metodo de filtrado
    def clean(self):

        try:
            username = self.cleaned_data['username']
            email = self.cleaned_data['email']
            first_name = self.cleaned_data['first_name']
            last_name = self.cleaned_data['last_name']
            password1 = self.cleaned_data["password1"]
            password2 = self.cleaned_data["password2"]
        except:
            # si hay problemas con lo ingresado, derivo la resolucion al backend
            return self.cleaned_data


        # si las contraseñas no concuerdan
        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no concuerdan")
        # si el usuario ya existe
        if User.objects.filter(username = username):
            raise forms.ValidationError("El usuario ya existe")
        
        # codifico datos en utf-8
        first_name_encoded = first_name.encode("utf-8", "ignore")
        last_name_encoded = last_name.encode("utf-8", "ignore")
        username_encoded = username.encode("utf-8", "ignore")
        email_encoded = email.encode("utf-8", "ignore")
        password1_encoded = password1.encode("utf-8", "ignore")
        password2_encoded = password2.encode("utf-8", "ignore")
        # decodifico datos desde utf-8, para quitar caracteres indeseados
        first_name_decoded = first_name_encoded.decode()
        last_name_decoded = last_name_encoded.decode()
        username_decoded = username_encoded.decode()
        email_decoded = email_encoded.decode()
        password1_decoded = password1_encoded.decode()
        password2_decoded = password2_encoded.decode()

        # si hay caracteres indeseados
        if first_name != first_name_decoded or \
           last_name != last_name_decoded or \
           username != username_decoded or \
           email != email_decoded or \
           password1 != password1_decoded or \
           password2 != password2_decoded:
            raise forms.ValidationError("Caracteres no válidos")

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
        

class LoginForm(forms.Form):
    username = forms.CharField(label='Username:', max_length=16, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(label='Contraseña:', max_length=32, min_length=8, widget=forms.PasswordInput(attrs={'placeholder':'Contraseña'}))

    def clean(self):
        password = self.cleaned_data["password"]
        username = self.cleaned_data["username"]
        
        # me fijo si existe un usuario con ese username
        username_confirmation = User.objects.filter(username = username)
        # autentico si existe un usuario con ese username y contraseña
        user = auth.authenticate(username=username, password = password)

        # si no existe el usuario
        if not username_confirmation:
            raise ValidationError('El usuario no existe')

        # si existe el usuario pero su cuenta no está activa
        if username_confirmation and not username_confirmation[0].is_active:
            raise ValidationError('Verifica tu cuenta para iniciar sesión')
        
        # si existe el usuario pero no con esa contraseña
        elif username_confirmation and not user:
            raise ValidationError('La contraseña es incorrecta')
        
        return self.cleaned_data
