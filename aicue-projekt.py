import multiprocessing 
from csv import writer
from datetime import datetime
import math
import time
import os
import sys

Icgoal = 0.001
Ube = 0.7
Beta = 250
Temp25 = 25
Tempn15 = -15
Temp50 = 50
Ucc = 12.0
Ucegoal = 4.8

def priorytet(): #nietestowane poza Windowsem, os.system() powoduje czarne okno na początku działania skryptu
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True
    if isWindows:
        os.system("wmic process where processid=\""+str(os.getpid())+"\" CALL setpriority 64")
    else:
        if os.nice(0) <= 0:
            os.nice(5)

def czas():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj, delimiter=';')
        csv_writer.writerow(list_of_elem)

def temperatura():
    global Temp25
    Temp25 = float(input("Wprowadź podstawową temperaturę [°C] (domyślnie 25 °C): "))
    global Tempn15
    Tempn15 = float(input("Wprowadź niższą? temperaturę [°C] (domyślnie -15 °C): "))
    global Temp50
    Temp50 = float(input("Wprowadź wyższą? temperaturę [°C] (domyślnie 50 °C): "))

def napiecia():
    global Ucc
    Ucc = float(input("Wprowadź napięcie zasilające układ Ucc [V] (domyślnie 12.0 V): "))
    global Ucegoal
    Ucegoal = float(input("Wprowadź pożądane napięcie Uce [V] (domyślnie 4.8 V): "))

def podstawoweParametry():
    global Icgoal
    Icgoal = float(input("Wprowadź porządany prąd kolektora [mA] (założony): "))*0.001
    global Ube
    Ube = float(input("Wprowadź napięcie Ube [V] (karta katalogowa): "))
    global Beta
    Beta = float(input("Wprowadź wzmocnienie Beta [1] (karta katalogowa): "))

def tolerance(proces,return_dict,postep,R1start,Szereg,Zakres,Ucc,Ucegoal,Icgoal,Ube,Beta,Ube_n15,Beta_n15,Ube_50,Beta_50):
    return_dict[proces]=[]
    wynik=[]
    postep[proces]=0
    for podstawaR1 in Zakres:
        R1 = round(R1start*podstawaR1,1) #każdy możliwy R1, początkowy E24 definiowany przez proces
        for podstawaR2 in Zakres:
            for mnoznikR2 in Szereg:
                R2 = round(podstawaR2*mnoznikR2,1) #każdy możliwy R2
                postep[proces]=postep[proces]+1
                Ubb =   (R2*Ucc)/(R1+R2)
                Rb  =   (R1*R2)/(R1+R2)
                for podstawaRc in Zakres:
                    Szereg0 = [0]+Szereg.copy() #potencjalnie tylko Rc i Re mogą być równe 0.
                    for mnoznikRc in  Szereg0:
                        Rc = round(podstawaRc*mnoznikRc,1) #każdy możliwy Rc
                        for podstawaRe in Zakres:
                            for mnoznikRe in  Szereg0:
                                Re = round(podstawaRe*mnoznikRe,1) #każdy możliwy Re
                                Ib  =   (Ubb-Ube)/(Rb+((Beta+1)*Re))
                                Ie  =   (Beta+1)*Ib
                                Ic  =   Beta*Ib
                                Uce =   Ucc-(Ic*Rc)-(Ie*Re)
                                Tolerancja_Ic = round(((Ic/Icgoal)*100-100),2)
                                if(Tolerancja_Ic < 5 and Tolerancja_Ic > -5):
                                    Toleranja_Uce = round(((Uce/Ucegoal)*100-100),2)
                                    if(Toleranja_Uce < 5 and Toleranja_Uce > -5):
                                        Ib_n15  =   (Ubb-Ube_n15)/(Rb+((Beta_n15+1)*Re))
                                        Ie_n15  =   (Beta_n15+1)*Ib_n15
                                        Ic_n15  =   Beta_n15*Ib_n15
                                        Uce_n15 =   Ucc-(Ic_n15*Rc)-(Ie_n15*Re)
                                        Tolerancja_Ic_n15 = round(((Ic_n15/Icgoal)*100-100),2)
                                        if(Tolerancja_Ic_n15 < 5 and Tolerancja_Ic_n15 > -5):
                                            Toleranja_Uce_n15 = round(((Uce_n15/Ucegoal)*100-100),2)
                                            if(Toleranja_Uce_n15 < 5 and Toleranja_Uce_n15 > -5):
                                                Ib_50  =   (Ubb-Ube_50)/(Rb+((Beta_50+1)*Re))
                                                Ie_50  =   (Beta_50+1)*Ib_50
                                                Ic_50  =   Beta_50*Ib_50
                                                Uce_50 =   Ucc-(Ic_50*Rc)-(Ie_50*Re)
                                                Tolerancja_Ic_50 = round(((Ic_50/Icgoal)*100-100),2)
                                                if(Tolerancja_Ic_50 < 5 and Tolerancja_Ic_50 > -5):
                                                    Toleranja_Uce_50 = round(((Uce_50/Ucegoal)*100-100),2)
                                                    if(Toleranja_Uce_50 < 5 and Toleranja_Uce_50 > -5):
                                                        wynik+=[[R1,R2,Rc,Re,Ic,Ic_n15,Ic_50,Uce,Uce_n15,Uce_50,Tolerancja_Ic,Tolerancja_Ic_n15,Tolerancja_Ic_50,Toleranja_Uce,Toleranja_Uce_n15,Toleranja_Uce_50]]
    return_dict[proces]+=wynik
    
