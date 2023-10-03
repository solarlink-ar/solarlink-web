from django.core.mail import EmailMessage
from celery import shared_task
from . import models
import json
import random

@shared_task()
def no_reply_sender(**kwargs):
    email = EmailMessage( kwargs["asunto"],
                          kwargs["mensaje"],
                          to=[kwargs["mail_to"]])
    email.send()

@shared_task()
def creador_datos():
    users = models.User.objects.all()
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