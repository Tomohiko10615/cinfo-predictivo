#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      SOPORTE
#
# Created:     25/02/2020
# Copyright:   (c) SOPORTE 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# Import para mostrar cuadros de diálogo
import pymsgbox as pm
# Import de módulos necesarios para enviar email
import smtplib, ssl

def generate_report(cursor, alert_id, cnxn):
    informe_alerta = [] # Almacenará los datos de las alertas nuevas
    informe_alerta_recurrente = [] # Almacenará los datos de as alertas recurrentes
    informe_alerta_pasada = [] # Almacenará los datos de las alertas pasadas
    string_fallos = "" # String que documenta el número de fallos por tipo de fallo
    tipos_de_fallo = ["Fuente", "RAM", "HDD", "Procesador", "Tarjeta de Video", "Placa", "Otros"] # Array con los tipos de fallos, se usará para crear "string_fallos"
    try:
        for row in cursor: # Itera cada fila de "cursor"
            for i in alert_id:
                if row.Id == i[0]: # i[0] es el Id que generó alerta, se buscará el Id en el inventario que coincide
                    if  row.Alerta == False and row.UltimaFalla == None: # Cuando no generó una falla anteriormente row.Alerta es 'False' y row.UltimaFalla está vacío, en este caso es una alerta nueva
                        for j in range(4, 11): # Iteramos desde 4, porque desde i[4] hasta i[10] se almacenan los números de fallos por tipo
                            if i[j] > 0: # Solo se agregará al string cuando exista al menos una falla de determinado tipo, no se generará "Ha tenido 0 fallas de 'x-tipo'"
                                string_fallos = string_fallos + "\n\tHa tenido " + str(i[j]) + " fallos(s) de " + tipos_de_fallo[j - 4] + "\n" # El índice del array "tipos_de_fallo" es "j - 4" porque debe comenzar desde 0
                        informe_alerta.append([row.Ubicación, row.Código, row.SBN, row.MarcaModelo, row.Descripción, string_fallos]) # Para generar la alerta se extraen los datos necesarios de la base de datos del inventario, además se almacena el "string_fallo" recién creado
                        string_fallos = "" # Debe esta vacío para almacenar el número de fallos por tipo de fallo del siguiente Id
                    elif row.UltimaFalla != i[3]: # i[3] almacena la fecha en que falló por última vez, si es diferente a la que está registrada quiere decir que es un equipo que generó alerta en el pasado y ha vuelto a fallar
                        informe_alerta_recurrente.append([row.Ubicación, row.Código, row.SBN, row.MarcaModelo, row.Descripción]) # Se extraen los datos necesarios para generar la alerta
                    elif row.Alerta == True: # Cuando row.Alerta es 'True' significa que ya generó alerta en el pasado
                        informe_alerta_pasada.append([row.Ubicación, row.Código, row.SBN, row.MarcaModelo, row.Descripción]) # Se extraen los datos necesarios para generar la alerta

        # Textos que irán en el email
        string_informe = "" # Alertas nuevas
        string_informe_recurrente = "" # Alertas recurrentes
        string_informe_pasada = "" # Alertas pasdas

        for i in informe_alerta: # Itera los elementos para crear el texto del email
            for j in i: # "informe_alerta" es un array de arrays, itera cada elemento de i, que es un array
                if isinstance(j, str): # Cuando el elemento es un string no se necesita transformarlo a string y solo se anexa
                    string_informe = string_informe + " " + j
                elif j == None: # Cuando el campo está vacío no anexamos nada
                    pass
                else: # Cuando el elemento no es un string se transforma a string y se anexa
                    string_informe = string_informe + " " + str(j) + "\n"
            string_informe = string_informe + "\n"

        # Se generan los dos siguientes informes de manera análoga
        for i in informe_alerta_recurrente:
            for j in i:
                if isinstance(j, str):
                    string_informe_recurrente = string_informe_recurrente + " " + j
                elif j == None:
                    pass
                else:
                    string_informe_recurrente = string_informe_recurrente + " " + str(j) + "\n"
            string_informe_recurrente = string_informe_recurrente + "\n"
        for i in informe_alerta_pasada:
            for j in i:
                if isinstance(j, str):
                    string_informe_pasada = string_informe_pasada + " " + j
                elif j == None:
                    pass
                else:
                    string_informe_pasada = string_informe_pasada + " " + str(j) + "\n"
            string_informe_pasada = string_informe_pasada + "\n"

        message = ""

        # Anexamos los informes en texto sólo si existen
        if informe_alerta:
            message = message + "\n" + "Los siguientes equipos han generado alertas:\n " + "\n" + string_informe
        if informe_alerta_recurrente:
            message = message + "\n" + "Los siguientes equipos que han generado alerta en el pasado han vuelto a generar una falla: " + "\n" + string_informe_recurrente
        if informe_alerta_pasada:
            message = message + "\n" + "Los siguientes equipos han generado alertas en el pasado: " + "\n" + string_informe_pasada

        asunto = "Reporte predictivo"
        message = 'Subject: {}\n\n{}'.format(asunto, message)
        context = ssl.create_default_context()
        port = 465
        password = "isopropilico"

        try:
            # Se enviará el email con los emails especificados
            if informe_alerta or informe_alerta_recurrente: # Sólo enviamos el email si existen alertas nuevas o recurrentes, no se enviará por alertas pasdas
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    server.login("soportecinfobolsistas", password)
                    sender_email = "soportecinfobolsistas@gmail.com"
                    receiver_email = ["soportecinfobolsistas@gmail.com", "cinfo.soporte@unmsm.edu.pe"]
                    for email in receiver_email: # Enviamos a todos los email especificados en receiver_email
                        server.sendmail(sender_email, email, message)

            cursor_update = cnxn.cursor()

            for i in alert_id:
                cursor_update.execute("update TablaActivos set Alerta = ?, UltimaFalla = ? where Id = ?", True, i[3], i[0]) # Actualizamos la tabla del inventario con Alerta = True para que lo reconozca como alerta pasada y además almacenamos la fecha de su última falla

            cnxn.commit() # Ejecutamos todos los cambios en la base de datos
            pm.alert("Presione aceptar", title="El programa se ejecutó con éxito")
        except:
            pm.alert("Compruebe la conexión a internet y vuelva a ejecutar, caso contrario contacte con el creador del programa.", title="Error al enviar el email")
    except:
        pm.alert("Por favor informe de este error al creador del programa.", title="Error al general el reporte")
