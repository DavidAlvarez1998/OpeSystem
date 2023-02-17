import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time 
import threading
from datetime import datetime as dt
#from datetime import datetime as dt


#-----------------------------------------Procesado de velas --------------------------------------------

#hace el calculo para crear las velas Heikin Ashi
def heikinAshi(df): 
    ha_close = (df['open'] + df['close'] + df['high'] + df['low']) / 4
    ha_open = [(df['open'].iloc[0] + df['close'].iloc[0]) / 2]
    for close in ha_close[:-1]:
        ha_open.append((ha_open[-1] + close) / 2)    
    ha_open = np.array(ha_open)
    elements = df['high'], df['low'], ha_open, ha_close
    ha_high, ha_low = np.vstack(elements).max(axis=0), np.vstack(elements).min(axis=0)
    return pd.DataFrame({
        'ha_open': ha_open,
        'ha_high': ha_high,    
        'ha_low': ha_low,
        'ha_close': ha_close
    }) 

#esta funcion pasa data de <class 'pandas.core.frame.DataFrame'> a <class 'list'>
def numpyAlist(data): 
    data=data.to_numpy().tolist()
    return data

#asigana tipo bajista o alcista y retorna una lista['alcista',high,low]
def asignarTipo(data): 
    data2=[]
    aux=0
    aux1=0
    aux2=0
    i=0
    while i<len(data): 
        if data[i][0]>data[i][3]:
            aux="bajista"
            aux1=data[i][1]
            aux2=data[i][2]
            data2.append(aux)
            data2.append(aux1)
            data2.append(aux2)
        else:
            aux="alcista"
            aux1=data[i][1]
            aux2=data[i][2]
            data2.append(aux)
            data2.append(aux1)
            data2.append(aux2)
        i=i+1
    return data2

#retorna una lista con la informacion secuencial del tipo de VELA['alcista',1,2,3,4,'bajista'1,2,...]
def granHeiken(data): 
    i=0
    x=data[0]
    data2=[x]
    while i< len(data):
        if type(data[i])==float:
            data2.append(data[i])
        else:
            if x!=data[i]:
                x=data[i]
                data2.append(data[i])
                
        i=i+1
    return data2

#retorna una lista con los puntos max(hihg) y min(low) de cada IMPULSO heiken
def granHeikenHighLow(data): 
    data.append("x")
    data2=[data[0]]
    aux=[]
    ma=0
    mi=0
    i=1
    while i < (len(data)):
        if type(data[i])==float:
            aux.append(data[i])
        else:
            ma=max(aux)
            mi=min(aux)
            data2.append(ma)
            data2.append(mi)
            data2.append(data[i])
            aux=[]
        i=i+1
    data2.pop(-1)
    return data2

#pasamos de tener una lista de una dimencion a dos dimenciones
def data1dimecionA2dimenciones(data): 
    data2=[]
    aux=[]
    i=0
    while i < len(data):
        aux=[data[i],data[i+1],data[i+2]]
        data2.append(aux)
        i=i+3
    return data2

#ajusta los valores de high y low de cada impulso
def ajusteImpusosH(data): 
    Hant=0  #high anterior
    Lant=0  #low anterior
    Haho=0  #high ahora
    Laho=0  #low ahora
    Hsig=0  #high sig
    Lsig=0  #low sig
    data2=[]
    aux=[]
    ma=0
    mi=0
    i=1
    while i < (len(data)-1):
        tipo=data[i][0]
        Hant=data[i-1][1]
        Lant=data[i-1][2]
        Haho=data[i][1]
        Laho=data[i][2]
        Hsig=data[i+1][1]
        Lsig=data[i+1][2]
        if tipo == 'alcista':
            aux=[Hsig,Haho]
            ma=max(aux)
            data2.append(tipo)
            data2.append(ma)
            aux=[Lant,Laho]
            mi=min(aux)
            data2.append(mi)
        else:
            aux=[Hant,Haho]
            ma=max(aux)
            data2.append(tipo)
            data2.append(ma)
            aux=[Lsig,Laho]
            mi=min(aux)
            data2.append(mi)
        i=i+1
    tipo=data[-1][0] #caso particular ultimo inpulso
    Hant=data[-2][1]
    Lant=data[-2][2]
    Haho=data[-1][1]
    Laho=data[-1][2]
    if tipo == 'alcista':
        aux=[Laho,Lant]
        mi=min(aux)
        data2.append(tipo)
        data2.append(Haho)
        data2.append(mi)
    else:
        aux=[Haho,Hant]
        ma=max(aux)
        data2.append(tipo)
        data2.append(ma)
        data2.append(Laho)
    return data2

#--------------------------------------toma de velas especificas --------------------------------------
def M15(simbolo):#me retorna el tipo de vela ultima cerrada en M15 ('alcista','bajista')
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M15,0,10)))
    data=heikinAshi(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-6]#penultimo tipo de vela
    return tipo   

