from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib import auth
from . import models
from .forms import RegisterForm
import datetime
import json
import random

def index(request):
    return render(request, "user_mngmnt/index.html")

def calculador_cantidad_true(lista:list):
    index = 0
    for i in lista:
        if i:
            index += 1
    return index
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
@unlogued_required(redirect_link="index")
def register(request):
    # si se rellena un login
    if request.method == "POST":
        
        # armo form
        form = RegisterForm(request.POST)

        if form.is_valid():
            # tomo los datos
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password_confirmation = form.cleaned_data['password_confirmation']

            # armo template
            form = RegisterForm()

            # reviso si las contraseñas coinciden
            if password_confirmation == password:


                # intento buscar el usuario
                user = auth.authenticate(username=username, password = password)
                # si existe
                if user:
                    error = "El usuario ya está registrado"
                    return render(request, 'user_mngmnt/register.html', {'form': form,'error': error})
                
                # si no existe, lo registro, lo logueo y voy a product
                else:

                    User.objects.create_user(email=email, username=username, password=password, first_name= first_name, last_name = last_name)
                    user = auth.authenticate(username=username, password = password)
                    auth.login(request, user)

                return redirect('index')
    
            # si las contraseñas no coinciden
            else:
                error = 'Las contraseñas no concuerdan!'
                return render(request, 'user_mngmnt/register.html', {'form': form, 'error': error})
        
    # si entro a la web con un GET
    else:
        # armo template
        form = RegisterForm()
        return render(request, 'user_mngmnt/register.html', {'form': form})
   

# login
@unlogued_required(redirect_link="index")
def login(request):
    # si rellena formulario
    if request.method == "POST":
        #obtengo user y pass
        username = request.POST['username']
        password = request.POST['password']

        #autentico
        user = auth.authenticate(username=username, password = password)
        
        # si existe, logueo
        if user:
            auth.login(request, user)
            return redirect('index')

        # si no existe, doy error
        else:
            error = 'El usuario es incorrecto'
            return render(request, 'user_mngmnt/login.html', {'error': error})
    else:
        return render(request, "user_mngmnt/login.html")
    

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

def data(request):
    # lista de objetos de usuario
    users = models.User.objects.all()

    # para cada usuario
    for user in users:
        voltaje_dia_red = []
        consumo_dia_red = 0
        consumo_dia_solar = 0
        horas = []
        dias = []
        meses = []
        años = []
        solar_por_hora = []
        potencia_dia_panel = 0
        horas_de_carga = []
        voltajes_bateria = []
        errores = []
        
        # todos los datos de cierto usuario
        user_data = models.Datos_hora.objects.filter(user=user)


        # entre los datos del usuario
        for data in user_data:
            # hago una lista con todos los años que tenga datos
            if not data.año in años:
                años.append(data.año)
            
        # para cada año
        for año in años:
            # filtro los datos de todo ese año
            año_data = user_data.filter(año = año)

            # entre todos los datos del año
            for data in año_data:
                # hago una lista con todos los meses que tengan datos
                if not data.mes in meses:
                    meses.append(data.mes)
            
            
            # para cada mes
            for mes in meses:
                # filtro los datos del mes
                mes_data = año_data.filter(mes=mes)

                # entre todos los datos del mes
                for data in mes_data:
                    # hago una lista con todos los dias que tengan datos
                    if not data.dia in dias:
                        dias.append(data.dia)
                    
                    #print(dias)
                    # para cada dia
                for dia in dias:
                    # filtro los datos del dia
                    dia_data = mes_data.filter(dia = dia)
                    
                    # entre todos los datos del dia
                    for data in dia_data:
                        # hago una lista con todas las horas que tengan datos
                        if not data.hora in dia_data:
                            horas.append(data.hora)
                    
                    # para cada hora
                    for hora in horas:
                        hora_data = dia_data.filter(hora=hora)
                        print(hora_data)

                        for data in hora_data:
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
                    
                            
                    
                    models.Datos_dias(user = user,
                                    voltaje_maximo_dia_red = max(voltaje_dia_red),
                                    voltaje_minimo_dia_red = min(voltaje_dia_red),
                                    consumo_dia_solar = consumo_dia_solar,
                                    consumo_dia_red = consumo_dia_red,

                                    dia = dia,
                                    mes = mes,
                                    año = año,

                                    horas_potencia_panel = calculador_cantidad_true(solar_por_hora),
                                    potencia_dia_panel = potencia_dia_panel,
                                    horas_de_carga = calculador_cantidad_true(horas_de_carga),
                                    voltajes_bateria = json.dumps(voltajes_bateria),
                                    errores = calculador_cantidad_true(errores),
                                    product_id = product_id).save()
                            
                            

        
                

            
        





def creador_datos(request):
        users = models.User.objects.all()
        lista = [True,False]
        for user in users:
            # se sube un dato por hora
            for d in range(1, 30):
                for h in range(0, 24):
                    models.Datos_hora(user = user,
                                    voltaje_hora_red = random.randint(170, 240),
                                    consumo_hora_red = random.randint(0, 4000),
                                    consumo_hora_solar = random.randint(0, 340),
                                    hora = h,
                                    dia = d,
                                    mes = 8,
                                    año = 2023,
                                    solar_ahora = random.choice(lista),
                                    panel_potencia = random.randint(0, 340),
                                    cargando = random.choice(lista),
                                    voltaje_bateria = random.randint(10, 15),
                                    errores = random.choice(lista),
                                    product_id = 'nashe23').save()

