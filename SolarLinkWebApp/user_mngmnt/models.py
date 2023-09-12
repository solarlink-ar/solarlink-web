from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models


# datos del micro por hora
class Datos_hora(models.Model):
    # usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    # promedio del voltaje en la hora proveniente de la red
    voltaje_hora_red = models.FloatField(default=None)
    # consumo total en la hora de origen solar
    consumo_hora_solar = models.FloatField(default=None)
    # consumo total en la hora proveniente de la red
    consumo_hora_red = models.FloatField(default=None)

    hora = models.IntegerField(default=None)
    dia = models.IntegerField(default=None)
    mes = models.IntegerField(default=None)
    año = models.IntegerField(default=None)

    # booleano que indica si la red esta alimentada ahora por el sistema solar
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

# datos guardados por dia
class Datos_dias(models.Model):
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
    horas_potencia_panel = models.IntegerField(default=None)
    # potencia entregada en el dia por el panel
    potencia_dia_panel = models.IntegerField(default=None)
    # horas que estuvo la bateria cargando
    horas_de_carga = models.IntegerField(default=None)
    # voltajes de la bateria en formato json-strings
    voltajes_bateria = models.CharField(max_length=400, default=None)    

    # si hubo errores en el dia
    errores = models.IntegerField(default=None)
    # product id
    product_id = models.CharField(max_length=50, default=None)

    

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

class Tiempo_real(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    voltaje = models.FloatField(default=None)
    consumo = models.FloatField(default=None)

    solar = models.BooleanField(default=None)
    cargando = models.BooleanField(default=None)
    voltaje_bateria = models.IntegerField(default=None) # porcentaje bateria

    errores = models.BooleanField(default=None)


class Users_tokens(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    signup_token = models.CharField(max_length= 300, default=None, null=True)
    password_reset_token = models.CharField(max_length=300, default=None, null = True)
    time = models.DateTimeField(default=None, null = True)