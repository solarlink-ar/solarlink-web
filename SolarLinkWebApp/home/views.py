from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import datetime
from django.http import JsonResponse
import json



def index(request):
    return render(request, "home/index.html")

def que_somos(request):
    return render(request, "home/que_somos.html")

def contacto(request):
    return render(request, "home/contacto.html")

def galeria(request):
    return render(request, "home/galeria.html")
    

