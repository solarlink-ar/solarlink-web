from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models


class User_link(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=50)

class Datos_hora(models.Model):
    voltaje_hora = models.FloatField(default=None)
    consumo_hora = models.FloatField(default=None)
    dia = models.IntegerField(default=None)
    mes = models.IntegerField(default=None)
    hora = models.IntegerField(default=None)
    product_id = models.CharField(max_length=50)


