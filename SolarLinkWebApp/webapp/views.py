from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
import datetime

data = 0

def HelloWorld(request):
    return HttpResponse('Hello World!')

def index(request):
    return render(request, "index.html")

def que_somos(request):
    return render(request, "que_somos.html")

def contacto(request):
    nombre = 15
    return render(request, "contacto.html")

def galeria(request):
    return render(request, "galeria.html")
