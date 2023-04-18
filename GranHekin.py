import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time 
import threading
from datetime import datetime as dt
import os





#-----------------------------------------Procesado de velas--------------------------------------------
#[t,o,h,l,c]
def heikinAshi(df): 
    ha_time = df['time']
    ha_close = (df['open'] + df['close'] + df['high'] + df['low']) / 4
    ha_open = [(df['open'].iloc[0] + df['close'].iloc[0]) / 2]
    for close in ha_close[:-1]:
        ha_open.append((ha_open[-1] + close) / 2)    
    ha_open = np.array(ha_open)
    elements = df['high'], df['low'], ha_open, ha_close
    ha_high, ha_low = np.vstack(elements).max(axis=0), np.vstack(elements).min(axis=0)
    return pd.DataFrame({
        'ha_time' : ha_time,
        'ha_open': ha_open,
        'ha_high': ha_high,    
        'ha_low': ha_low,
        'ha_close': ha_close
    }) 

#[t,o,h,l,c]
def joponesa(df): 
    ha_time = df['time']
    ha_close = df['close']
    ha_open = df['open']   
    ha_high = df['high'] 
    ha_low = df ['low']
    return pd.DataFrame({
        'ha_time' : ha_time,
        'ha_open': ha_open,
        'ha_high': ha_high,    
        'ha_low': ha_low,
        'ha_close': ha_close
    }) 

#esta funcion pasa data de <class 'pandas.core.frame.DataFrame'> a <class 'list'>
def numpyAlist(data): 
    data=data.to_numpy().tolist()
    return data

#asigana tipo bajista o alcista y retorna una lista[t,'alcista',high,low]
def asignarTipo(data): 
    data2=[]
    aux=0
    aux1=0
    aux2=0
    auxT=0
    i=0
    while i<len(data): 
        auxT=int(data[i][0])
        if data[i][1]>data[i][4]:
            aux="bajista"
            aux1=data[i][2]
            aux2=data[i][3]
            data2.append(auxT)
            data2.append(aux)
            data2.append(aux1)
            data2.append(aux2)
        else:
            aux="alcista"
            aux1=data[i][2]
            aux2=data[i][3]
            data2.append(auxT)
            data2.append(aux)   
            data2.append(aux1)
            data2.append(aux2)
        i=i+1
    return data2

#retorna una lista con la informacion secuencial del tipo de VELA['alcista',1,2,3,4,'bajista'1,2,...]
def agrupacionVelas(data): 
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

#pasamos de tener una lista de una dimencion a dos dimenciones
def data1dimecionA2dimenciones(data): 
    data2=[]
    aux=[]
    i=1
    while i<(len(data)):      
        if type(data[i])==int:
            #t=str(dt.utcfromtimestamp(data[i-4]))
            t=data[i-4]
            aux.append(data[i-3])
            aux.append(t)
            aux.append(data[i-2])
            aux.append(data[i-1])
            data2.append(aux)
            aux=[]         
        i=i+1
    aux.append(data[-3])#agregamos la info de la ultima vela
    aux.append(data[-4])
    aux.append(data[-2])
    aux.append(data[-1])
    data2.append(aux)
    
    return data2

#retorna una lista con los puntos max(hihg) y min(low) de cada IMPULSO 
def estremosImpulsos(data): 
    valores=data
    tipo_actual = valores[0][0]
    max_valor = valores[0][2]
    max_fecha = valores[0][1]
    min_valor = valores[0][3]
    min_fecha = valores[0][1]
    resultado = []
    
    for valor in valores[1:]:
        if valor[0] != tipo_actual:
            resultado.append([tipo_actual, max_fecha, max_valor, min_fecha, min_valor])
            tipo_actual = valor[0]
            max_valor = valor[2]
            max_fecha = valor[1]
            min_valor = valor[3]
            min_fecha = valor[1]
        else:
            if valor[2] > max_valor:
                max_valor = valor[2]
                max_fecha = valor[1]
            if valor[3] < min_valor:
                min_valor = valor[3]
                min_fecha = valor[1]
    
    resultado.append([tipo_actual, max_fecha, max_valor, min_fecha, min_valor])
    
    return resultado

