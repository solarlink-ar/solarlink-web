from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import datetime

# Create your views here.

def index(response):
    return HttpResponse('Hola xd')