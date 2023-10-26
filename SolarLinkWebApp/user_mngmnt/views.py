from django.contrib.auth.decorators import login_required
from .forms import SignupForm, PasswordSetForm, LoginForm
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
# VERCEL NO SOPORTA CELERY, SOPORTE DESACTIVADO
#from .tasks import no_reply_sender, creador_datos
from django.shortcuts import render, redirect
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.contrib import auth
from django.views import View
from bs4 import BeautifulSoup
from django.core.mail import EmailMessage
from django.utils import timezone
from . import models
import datetime, requests, secrets, random, asyncio, json


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

# sender de mails, tomado de celery tasks
def no_reply_sender(email, subject, html_message):
    mail = EmailMessage(subject, html_message, to=[email])
    mail.content_subtype = 'html' # aclaracion de tipo de contenido
    mail.send()

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
            # genero offline user y
            # deshabilito al usuario hasta que verifique por mail
            models.isOnline(user=user, is_online = False).save()
            user.is_active = False
            user.save()

            context = {"first_name": user.first_name, "username": user.username, "mail": user.email, "url": f"{request.build_absolute_uri('/')}user/signup-verification/{token}", "base": request.build_absolute_uri('/')}
            # mando mail
            no_reply_sender(email = user.email, subject='¡Confirmá tu registro!', html_message=render_to_string("user_mngmnt/auth/confirmacion_signup.html", context))

            # redirijo a pestaña a continuación
            return render(request, 'user_mngmnt/auth/signup-verification.html')
    
            
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
            no_reply_sender(email=user.email, subject="¡Tu cuenta se ha verificado!", html_message=f"""
¡Felicidades, {user.first_name}! El usuario de Solar Link {user.username} se ha verificado. ¡Ya podés acceder a la plataforma!""")
            # devuelvo que el usuario se registro adecuadamente
            return render(request, 'user_mngmnt/auth/signup-verification.html')
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

                context = {"first_name": user.first_name, "username": user.username, "mail": user.email, "url": f"{request.build_absolute_uri('/')}user/password-set/{token}", "base": request.build_absolute_uri('/')}
                # mando mail
                no_reply_sender(email = user.email, subject='Cambio de contraseña', html_message=render_to_string("user_mngmnt/auth/confirmacion_password.html", context))
        # devuelvo vista con booleano para avisar que ya se envió mail
        return render(request, 'user_mngmnt/auth/password-reset-done.html')
    
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
            # si no, redirijo a index
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
            return render(request, 'user_mngmnt/auth/password-set-done.html')
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
            return redirect('userpage')
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
class UserPage(View):
    
    def get(self, request):
        # usuario
        user = request.user

        ############### DATOS SEMANA ###############
        # mes actual
        mes_actual = timezone.now().month
        # mes anterior
        prev = timezone.now().replace(day=1) - timezone.timedelta(days=1)

        # datos del mes actual, filtrados de la ultima semana, ordenados desde hoy
        mes_data = models.DatosDias.objects.filter(user=user, mes__range=(prev.month, mes_actual)).order_by("-año", "-mes","-dia")
        dias = []
        semanasolar = []
        semanaprov = []
        # si hay datos
        if mes_data:
            # para los ultimos 7 dias
            for i in range(7):
                # si hay index
                try:
                    # apendo dato de cada dia
                    semanaprov.append(mes_data[i].consumo_dia_red)
                    semanasolar.append(mes_data[i].consumo_dia_solar)
                    dias.append(f"{mes_data[i].dia}/{mes_data[i].mes}")
                # relleno con ceros
                except:
                    semanaprov.append(0)
                    semanasolar.append(0)
                    dias.append("")

        ############### DATOS AÑO ###############
        año_data = models.DatosDias.objects.filter(user=user, año = 2023)

        consumo_prov_meses = []
        consumo_ahorrado_meses = []
        # para cada mes del año
        for mes in range(1, 13):
            # filtro datos de ese mes
            mes_data = año_data.filter(mes = mes)
            # acumuladores
            consumo_prov_mes = 0
            consumo_ahorro_mes = 0
            # para cada dato de ese mes
            for data in mes_data:
                # acumulo
                consumo_prov_mes += data.consumo_dia_red
                consumo_ahorro_mes += data.consumo_dia_solar
            # apendo
            consumo_ahorrado_meses.append(int(consumo_ahorro_mes))
            consumo_prov_meses.append(int(consumo_prov_mes))

        ############### DATOS HOY ###############
        consumo_l1_solar = []
        consumo_l1_proveedor = []
        consumo_l2_solar = []
        consumo_l2_proveedor = []
        horas = []
        hoy = timezone.now()
    
        print(hoy)
        hoy_data = models.DatosHora.objects.filter(año = hoy.year, mes = hoy.month, dia = hoy.day)

        for i in range(0,24):
            data = hoy_data.filter(hora = i)
            if data:
                data = data[0]
                consumo_l1_solar.append(data.consumo_l1_solar)
                consumo_l1_proveedor.append(data.consumo_l1_proveedor)
                consumo_l2_solar.append(data.consumo_l2_solar)
                consumo_l2_proveedor.append(data.consumo_l2_proveedor)
            else:
                consumo_l1_solar.append(0)
                consumo_l1_proveedor.append(0)
                consumo_l2_solar.append(0)
                consumo_l2_proveedor.append(0)
        
        context = {}
        # si faltan todos los datos

        if año_data:
            context["datos_anual"] = True
            context["consumo_ahorrado_meses"] = consumo_ahorrado_meses
            context["consumo_prov_meses"] = consumo_prov_meses
        else:
            context["datos_anual"] = False

        #if mes_data:
        context["datos_7dias"] = True
        context["semanasolar"] = semanasolar
        context["semanaprov"] = semanaprov
        context["porcentaje_ahorro"] = round(sum(semanasolar)/sum(semanaprov) * 100, 2)
        context["dias"] = dias
        context["total_semanasolar"] = int(sum(semanasolar))
        context["total_semanaprov"] = int(sum(semanaprov))
        #else:
        #    context["datos_7dias"] = False

        if hoy_data:
            context["datos_hoy"] = True
            context["consumo_l1_solar"] = consumo_l1_solar
            context["consumo_l2_solar"] = consumo_l2_solar
            context["consumo_l1_prov"] = consumo_l1_proveedor
            context["consumo_l2_prov"] = consumo_l2_proveedor

        else:
            context["datos_hoy"] = False
        """
        # muestro
        else:
            datos_ahorro_ok = True
            context = {"semanasolar": semanasolar, "semanaprov": semanaprov, "dias": dias,
            "total_semanasolar":int(sum(semanasolar)),
            "total_semanaprov": int(sum(semanaprov)),
            ########
            "porcentaje_ahorro": round(sum(semanasolar)/sum(semanaprov) * 100, 2),
            "consumo_ahorrado_meses":consumo_ahorrado_meses,
            "consumo_prov_meses": consumo_prov_meses,
            ########
            "datos_ahorro_ok": datos_ahorro_ok,
            ########
            "consumo_l1_solar": consumo_l1_solar,
            "consumo_l2_solar": consumo_l2_solar,
            "consumo_l1_prov": consumo_l1_proveedor,
            "consumo_l2_prov": consumo_l2_proveedor}
        """
        return render(request, "user_mngmnt/index.html", context)




    #username = request.user.username
    #return render(request, "user_mngmnt/userpage.html", {"username": username})

