from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render
from django.template import loader
from django.contrib import auth
from . import models
import datetime


def register(request):
    if request.method == "POST":
        next_url = request.GET.get('next')
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password_conf = request.POST['password_conf']

        if password_conf == password:
            try:
                User.objects.get(username = username)
                error = "El usuario ya está registrado"
                return render(request, 'register.html', {'error': error})
            
            except User.DoesNotExist:
                User.objects.create_user(email=email, username=username, password=password)
                error = 'Registrado!'
                if next_url:
                    return HttpResponseRedirect(next_url)
                else:
                    return render(request, 'register.html', {'error': error})
        else:
            error = 'Las contraseñas no concuerdan!'
            return render(request, 'register.html', {'error': error})
    else:
        return render(request, 'register.html')

def product(request):
    if request.method == "POST":
        next_url = request.GET.get('next')
        username = request.POST['username']
        password = request.POST['password']
        product_id = request.POST['product_id']

        user = auth.authenticate(username=request.POST['username'],password = request.POST['password'])
        if user:
            auth.login(request, user)
            models.User_link(user=user, product_id = product_id).save()

            return HttpResponse('nashe')
        else:
            error = 'El usuario no existe'
            return render(request, 'product.html', {'error': error})
    else:
        return render(request, 'product.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=request.POST['username'],password = request.POST['password'])
        
        if user:
            auth.login(request, user)
            email = user.email
            product_id = user.user_link.product_id

            data = models.Datos.objects.filter(product_id = product_id)
            print(data)
            
            for i in data:
                print(i.consumo_mins, i.voltaje_mins)

        
            return HttpResponse(f'{email}, {data}')

        else:
            error = 'El usuario no existe'
            return render(request, 'registration/login.html', {'error': error})
    else:
        return render(request, "login.html")


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