#ajusta los valores de high y low de cada impulso(minimo anterior y maximo siguiente, maximo anterior y minimo siguiente)
def ajusteImpusos(data):
    datos=data 
    nuevos_datos = []
    for i in range(len(datos)):
        if datos[i][0] == 'alcista':
            if i == 0:
                hi = datos[i][2]
                tiempo_hi = datos[i][1]
                lo = datos[i][4]
                tiempo_lo = datos[i][3]
            elif i == len(datos)-1:
                hi = datos[i][2]
                tiempo_hi = datos[i][1]
                lo = min(datos[i][4], datos[i-1][4])
                tiempo_lo = datos[i-1][3] if datos[i-1][4] < datos[i][4] else datos[i][3]
            else:
                hi = max(datos[i][2], datos[i+1][2])
                tiempo_hi = datos[i+1][1] if datos[i+1][2] > datos[i][2] else datos[i][1]
                lo = min(datos[i][4], datos[i-1][4])
                tiempo_lo = datos[i-1][3] if datos[i-1][4] < datos[i][4] else datos[i][3]
            nuevos_datos.append(['alcista', tiempo_hi, hi, tiempo_lo, lo])
        elif datos[i][0] == 'bajista':
            if i == 0:
                hi = datos[i][2]
                tiempo_hi = datos[i][1]
                lo = datos[i][4]
                tiempo_lo = datos[i][3]
            elif i == len(datos)-1:
                hi = max(datos[i][2], datos[i-1][2])
                tiempo_hi = datos[i-1][1] if datos[i-1][2] > datos[i][2] else datos[i][1]
                lo = datos[i][4]
                tiempo_lo = datos[i][3]
            else:
                hi = max(datos[i][2], datos[i-1][2])
                tiempo_hi = datos[i-1][1] if datos[i-1][2] > datos[i][2] else datos[i][1]
                lo = min(datos[i][4], datos[i+1][4])
                tiempo_lo = datos[i+1][3] if datos[i+1][4] < datos[i][4] else datos[i][3]
            nuevos_datos.append(['bajista', tiempo_hi, hi, tiempo_lo, lo])
    return nuevos_datos           
#-----------------------------------------Procesado de velas --------------------------------------------





#--------------------------------------toma de velas especificas --------------------------------------
#me retorna el tipo de vela ultima cerrada en M15 Heikin Ashi
def M15Heikin(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M15,0,10)))
    data=heikinAshi(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-7]#penultimo tipo de vela
    return tipo

#me retorna el tipo de vela ultima cerrada en M5 Heikin Ashi
def M5Heikin(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M5,0,10)))
    data=heikinAshi(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-7]#penultimo tipo de vela
    return tipo  

#retorna el ultimo tipo de vela cerrada en M1 y su valor de close 
def M1(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,10)))
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    close=data[-2][4]#valor de cierre ultima vela cerrada
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-7]#tipo de vela ( vela cerrada)
    return tipo,close

#retorna el ultimo tipo de vela cerrada en M15 y su valor de close
def M15(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M15,0,10)))
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    close=data[-2][4]#valor de cierre ultima vela cerrada
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-7]#tipo de vela ( vela cerrada)
    return tipo,close

#retorna el tipo de vela de la vela anterior a la ultima cerrada
def M1anterior(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,10)))
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-11]#penultimo tipo de vela () 
    return tipo 

#retorna el tipo de vela de la vela anterior anterior a la ultima cerrada
def M1anteriorAnterior(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,10)))
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)#list[[open,high,low,close]]
    data=asignarTipo(data)#list['alcista,h,l,'alcista',h,l]
    tipo=data[-15]#penultimo tipo de vela () 
    return tipo 
#--------------------------------------toma de velas especificas --------------------------------------





#-------------------------------------Sistema y Operaciones ---------------------------------------------
def ordenar(tipo,lote,tp,sl,simbolo,comentario):
    
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
            "comment": comentario,
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
            "comment": comentario,
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
            "comment": "",
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
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # send a trading request
        result = mt5.order_send(request)
        # check the execution result 
        return ("orden cerrada",result)

def cuandoCerrar(): 
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
                comentario=posiciones[i][17]
                if comentario=="M15":#solo cerrar ordenes con sistema M15
                    if tipo==0:
                        tipo='compra'
                    else:
                        tipo='venta'
                                
                    if tipo=='compra':
                        aux=M15Heikin(simbolo)
                        if aux=='bajista':
                            cerrarOrden(tikect,lote,tipo,simbolo)
                            aux=''
                    if tipo=='venta':
                        aux=M15Heikin(simbolo)
                        if aux=='alcista':
                            cerrarOrden(tikect,lote,tipo,simbolo)
                            aux=''
                i=i+1
        time.sleep(0.5)
  
def calculoRiesgo(pips,riesgo):
    cuenta=(mt5.account_info())
    cuenta=cuenta[13]
    riesgo=float(cuenta*riesgo/100)
    lote=0.01
    while lote*pips<=riesgo:
        lote+=0.01
    lote=round(lote,1)
    if lote>100:#lotaje maximo permitido es 100
        lote=100
    if lote<0.1:#lotaje minimo permitido es 0.1
        lote=0.1
    return lote
#-------------------------------------Sistema y Operaciones ----------------------------------------------





#-------------------------------------Sistema BE ---------------------------------------------------------
def modificarOrdenBe(simbolo,ticket,tipo,tp,preciOrden):
    puntosBreakeven=2
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