class UserCalc(View):

    def get(self, request):
        ...
###############################################################################################################
################################################# API #########################################################
###############################################################################################################

class OnlineUsersUpdate(View):
    def post(self, request):
        # usuario
        user = request.user

        user.isonline.is_online = False

        user.isonline.save()

        models.TiempoReal.objects.filter(user=user).delete()


        return JsonResponse({"response":True})


    def get(self, request):
        # usuario
        user = request.user

        user.isonline.is_online = True

        user.isonline.save()


        return JsonResponse({"response":True})

class shouldPost(View):
    def get(self, request):
        # si el contenido esta en post
        if request.GET:
            # usuario posteado
            data = request.GET
        # si el contenido esta en body
        if request.body and not request.GET:
            data = json.loads(request.body)

        username = data["username"]
        password = data["password"]

        # autentico
        user = auth.authenticate(username=username, password=password)

        # si el usuario esta logueado, mando True
        if user.isonline.is_online:
            return JsonResponse({"response": True})
        else:
            return JsonResponse({"response": False})
        
    def post(self, request):
        # si el contenido esta en post
        if request.POST:
            # usuario posteado
            data = request.POST
        # si el contenido esta en body
        if request.body and not request.POST:
            data = json.loads(request.body)

        username = data["username"]
        password = data["password"]

        user = auth.authenticate(username=username, password = password)

        models.TiempoReal(user = user, 
                          voltaje = data["voltaje"],
                          consumo_l1 = data["consumo_l1"],
                          solar_l1 = data["solar_l1"],
                          consumo_l2 = data["solar_l2"],
                          solar_l2 = data["solar_l2"],
                          solar = ["solar"]).save()
        
        return JsonResponse({"response": True})
        

    
