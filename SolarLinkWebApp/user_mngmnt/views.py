from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .tasks import no_reply_sender, creador_datos
from .forms import SignupForm, PasswordSetForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.views import View
from . import models
import secrets
import random
import json


###############################################################################################################
############################################ FUNCIONES ########################################################
###############################################################################################################

def index(request):
    return render(request, "user_mngmnt/index.html")


# decorador para pestañas que solo se pueden acceder sin estar logueado (regisro, login, etc)
def unlogued_required(redirect_link):
    def decorator(func):
        def check(request):
            if request.user.username == '':
                return func(request)
            else:
                return redirect(redirect_link)
        return check
    return decorator

###############################################################################################################
################################################ SIGNUP #######################################################
###############################################################################################################

# registro
class Signup(View):
    # si se rellena un login
    def post(self, request):     
        # consigo el form con los datos posteados
        form = SignupForm(request.POST)

        # si el formulario es valido
        if form.is_valid():
            # tomo los datos
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            # creo el usuario
            User.objects.create_user(email=email, 
                                        username=username, 
                                        password=password1, 
                                        first_name= first_name, 
                                        last_name = last_name)
            # lo autentico y logueo
            user = auth.authenticate(username=username, password = password1)
            auth.login(request, user)
            # genero token de confirmacion de registro
            token = secrets.token_urlsafe(32)
            # lo guardo en la base de datos
            models.UsersTokens(user=user, signup_token=token).save()
            # deshabilito al usuario hasta que verifique por mail
            user.is_active = False
            user.save()

            # mando mail
            no_reply_sender.delay(mail_to=user.email, asunto='Confirma tu registro!', mensaje=f'''
Hola, {user.first_name}. Abre este link para confirmar el registro de {user.username}: 
http://127.0.0.1:8000/user/signup-verification/{token}''')

            # redirijo a pestaña a continuación
            return render(request, 'user_mngmnt/auth/signup_verification.html')
    
            
        # si el form no es válido
        else:
            # codigo de error
            error = form.errors.as_data()['__all__'][0].message
            # retorno con codigo de error
            return render(request, 'user_mngmnt/auth/signup.html', {'form': form, 'error': error})
            
        
    # si entro a la web con un GET
    def get(self, request, *args, **kwargs):
        # armo template
        form = SignupForm()
        return render(request, 'user_mngmnt/auth/signup.html', {'form': form})


# verificacion de registro
class SignupVerification(View):
    def get(self, request, token):
        # busco en la tabla de tokens un token igual al ingresado
        data = models.UsersTokens.objects.filter(signup_token=token)
        # si el token esta entre los tokens guardados
        if data and token in data[0].signup_token:
            user = data[0].user
            # activo al usuario
            user.is_active = True
            user.save()
            # borro el token
            models.UsersTokens.objects.filter(signup_token = token).delete()
            # aviso por mail que el usuario se ha verificado
            no_reply_sender.delay(mail_to = user.email, asunto="Tu cuenta se ha verificado", mensaje=f"""
Felicidades, {user.first_name}! El usuario de Solar Link {user.username} se ha verificado. Ya podés acceder a la plataforma!""")
            # devuelvo que el usuario se registro adecuadamente
            return render(request, 'user_mngmnt/auth/signup_verification.html')
        # si no hay token o es invalido, devuelvo signup
        else:
            return redirect('signup')

###############################################################################################################
########################################### PASSWORD RESET ####################################################
###############################################################################################################

# Password reset
class PasswordReset(View):
    def get(self, request):
        return render(request, "user_mngmnt/auth/password-reset.html")
    
    def post(self, request):
        # tomo mail
        email = request.POST['email']
        # busco usuarios con ese mail
        users = User.objects.filter(email=email)
        # si hay usuarios
        if users:
            # para cada usuario
            for user in users:
                # genero token
                token = secrets.token_urlsafe(32)
                # guardo token a usuario
                models.UsersTokens(user=user, password_reset_token=token).save()
                # mando mail
                no_reply_sender.delay(mail_to=user.email, asunto=f'Cambiá tu contraseña para {user.username}', mensaje=f'''
Hola, {user.first_name}. Cambiá la contraseña para el usuario {user.username} con el siguiente link:
http://127.0.0.1:8000/user/password-set/{token}''')
            # devuelvo vista con booleano para avisar que ya se envió mail
            return render(request, 'user_mngmnt/auth/password-reset.html', {'done': True})
    
