# TODO:
# 1. zmiana priorytetu procesów na mniejsze
# 2. optymalizacja liczenia
# 3. sprawdzanie czy brak rezystora (0) pomaga
#

import multiprocessing 
from csv import writer
from datetime import datetime
import math
import time

def czas():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)

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
                for podstawaRc in Zakres:
                    for mnoznikRc in  Szereg:
                        Rc = round(podstawaRc*mnoznikRc,1) #każdy możliwy Rc
                        for podstawaRe in Zakres:
                            for mnoznikRe in  Szereg:
                                Re = round(podstawaRe*mnoznikRe,1) #każdy możliwy Re
                                Ubb =   float( (R2*Ucc)/(R1+R2) )
                                Rb  =   float( (R1*R2)/(R1+R2) )
                                Ib  =   float( (Ubb-Ube)/(Rb+((Beta+1)*Re)) )
                                Ie  =   float( (Beta+1)*Ib )
                                Ic  =   float( Beta*Ib )
                                Uce =   float( Ucc-(Ic*Rc)-(Ie*Re) )
                                
                                Tolerancja_Ic = round(((Ic/Icgoal)*100-100),2)
                                Toleranja_Uce = round(((Uce/Ucegoal)*100-100),2)

                                Ib_n15  =   float( (Ubb-Ube_n15)/(Rb+((Beta_n15+1)*Re)) )
                                Ie_n15  =   float( (Beta_n15+1)*Ib_n15 )
                                Ic_n15  =   float( Beta_n15*Ib_n15 )
                                Uce_n15 =   float( Ucc-(Ic_n15*Rc)-(Ie_n15*Re) )

                                Tolerancja_Ic_n15 = round(((Ic_n15/Icgoal)*100-100),2)
                                Toleranja_Uce_n15 = round(((Uce_n15/Ucegoal)*100-100),2)

                                Ib_50  =   float( (Ubb-Ube_50)/(Rb+((Beta_50+1)*Re)) )
                                Ie_50  =   float( (Beta_50+1)*Ib_50 )
                                Ic_50  =   float( Beta_50*Ib_50 )
                                Uce_50 =   float( Ucc-(Ic_50*Rc)-(Ie_50*Re) )

                                Tolerancja_Ic_50 = round(((Ic_50/Icgoal)*100-100),2)
                                Toleranja_Uce_50 = round(((Uce_50/Ucegoal)*100-100),2)
                                if Tolerancja_Ic < 5 and Tolerancja_Ic > -5 and Toleranja_Uce < 5 and Toleranja_Uce > -5 and Tolerancja_Ic_n15 < 5 and Tolerancja_Ic_n15 > -5 and Toleranja_Uce_n15 < 5 and Toleranja_Uce_n15 > -5 and Tolerancja_Ic_50 < 5 and Tolerancja_Ic_50 > -5 and Toleranja_Uce_50 < 5 and Toleranja_Uce_50 > -5:
                                    wynik+=[[R1,R2,Rc,Re,Toleranja_Uce,Tolerancja_Ic,Toleranja_Uce_n15,Tolerancja_Ic_n15,Toleranja_Uce_50,Tolerancja_Ic_50]]
    return_dict[proces]+=wynik
    
