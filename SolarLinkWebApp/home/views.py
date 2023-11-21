from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import datetime
from django.http import JsonResponse
import json

# vista de home
def index(request):
    return render(request, "home/index.html")
# vista de galeria
def galeria(request):
    return render(request, "home/galeria.html")
    

