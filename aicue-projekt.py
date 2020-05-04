# Todo
# 1. Wielowątkowość

from datetime import datetime
from csv import writer
import math

def czas():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)

Icgoal = float(input("Wprowadź porządany prąd kolektora [mA]: "))*0.001
Ube = float(input("Wprowadź napięcie Ube [V]: "))
Beta = float(input("Wprowadź wzmocnienie Beta [1]: "))

Ube_n15=Ube+(-0.002*-40)
Ube_55=Ube+(-0.002*30)

Beta_n15=Beta*(1+0.005*-40)
Beta_55=Beta*(1+0.005*30)

Ucc=float(12)
Ucegoal=float(4.8)

print("Wprowadzono następujące wartosci:\n")
print("Ic =",Icgoal,"A")
print("Ube =",Ube,"V")
print("Beta =",Beta)

E24 = [10,11,12,13,15,16,18,20,22,24,27,30,33,36,39,43,47,51,56,62,68,75,82,91]
#zakres dopuszczalnych rezystorów od 1 Ohma * E24 do 910 kOhm * E24 
Zakres = [0.1, 1 , 10, 100, 1000, 10000, 100000]

print("Zaczynam podstawianie rezystorów w celu uzyskania tolerancji dla każdego zestawu rezystorów \n(to potrwa dość długo, trzeba przeliczyć ~800 milionów kombinacji)")
print("\nCzas startu:",czas())
nazwa = "Projekt-wyniki_"+str(Icgoal*1000)+"mA_"+str(Ube)+"V_"+str(math.floor(Beta))+".csv"
print("\nWyniki zostaną zapisane do pliku",nazwa)
print("Format wyniku: R1,R2,Rc,Re,Tol. Uce, Tol. Ic, Tol. Uce(-15 stopni), Tol. Ic(-15), Tol. Uce(55), Tol. Ic(55)\n")

czyscplik = open(nazwa, 'w', newline='')
czyscplik.close();
iteracja = 0;
postep = 0;
for podstawaR1 in Zakres:
    for mnoznikR1 in E24:
        R1 = round(podstawaR1*mnoznikR1,1) #każdy możliwy R1
        print("[",czas(),"] Postęp: ",round(postep/168*100,2),"% (znaleziono na razie",iteracja,"rozwiązań)")
        postep=postep+1
        for podstawaR2 in Zakres:
            for mnoznikR2 in  E24:
                R2 = round(podstawaR2*mnoznikR2,1) #każdy możliwy R2
                for podstawaRc in Zakres:
                    for mnoznikRc in  E24:
                        Rc = round(podstawaRc*mnoznikRc,1) #każdy możliwy Rc
                        for podstawaRe in Zakres:
                            for mnoznikRe in  E24:
                                Re  =   round(podstawaRe*mnoznikRe,1) #każdy możliwy Re
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

                                Ib_55  =   float( (Ubb-Ube_55)/(Rb+((Beta_55+1)*Re)) )
                                Ie_55  =   float( (Beta_55+1)*Ib_55 )
                                Ic_55  =   float( Beta_55*Ib_55 )
                                Uce_55 =   float( Ucc-(Ic_55*Rc)-(Ie_55*Re) )

                                Tolerancja_Ic_55 = round(((Ic_55/Icgoal)*100-100),2)
                                Toleranja_Uce_55 = round(((Uce_55/Ucegoal)*100-100),2)

                                if Tolerancja_Ic < 5 and Tolerancja_Ic > -5 and Toleranja_Uce < 5 and Toleranja_Uce > -5 and Tolerancja_Ic_n15 < 5 and Tolerancja_Ic_n15 > -5 and Toleranja_Uce_n15 < 5 and Toleranja_Uce_n15 > -5 and Tolerancja_Ic_55 < 5 and Tolerancja_Ic_55 > -5 and Toleranja_Uce_55 < 5 and Toleranja_Uce_55 > -5:
                                    append_list_as_row(nazwa, [R1,R2,Rc,Re,Toleranja_Uce,Tolerancja_Ic,Toleranja_Uce_n15,Tolerancja_Ic_n15,Toleranja_Uce_55,Tolerancja_Ic_55])
                                    iteracja = iteracja+1
print("Czas końca: ",czas())
print("Zakończono pracę, znaleziono",iteracja,"rozwiązań dla których tolerancja prądu i napięcia dla każdej temperatury jest mniejsza niż 5%.")
print("Wyniki zostały zapisane w pliku",nazwa,"w lokalizacji uruchomienia skryptu.")
input("Wciśnij jakikolwiek przycisk by zakończyć...")