if __name__ == "__main__": 
    Szereg = [10,11,12,13,15,16,18,20,22,24,27,30,33,36,39,43,47,51,56,62,68,75,82,91]

    Zakres = [0.1, 1 , 10, 100, 1000, 10000, 100000, 1000000]
    #każdy możliwy rezystor to coś z Szereg * Zakres -> od 1 Ohma do 9,1 MOhm
    #żeby uwzględniać rezystory 0 Ohm (brak rezystrów) trzeba by zabezpieczać wszystkie dzielenia

    priorytet()

    print("Ten program obliczy wszytkie możliwe konfiguracje R1, R2, Rc, Re")
    print("tranzystora bipolarnego w układzie potencjometrycznym.\n")

    podstawoweParametry()
    
    while(1):
        #Icgoal = float(input("Wprowadź porządany prąd kolektora [mA] (założony): "))*0.001
        #Ube = float(input("Wprowadź napięcie Ube [V] (karta katalogowa): "))
        #Beta = float(input("Wprowadź wzmocnienie Beta [1] (karta katalogowa): "))

        #Ube i Beta dla -15 (n15) i 50 stopni
        Ube_n15=Ube+(-0.002*(Tempn15-Temp25))
        Ube_50=Ube+(-0.002*(Temp50-Temp25))
        Beta_n15=Beta*(1+0.005*(Tempn15-Temp25))
        Beta_50=Beta*(1+0.005*(Temp50-Temp25))

        print("\nSzukanie rezystorów do układu potencjometrycznego dla konfiguracji:")
        print("\tUcc =",Ucc,"V\n")
        print("\tUbe =",Ube,"V [dla 25 stopni]")
        print("\tBeta =",Beta," [dla 25 stopni]\n")
        print("\tUbe =",round(Ube_n15,2),"V [dla",Tempn15,"stopni]")
        print("\tBeta =",round(Beta_n15,2)," [dla",Tempn15,"stopni]\n")
        print("\tUbe =",round(Ube_50,2),"V [dla",Temp50,"stopni]")
        print("\tBeta =",round(Beta_50,2)," [dla",Temp50,"stopni]\n")
        print("Aby uzyskać wyjściowo (dla wszystkich 3 temperatur):")
        print("\tIc =",round(Icgoal,5),"A (dopuszczalne 5% tolerancji)")
        print("\tUce =",Ucegoal,"V (dopuszczalne 5% tolerancji)")

        print("\n1. Kontynuuj (lub wciśnij t)")
        print("2. Edytuj Ic, Ube, Beta")
        print("3. Edytuj napięcie Ucc i Uce (zadane domyślnie)")
        print("4. Edytuj temperatury (zadane domyślnie)")
        print("5. Zakończ działanie skryptu (lub wciśnij cokolwiek)")
        decyzja = str(input("\nWybierz opcje [1-5]: "))
        if decyzja=="1" or decyzja=="t" or decyzja=="T":
            break
        elif decyzja=="2":
            podstawoweParametry()
        elif decyzja=="3":
            napiecia()
        elif decyzja=="4":
            temperatura()
        else:
            sys.exit()

    #multiprocesowe sprawy
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    postep = manager.dict()
    jobs = []
    czas_start = datetime.now();
    print("\nCzas startu: ",czas_start.strftime("%H:%M:%S"))
    print("Uruchamiam procesy liczące.")

    #tyle procesów ile zmiennych w Szereg, każdy proces bierze 1 wartość z szeregu dla R1 i przemnaża razy podstawę, podstawiając R2 Rc i Re.
    for i in range(len(Szereg)):
        p = multiprocessing.Process(target=tolerance, args=(i,return_dict,postep,Szereg[i],Szereg,Zakres,Ucc,Ucegoal,Icgoal,Ube,Beta,Ube_n15,Beta_n15,Ube_50,Beta_50))
        jobs.append(p)
        p.start()

    #wiem ile jest zmiennych i podstaw, wiem ile razy wykonają się pętle - z drugą iteracją pętli zwiększam liczniki w każdym procesie, tutaj na bierząco odczytuje
    print("\nCzekam aż każdy z procesów skończy obliczenia.")
    print("Aktualizacja postępu co 10 sekund, to chwilę potrwa:\n")
    while(1):
        pasek=0
        for i in postep.values():
            pasek=pasek+i
        print("Postęp: ",str(round(pasek/(len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres))*100,3)),"% [",pasek,"/",len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres),"]")
        if pasek==(len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres)):
            break
        time.sleep(10) #wyświetlenie postępu co 10 sekund
    for proc in jobs: #pętla kończy się gdy przejdą wszystkie iteracje (procesy się zakończą)
        proc.join()
        
    czas_procesy = czas();
    print("[Procesy skończyły (",czas_procesy,")]")
    nazwa = "Projekt-kombinacje-rezystorów_"+str(Icgoal*1000)+"mA_"+str(Ube)+"V_"+str(math.floor(Beta))+".csv" #nazwa pliku, .csv
    print("\nZaczynam zapis do formatu .csv (to też chwilę potrwa)")
    czyscplik = open(nazwa, 'w', newline='') #wyczyszczenie, jeżeli wcześniej plik był już utworzony
    czyscplik.close();
    append_list_as_row(nazwa, ["R1","R2","Rc","Re","Ic(+25)[A]","Ic(-15)[A]","Ic(+50)[A]","Uce(+25)[V]","Uce(-15)[V]","Uce(+50)[V]","Tol. Ic(+25)[%]","Tol.Ic(-15)[%]","Tol.Ic(+50)[%]","Tol.Uce(+25)[%]","Tol.Uce(-15)[%]","Tol.Uce(+50)[%]"]) #header
    licznik = 0
    for i in return_dict:
        for j in return_dict[i]:
            for indeks,element in enumerate(j): 
                j[indeks] = str(element).replace(".",",") #formatowanie do bezpośredniego wczytania do EXCELA
            append_list_as_row(nazwa, j) #dopisywanie danych z każdego procesu linijka po linijce
            licznik = licznik + 1 #licznik do sumowania poprawnych konfiguracji
    print("Plik został zapisany jako:",nazwa)
    print("(zapisany w scieżce odplenia skryptu)")
    czas_koniec = datetime.now();
    print("\nCzas startu:",czas_start.strftime("%H:%M:%S"))
    print("Czas końca :",czas_koniec.strftime("%H:%M:%S"))
    print("Różnica czasu :",(czas_koniec-czas_start))
    print("\nZnaleziono",licznik,"rozwiązań spośród",len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres),"kombinacji rezystorów.")
    input("\nWciśnij jakikolwiek przycisk by zakończyć...")

