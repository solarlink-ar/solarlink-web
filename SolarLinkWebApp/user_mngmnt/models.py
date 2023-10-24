from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
import datetime


class isOnline(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=None)

# datos del micro por hora
class DatosHora(models.Model):
    # usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    # promedio del voltaje en la hora proveniente de la red
    voltaje_hora_red = models.FloatField(default=None)
    # consumo total en la hora de origen solar
    consumo_hora_solar = models.FloatField(default=None)
    # consumo total en la hora proveniente de la red
    consumo_hora_red = models.FloatField(default=None)
    # consumo linea 1
    consumo_l1 = models.FloatField(default=None)
    # consumo linea 2
    consumo_l2 = models.FloatField(default=None)


    hora = models.IntegerField(default=None)
    dia = models.IntegerField(default=None)
    mes = models.IntegerField(default=None)
    año = models.IntegerField(default=None)

    # booleano que indica si las lineas estan alimentadas ahora por el sistema solar
    solar_ahora = models.BooleanField(default=None)
    # potencia entregada por el panel en esa hora
    panel_potencia = models.IntegerField(default=None)
    # booleano que indica si la bateria esta cargando ahora
    cargando = models.BooleanField(default=None)
    # voltaje de la bateria actual, con esto se puede sacar el porcentaje de la bateria
    voltaje_bateria = models.IntegerField(default=None)

    # booleano que indica que en esta hora hubo errores
    errores = models.BooleanField(default=None)

    # id de producto
    product_id = models.CharField(max_length=50)

    class Meta:
        ordering = ["user", "año", "mes", "dia", "hora"]

# datos guardados por dia
class DatosDias(models.Model):
    # usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    # voltaje maximo del dia en la red
    voltaje_maximo_dia_red = models.FloatField(default=None)
    # voltaje minimo del dia en la red
    voltaje_minimo_dia_red = models.FloatField(default=None)

    # consumo total del dia de la red
    consumo_dia_red = models.FloatField(default=None)
    # consumo total del dia de origen solar
    consumo_dia_solar = models.FloatField(default=None)

    dia = models.IntegerField(default=None)
    mes = models.IntegerField(default=None)
    año = models.IntegerField(default=None)

    # horas que el panel estuvo entregando potencia
    horas_potencia_panel = models.IntegerField(default=None, null = True)
    # potencia entregada en el dia por el panel
    potencia_dia_panel = models.IntegerField(default=None, null = True)
    # horas que estuvo la bateria cargando
    horas_de_carga = models.IntegerField(default=None, null = True)
    # voltajes de la bateria en formato json-strings
    voltajes_bateria = models.CharField(max_length=400, default=None, null = True)    

    # si hubo errores en el dia
    errores = models.IntegerField(default=None, null = True)
    # product id
    product_id = models.CharField(max_length=50, default=None, null=True)

    class Meta:
        ordering = ["user", "año", "mes", "dia"]


# lista de productos activos
class Productos(models.Model):
    product_id = models.CharField(max_length=50, primary_key=True)
    conexion = models.GenericIPAddressField(max_length=12)

# mensajes de emergencia
class Emergencia(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    voltaje = models.FloatField(default=None)
    consumo = models.FloatField(default=None)

    dia = models.IntegerField(default=None)
    mes = models.IntegerField(default=None)
    hora = models.IntegerField(default=None)

    voltaje_bajo = models.BooleanField()
    voltaje_alto = models.BooleanField()
    red = models.BooleanField()

    corriente = models.BooleanField()

class TiempoReal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    voltaje = models.FloatField(default=None)

    # consumo linea 1
    consumo_l1 = models.FloatField(default=None)
    # consumo linea 2
    consumo_l2 = models.FloatField(default=None)

    # si se está usando energía solar en alguna linea
    solar = models.BooleanField(default=None)
    # si la batería está cargando
    cargando = models.BooleanField(default=None, null = True)
    # voltaje de la batería == porcentaje de carga
    voltaje_bateria = models.IntegerField(default=None, null=True)

    errores = models.BooleanField(default=None, null = True)


class UsersTokens(models.Model):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    # token de confirmación de registro
    signup_token = models.CharField(max_length= 300, default=None, null=True)
    # token de reseteo de contraseña
    password_reset_token = models.CharField(max_length=300, default=None, null = True)
    # hora de pedido
    time = models.DateTimeField(default=datetime.datetime.now, null = True)