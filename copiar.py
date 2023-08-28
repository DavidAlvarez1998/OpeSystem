import MetaTrader5 as mt5
import pickle as pi
import time
import os




mensaje="cuenta copiar mia: "
#---------------------------------------------DATOS COPIAR--------------------------------------------
'''
cuenta=61161211
contraseña="Or5ynex3"
servidor="mt5-demo01.pepperstone.com"
'''

cuenta=82116717
contraseña="nwahge5c47"
servidor="EightcapEU-Live"

rutaTerminal=os.path.join(os.path.dirname(os.path.abspath(__file__)),'terminales/copiar/terminal64.exe')#ruta terminal
rutaDatos=os.path.join(os.path.dirname(os.path.abspath(__file__)),'DATA')#ruta data
autorizar=mt5.initialize(rutaTerminal,login=cuenta,Password=contraseña,server=servidor)

#-----------------------------------------------------------------------------------------------------


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


def actualizarData(rutaDatos):
    cuenta=mt5.account_info() #tamaño de la cuenta
    cuenta=cuenta[13]         #tamaño de la cuenta
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
            precio=operaciones[i][10]
            lista=[tikect,simbolo,lote,sl,tp,tipo,cuenta,precio]
            datos.append(lista)
            i=i+1
        data=open(rutaDatos,"wb")#abrimos en escritura
        pi.dump(datos,data)#agregamos la lista al archivo
        data.close
        time.sleep(0.2)
actualizarData(rutaDatos)
















