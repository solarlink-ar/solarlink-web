from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models


class User_link(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=50)

class Datos(models.Model):
    voltaje_mins = models.FloatField(default=None)
    consumo_mins = models.FloatField(default=None)
    tiempo = models.TimeField(default=None)
    product_id = models.CharField(max_length=50)


