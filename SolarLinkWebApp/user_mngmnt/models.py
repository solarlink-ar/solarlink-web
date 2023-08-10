from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models

# vinculo usuario-producto
class User_data(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

# datos del micro por hora
class Datos_hora(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    voltaje_hora_solar = models.FloatField(default=None)
    voltaje_hora_red = models.FloatField(default=None)
    consumo_hora_solar = models.FloatField(default=None)
    consumo_hora_red = models.FloatField(default=None)

    dia = models.IntegerField(default=None)
    mes = models.IntegerField(default=None)
    hora = models.IntegerField(default=None)

    solar_ahora = models.IntegerField(default=None)
    cargando = models.BooleanField(default=None)
    voltaje_bateria = models.IntegerField(default=None)

    errores = models.BooleanField(default=None)

    product_id = models.CharField(max_length=50)

# datos guardados por dia
class Datos_dias(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    voltaje_maximo_dia_red = models.FloatField(default=None)
    voltaje_maximo_dia_red = models.FloatField(default=None)

    consumo_dia_red = models.FloatField(default=None)
    consumo_dia_solar = models.FloatField(default=None)
    

# lista de productos activos
class Productos (models.Model):
    product_id = models.CharField(max_length=50, primary_key=True)
    conexion = models.GenericIPAddressField(max_length=12)

# mensajes de emergencia
class Emergencia(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    voltaje = models.FloatField(default=None)
    consumo = models.FloatField(default=None)

    dia = models.IntegerField(default=None)
    mes = models.IntegerField(default=None)
    hora = models.IntegerField(default=None)

    voltaje_bajo = models.BooleanField()
    voltaje_alto = models.BooleanField()
    red = models.BooleanField()

    corriente = models.BooleanField()