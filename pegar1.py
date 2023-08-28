import os
import MetaTrader5 as mt5
import pickle as pi
import time



#---------------------------------------------DATOS CUENTA PEGAR--------------------------------------------
mensaje="cuenta pegar1 mia: "
cuenta=51254060
contraseña="9s5TSJxI"
servidor="ICMarketsSC-Demo"
rutaTerminal=os.path.join(os.path.dirname(os.path.abspath(__file__)),'terminales/pegar1/terminal64.exe')#ruta terminal
rutaDatos=os.path.join(os.path.dirname(os.path.abspath(__file__)),'DATA')#ruta data
autorizar=mt5.initialize(rutaTerminal,login=cuenta,Password=contraseña,server=servidor)

#/--------------------------------------------DATOS CUENTA PEGAR--------------------------------------------



if autorizar:
    balance=mt5.account_info() #tamaño de la cuenta actual
    balance=balance[13]         #tamaño de la cuenta actual
    print(mensaje+'\ncuenta: '+str(cuenta)+'\nbalance: '+str(balance))
else:
    print("error el terminal", mt5.last_error())
    quit()

try:
    os.remove("datos")
except:
    1

def copiarOrden(rutaDatos):
    trades=[]# [ticketPrincipal,ticketSegundario,tipo,sl,tp,lote,simbolo,]
    while 1:
        try:
            data=open(rutaDatos,"rb")#abrimos en lectura
            data=pi.load(data)#pasamos de binario a list
            if len(data) > len(trades):#nueva orden 
                x=[]
                ope=data[-1]
                tikect=ope[0]
                simbolo=ope[1]
                #-------calculo lotage----------
                cuenta=ope[-1]#tamaño cuenta principal
                lote=ope[2]   #lote de orden cuenta principal
                lotePorcieto=(lote/cuenta)*100
                cuenta=mt5.account_info() #tamaño de la cuenta actual
                cuenta=cuenta[13]         #tamaño de la cuenta actual
                lote=lotePorcieto*cuenta/100 
                if lote<0.1:
                    lote=0.1
                lote=round(lote,1)
                #-----------------------------
                if simbolo=="NDX100":
                    simbolo="USTEC"
                sl=ope[3]
                tp=ope[4]
                tipo=ope[5]
                operacion=ordenar(simbolo,lote,sl,tp,tipo)
                #-----------informarcion de la orden------------------
                print(operacion)
                print("-------------------------------")
                #-----------------------------------------------------
                x.append(tikect)
                x.append(operacion[2])  
                x.append(operacion[10][10])
                x.append(operacion[10][7])
                x.append(operacion[10][8])
                x.append(operacion[10][4])
                x.append(operacion[10][3])
                x.append(operacion[10][5])
                trades.append(x)

            if len(data)>0: 
                modificando(data,trades)#cambia el tp y el stop si han cambiado

            if len(data) < len(trades):#se cerro orden
                trades=queOrdenSeCerro(data,trades)
            time.sleep(0.2) 
        except:
            time.sleep(0.2)

            
def ordenar(simbolo,lote,sl,tp,tipo):#monta orden en el mercado
    precio=mt5.symbol_info_tick(simbolo).ask
    deviation = 10
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
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # send a trading request
        result = mt5.order_send(request)
        # check the execution result 
        return result
        return result[2]#retornamos el ticket de la orden 
        
    else:
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
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        # check the execution result 
        return result
        return result[2]#retornamos el ticket de la orden 
        
def cerrarOrden(simbolo,ticket,lote,tipo):
    precio=mt5.symbol_info_tick(simbolo).ask
    deviation = 0
    if tipo == 0:
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

def modificar(simbolo,tikect,sl,tp):# modifica el sl y tp   
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": simbolo,
        "position": tikect,
        "sl": sl,
        "tp": tp,
        "magic": 235000,
        }
    result = mt5.order_send(request)

def modificando(data,trades):# compara el sl y el tp de cada orden
    i=0
    while i <len(data):#modificando sl y tp 
        ope=data[i]             
        slData=ope[3]
        tpData=ope[4]
        precioData=ope[7]
        puntosSLData=0
        puntosTPData=0
        puntosSLTrades=0
        puntosTPTrades=0
        tipo=ope[5]
        simbolo=ope[1]
        ope=trades[i]
        tikectTrades=ope[1]#tickec de orden, cuenta segundaria
        precioTrade=ope[7]          
        slTrades=ope[3]
        tpTrades=ope[4]
        
        
        #VARIABLES DE DATOS CUENTA COPIAR (precioData tpData slData)
        #print(tpData,slData)
        #print(ope)
        #--------calculo de puntos------
        if tipo==0:
            puntosSLData=precioData-slData
            puntosTPData=tpData-precioData 
            sl=precioTrade-puntosSLData
            tp=precioTrade+puntosTPData
            puntosTPTrades=tpTrades-precioTrade
            puntosSLTrades=precioTrade-slTrades

            
        elif tipo==1:
            puntosSLData=slData-precioData
            puntosTPData=precioData-tpData 
            sl=precioTrade+puntosSLData
            tp=precioTrade-puntosTPData
            puntosTPTrades=precioTrade-tpTrades
            puntosSLTrades=slTrades-precioTrade
        
        #--------calculo de puntos------
    
        if puntosSLTrades != puntosSLData or puntosTPTrades != puntosTPData:
            modificar(simbolo,tikectTrades,sl,tp)
        if slData == 0.0 and slTrades!=0.0: # caso cuando se elimina el SL
            modificar(simbolo,tikectTrades,0.0,tp)
        if tpData == 0.0 and tpTrades!=0.0:# caso cuando se elimina el TP
            modificar(simbolo,tikectTrades,sl,0.0)

        i=i+1

def queOrdenSeCerro(data,trades):
    if len(data)==0:#caso particular cuando se cierra la unica orden que hay
        ope=trades[0]
        ticket=ope[1] 
        simbolo=ope[6]
        lote=ope[5]        
        tipo=ope[2]
        cerrarOrden(simbolo,ticket,lote,tipo)
        trades=[]
    elif data[-1][0]!=trades[-1][0]:#caso particular cuando se cierra la ultima
        ope=trades[-1]
        ticket=ope[1] 
        simbolo=ope[6]
        lote=ope[5]        
        tipo=ope[2]
        cerrarOrden(simbolo,ticket,lote,tipo)
        trades.pop(-1)
    elif len(data)>0:
        i=0
        while i < len(data):
            ticket0=data[i][0]
            ticket1=trades[i][0]
            ticket2=trades[i][1]
            simbolo=trades[i][6]
            lote=trades[i][5] 
            tipo=trades[i][2]
            if ticket0 != ticket1:
                cerrarOrden(simbolo,ticket2,lote,tipo)
                trades.pop(i)
            i=i+1
 
    return trades



copiarOrden(rutaDatos)