def be():
    while 1:
        posiciones=list(mt5.positions_get())
        if len(posiciones)>0:
            i=0
            while i<len(posiciones):
                aux=posiciones[i]
                simbolo=aux[16]
                precioActual=mt5.symbol_info_tick(simbolo).ask
                ticket=aux[0]
                tipo=aux[5]
                sl=aux[11]#precio
                tp=aux[12]#precio
                preciOrden=aux[10]
                if sl > 0:
                    if tipo == 0: # si es compra
                        if preciOrden>sl:
                            sl=preciOrden-sl
                            be=preciOrden+sl
                            if precioActual>=be:
                                (modificarOrdenBe(simbolo,ticket,tipo,tp,preciOrden))
                    if tipo == 1: # si es venta
                        if preciOrden<sl:
                            sl=sl-preciOrden
                            be=preciOrden-sl
                            if precioActual<=be:
                                (modificarOrdenBe(simbolo,ticket,tipo,tp,preciOrden))
                i=i+1
        time.sleep(0.2)
#-------------------------------------Sistema BE ---------------------------------------------------------





#-------------------------------------Media Movil---------------------------------------------------------
def mediaMovilM1(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,20)))#toma de data [time,open,high,low,close...     
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)  
    aux=0
    for x in data:
        aux=aux+x[4]
    aux=aux/len(data)
    return aux

def mediaMovilM5(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M5,0,20)))#toma de data [time,open,high,low,close...     
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)  
    aux=0
    for x in data:
        aux=aux+x[4]
    aux=aux/len(data)
    return aux

def mediaMovilM15(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M15,0,20)))#toma de data [time,open,high,low,close...     
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)  
    aux=0
    for x in data:
        aux=aux+x[4]
    aux=aux/len(data)
    return aux
#-------------------------------------Media Movil---------------------------------------------------------





#-------------------------------------Logica operaciones--------------------------------------------------
def niveles14(data):#retorna lista con niveles 1/4 del ultimo impulso
    impulsoAnt=data[-2]
    highAnt=impulsoAnt[2]#maximo del ultimo impulso finalizado
    lowAnt=impulsoAnt[4]#minimo del ultimo impulso finalizado
    #print(impulsoAnt[0],highAnt,lowAnt)#muestra ultimo impulso
    nivelesImpulso=[]
    while lowAnt<=highAnt:
        lowAntList=list(str(lowAnt))
        i=2
        while i<len(lowAntList):
            aux1=lowAntList[i]
            aux2=lowAntList[i-1]
            aux3=lowAntList[i-2]
            if aux1=='.':
                aux4=int(aux3+aux2)
                if aux4 in [0,00,25,50,75]:
                    nivelesImpulso.append(lowAnt)
            i=i+1
        lowAnt=lowAnt+1
    return nivelesImpulso

def identificarRompimientoM30(simbolo):# retorna texto compras o ventas si asi lo dice el sistema de m30 en m30
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M30,0,50)))#toma de data [time,open,high,low,close...
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)
    data=asignarTipo(data)
    data=agrupacionVelas(data) 
    data=data1dimecionA2dimenciones(data)
    data=estremosImpulsos(data)
    data=ajusteImpusos(data)
    precioBid=mt5.symbol_info_tick(simbolo).bid

    cuartolow=data[-4][4]
    tercerolow=data[-3][4]
    segundolow=data[-2][4]
    primerolow=data[-1][4]

    cuartohigh=data[-4][2]
    tercerohig=data[-3][2]
    segundohig=data[-2][2]
    primerohig=data[-1][2]

    r=''

    if precioBid < segundolow:
        r='compras'
        
    elif precioBid > segundohig:
        r='ventas'
        
    elif segundolow<cuartolow:
        r='compras'

    elif segundohig>cuartohigh:
        r='ventas'
        
    elif r=='':
        i=len(data)-1
        while i<=len(data)+3:
            cuartolow=data[i-3][4]
            tercerolow=data[i-2][4]
            segundolow=data[i-1][4]
            primerolow=data[i][4]

            cuartohigh=data[i-3][2]
            tercerohig=data[i-2][2]
            segundohig=data[i-1][2]
            primerohig=data[i][2]

            if segundolow<cuartolow:
                r='compras'
                
                break
            elif segundohig>cuartohigh:
                r='ventas'
                
                break
            i=i-1

    return(r)

def confirmarEntrada(t,simbolo):#retorna 0 si ya se tomo una orden en ese mento y 1 si no 
    #posiciones=list(mt5.positions_get())
    info=mt5.symbol_info(simbolo) 
    now=(dt.utcfromtimestamp(info[10]))#hora exacta del simbolo
    hoy = dt(now.year, now.month , now.day)
    historial = list(mt5.history_deals_get(hoy,now))#historial de hoy
    t=str(t)
    for e in historial:
        n=e[16]
        n=n.split(",")             
        if n[0]=='V':#si ya hubo una orden con sistemas VECTORES en ese punto
            x=n[1]
            if t==x:
                return 0
        elif n[0]=='M15':#si ya hubo una orden con sistemas M15 en ese punto
            x=n[1]
            if t==x:
                return 0
        elif n[0]=='M30':#si ya hubo una orden con sistemas M30 en ese punto
            x=n[1]
            if t==x:
                return 0
    return 1#no hay ordenes en este punto

