
import time

def respira():
    n=0
    while 1:
        n=n+1
        time.sleep(1)
        print(n)
        if n==5:
            time.sleep(0.5)
            n=n+0.5
            print(str(n)+" cambio")
            n=0
respira()



def respiraAuto():
    n=0
    while 1:
        n=n+1
        time.sleep(1)
        print(n)
        if n==5:
            time.sleep(0.5)
            n=n+0.5
            print(str(n)+" cambio")
            n=0



