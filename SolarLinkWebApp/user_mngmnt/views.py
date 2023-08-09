from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib import auth
from . import models
import datetime

# registro
def register(request):
    #si no está logueado
    if request.user.username == '':
        # si se rellena un login
        if request.method == "POST":
            # obtengo datos
            email = request.POST['email']
            username = request.POST['username']
            password = request.POST['password']
            password_conf = request.POST['password_conf']

            # reviso si las contraseñas coinciden
            if password_conf == password:

                # intento buscar el usuario
                try:
                    User.objects.get(username = username)
                    error = "El usuario ya está registrado"
                    return render(request, 'register.html', {'error': error})
                
                # si no existe, lo registro, lo logueo y voy a product
                except User.DoesNotExist:
                    User.objects.create_user(email=email, username=username, password=password)

                    user = auth.authenticate(username=username, password=password)
                    auth.login(request, user)

                    return redirect('product')
            
            # si las contraseñas no coinciden
            else:
                error = 'Las contraseñas no concuerdan!'
                return render(request, 'register.html', {'error': error})
            
        # si entro a la web con un GET
        else:
            return render(request, 'register.html')
    #si está logueado
    else:
        return redirect("index")

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
                return redirect('product')

            # si no existe, doy error
            else:
                error = 'El usuario no existe'
                return render(request, 'login.html', {'error': error})
        else:
            return render(request, "login.html")
    
    # si está logueado
    else:
        return redirect('index')

#logout
@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')

# Registro de product_id
@login_required
def product(request):

    # si relleno el formulario
    if request.method == "POST":

        # obtengo product_id del form        
        product_id = request.POST['product_id']
        
        # lo guardo en la db
        models.User_link(user = request.user, product_id = product_id).save()

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




'''
email = user.email
product_id = user.user_link.product_id

data = models.Datos.objects.filter(product_id = product_id)
print(data)

for i in data:
    print(i.consumo_mins, i.voltaje_mins)
'''