# password 
class PasswordSet(View):
    def get(self, request, token):
        # busco si hay pedidos de cambio de contraseña con ese token
        data = models.UsersTokens.objects.filter(password_reset_token = token)
        # si hay, y el token es valido
        if data and token in data[0].password_reset_token:
            # armo form
            form = PasswordSetForm()
            # devuelvo form con el token en ctx para postear
            return render(request, 'user_mngmnt/auth/password-set.html', {"form":form, "token":token})
        else:
            # si no, redirijo a login
            return redirect('login')

    def post(self, request, token):
        # armo form con parametros posteados
        form = PasswordSetForm(request.POST)
        # si el form es valido
        if form.is_valid():
            # tomo nueva contraseña
            new_password = form.cleaned_data['password1']
            # busco los datos del token ingresado
            data = models.UsersTokens.objects.filter(password_reset_token = token)
            # tomo el usuario de ese token
            user = data[0].user
            # le cambio la contraseña y guardo
            user.set_password(new_password)
            user.save()
            # borro token
            models.UsersTokens.objects.filter(password_reset_token = token).delete()
            # devuelvo vista con booleano para la vista de success
            return render(request, 'user_mngmnt/auth/password-set.html', {"form":form, "done":True})
        # si el form no es valido
        else:
            # devuelvo mensaje de error
            error = form.errors.as_data()['__all__'][0].message
            # se carga vista, se vuelve a mandar token para seguir pudiendo postear aun con intentos fallidos!!
            return render(request, 'user_mngmnt/auth/password-set.html', {'form':form, 'error': error, "token": token})
            

###############################################################################################################
################################################ LOGIN ########################################################
###############################################################################################################


class Login(View):

    def get(self, request, *args, **kwargs):
        return render(request, "user_mngmnt/auth/login.html")
    
    def post(self, request):
        #obtengo user y pass
        username = request.POST['username']
        password = request.POST['password']

        # me fijo si existe un usuario con ese username
        username_confirmation = User.objects.filter(username = username)
        # autentico si existe un usuario con ese username y contraseña
        user = auth.authenticate(username=username, password = password)

        # si existe el usuario pero su cuenta no está activa
        if not username_confirmation[0].is_active:
            error = 'Verifica tu cuenta para iniciar sesión'
            return render(request, 'user_mngmnt/auth/login.html', {'error': error})
        
        # si existe el usuario pero no con esa contraseña
        elif username_confirmation and not user:
            error = 'La contraseña es incorrecta'
            return render(request, 'user_mngmnt/auth/login.html', {'error': error})

        # en el resto de casos
        else:
            # si existe, logueo
            if user:
                auth.login(request, user)
                return redirect('index')

            # si no existe, doy error
            else:
                error = 'El usuario no existe'
                return render(request, 'user_mngmnt/auth/login.html', {'error': error})


# logout
@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')

###############################################################################################################
################################################ DATOS ########################################################
###############################################################################################################

def load_data(request):
    if request.method == "GET":
        data = request.GET.dict()
        user = auth.authenticate(username=data["username"], password=data["password"])
        if user:
            response = {"result": True}
            # cargar datos proximamente
        else:
            response = {"result": False}
        return JsonResponse(response)


#Userpage
@login_required
def userpage(request):
    username = request.user.username
    return render(request, "user_mngmnt/userpage.html", {"username": username})


def sender(request):
    no_reply_sender.delay(mail_to='ivanchicago70@gmail.com', asunto='nashe', mensaje='nashe')

def creador(request):
    creador_datos.delay()
    return HttpResponse(request, "Hecho")

def confirmation(request):
    return render(request, "user_mngmnt/auth/confirmacion.html")
