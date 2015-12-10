#!/usr/bin/env python


import struct
import socket
import time
import pickle
import sys
import datetime
import calendar

archivo_alarmas='alarmas_MSC.txt'
SEGUNDOS_ALARMA = 60
TIEMPOCRON = 300

#numero de MME sin conectividad para una sola MSC
MME_MAX_SIN_CONECTIVIDAD = 3

#creamos lista de alarmas y lista de clearalarmas

lista_alarmas_por_MME = []
lista_alarmas_temporal = []
alarmas_NAGIOS = []
hora_actual=calendar.timegm(time.gmtime())




for line in open(archivo_alarmas):

        #Guardar los datos necesarios en las variables MSC, MME, Fecha y alarma
        columna = line.split(";")
        MME_t=columna[0].split("/")
        MME=MME_t[4]

        alarma_t=columna[0].split(":")
        alarma=alarma_t[1]

        MSC_t=columna[2].split(".")
        MSC=MSC_t[0]

        hora_alarma=columna[1]
        pattern = '%Y-%m-%d_%H:%M:%S'
        epoch = int(time.mktime(time.strptime(hora_alarma, pattern)))


        #Revisamos si la alarma ha tenido lugar en los ultimos 2 minutos


        if ( epoch > hora_actual - TIEMPOCRON):                 #lo pongo < para pruebas, luego volver a poner a >
                #vamos almacenando las alarmas que lo cumplan
                if ('clearAlarm' in alarma):
                        #busca la alarma ya generada anteriormente ( ya que es el clear)
                        for sublist in lista_alarmas_por_MME:
                                if sublist[0] == MME and sublist[1] == MSC:
                                        print "alarma encontrada", sublist
                                        #calcular tiempo entre alarmas:
                                        diferencia=epoch-sublist[2]
                                        print diferencia
                                        if(diferencia < SEGUNDOS_ALARMA):
                                                print "Caida no critica de MME ",MME,"-MSC:",MSC ,"TIempos:",sublist[2],"-", epoch
                                                lista_alarmas_por_MME.remove(sublist)
                                        else:
                                                print "ALARMA 1 MME OJO"
                                                #LIMPIAMOS entrada
                                                lista_alarmas_por_MME.remove(sublist)
                                                lista_alarmas_temporal.append((MME,MSC,epoch,''))
                                        break
                else:
                        lista_alarmas_por_MME.append((MME,MSC,epoch,''))
                        print "Creacion alarma por MME", MME, MSC,epoch




#tras recorrer el archivo de alarmas completo, buscamos aquellas MSC que hayan caido en mas de un MME:

#tenemos en la variable lista_alarmas_temporal todas las alarmas que hayan estado mas de SEGUNCOS_ALARMA sin limpiar.


#SOlo hay que buscar si la misma MSC canta en mas de un MME
MSC_BASE = []

for sublist in lista_alarmas_temporal:
        if sublist[1] not in MSC_BASE:
                MSC_BASE.append(sublist[1])             #generamos la lista de MSC presentes, por si hubiera mas de una

#recorremos la lista por cada MSC:
for MSC_temp in MSC_BASE:
        cuenta_MME_truchos = 0
        MME_truchos = []
        for sublist in lista_alarmas_temporal:
                 if sublist[1] == MSC_temp:
                        if sublist[0] not in MME_truchos:
                                MME_truchos.append(sublist[0])
                                cuenta_MME_truchos += 1

                        #para cada MSC diferente, hay que soltar un evento.
                        #por si acaso lo logo a archivo tambien para que nosotros tengamos historico
                        #hay que enviar a NAGIOS la cadena de mas abajo
                        #tambien lo almaceno en una variable, con todas las alarmas:alarmas_NAGIOS()
                        #cada linea de la lista sera una alarma, y se recorre con for enviar in alarmas_NAGIOS:
                        #y en el bucle, enviar.
        if(cuenta_MME_truchos > MME_MAX_SIN_CONECTIVIDAD):
                NAGIOS = "MSC:",MSC_temp," con ", cuenta_MME_truchos ," MME's sin conectividad"
                print NAGIOS
                alarmas_NAGIOS.append(NAGIOS)