class LoadData(View):
    def post(self, request):
        # si el contenido esta en post
        if request.POST:
            # usuario posteado
            data = request.POST
            
        # si el contenido esta en body
        if request.body and not request.POST:
            data = json.loads(request.body)
        
        username = data["username"]
        password = data["password"]

        # autentico
        user = auth.authenticate(username=username, password=password)
        # si existe el usuario
        if user:
            # guardo datos
            models.DatosHora(
                user = user,
                voltaje_hora_red = data["voltaje_hora_red"],
                consumo_hora_solar = data["consumo_hora_solar"],
                consumo_hora_red = data["consumo_hora_red"],
                consumo_l1_solar = data["consumo_l1_solar"],
                consumo_l2_solar = data["consumo_l2_solar"],
                consumo_l1_proveedor = data["consumo_l1_proveedor"],
                consumo_l2_proveedor = data["consumo_l2_proveedor"],
                hora = data["hora"],
                dia = data["dia"],
                mes = data["mes"],
                año = data["agno"],
                solar_ahora = data["solar_ahora"]).save()
            
            return JsonResponse({"response": True})
            


class loadDataNow(View):
    def get(self, request):
        user = request.user
        data = models.TiempoReal.objects.filter(user=user)
        if data:
            for d in data:
                now = d
            response = {"voltaje": now.voltaje,
                        "consumo_l1": now.consumo_l1,
                        "consumo_l2": now.consumo_l2,
                        "solar": (now.solar_l1 or now.solar_l2)}
            
            return JsonResponse(response)
        else:
            return JsonResponse({"response": False})

    def post(self, request):
        # si el contenido esta en post
        if request.POST:
            # usuario posteado
            data = request.POST
            
        # si el contenido esta en body
        if request.body and not request.POST:
            data = json.loads(request.body)

        username = data["username"]
        password = data["password"]
        voltaje = data["voltaje"]
        consumo_l1 = data["consumo_l1"]
        consumo_l2 = data["consumo_l2"]
        solar_l1 = data["solar_l1"]
        solar_l2 = data["solar_l2"]
        
        user = auth.authenticate(username = username, password=password)

        models.TiempoReal(user=user,
                          voltaje=voltaje,
                          consumo_l1 = consumo_l1,
                          consumo_l2 = consumo_l2,
                          solar_l1 = solar_l1,
                          solar_l2 = solar_l2).save()
        return JsonResponse({"response": True})
        

