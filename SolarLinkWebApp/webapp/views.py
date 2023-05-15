from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
import datetime

def HelloWorld(request):
    return HttpResponse('Hello World!')

def index(request):
    return render(request, "index.html")

def que_somos(request):
    return render(request, "que_somos.html")

def contacto(request):
    return render(request, "contacto.html")

def galeria(request):
    return render(request, "galeria.html")

def datos(request):
    def datos(request):
    global data
    if request.body.decode("utf-8"):
        data = request.body.decode("utf-8")
    return HttpResponse(f'{data}')