if __name__ == "__main__": 
    Szereg = [10,11,12,13,15,16,18,20,22,24,27,30,33,36,39,43,47,51,56,62,68,75,82,91]
    Zakres = [0.1, 1 , 10, 100, 1000, 10000, 100000, 1000000]
    #każdy możliwy rezystor to coś z Szereg * Zakres -> od 1 Ohma do 9,1 MOhm
    #żeby uwzględniać rezystory 0 Ohm (brak rezystrów) trzeba by zabezpieczać wszystkie dzielenia
    
    while(1):
        Icgoal = float(input("Wprowadź porządany prąd kolektora [mA]: "))*0.001
        Ube = float(input("Wprowadź napięcie Ube [V]: "))
        Beta = float(input("Wprowadź wzmocnienie Beta [1]: "))

        #Ube i Beta dla -15 (n15) i 50 stopni
        Ube_n15=Ube+(-0.002*-40)
        Ube_50=Ube+(-0.002*25)
        Beta_n15=Beta*(1+0.005*-40)
        Beta_50=Beta*(1+0.005*25)

        Ucc=float(12)
        Ucegoal=float(4.8)

        print("\nSzukanie rezystorów do układu potencjometrycznego dla konfiguracji:")
        print("\tUcc =",Ucc,"V")
        print("\tUbe =",Ube,"V [dla 25 stopni]")
        print("\tBeta =",Beta," [dla 25 stopni]")
        print("Aby uzyskać wyjściowo:")
        print("\tIc =",round(Icgoal,5),"A (dopuszczalne 5% tolerancji)")
        print("\tUce =",Ucegoal,"V (dopuszczalne 5% tolerancji)")

        decyzja = input("Czy chcesz konytnuować? [t/n]: ")
        if decyzja=="t" or decyzja=="T":
            break

    #multiprocesowe sprawy
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    postep = manager.dict()
    jobs = []
    print("\nCzas startu: ",czas())
    print("Uruchamiam procesy liczące")

    #tyle procesów ile zmiennych w Szereg, każdy proces bierze 1 wartość z szeregu dla R1 i przemnaża razy podstawę, podstawiając R2 Rc i Re.
    for i in range(len(Szereg)):
        p = multiprocessing.Process(target=tolerance, args=(i,return_dict,postep,Szereg[i],Szereg,Zakres,Ucc,Ucegoal,Icgoal,Ube,Beta,Ube_n15,Beta_n15,Ube_50,Beta_50))
        jobs.append(p)
        p.start()

    #wiem ile jest zmiennych i podstaw, wiem ile razy wykonają się pętle - z drugą iteracją pętli zwiększam liczniki w każdym procesie, tutaj na bierząco odczytuje
    print("\nCzekam aż każdy z procesów skończy obliczenia (to potrwa baaaardzo długo):")
    while(1):
        pasek=0
        for i in postep.values():
            pasek=pasek+i
        print("Postęp: ",str(round(pasek/(len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres))*100,3)),"% [",pasek,"/",len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres),"]")
        if pasek==(len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres)):
            break
        time.sleep(5) #wyświetlenie postępu co 5 sekund
    for proc in jobs: #pętla kończy się gdy przejdą wszystkie iteracje (procesy się zakończą), ale dla pewności zamykamy procesy
        proc.join()
    
    print("[Procesy skończyły (",czas(),")]")
    nazwa = "Projekt-wyniki_"+str(Icgoal*1000)+"mA_"+str(Ube)+"V_"+str(math.floor(Beta))+".csv" #nazwa pliku, .csv
    print("\nZaczynam zapis do formatu .csv (to też chwilę potrwa)")
    czyscplik = open(nazwa, 'w', newline='') #wyczyszczenie, jeżeli wcześniej plik był już utworzony
    czyscplik.close();
    append_list_as_row(nazwa, ["R1","R2","Rc","Re","dUce","dIc","dUce(-15)","dIc(-15)","dUce(+50)","dIc(+50)"]) #header
    licznik = 0
    for i in return_dict:
        for j in return_dict[i]:
            append_list_as_row(nazwa, j) #dopisywanie danych z każdego procesu linijka po linijce
            licznik = licznik + 1 #licznik do sumowania poprawnych konfiguracji
    print("Czas końca: ",czas())
    print("Plik został zapisany jako:",nazwa)
    print("(zapisany w scieżce odplenia skryptu)")
    print("Czas końca: ",czas())
    print("Znaleziono",licznik,"rozwiązań spośród",len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres)*len(Szereg)*len(Zakres),"kombinacji rezystorów.")
    input("\nWciśnij jakikolwiek przycisk by zakończyć...")