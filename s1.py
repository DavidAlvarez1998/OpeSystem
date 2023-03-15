import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime as dt
import time
import threading

info=0
simbolo='NAS100'
mt5.initialize()

#info=mt5.symbols_total() #numero de instrumentos finacieros
#info=mt5.symbols_get() #data de todos instrumentos finacieros 
#info=(mt5.symbol_info(simbolo)) #data de instrumento
#info=mt5.symbol_info_tick(simbolo).ask
#info=mt5.symbol_info_tick(simbolo).bid
#print(dt.utcfromtimestamp(info[10]))#16:30 es la apertura (9:30)
#tick = mt5.symbol_info_tick(simbolo)
#print("Bid:", tick.bid)
#print("Ask:", tick.ask)



def S1():

    while 1:
        info= mt5.symbol_info(simbolo)
        now = dt.utcfromtimestamp(info[10])
        m=now.second
        print(m)
        time.sleep(0.1)
        if m==0:
            break

    contador=0# indica cada cuandos ciclos es un segundo, cada ciclo es un tick
    s1=[]# lista donde se agragan los valores de tick
    ohlc=[]# lista donde se cuardan los valores ohlc de cada segundo
    m1=[]# valores de ohlc del minuto respecto a los segundos calculados
    while 1:
        tick = mt5.symbol_info_tick(simbolo)
        #--------------creacion de ohlc de cada segundo-----------------------
        if contador<=10:
            s1.append(tick.bid)
        if contador>10:
            o=s1[0]
            h=max(s1)
            l=min(s1)
            c=s1[-1]
            s1=[]
            aux=[o,h,l,c]
            ohlc.append(aux)
            contador=0
        contador=contador+1
        #--------------creacion de ohlc de cada segundo-----------------------
        
        
        if len(ohlc)==60:
            aux=[]
            for x in ohlc:
                for y in x:
                    aux.append(y)
            o=aux[0]
            h=max(aux)
            l=min(aux)
            c=aux[-1]
            aux=[o,h,l,c]
            m1.append(aux)
            return m1
        
        print(len(ohlc))
        time.sleep(0.1)  

print(S1())