class APILogin(View):
    async def post(self, request):
        # si el contenido esta en post
        if request.POST:
            # usuario posteado
            username = request.POST["username"]
            password = request.POST["password"]
        # si el contenido esta en body
        if request.body and not request.POST:
            async_json_loads = sync_to_async(json.loads, thread_sensitive=False)
            username = (await async_json_loads(request.body))["username"]
            password = (await async_json_loads(request.body))["password"]

        # autentico
        async_auth = sync_to_async(auth.authenticate, thread_sensitive=False)
        user = await async_auth(username=username, password=password)

        # si existe el usuario, respondo aprobación
        if user:
            response = {"login": True}
        else:
            response = {"login": False}
        
        return JsonResponse(response)
    
class EdesurEdenor(View):

    async def get(self, request):
        web = requests.get('https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/7A2E515E48ECD5EB032589650044C8A6?opendocument')
        soup = BeautifulSoup(web.content, 'html.parser')
        

###############################################################################################################
################################################ CRONS ########################################################
###############################################################################################################

# ADAPTACION DE CRON JOBS A VIEWS YA QUE VERCEL NO SOPORTA CELERY

def ordenador(request):
    # usuarios
    users = models.User.objects.all()

    # para cada usuario
    for user in users:
        # datos del usuario
        user_data = models.DatosHora.objects.filter(user=user)

        # mientras existan datos
        while user_data:
            # variables temporales
            voltaje_dia_red = []
            consumo_dia_red = 0
            consumo_dia_solar = 0
            solar_por_hora = []
            potencia_dia_panel = 0
            horas_de_carga = []
            voltajes_bateria = []
            errores = []

            # referencia para dia, mes
            referencia = user_data[0]
            #datos del dia buscado
            dia_data = user_data.filter(dia=referencia.dia, mes=referencia.mes, año=referencia.año)

            # para cada dato del dia
            for data in dia_data:
                # acumulo en valores sumario diario
                voltaje_dia_red.append(data.voltaje_hora_red)
                consumo_dia_solar += data.consumo_hora_solar
                consumo_dia_red += data.consumo_hora_red

                solar_por_hora.append(data.solar_ahora)
                potencia_dia_panel += data.panel_potencia
                horas_de_carga.append(data.cargando)
                voltajes_bateria.append(data.voltaje_bateria)

                errores.append(data.errores)
                product_id = data.product_id

                # borro el dato
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
            
            # sobreescribo user_data, para quitar los datos que acabo de borrar
            user_data = models.DatosHora.objects.filter(user=user)


def token_clean(request):
    # todos los tokens activos
    data = models.UsersTokens.objects.all()
    # hora en timezone
    actual = timezone.now()
    # para cada dato
    for d in data:
        # si el tiempo entre que el token fue creado y el actual es mayor a 2hs
        if (actual - d.time) > datetime.timedelta(hours=1):
            # borro el token
            d.delete()


###############################################################################################################
################################################ TOOLS ########################################################
###############################################################################################################

def creador(request):
    user = request.user
    lista = [True,False]
    # se sube un dato por hora
    for d in range(1, 31):
        for h in range(0, 24):
            models.DatosHora(user = user,
                            voltaje_hora_red = random.randint(170, 240),
                            consumo_hora_red = random.randint(0, 4000),
                            consumo_hora_solar = random.randint(0, 340),
                            consumo_l1 = random.randint(0, 4000),
                            consumo_l2 = random.randint(0,4000),
                            hora = h,
                            dia = d,
                            mes = 10,
                            año = 2023,
                            solar_ahora = random.choice(lista),
                            panel_potencia = random.randint(0, 340),
                            cargando = random.choice(lista),
                            voltaje_bateria = random.randint(10, 15),
                            errores = random.choice(lista),
                            product_id = 'nashe23').save()
                
def sender(request):
    no_reply_sender('ivanchicago70@gmail.com', 'nashe', 'nashe')
    #mail = EmailMessage('Hola', 'hola', to=['ivanchicago70@gmail.com'])
    #mail.content_subtype = 'html' # aclaracion de tipo de contenido
    #mail.send()

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
