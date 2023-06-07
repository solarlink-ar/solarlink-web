from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
import datetime


def registered(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        User.objects.create_user(email=email, username=username, password=password)

    return HttpResponse('Estás registrado!')

def register(request):
    return render(request, 'register.html')

