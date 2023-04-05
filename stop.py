
cuenta=10000

riesgoPor=1

riesgo=cuenta*riesgoPor/100
print("cuenta: "+str(cuenta)+"\nriesgo: "+str(riesgoPor)+"%"+"  "+str(int(riesgo))+"$")
while 1:
    pips=float(input("pips: "))
    lote=0.01
    while lote*pips<=riesgo:
        lote+=0.001
    print(lote)



