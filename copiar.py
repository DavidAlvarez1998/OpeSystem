import MetaTrader5 as mt5
import pickle as pi
import time
import os



'''
cuenta=61129885
contraseña="qB0fnmv3"
servidor="mt5-demo01.pepperstone.com"
rutaTerminal=os.path.join(os.path.dirname(os.path.abspath(__file__)),'terminales/copiar/terminal64.exe')#ruta terminal
rutaDatos=os.path.join(os.path.dirname(os.path.abspath(__file__)),'DATA')#ruta data
autorizar=mt5.initialize(rutaTerminal,login=cuenta,Password=contraseña,server=servidor)

'''
mensaje="cuenta copiar Noah: "
#---------------------------------------------DATOS COPIAR--------------------------------------------

cuenta=300371831
contraseña="vmdmrufg34"
servidor="TradersGlobalGroup-Demo"
rutaTerminal=os.path.join(os.path.dirname(os.path.abspath(__file__)),'terminales/copiar/terminal64.exe')#ruta terminal
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
def actualizarData(rutaDatos): 
    while 1:
        datos=[]
        i=0
        operaciones=mt5.positions_get()
        numeeroOpe=len(operaciones)
        while numeeroOpe>0 and i<numeeroOpe:
            tikect=operaciones[i][0]
            simbolo=operaciones[i][16]
            lote=operaciones[i][9]
            sl=operaciones[i][11]
            tp=operaciones[i][12]
            tipo=operaciones[i][5]
            cuenta=mt5.account_info() #tamaño de la cuenta
            cuenta=cuenta[13]         #tamaño de la cuenta
            lista=[tikect,simbolo,lote,sl,tp,tipo,cuenta] 
            datos.append(lista)
            i=i+1
        data=open(rutaDatos,"wb")#abrimos en escritura
        pi.dump(datos,data)#agregamos la lista al archivo
        data.close
        time.sleep(0.1)
actualizarData(rutaDatos)
















