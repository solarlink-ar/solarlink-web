from django.core.mail import EmailMessage
from django.core import mail
from celery import shared_task
from . import models
import json
import time
import random

# funcion que calcula cantidad de trues en una lista de booleanos
def calculador_cantidad_true(lista:list):
    index = 0
    for i in lista:
        if i:
            index += 1
    return index


@shared_task()
def no_reply_sender(email, subject, html_message):
    mail = EmailMessage(subject, html_message, to=[email])
    mail.content_subtype = 'html' # aclaracion de tipo de contenido
    mail.send()

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



    