def M1(simbolo):#retorna el ultimo tipo de vela cerrada en M1
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,10)))
    data=heikinAshi(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-6]#tipo de vela ( vela cerrada)
    return tipo  

def M1anterior(simbolo):#retorna el tipo de vela de la vela anterior a la ultima cerrada
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,10)))
    data=heikinAshi(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-9]#penultimo tipo de vela () 
    return tipo  



#-------------------------------------Sistema y Operaciones ---------------------------------------------
def ordenar(tipo,lote,tp,sl,simbolo):
    precio=mt5.symbol_info_tick(simbolo).ask
    deviation = 30
    if tipo==1:
        tp=precio-tp
        sl=precio+sl
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
        #return result[2]#retornamos el ticket de la orden 
        return result
    else:
        tp=precio+tp
        sl=precio-sl
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
        result = mt5.order_send(request)
        # check the execution result 
        #return result[2]#retornamos el ticket de la orden 
        return result

def cerrarOrden(ticket,lote,tipo,simbolo):
    precio=mt5.symbol_info_tick(simbolo).ask
    deviation = 0
    if tipo == 'compra':
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": simbolo,
            "volume": lote,
            "type": mt5.ORDER_TYPE_SELL,
            "position": ticket,
            "price": precio,
            "sl": 0.0,
            "tp": 0.0,
            "deviation": int(deviation),
            "magic": int(235000),
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # send a trading request
        result = mt5.order_send(request)
        # check the execution result 
        return ("orden cerrada",result)
    else:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": simbolo,
            "volume": lote,
            "type": mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": precio,
            "sl": 0.0,
            "tp": 0.0,
            "deviation": int(deviation),
            "magic": int(235000),
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # send a trading request
        result = mt5.order_send(request)
        # check the execution result 
        return ("orden cerrada",result)

def cuandoCerrar():#actualizado 2.0 actualizacion para cerrar mulples posiciones 
    aux=''
    while 1:
        posiciones=mt5.positions_get()  
        if len(posiciones)>0:
            i=0
            while i<len(posiciones):
                tikect=posiciones[i][0]
                tipo=posiciones[i][5]
                lote=posiciones[i][9]
                simbolo=posiciones[i][16]
                if tipo==0:
                    tipo='compra'
                else:
                    tipo='venta'
                            
                if tipo=='compra':
                    aux=M15(simbolo)
                    if aux=='bajista':
                        cerrarOrden(tikect,lote,tipo,simbolo)
                        aux=''
                if tipo=='venta':
                    aux=M15(simbolo)
                    if aux=='alcista':
                        cerrarOrden(tikect,lote,tipo,simbolo)
                        aux=''
                i=i+1
        time.sleep(0.5)

def breakeven(ticket,tipo,tp,preciOrden):# pone en libre de riesgo la ultima orden
    global simbolo
    puntosBreakeven=2.5
    if tipo==0:
        request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": simbolo,
        "position": ticket,
        "sl": preciOrden+puntosBreakeven,
        "tp": tp,
        "magic": 235000,
        }
        result = mt5.order_send(request)
    else:
        request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": simbolo,
        "position": ticket,
        "sl": preciOrden-puntosBreakeven,
        "tp": tp,
        "magic": 235000,
        }
        result = mt5.order_send(request)
    return result
    
def cuandoBreakeven():
    while 1:
        operaciones=list(mt5.positions_get())
        if len(operaciones)>0:
            ticket=operaciones[0][0]
            tipo=operaciones[0][5]
            sl=operaciones[0][11]
            tp=operaciones[0][12]
            preciOrden=operaciones[0][10]
            precioActual=mt5.symbol_info_tick(simbolo).ask
            if tipo==0:
                sl=preciOrden-sl
                be=preciOrden+sl
                if be>=precioActual:
                    print(breakeven(ticket,tipo,tp,preciOrden))
            if tipo==1: 
                sl=sl-preciOrden
                be=preciOrden-sl
                if be<=precioActual:
                    print(breakeven(ticket,tipo,tp,preciOrden))
        time.sleep(0.25) 

def calculoRiesgo(pips,riesgo):# para el nas100
    cuenta=(mt5.account_info())
    cuenta=cuenta[13]
    riesgo=float(cuenta*riesgo/100)
    lote=0.01
    while lote*pips<=riesgo:
        lote+=0.01
    lote=round(lote,1)
    return lote

#-------------------------------------Logica operaciones--------------------------------------------------

