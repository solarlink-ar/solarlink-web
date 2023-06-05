from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
import datetime


# Create your views here.

def register(response):
    user = User.objects.create_user(email='jose24@gmail.com', password='1234', username='juan23')
    return HttpResponse("Done!")

def user_data(response):
    user = User.objects.get(email='jose24@gmail.com')
    return HttpResponse(user.get_username())

