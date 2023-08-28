import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime as dt
import time
import threading



cuenta=61160245
contraseña="mgI3ncev"
servidor="mt5-demo01.pepperstone.com"



cuenta=82117703
contraseña="bqkkeprcu4"
servidor="EightcapEU-Live"

cuenta=82117069 
contraseña="bqkkeprcu4"
servidor="EightcapEU-Live"
autorizar=mt5.initialize(login=cuenta,Password=contraseña,server=servidor)

#-----------------------------------------------------------------------------------------------------
mensaje='xxx: '
if autorizar:
    balance=mt5.account_info() #tamaño de la cuenta actual
    balance=balance[13]         #tamaño de la cuenta actual
    print(mensaje+'\ncuenta: '+str(cuenta)+'\nbalance: '+str(balance))
else:
    print("error el terminal", mt5.last_error())
    quit()

mt5.initialize()

'''
while 1:
    operaciones=mt5.positions_get()
    print(operaciones)
    time.sleep(1)
'''
simbolo='NDX100'
lote=0.01
sl=0.0
tp=0.0
tipo=1
def ordenar(simbolo,lote,sl,tp,tipo):#monta orden en el mercado
    precio=mt5.symbol_info_tick(simbolo).ask
    deviation = 30
    if tipo==1:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": simbolo,
            "volume": lote,
            "type": tipo,
            "price": precio,
            "sl": sl,
            "tp": tp,
            "deviation": int(deviation),
            "magic": int(235000),
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # send a trading request
        result = mt5.order_send(request)
        # check the execution result 
        return result
print(ordenar(simbolo,lote,sl,tp,tipo))
#info=mt5.symbols_total() #numero de instrumentos finacieros
#info=mt5.symbols_get() #data de todos instrumentos finacieros 
#info=(mt5.symbol_info(simbolo)) #data de instrumento
#info=mt5.symbol_info_tick(simbolo).ask
#info=mt5.symbol_info_tick(simbolo).bid
#print(dt.utcfromtimestamp(info[10]))#16:30 es la apertura (9:30)
#tick = mt5.symbol_info_tick(simbolo)
#print("Bid:", tick.bid)
#print("Ask:", tick.ask)

#print(info)


def S1():

    while 1:
        info= mt5.symbol_info(simbolo)
        now = dt.utcfromtimestamp(info[10])
        m=now.second
        print(m)
        time.sleep(0.1)
        if m==0:
            break

    s1=[]# lista donde se agragan los valores de tick
    ohlc=[]# lista donde se cuardan los valores ohlc de cada segundo
    m1=[]# valores de ohlc del minuto respecto a los segundos calculados
    aux=0
    while 1:
        
        s = aux
        while s==aux:
            tick = mt5.symbol_info_tick(simbolo)
            s1.append(tick.bid) 
            info = mt5.symbol_info(simbolo)
            now = dt.utcfromtimestamp(info[10])
            s = now.second

        o=s1[0]
        h=max(s1)
        l=min(s1)
        c=s1[-1]
        s1=[]
        aux=[o,h,l,c]
        ohlc.append(aux)
        aux=s
        print(len(ohlc))
        #----------finalizar minuto
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
        #----------finalizar minuto
        
        #time.sleep(1/contador2)
