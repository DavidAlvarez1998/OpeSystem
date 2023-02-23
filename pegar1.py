import os
import MetaTrader5 as mt5
import pickle as pi
import time




'''
cuenta=61126871
contraseña="uj0xtfr3"
servidor="mt5-demo01.pepperstone.com"
rutaTerminal=os.path.join(os.path.dirname(os.path.abspath(__file__)),'terminales/pegar1/terminal64.exe')#ruta terminal
rutaDatos=os.path.join(os.path.dirname(os.path.abspath(__file__)),'DATA')#ruta data
autorizar=mt5.initialize(rutaTerminal,login=cuenta,Password=contraseña,server=servidor)

'''
mensaje="cuenta pegar1 reni: "
#---------------------------------------------DATOS PEGAR1--------------------------------------------

cuenta=7147703
contraseña="1IbCicPb"
servidor="ICMarketsSC-MT5-2"
rutaTerminal=os.path.join(os.path.dirname(os.path.abspath(__file__)),'terminales/pegar1/terminal64.exe')#ruta terminal
rutaDatos=os.path.join(os.path.dirname(os.path.abspath(__file__)),'DATA')#ruta data
autorizar=mt5.initialize(rutaTerminal,login=cuenta,Password=contraseña,server=servidor)

#-----------------------------------------------------------------------------------------------------



if autorizar:
    print(mensaje+str(cuenta))
else:
    print("error el terminal", mt5.last_error())
    quit()

try:
    os.remove("datos")
except:
    1


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
            "comment": "python script open",
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
        simbolo=ope[1]
        ope=trades[i]
        tikectTrades=ope[1]#tickec de orden, cuenta segundaria             
        slTrades=ope[3]
        tpTrades=ope[4]
        if slTrades != slData or tpTrades != tpData:
            modificar(simbolo,tikectTrades,slData,tpData)
        if slData == 0 or tpData == 0:
            modificar(simbolo,tikectTrades,slData,tpData)
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
                sl=ope[3]
                tp=ope[4]
                tipo=ope[5]
                ordenar(simbolo,lote,sl,tp,tipo)
                
                operaciones=mt5.positions_get()
                operaciones=operaciones[-1]
                x.append(tikect)
                x.append(operaciones[0])
                x.append(operaciones[5])
                x.append(operaciones[11])
                x.append(operaciones[12])
                x.append(operaciones[9])
                x.append(operaciones[16])
                trades.append(x)
    
            if len(data)>0:
                modificando(data,trades)#cambia el tp y el stop si han cambiado
            
            if len(data) < len(trades):#se cerro orden
                trades=queOrdenSeCerro(data,trades)
            time.sleep(0.2)
        except:
            time.sleep(0.2)

copiarOrden(rutaDatos)
 