def logica(data,simbolo,riesgo):
    now=dt.now()
    m15=M15(simbolo)
    m1=M1(simbolo)
    M1ant=M1anterior(simbolo)
    primero=0
    rompimiento=0
    if m15=='alcista' and m1=='alcista':
        primero=data[-4][2]#le asigno el Low de la penultima impulso bajista
        rompimiento=data[-2][2]#le asigno el low del impulso bajista
        ultimoimpulso=data[-1][2]#low del impulso actual
        if rompimiento<primero and ultimoimpulso==rompimiento and M1ant=='bajista':
            print("compra: "+str(simbolo)+" : "+str(now))# 0 si es compra y 1 si es venta
            precio=mt5.symbol_info_tick(simbolo).ask
            sl=precio-rompimiento
            tp=sl+sl/2
            lote=int(calculoRiesgo(sl,riesgo))
            if lote>100:#lotaje maximo permitido es 100
                lote=100
            if lote<0.1:#lotaje minimo permitido es 0.1
                lote=0.1
            lote=float(lote)
            print(ordenar(0,lote,tp,sl,simbolo))   

    if m15=='bajista' and m1=='bajista':
        primero=data[-4][1]#le asigno el high de la penultima impulso alcista
        rompimiento=data[-2][1]#le asigno el high del impulso alcista 
        ultimoimpulso=data[-1][1]#high del impulso actual
        if rompimiento>primero and ultimoimpulso==rompimiento and M1ant=='alcista':
            print("venta: "+str(simbolo)+" : "+str(now))#1 si es venta y 0 si es compra 
            precio=mt5.symbol_info_tick(simbolo).ask
            sl=rompimiento-precio
            tp=sl+sl/2
            lote=calculoRiesgo(sl,riesgo)
            if lote>100:#lotaje maximo permitido es 100
                lote=100
            if lote<0.1:#lotaje minimo permitido es 0.1
                lote=0.1
            lote=float(lote)
            print(ordenar(1,lote,tp,sl,simbolo))               

#---------------------------------------------------------------------------------------------------------       


def inicio(riesgo):
    global simbolos
    while 1:
        i=0
        while i<len(simbolos):
            simbolo=simbolos[i]# cada uno de los simbolos es testeado
            spread=(mt5.symbol_info(simbolo)) #data de instrumento
            spread=list(spread)
            spread=spread[12]
            #if spread==100 or spread==10:
            if 1==1:
                data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,200)))#toma de data [time,open,high,low,close...]
                data=heikinAshi(data)#Dataframe 
                data=numpyAlist(data)#list[[open,high,low,close]]
                data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
                data=granHeiken(data) #list[´alcista´,h,l,h,l,h,l]
                data=granHeikenHighLow(data)#list[´alcista´,h,l,'bajista',h,l,'alcista',h,l]
                data=data1dimecionA2dimenciones(data)#list[[´alcista´,h,l],['bajista',h,l]]
                data=ajusteImpusosH(data)#list[´alcista´,h,l,'bajista',h,l,'alcista',h,l]
                data=data1dimecionA2dimenciones(data)
                '''
                info=mt5.symbol_info(simbolo) 
                now=(dt.utcfromtimestamp(info[10]))#hora exacta del simbolo
                hoy = dt(now.year, now.month , now.day)
                historial = list(mt5.history_deals_get(hoy,now))#historial de hoy
                e=0
                simboloOperado=[]
                while e<len(historial):
                    simboloOperado.append(historial[e][15])
                    e=e+1
                if  simbolo not in simboloOperado:#si no se han abiero operaciones en este simbolo pasa 
                    logica(data,simbolo,riesgo)
                '''     
                posiciones=list(mt5.positions_get())
                if len(posiciones)==0:
                    logica(data,simbolo,riesgo)
                elif len(posiciones)>0:
                    simboloPosiciones=[]
                    for x in posiciones: 
                        simboloPosiciones.append(x[16])
                    if simbolo not in simboloPosiciones:
                        logica(data,simbolo,riesgo)

            i=i+1
        time.sleep(0.2)
        
#-----------------------------------------------      2.0      ---------------------------------------------------------------
riesgo=2  #   1 = 1% de de la cuenta
simbolos=['NAS100','US30','US500','GER40']
#--------------------------------------------------------------------------------------------------------------
cuenta=61126218
contraseña="3anqbsZj"
servidor="mt5-demo01.pepperstone.com"
ruta="C:/Users/adjua/Desktop/Terminales/JOSE/metaC/terminal64.exe"#ruta terminal
autorizar=mt5.initialize(ruta,login=cuenta,Password=contraseña,server=servidor)
if autorizar:
    print("CUENTA GRAN HEIKEN: "+str(cuenta))
else:
    print("error el terminal cuenta 1", mt5.last_error())
    quit()
#--------------------------------------------------------------------------------------------------------------
hilo1 = threading.Thread(target=inicio,args=(riesgo,))#manera correcta de pasar parametros a un hilo, con ","
hilo2 = threading.Thread(target=cuandoCerrar)
hilo3 = threading.Thread(target=cuandoBreakeven)
hilo1.start()
hilo2.start()
#hilo3.start()
#--------------------------------------------------------------------------------------------------------------

