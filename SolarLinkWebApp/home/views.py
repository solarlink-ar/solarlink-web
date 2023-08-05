from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import datetime


def index(request):
    return render(request, "index.html")

def que_somos(request):
    return render(request, "que_somos.html")

def contacto(request):
    return render(request, "contacto.html")

def galeria(request):
    return render(request, "galeria.html")