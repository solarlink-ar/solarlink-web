from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib import auth
from . import models
from .forms import RegisterForm
import datetime

# registro
def register(request):
    #si no está logueado
    if request.user.username == '':
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
                        return render(request, 'register.html', {'form': form,'error': error})
                    
                    # si no existe, lo registro, lo logueo y voy a product
                    else:

                        User.objects.create_user(email=email, username=username, password=password, first_name= first_name, last_name = last_name)
                        user = auth.authenticate(username=username, password = password)
                        auth.login(request, user)

                    return redirect('index')
        
                # si las contraseñas no coinciden
                else:
                    error = 'Las contraseñas no concuerdan!'
                    return render(request, 'register.html', {'form': form, 'error': error})
            
        # si entro a la web con un GET
        else:
            # armo template
            form = RegisterForm()
            return render(request, 'register.html', {'form': form})
    #si está logueado
    else:
        return redirect("index")

# login
def login(request):
    # si no está logueado
    if request.user.username == '':
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
                return render(request, 'login.html', {'error': error})
        else:
            return render(request, "login.html")
    
    # si está logueado
    else:
        return redirect('index')

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
    return render(request, "userpage.html", {"username": username})

def data(request):
    # lista de objetos de usuario
    users = models.User.objects.all()

    # para cada usuario
    for user in users:
        # se sube un dato por hora
        for i in range(0, 24):
            models.Datos_hora(user = user,
                              voltaje_hora_red = 220,
                              consumo_hora_red = 500,
                              consumo_hora_solar = 300,
                              hora = i,
                              dia = 22,
                              mes = 8,
                              año = 2023,
                              solar_ahora = True,
                              panel_potencia = 340,
                              cargando = True,
                              voltaje_bateria = 12.5,
                              errores = False,
                              product_id = 'nashe23').save()
        
        # todos los datos de cierto usuario
        data = models.Datos_hora.objects.filter(user = users[0])
        # dentro del primer dato, su hora
        print(data[0].hora)
    return HttpResponse("nashe")

'''
def answer(request):
    print(request.GET.dict())
    return JsonResponse({"god": "god"})
'''
'''
# Registro de product_id
@login_required
def product(request):

    # si relleno el formulario
    if request.method == "POST":

        # obtengo product_id del form        
        product_id = request.POST['product_id']
        
        # lo guardo en la db
        models.User_link(user = request.user, product_id = product_id).save()

    #si hago un GET
    else:
        return render(request, 'product.html')

def data(request):
    if request.method == "POST":
        product_id = request.POST['product_id']
        consumo = request.POST['consumo']
        voltaje = request.POST['voltaje']
        tiempo = datetime.datetime.now()

        models.Datos.objects.create(product_id = product_id, consumo_mins=consumo, voltaje_mins=voltaje, tiempo = tiempo)
        return HttpResponse("Hecho!")
    else:
        return render(request, "data.html")





email = user.email
product_id = user.user_link.product_id

data = models.Datos.objects.filter(product_id = product_id)
print(data)

for i in data:
    print(i.consumo_mins, i.voltaje_mins)
'''