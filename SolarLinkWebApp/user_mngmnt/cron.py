from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib import auth
from .forms import RegisterForm
from . import models
import datetime
import requests

def sorter():
    '''
    models.User.objects()
    for i in range(0,23):
        models.User_link(user = user, product_id = product_id).save()

    models.Datos_hora.objects.filter()
    '''
    pass