#-------------------------------------------------------------------------------
# Name:        Detector de alertas
# Purpose:     Devuelve un array con los equipos que han generado alertas
#
# Author:      Tomohiko Inafuko Miyashiro
#
# Created:     20/02/2020
#-------------------------------------------------------------------------------
# Import para mostrar cuadros de diálogo
import pymsgbox as pm
from datetime import datetime

def check_fails(cm):
    """
    Analiza el historial de mantemiento y detecta alertas bajo condiciones
    preestablecidas.

    Parámetros
    ----------
    cm : Objeto tipo cursor
        Tiene información de la tabla del historial de mantenimiento

    Retorna
    -------
    alert_id : array de arrays
        Cada array del array contiene:
            Id del equipo que generó alerta
            Número total de fallas
            Tiempo entre la última y primera falla (en días)
            Fecha de la última falla
            Número de fallas de fuente
            Número de fallas de RAM
            Número de fallas de HDD
            Número de fallas de Procesador
            Número de fallas de Tarjeta de Video
            Número de fallas de Placa
            Número de fallas de otros

    """
    alertas = []
    items = []
    try:
        for row in cm: # Se iteran todas las filas del Historial de Mantenimiento
            # Se inician todos los contadores del número de fallas
            counter = 0
            counter_fuente = 0
            counter_RAM = 0
            counter_HDD = 0
            counter_procesador = 0
            counter_tarjetadevideo = 0
            counter_placa = 0
            counter_otros = 0

            incidencias = [row.Fuente, row.RAM, row.HDD, row.Procesador, row.TarjetaDeVideo, row.Placa, row.Otros]
            counters = [counter_fuente, counter_RAM, counter_HDD, counter_procesador, counter_tarjetadevideo, counter_placa, counter_otros]

            for inc in incidencias: # Se hace el conteo de fallas totales por incididencia
                if inc == True:
                    counter = counter + 1
            for i in range(0, 7): # Se hace el conteo de fallas por tipo de falla por incidencia
                if incidencias[i] == True:
                    counters[i] = counters[i] + 1
            items.append([row.Id, counter, row.Fecha, counters[0], counters[1], counters[2], counters[3], counters[4], counters[5], counters[6]])

        # Se ordena por número de Id y fecha
        items.sort(key=lambda x: (x[0], x[2]))

        num_fallas_por_id = []
        Id_previa = 0

        counter = 0
        counter_fuente = 0
        counter_RAM = 0
        counter_HDD = 0
        counter_procesador = 0
        counter_tarjetadevideo = 0
        counter_placa = 0
        counter_otros = 0

        incidencias = [row.Fuente, row.RAM, row.HDD, row.Procesador, row.TarjetaDeVideo, row.Placa, row.Otros]
        counters = [counter_fuente, counter_RAM, counter_HDD, counter_procesador, counter_tarjetadevideo, counter_placa, counter_otros]
        i = -1

        for item in items:
            if item[0] == Id_previa: # item[0] es la Id actual
                counter = counter + item[1] # Si es igual que la anterior se aumenta el número de fallas totales por Id
                for j in range(0, 7):
                    counters[j] = counters[j] + item[j + 3] # Luego se aumenta el número de cada falla específica
                tiempo_entre_fallas = item[2] - tiempo_inicial # item[2] contiene la fecha, con esto se calcula el tiempo entre fallas (en días)
                num_fallas_por_id[i] = ([item[0], counter, tiempo_entre_fallas.days, item[2], counters[0], counters[1], counters[2], counters[3], counters[4], counters[5], counters[6]])
            else:
                counter = item[1] # Cuando no es igual, se empezará a hacer el conteo de fallas para la siguiente Id
                for j in range(0, 7):
                    counters[j] = item[j + 3]
                i = i + 1
                tiempo_inicial = item[2] # Como está ordenado por fecha aquí se guarda la fecha de la primera falla
                num_fallas_por_id.append([item[0], counter, 0, item[2], counters[0], counters[1], counters[2], counters[3], counters[4], counters[5], counters[6]])
            Id_previa = item[0]

        alert_id = []
        alert_id_item = []

        for item in num_fallas_por_id:
            if item[1] >= 5: # item[1] es el número total de fallas, si son más de 5 genera la alerta
                for j in range(0, 11):
                    alert_id_item.append(item[j]) # Se adjuntan todos los datos del Id que ha generado alerta
                alert_id.append(alert_id_item) # El array recién creado se adjunta a alert_id
                alert_id_item = [] # Se vacía el array para la siguiente Id
            elif item[1] < 5 and item[1] >= 3:
                if (3 * item[1] - 3) >= item[2] / 30: # Para decidir si genera alerta sigue una función lineal "3 * #fallas - 3 >= tiempo entre fallas (en días)"
                    for j in range(0, 11):
                        alert_id_item.append(item[j])
                    alert_id.append(alert_id_item)
                    alert_id_item = []
        return alert_id
    except:
        pm.alert("Por favor informe de este error al creador del programa.", title="Error al procesar la base de datos")