def logicaM15(simbolo,riesgo):# sistema m15
    comentario="M15"
    t=mt5.symbol_info(simbolo)#now
    t=t[10]
    t=(t // 60) * 60
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,200)))#toma de data [time,open,high,low,close...
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)
    data=asignarTipo(data)
    data=agrupacionVelas(data) 
    data=data1dimecionA2dimenciones(data)
    data=estremosImpulsos(data)
    data=ajusteImpusos(data)
    m15=M15Heikin(simbolo)
    m1,close=M1(simbolo)
    M1ant=M1anterior(simbolo)
    M1antAnt=M1anteriorAnterior(simbolo)
    primero=0
    rompimiento=0
    #el ultimo impulso es varible segun la direccion de la ultima vela no cerrada con respecto a la anterior a ella
    niveles=niveles14(data)#lista de los niveles 1/4 del ultimo impulso
    cierreAfavor=0 # variable para determinar si se cerro a favor de la dioreccion con respecto a 1/4
    if m15=='alcista' and m1=='alcista' and confirmarEntrada(t,simbolo)==1:
        primero=data[-4][4]#le asigno el Low de la penultima impulso bajista
        rompimiento=data[-2][4]#le asigno el low del impulso bajista
        ultimoimpulso=data[-1][4]#low del impulso actual
        for x in niveles:
                if close>=x:
                    cierreAfavor=1
        if rompimiento<primero and ultimoimpulso==rompimiento and ((M1ant=='bajista') or (M1ant=='alcista' and M1antAnt=='bajista')) and cierreAfavor==1:
            precio=mt5.symbol_info_tick(simbolo).ask
            sl=precio-rompimiento
            tp=sl*2#--------------------------tp
            lote=calculoRiesgo(sl,riesgo)
            comentario=comentario+','+str(t)
            print('compra: '+comentario)
            (ordenar(0,lote,tp,sl,simbolo,comentario))
              

    elif m15=='bajista' and m1=='bajista' and confirmarEntrada(t,simbolo)==1:
        primero=data[-4][2]#le asigno el high de la penultima impulso alcista
        rompimiento=data[-2][2]#le asigno el high del impulso alcista 
        ultimoimpulso=data[-1][2]#high del impulso actual
        for x in niveles:
                if close<=x:
                    cierreAfavor=1
        if rompimiento>primero and ultimoimpulso==rompimiento and ((M1ant=='alcista') or (M1ant=='bajista' and M1antAnt=='alcista')) and cierreAfavor==1:
            precio=mt5.symbol_info_tick(simbolo).ask
            sl=rompimiento-precio
            tp=sl*2#--------------------------tp
            lote=calculoRiesgo(sl,riesgo)
            comentario=comentario+','+str(t)
            print('compra: '+comentario)
            (ordenar(1,lote,tp,sl,simbolo,comentario))                     

