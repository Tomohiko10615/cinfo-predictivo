#-------------------------------------------------------------------------------
# Name:        Predictivo de fallas
# Purpose:     Analiza la base de datos del historial de mantemiento del Cinfo
#              y crea un reporte de alertas.
#
# Author:      Tomohiko Inafuko Miyashiro
#
# Created:     13/02/2020
#-------------------------------------------------------------------------------
# Import de pyodbc para conectar con la base de datos
import pyodbc
# Import de la función checkfails que devuelve las Id de los equipos que cumplen
# las condiciones de alerta
import checkfails as cf
# Import de la función que genera el reporte
import generatereport as gr

# Conectando con la base de datos, se necesita la ubicación del archivo *.accdb
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=C:\Users\SOPORTE\Desktop\INVENTARIO\INVENTARIOCINFO.accdb;'
    )
cnxn = pyodbc.connect(conn_str)

# Se crea el cursor "cursor" que almacena los datos de la tabla con los registros del inventario
cursor = cnxn.cursor()
cursor.execute("select Id, Ubicación, Código, SBN, MarcaModelo, Descripción, Alerta, UltimaFalla from TablaActivos")

# Se crea el cursor "cursor_mantemiento" que almacena los datos de la tabla del historial de mantenimiento
cursor_mantemiento = cnxn.cursor()
cursor_mantemiento.execute("select Id, Fuente, RAM, HDD, Procesador, TarjetaDeVideo, Placa, Otros, Solucionado, Fecha from HistorialMantenimiento")

# Se ejecutará la función check_fails con el objeto "cursor_mantenimiento"
# como argumento, que devolverá un array con los Id que generaron alerta así
# como el número total de fallos, tiempo entre el último y el primer fallo y la
# número de cada fallo
alert_id = cf.check_fails(cursor_mantemiento)

# Se ejecutará la función generate_report para genera el reporte
gr.generate_report(cursor, alert_id, cnxn)
