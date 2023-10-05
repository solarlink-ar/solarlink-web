from django.core.mail import EmailMessage
from django.core import mail
from celery import shared_task
from . import models
import json
import random

# funcion que calcula cantidad de trues en una lista de booleanos
def calculador_cantidad_true(lista:list):
    index = 0
    for i in lista:
        if i:
            index += 1
    return index


@shared_task()
def no_reply_sender(**kwargs):
    mail.send_mail([kwargs["mail_to"]], subject=kwargs["asunto"], html_message=kwargs["mensaje"])

@shared_task()
def creador_datos():
    users = models.User.objects.all()
    '''
    models.DatosHora(user = users[2],
                voltaje_hora_red = random.randint(170, 240),
                consumo_hora_red = random.randint(0, 4000),
                consumo_hora_solar = random.randint(0, 340),
                hora = 7,
                dia = 10,
                mes = 8,
                año = 2023,
                solar_ahora = True,
                panel_potencia = random.randint(0, 340),
                cargando = True,
                voltaje_bateria = random.randint(10, 15),
                errores = True,
                product_id = 'nashe23').save()
    models.DatosHora(user = users[2],
                voltaje_hora_red = random.randint(170, 240),
                consumo_hora_red = random.randint(0, 4000),
                consumo_hora_solar = random.randint(0, 340),
                hora = 6,
                dia = 11,
                mes = 8,
                año = 2023,
                solar_ahora = True,
                panel_potencia = random.randint(0, 340),
                cargando = True,
                voltaje_bateria = random.randint(10, 15),
                errores = True,
                product_id = 'nashe23').save()
    '''
    lista = [True,False]
    for user in users:
        # se sube un dato por hora
        for d in range(1, 31):
            for h in range(0, 24):
                models.DatosHora(user = user,
                                voltaje_hora_red = random.randint(170, 240),
                                consumo_hora_red = random.randint(0, 4000),
                                consumo_hora_solar = random.randint(0, 340),
                                hora = h,
                                dia = d,
                                mes = 8,
                                año = 2023,
                                solar_ahora = random.choice(lista),
                                panel_potencia = random.randint(0, 340),
                                cargando = random.choice(lista),
                                voltaje_bateria = random.randint(10, 15),
                                errores = random.choice(lista),
                                product_id = 'nashe23').save()

@shared_task()
def ordenador():
    users = models.User.objects.all()
    
    for user in users:
        voltaje_dia_red = []
        consumo_dia_red = 0
        consumo_dia_solar = 0
        solar_por_hora = []
        potencia_dia_panel = 0
        horas_de_carga = []
        voltajes_bateria = []
        errores = []

        user_data = models.DatosHora.objects.filter(user=user)

        ultimo_dia =  None
        ultimo_mes = None
        ultimo_año = None

        for data in user_data:
            if data.dia != ultimo_dia:
                # creo dato dia
                models.DatosDias(user = user,
                                voltaje_maximo_dia_red = max(voltaje_dia_red),
                                voltaje_minimo_dia_red = min(voltaje_dia_red),
                                consumo_dia_solar = consumo_dia_solar,
                                consumo_dia_red = consumo_dia_red,

                                dia = ultimo_dia,
                                mes = ultimo_mes,
                                año = ultimo_año,

                                horas_potencia_panel = calculador_cantidad_true(solar_por_hora),
                                potencia_dia_panel = potencia_dia_panel,
                                horas_de_carga = calculador_cantidad_true(horas_de_carga),
                                voltajes_bateria = json.dumps(voltajes_bateria),
                                errores = calculador_cantidad_true(errores),
                                product_id = data.product_id).save()
                # limpio
                voltaje_dia_red = []
                consumo_dia_red = 0
                consumo_dia_solar = 0
                solar_por_hora = []
                potencia_dia_panel = 0
                horas_de_carga = []
                voltajes_bateria = []
                errores = []
                
            else:
                voltaje_dia_red.append(data.voltaje_hora_red)
                consumo_dia_solar += data.consumo_hora_solar
                consumo_dia_red += data.consumo_hora_red

                solar_por_hora.append(data.solar_ahora)
                potencia_dia_panel += data.panel_potencia
                horas_de_carga.append(data.cargando)
                voltajes_bateria.append(data.voltaje_bateria)

                errores.append(data.errores)

                #product_id = data.product_id
                ultimo_dia = data.dia
                ultimo_mes = data.mes
                ultimo_año = data.año

        user_data.delete()