def logicaM30(simbolo,riesgo):# sistema m30 
    comentario="M30"
    t=mt5.symbol_info(simbolo)#now
    t=t[10]
    t=(t // 60) * 60
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,100)))#toma de data [time,open,high,low,close...
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)
    data=asignarTipo(data)
    data=agrupacionVelas(data) 
    data=data1dimecionA2dimenciones(data)
    data=estremosImpulsos(data)
    data=ajusteImpusos(data)
    m1,close=M1(simbolo)
    M5He=M5Heikin(simbolo)
    M1ant=M1anterior(simbolo)
    M1antAnt=M1anteriorAnterior(simbolo)
    cierreAfavor=0
    niveles=niveles14(data)#lista de los niveles 1/4 del ultimo impulso
    precio=mt5.symbol_info_tick(simbolo).ask

    #--------------------------caso compra----------------------------------    
    if identificarRompimientoM30(simbolo)=='compras' and m1=='alcista' and confirmarEntrada(t,simbolo)==1:
        primero=data[-4][4]#le asigno el Low del penultima impulso 
        rompimiento=data[-2][4]#le asigno el low del impulso 
        ultimoimpulso=data[-1][4]#low del impulso actual
        for x in niveles:
                if close>=x:
                    cierreAfavor=1
        if rompimiento<primero and ultimoimpulso==rompimiento and ((M1ant=='bajista') or (M1ant=='alcista' and M1antAnt=='bajista')) and cierreAfavor==1 and  M5He=="alcista":
        #if rompimiento<primero and ultimoimpulso==rompimiento and (M1ant=='bajista') and cierreAfavor==1 and  M5He=="alcista":            
            precio=mt5.symbol_info_tick(simbolo).ask
            sl=precio-rompimiento
            tp=sl*2#--------------------------tp
            lote=calculoRiesgo(sl,riesgo)
            comentario=comentario+','+str(t)
            print('compra: '+comentario)
            (ordenar(0,lote,tp,sl,simbolo,comentario))
            print(lote)
    #--------------------------caso compra----------------------------------
    #--------------------------caso venta-----------------------------------
    if identificarRompimientoM30(simbolo)=='ventas' and m1 =='bajista' and confirmarEntrada(t,simbolo)==1:
        primero=data[-4][2]#le asigno el high de la penultima impulso 
        rompimiento=data[-2][2]#le asigno el high del impulso  
        ultimoimpulso=data[-1][2]#high del impulso actual
        for x in niveles:
                if close<=x:
                    cierreAfavor=1
        if rompimiento>primero and ultimoimpulso==rompimiento and ((M1ant=='alcista') or (M1ant=='bajista' and M1antAnt=='alcista')) and cierreAfavor==1  and M5He=="bajista":
        #if rompimiento>primero and ultimoimpulso==rompimiento and (M1ant=='alcista') and cierreAfavor==1  and M5He=="bajista":             
            precio=mt5.symbol_info_tick(simbolo).ask
            sl=rompimiento-precio
            tp=sl*2#--------------------------tp
            lote=calculoRiesgo(sl,riesgo)
            comentario=comentario+','+str(t)
            print('compra: '+comentario)
            (ordenar(1,lote,tp,sl,simbolo,comentario))
    #--------------------------caso venta-----------------------------------

