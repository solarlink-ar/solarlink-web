from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .tasks import no_reply_sender, creador_datos, ordenador
from .forms import SignupForm, PasswordSetForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.template.loader import render_to_string
from django.views import View
from . import models
import secrets
import random
import json


###############################################################################################################
############################################ FUNCIONES ########################################################
###############################################################################################################

def calculador_cantidad_true(lista:list):
    index = 0
    for i in lista:
        if i:
            index += 1
    return index

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
{request.build_absolute_uri('/')}user/signup-verification/{token}''')
            #no_reply_sender.delay(mail_to=user.email, asunto='Confirma tu registro!', mensaje=render_to_string("user_mngmnt/auth/confirmacion.html"))

            # redirijo a pestaña a continuación
            return render(request, 'user_mngmnt/auth/signup_verification.html')
    
            
        # si el form no es válido
        else:
            # codigo de error
            try:
                # intento encontrar mensaje de error
                error = form.errors.as_data()['__all__'][0].message
            # si no lo encuentro
            except:
                # hago diccionario de errores
                errors = form.errors.as_data()
                # para cada error
                for i in errors:
                    # busco el ultimo mensaje
                    error = errors[i][0].message
                # si el mensaje es el mencionado abajo
                if error == 'This field is required.':
                    # devuelvo error
                    error = 'Caracteres no validos'

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
{request.build_absolute_uri('/')}user/password-set/{token}''')
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

    def get(self, request):
        form = LoginForm()
        return render(request, "user_mngmnt/auth/login.html", {"form":form})
    
    def post(self, request):
        form = LoginForm(request.POST)

        # si el form es valido
        if form.is_valid():
            #obtengo user y pass
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # autentico si existe usuario
            user = auth.authenticate(username=username, password = password)

            # logueo
            auth.login(request, user)
            # redirijo a index
            return redirect('index')
        # si el form no es valido
        else:
            # codigo de error
            try:
                # intento encontrar mensaje de error
                error = form.errors.as_data()['__all__'][0].message
            # si no lo encuentro
            except:
                # hago diccionario de errores
                errors = form.errors.as_data()
                # para cada error
                for i in errors:
                    # busco el ultimo mensaje
                    error = errors[i][0].message
                # si el mensaje es el mencionado abajo
                if error == 'This field is required.':
                    # devuelvo error
                    error = 'Caracteres no validos'
                
            return render(request, 'user_mngmnt/auth/login.html', {"form": form, 'error': error})


# logout
@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')

###############################################################################################################
################################################ DATOS ########################################################
###############################################################################################################

#Userpage
@login_required
def userpage(request):
    username = request.user.username
    return render(request, "user_mngmnt/userpage.html", {"username": username})

###############################################################################################################
################################################# API #########################################################
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
    
class APILogin(View):
    def post(self, request):
        # datos de la ESP
        username = request.POST["username"]
        password = request.POST["password"]

        # autentico
        user = auth.authenticate(username=username, password=password)

        # si existe el usuario, respondo aprobación
        if user:
            response = {"login": True}
        else:
            response = {"login": False}
        
        return JsonResponse(response)
        
###############################################################################################################
################################################ TOOLS ########################################################
###############################################################################################################

def sender(request):
    no_reply_sender.delay(mail_to='ivanchicago70@gmail.com', asunto='nashe', mensaje='nashe')

def creador(request):
    creador_datos.delay()
    #models.UsersTokens(user=request.user, signup_token = 'dajkalsd').save()
    #import time
    #time.sleep(1)
    #data = models.DatosHora.objects.all()
    #for i in data:
    #    print(i.hora, i.dia, i.mes, i.año)
    #return render(request, "user_mngmnt/auth/confirmacion.html")

def confirmation(request):
    #ordenador.delay()
    users = models.User.objects.all()
    
    for user in users:

        user_data = models.DatosHora.objects.filter(user=user)

        while user_data:

            voltaje_dia_red = []
            consumo_dia_red = 0
            consumo_dia_solar = 0
            solar_por_hora = []
            potencia_dia_panel = 0
            horas_de_carga = []
            voltajes_bateria = []
            errores = []

            referencia = user_data[0]

            dia_data = user_data.filter(dia=referencia.dia, mes=referencia.mes, año=referencia.año)
            
            for data in dia_data:
                # guardado de datos
                voltaje_dia_red.append(data.voltaje_hora_red)
                consumo_dia_solar += data.consumo_hora_solar
                consumo_dia_red += data.consumo_hora_red

                solar_por_hora.append(data.solar_ahora)
                potencia_dia_panel += data.panel_potencia
                horas_de_carga.append(data.cargando)
                voltajes_bateria.append(data.voltaje_bateria)

                errores.append(data.errores)
                product_id = data.product_id

                data.delete()
            
            # creo dato dia
            models.DatosDias(user = user,
                            voltaje_maximo_dia_red = max(voltaje_dia_red),
                            voltaje_minimo_dia_red = min(voltaje_dia_red),
                            consumo_dia_solar = consumo_dia_solar,
                            consumo_dia_red = consumo_dia_red,

                            dia = referencia.dia,
                            mes = referencia.mes,
                            año = referencia.año,

                            horas_potencia_panel = calculador_cantidad_true(solar_por_hora),
                            potencia_dia_panel = potencia_dia_panel,
                            horas_de_carga = calculador_cantidad_true(horas_de_carga),
                            voltajes_bateria = json.dumps(voltajes_bateria),
                            errores = calculador_cantidad_true(errores),
                            product_id = data.product_id).save()
            
            user_data = models.DatosHora.objects.filter(user=user)
