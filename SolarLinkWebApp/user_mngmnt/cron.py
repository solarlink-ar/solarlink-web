
from django.core.mail import EmailMessage
from django.utils import timezone
from . import models
import requests
import datetime
import json


# funcion que calcula cantidad de trues en una lista de booleanos
def calculador_cantidad_true(lista:list):
    index = 0
    for i in lista:
        if i:
            index += 1
    return index

def ordenador():
    # usuarios
    users = models.User.objects.all()
    
    # para cada usuario
    for user in users:
        # datos del usuario
        user_data = models.DatosHora.objects.filter(user=user)

        # mientras existan datos
        while user_data:
            # variables temporales
            voltaje_dia_red = []
            consumo_dia_red = 0
            consumo_dia_solar = 0
            solar_por_hora = []
            potencia_dia_panel = 0
            horas_de_carga = []
            voltajes_bateria = []
            errores = []

            # referencia para dia, mes
            referencia = user_data[0]
            #datos del dia buscado
            dia_data = user_data.filter(dia=referencia.dia, mes=referencia.mes, año=referencia.año)

            # para cada dato del dia
            for data in dia_data:
                # acumulo en valores sumario diario
                voltaje_dia_red.append(data.voltaje_hora_red)
                consumo_dia_solar += data.consumo_hora_solar
                consumo_dia_red += data.consumo_hora_red

                solar_por_hora.append(data.solar_ahora)
                potencia_dia_panel += data.panel_potencia
                horas_de_carga.append(data.cargando)
                voltajes_bateria.append(data.voltaje_bateria)

                errores.append(data.errores)
                product_id = data.product_id

                # borro el dato
                data.delete()
            
            # creo dato dia
            models.DatosDias(user = user,
                            voltaje_maximo_dia_red = max(voltaje_dia_red),
                            voltaje_minimo_dia_red = min(voltaje_dia_red),
                            consumo_dia_solar = consumo_dia_solar,
                            consumo_dia_red = consumo_dia_red,

                            dia = referencia.dia,
                            mes = referencia.mes,
                            año = referencia.año,

                            horas_potencia_panel = calculador_cantidad_true(solar_por_hora),
                            potencia_dia_panel = potencia_dia_panel,
                            horas_de_carga = calculador_cantidad_true(horas_de_carga),
                            voltajes_bateria = json.dumps(voltajes_bateria),
                            errores = calculador_cantidad_true(errores),
                            product_id = data.product_id).save()
            
            # sobreescribo user_data, para quitar los datos que acabo de borrar
            user_data = models.DatosHora.objects.filter(user=user)


def token_clean():
    requests.get("http://127.0.0.1:8000/")
    # todos los tokens activos
    data = models.UsersTokens.objects.all()
    # hora en timezone
    actual = timezone.now()
    # para cada dato
    for d in data:
        # si el tiempo entre que el token fue creado y el actual es mayor a 2hs
        if (actual - d.time) > datetime.timedelta(hours=1):
            # borro el token
            d.delete()


#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################


def ordenador_viejo():
    # lista de objetos de usuario
    users = models.User.objects.all()

    # para cada usuario
    for user in users:
        voltaje_dia_red = []
        consumo_dia_red = 0
        consumo_dia_solar = 0
        horas = []
        dias = []
        meses = []
        años = []
        solar_por_hora = []
        potencia_dia_panel = 0
        horas_de_carga = []
        voltajes_bateria = []
        errores = []
        
        # todos los datos de cierto usuario
        user_data = models.DatosHora.objects.filter(user=user)


        # entre los datos del usuario
        for data in user_data:
            # hago una lista con todos los años que tenga datos
            if not data.año in años:
                años.append(data.año)
            
        # para cada año
        for año in años:
            # filtro los datos de todo ese año
            año_data = user_data.filter(año = año)

            # entre todos los datos del año
            for data in año_data:
                # hago una lista con todos los meses que tengan datos
                if not data.mes in meses:
                    meses.append(data.mes)
            
            
            # para cada mes
            for mes in meses:
                # filtro los datos del mes
                mes_data = año_data.filter(mes=mes)

                # entre todos los datos del mes
                for data in mes_data:
                    # hago una lista con todos los dias que tengan datos
                    if not data.dia in dias:
                        dias.append(data.dia)
                    
                    # para cada dia
                for dia in dias:
                    # filtro los datos del dia
                    dia_data = mes_data.filter(dia = dia)
                    
                    # entre todos los datos del dia
                    for data in dia_data:
                        # hago una lista con todas las horas que tengan datos
                        if not data.hora in dia_data:
                            horas.append(data.hora)
                    
                    # para cada hora
                    for hora in horas:
                        hora_data = dia_data.filter(hora=hora)

                        for data in hora_data:
                            # guardado de datos
                            voltaje_dia_red.append(data.voltaje_hora_red)
                            consumo_dia_solar += data.consumo_hora_solar
                            consumo_dia_red += data.consumo_hora_red

                            solar_por_hora.append(data.solar_ahora)
                            potencia_dia_panel += data.panel_potencia
                            horas_de_carga.append(data.cargando)
                            voltajes_bateria.append(data.voltaje_bateria)

                            errores.append(data.errores)
                            product_id = data.product_id


                    
                            
                    # creo dato dia
                    models.DatosDias(user = user,
                                    voltaje_maximo_dia_red = max(voltaje_dia_red),
                                    voltaje_minimo_dia_red = min(voltaje_dia_red),
                                    consumo_dia_solar = consumo_dia_solar,
                                    consumo_dia_red = consumo_dia_red,

                                    dia = dia,
                                    mes = mes,
                                    año = año,

                                    horas_potencia_panel = calculador_cantidad_true(solar_por_hora),
                                    potencia_dia_panel = potencia_dia_panel,
                                    horas_de_carga = calculador_cantidad_true(horas_de_carga),
                                    voltajes_bateria = json.dumps(voltajes_bateria),
                                    errores = calculador_cantidad_true(errores),
                                    product_id = product_id).save()
                    # limpio
                    voltaje_dia_red = []
                    consumo_dia_red = 0
                    consumo_dia_solar = 0
                    solar_por_hora = []
                    potencia_dia_panel = 0
                    horas_de_carga = []
                    voltajes_bateria = []
                    errores = []
                    horas = []
                
                dias = []
            meses = []
        años = []
        # borro datos hora
        user_data.delete()
    requests.get("http://127.0.0.1:8000/")