def logicaVectores(simbolo,riesgo):# sistema vectores
    comentario='V'
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,300)))#toma de data [time,open,high,low,close...
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)
    data=asignarTipo(data)
    data=agrupacionVelas(data) 
    data=data1dimecionA2dimenciones(data)
    data=estremosImpulsos(data)
    data=ajusteImpusos(data)
    precio=mt5.symbol_info_tick(simbolo).ask
    mv=mediaMovilM1(simbolo)
    m1,close=M1(simbolo)
    lista_invertida = data[::-1]#data al reves
    #------------------------------caso compras-----------------------------------------
    if m1=='alcista':
        ultimoThigh=data[-2][1]
        ultimoHigh=data[-2][2]
        siguienteThigh=0
        siguienteHigh=0
        i=3
        while i<len(lista_invertida):
            siguienteHigh=lista_invertida[i][2]
            if siguienteHigh>ultimoHigh:
                siguienteThigh=lista_invertida[i][1]
                break
            i=i+1
        if siguienteThigh!=0:#restringimos el caso en que no encuentre un estremo anterior 
            x1=ultimoThigh
            y1=ultimoHigh
            x2=siguienteThigh
            y2=siguienteHigh
            x=mt5.symbol_info(simbolo)#now
            x=x[10]
            m=(y2-y1)/(x2-x1)
            b=y2-m*x2
            y=m*x+b
            #print(dt.utcfromtimestamp(x1),y1,dt.utcfromtimestamp(x2),y2)
            #print('compras: '+str(y))
            #----------------donde poner sl-------------
            i=2
            while i<len(lista_invertida):#donde poner stop (estremo siguiente con respecto al precio actual)
                ultimoLow=lista_invertida[i][4]
                if ultimoLow<precio:
                    break
                i=i+1
            #----------------donde poner sl-------------
            sl=precio-ultimoLow
            tp=sl*2
            #print('sl Compras: '+str(ultimoLow))
            lote=calculoRiesgo(sl,riesgo)
            t=(ultimoThigh // 60) * 60# eliminamos los segundos 
            if close>mv and close>y and confirmarEntrada(t,simbolo)==1:
                comentario=comentario+','+str(t)
                print('compra: '+comentario)
                (ordenar(0,lote,tp,sl,simbolo,comentario))         
    #------------------------------caso compras-----------------------------------------
    
    #------------------------------caso ventas-----------------------------------------   
    elif m1=='bajista':
        ultimoTlow=data[-2][3]
        ultimoLow=data[-2][4]
        siguienteTlow=0
        siguienteLow=0
        i=3
        while i<len(lista_invertida):
            siguienteLow=lista_invertida[i][4]
            if siguienteLow<ultimoLow:
                siguienteTlow=lista_invertida[i][3]
                break
            i=i+1
        if siguienteTlow!=0:
            x1=ultimoTlow
            y1=ultimoLow
            x2=siguienteTlow
            y2=siguienteLow
            x=mt5.symbol_info(simbolo)#now
            x=x[10]
            m=(y2-y1)/(x2-x1)
            b=y2-m*x2
            y=m*x+b
            #print(dt.utcfromtimestamp(x1),y1,dt.utcfromtimestamp(x2),y2)
            #print('ventas: '+str(y))
            #----------------donde poner sl-------------
            i=2
            while i<len(lista_invertida):
                ultimoHigh=lista_invertida[i][2] 
                if ultimoHigh>precio:
                    break
                i=i+1
            #----------------donde poner sl-------------
            sl=ultimoHigh-precio
            tp=sl*2
            #print('sl Venta: '+str(ultimoHigh))
            lote=calculoRiesgo(sl,riesgo)
            t=(ultimoTlow // 60) * 60
            if close<mv and close<y and  confirmarEntrada(t,simbolo)==1:
                comentario=comentario+','+str(t)
                print('venta: '+comentario)
                (ordenar(1,lote,tp,sl,simbolo,comentario))
    #------------------------------caso ventas-----------------------------------------  
    
#-------------------------------------Logica operaciones--------------------------------------------------    





#-------------------------------------Logica Armonia Vectores---------------------------------------------

def ConfirmarArmoniaVectoresM15(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M15,0,300)))#toma de data [time,open,high,low,close...
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)
    data=asignarTipo(data)
    data=agrupacionVelas(data) 
    data=data1dimecionA2dimenciones(data)
    data=estremosImpulsos(data)
    data=ajusteImpusos(data)
    precio=mt5.symbol_info_tick(simbolo).ask
    mv=mediaMovilM15(simbolo)
    lista_invertida = data[::-1]#data al reves
    #------------------------------caso compras-----------------------------------------
    ultimoThigh=data[-2][1]
    ultimoHigh=data[-2][2]
    siguienteThigh=0
    siguienteHigh=0
    i=3
    while i<len(lista_invertida):
        siguienteHigh=lista_invertida[i][2]
        if siguienteHigh>ultimoHigh:
            siguienteThigh=lista_invertida[i][1]
            break
        i=i+1
    if siguienteThigh!=0:#restringimos el caso en que no encuentre un estremo anterior 
        x1=ultimoThigh
        y1=ultimoHigh
        x2=siguienteThigh
        y2=siguienteHigh
        x=mt5.symbol_info(simbolo)#now
        x=x[10]
        m=(y2-y1)/(x2-x1)
        b=y2-m*x2
        y=m*x+b
        if precio>mv and precio>y:
            return 'compras'    
    #------------------------------caso compras-----------------------------------------
    
    #------------------------------caso ventas-----------------------------------------   
    ultimoTlow=data[-2][3]
    ultimoLow=data[-2][4]
    siguienteTlow=0
    siguienteLow=0
    i=3
    while i<len(lista_invertida):
        siguienteLow=lista_invertida[i][4]
        if siguienteLow<ultimoLow:
            siguienteTlow=lista_invertida[i][3]
            break
        i=i+1
    if siguienteTlow!=0:
        x1=ultimoTlow
        y1=ultimoLow
        x2=siguienteTlow
        y2=siguienteLow
        x=mt5.symbol_info(simbolo)#now
        x=x[10]
        m=(y2-y1)/(x2-x1)
        b=y2-m*x2
        y=m*x+b
        if precio<mv and precio<y:
            return 'ventas'  
    return 0
    #------------------------------caso ventas-----------------------------------------  

def ConfirmarArmoniaVectoresM5(simbolo):
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M5,0,300)))#toma de data [time,open,high,low,close...
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)
    data=asignarTipo(data)
    data=agrupacionVelas(data) 
    data=data1dimecionA2dimenciones(data)
    data=estremosImpulsos(data)
    data=ajusteImpusos(data)
    precio=mt5.symbol_info_tick(simbolo).ask
    mv=mediaMovilM5(simbolo)
    lista_invertida = data[::-1]#data al reves
    #------------------------------caso compras-----------------------------------------
    ultimoThigh=data[-2][1]
    ultimoHigh=data[-2][2]
    siguienteThigh=0
    siguienteHigh=0
    i=3
    while i<len(lista_invertida):
        siguienteHigh=lista_invertida[i][2]
        if siguienteHigh>ultimoHigh:
            siguienteThigh=lista_invertida[i][1]
            break
        i=i+1
    if siguienteThigh!=0:#restringimos el caso en que no encuentre un estremo anterior 
        x1=ultimoThigh
        y1=ultimoHigh
        x2=siguienteThigh
        y2=siguienteHigh
        x=mt5.symbol_info(simbolo)#now
        x=x[10]
        m=(y2-y1)/(x2-x1)
        b=y2-m*x2
        y=m*x+b
        if precio>mv and precio>y:
            return 'compras'    
    #------------------------------caso compras-----------------------------------------
    
    #------------------------------caso ventas-----------------------------------------   
    ultimoTlow=data[-2][3]
    ultimoLow=data[-2][4]
    siguienteTlow=0
    siguienteLow=0
    i=3
    while i<len(lista_invertida):
        siguienteLow=lista_invertida[i][4]
        if siguienteLow<ultimoLow:
            siguienteTlow=lista_invertida[i][3]
            break
        i=i+1
    if siguienteTlow!=0:
        x1=ultimoTlow
        y1=ultimoLow
        x2=siguienteTlow
        y2=siguienteLow
        x=mt5.symbol_info(simbolo)#now
        x=x[10]
        m=(y2-y1)/(x2-x1)
        b=y2-m*x2
        y=m*x+b
        if precio<mv and precio<y:
            return 'ventas'  
    return 0
    #------------------------------caso ventas-----------------------------------------  

