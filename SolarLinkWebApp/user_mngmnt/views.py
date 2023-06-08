from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import User
import datetime


def registered(request):
    if request.method == "POST":
        next_url = request.GET.get('next')
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password_conf =request.POST['password_conf']

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


def register(request):
    return render(request, 'register.html')

