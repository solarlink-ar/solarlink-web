from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .tasks import no_reply_sender, creador_datos
from django.contrib import auth
from .forms import SignupForm
from . import models
import secrets
import random
import json


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


# registro
# el usuario no debe estar logueado
@unlogued_required(redirect_link="index")
def signup(request):
    # si se rellena un login
    if request.method == "POST":
        
        # consigo el form con los datos posteados
        form = SignupForm(request.POST)

        if form.is_valid():
            # tomo los datos
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']


            # reviso si las contraseñas coinciden
            if password1 == password2:

                # intento buscar el usuario
                username_confirmation = User.objects.filter(username = username) 
                # si existe un usuario con ese username
                if username_confirmation:
                    # codigo de error
                    error = "El usuario ya está registrado"
                    # retorno el form con los datos previos y con codigo de error
                    return render(request, 'user_mngmnt/auth/signup.html', {'form': form,'error': error})
                
                # si no existe un usuario con ese username
                else:
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
                    models.Users_tokens(user=user, signup_token=token).save()
                    # deshabilito al usuario hasta que verifique por mail
                    user.is_active = False
                    user.save()

                    # mando mail
                    no_reply_sender.delay(mail_to=user.email, asunto='Confirma tu registro!', mensaje=f'''
Abre este link para confirmar tu registro:
http://127.0.0.1:8000/user/signup-verification/{token}''')


                    # redirijo a pestaña a continuación
                    return render(request, 'user_mngmnt/auth/signup_verification.html')
    
            # si las contraseñas no coinciden
            else:
                # codigo de error
                error = 'Las contraseñas no concuerdan!'                    
                # retorno el form con los datos previos y con codigo de error
                return render(request, 'user_mngmnt/auth/signup.html', {'form': form, 'error': error})
            
        # si el form no es válido
        else:
            # armo el template
            form = SignupForm()
            # codigo de error
            error = 'Datos mal ingresados'
            # retorno con codigo de error
            return render(request, 'user_mngmnt/auth/signup.html', {'form': form, 'error': error})
            
        
    # si entro a la web con un GET
    else:
        # armo template
        form = SignupForm()
        return render(request, 'user_mngmnt/auth/signup.html', {'form': form})

def signup_verification(request, token):
    if request.method == "GET":
        # busco en la tabla de tokens un token igual al ingresado
        data = models.Users_tokens.objects.filter(signup_token=token)
        # si el token esta entre los tokens guardados
        if data and token in data[0].signup_token:
            user = data[0].user
            # activo al usuario
            user.is_active = True
            user.save()
            # borro el token
            models.Users_tokens.objects.filter(signup_token = token).delete()
            # aviso por mail que el usuario se ha verificado
            no_reply_sender.delay(mail_to = user.email, asunto="Tu cuenta se ha verificado", mensaje="""
Felicidades! Tu cuenta de Solar Link se ha verificado. Ya podés acceder a la plataforma!""")
            # devuelvo que el usuario se registro adecuadamente
            return render(request, 'user_mngmnt/auth/signup_verification.html')
        # si no hay token o es invalido, devuelvo index
        else:
            return redirect('index')

# login
# el usuario no debe estar logueado
@unlogued_required(redirect_link="index")
def login(request):
    # si rellena formulario
    if request.method == "POST":
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
    # si hago un GET
    else:
        return render(request, "user_mngmnt/auth/login.html")

# logout
@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')

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