def logicaArmoniaVectores(simbolo,riesgo):#sistema vectores con armonia en M5 y M15
    comentario='V'
    data=pd.DataFrame((mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,300)))#toma de data [time,open,high,low,close...
    data=joponesa(data)#Dataframe 
    data=numpyAlist(data)
    data=asignarTipo(data)
    data=agrupacionVelas(data) 
    data=data1dimecionA2dimenciones(data)
    data=estremosImpulsos(data)
    data=ajusteImpusos(data)
    precio=mt5.symbol_info_tick(simbolo).ask
    mv=mediaMovilM1(simbolo)
    m1,close=M1(simbolo)
    lista_invertida = data[::-1]#data al reves
    #------------------------------caso compras-----------------------------------------
    if m1=='alcista' and ConfirmarArmoniaVectoresM5(simbolo)=='compras' and ConfirmarArmoniaVectoresM15(simbolo)=='compras':
        ultimoThigh=data[-2][1]
        ultimoHigh=data[-2][2]
        siguienteThigh=0
        siguienteHigh=0
        i=3
        while i<len(lista_invertida):
            siguienteHigh=lista_invertida[i][2]
            if siguienteHigh>ultimoHigh:
                siguienteThigh=lista_invertida[i][1]
                break
            i=i+1
        if siguienteThigh!=0:#restringimos el caso en que no encuentre un estremo anterior 
            x1=ultimoThigh
            y1=ultimoHigh
            x2=siguienteThigh
            y2=siguienteHigh
            x=mt5.symbol_info(simbolo)#now
            x=x[10]
            m=(y2-y1)/(x2-x1)
            b=y2-m*x2
            y=m*x+b
            #print(dt.utcfromtimestamp(x1),y1,dt.utcfromtimestamp(x2),y2)
            #print('compras: '+str(y))
            #----------------donde poner sl-------------
            i=2
            while i<len(lista_invertida):#donde poner stop (estremo siguiente con respecto al precio actual)
                ultimoLow=lista_invertida[i][4]
                if ultimoLow<precio:
                    break
                i=i+1
            #----------------donde poner sl-------------
            sl=precio-ultimoLow
            tp=sl*2
            #print('sl Compras: '+str(ultimoLow))
            lote=calculoRiesgo(sl,riesgo)
            t=(ultimoThigh // 60) * 60# eliminamos los segundos 
            if close>mv and close>y and confirmarEntrada(t,simbolo)==1:
                comentario=comentario+','+str(t)
                print('compra: '+comentario)
                (ordenar(0,lote,tp,sl,simbolo,comentario))         
    #------------------------------caso compras-----------------------------------------
    
    #------------------------------caso ventas-----------------------------------------   
    elif m1=='bajista'and ConfirmarArmoniaVectoresM5(simbolo)=='ventas' and ConfirmarArmoniaVectoresM15(simbolo)=='ventas':
        ultimoTlow=data[-2][3]
        ultimoLow=data[-2][4]
        siguienteTlow=0
        siguienteLow=0
        i=3
        while i<len(lista_invertida):
            siguienteLow=lista_invertida[i][4]
            if siguienteLow<ultimoLow:
                siguienteTlow=lista_invertida[i][3]
                break
            i=i+1
        if siguienteTlow!=0:
            x1=ultimoTlow
            y1=ultimoLow
            x2=siguienteTlow
            y2=siguienteLow
            x=mt5.symbol_info(simbolo)#now
            x=x[10]
            m=(y2-y1)/(x2-x1)
            b=y2-m*x2
            y=m*x+b
            #print(dt.utcfromtimestamp(x1),y1,dt.utcfromtimestamp(x2),y2)
            #print('ventas: '+str(y))
            #----------------donde poner sl-------------
            i=2
            while i<len(lista_invertida):
                ultimoHigh=lista_invertida[i][2] 
                if ultimoHigh>precio:
                    break
                i=i+1
            #----------------donde poner sl-------------
            sl=ultimoHigh-precio
            tp=sl*2
            #print('sl Venta: '+str(ultimoHigh))
            lote=calculoRiesgo(sl,riesgo)
            t=(ultimoTlow // 60) * 60
            if close<mv and close<y and  confirmarEntrada(t,simbolo)==1:
                comentario=comentario+','+str(t)
                print('venta: '+comentario)
                (ordenar(1,lote,tp,sl,simbolo,comentario))
    #------------------------------caso ventas-----------------------------------------  

#-------------------------------------Logica Armonia Vectores---------------------------------------------





#-------------------------------------Numero De Operaciones Por Dia---------------------------------------
def numeroOperacionesDia(simbolo,riesgo):
    vectores=2# numero de operaciones al dia del sistema VECTORES
    m15=1# numero de operaciones al dia del sistema M15
    m30=0# numero de operaciones al dia del sistema M30
    info=mt5.symbol_info(simbolo) 
    now=(dt.utcfromtimestamp(info[10]))#hora exacta del simbolo
    hoy = dt(now.year, now.month , now.day)
    historial = list(mt5.history_deals_get(hoy,now))#historial de hoy
    for e in historial:
        n=e[16]
        n=n.split(",")             
        if n[0]=='V':
            vectores=vectores-1
        elif n[0]=='M15':
            m15=m15-1
        elif n[0]=='M30':
            m30=m30-1
    if vectores>0:
        logicaVectores(simbolo,riesgo)
    if m15>0:
        logicaM15(simbolo,riesgo)
    if m30>0:
        logicaM30(simbolo,riesgo)
#-------------------------------------Numero De Operaciones Por Dia---------------------------------------





#-------------------------------------restricciones y toma de datos---------------------------------------
def inicio(riesgo):
    global simbolos
    while 1:
        i=0
        while i<len(simbolos):
            simbolo=simbolos[i]# cada uno de los simbolos es testeado

            #-----todos los sistemas------
            #logicaM15(simbolo,riesgo)
            #logicaM30(simbolo,riesgo)
            #logicaVectores(simbolo,riesgo)
            #logicaArmoniaVectores(simbolo,riesgo)
            #-----todos los sistemas------

            #-----como operar------
            #numeroOperacionesDia(simbolo,riesgo)
            #-----como operar------

            i=i+1
        time.sleep(0.1)
#-------------------------------------restricciones y toma de datos---------------------------------------





#-------------------------------------Creacion S1---------------------------------------------------------
def S1():
    global simbolos
    contador=0
    s1=[]
    ohlc=[]
    
    while 1:
        tick = mt5.symbol_info_tick(simbolos[0])
        #print("Bid:", tick.bid)
        #print("Ask:", tick.ask)
        if contador<=100:
            s1.append(tick.bid)
        if contador>100:
            o=s1[0]
            h=max(s1)
            l=min(s1)
            c=s1[0-1]
            s1=[]
            aux=[o,h,l,c]
            ohlc.append(aux)
            contador=0
        contador=contador+1
        #------------convertir S1 en impulsos------------------
        '''
        if len(ohlc)>2:
            data=asignarTipo(ohlc)
            data=agrupacionVelas(data) #list[´alcista´,h,l,h,l,h,l]
            data=estremosImpulsos(data)#list[´alcista´,h,l,'bajista',h,l,'alcista',h,l]
            data=data1dimecionA2dimenciones(data)#list[[´alcista´,h,l],['bajista',h,l]]
            data=ajusteImpusos(data)#list[´alcista´,h,l,'bajista',h,l,'alcista',h,l]
            print(data)
        '''
        #------------convertir S1 en impulsos------------------

        time.sleep(0.01)     
#-------------------------------------Creacion S1---------------------------------------------------------





#-----------------------------------------varibles--------------------------------------------------------
riesgo=1  #   0.5 = 0.5% de de la cuenta
simbolos=['NAS100']
#-----------------------------------------varibles--------------------------------------------------------





#-----------------------------------------variblesCuenta--------------------------------------------------------
cuenta=61143461
contraseña="xc7ynBa3"
servidor="mt5-demo01.pepperstone.com"
ruta="C:/Users/adjua/Desktop/Terminales/Terminal_Pruebas/terminal64.exe"#ruta terminal
#-----------------------------------------variblesCuenta--------------------------------------------------------





#---------------------------------------------------------------------------------------------------------
autorizar=mt5.initialize(ruta,login=cuenta,Password=contraseña,server=servidor)
if autorizar:
    print("CUENTA GRAN HEIKEN: "+str(cuenta))
else:
    print("error el terminal cuenta 1", mt5.last_error())
    quit()
#---------------------------------------------------------------------------------------------------------





#------------------------------------------hilos----------------------------------------------------------
hilo1 = threading.Thread(target=inicio,args=(riesgo,))#manera correcta de pasar parametros a un hilo, con ","
hilo2 = threading.Thread(target=cuandoCerrar)
hilo3 = threading.Thread(target=be)
hilo1.start()
hilo2.start()
hilo3.start()


#------------------------------------------hilos----------------------------------------------------------

