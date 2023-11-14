import matplotlib.pyplot as plt
from typing import Tuple, List
from itertools import product
import math


class Koule:
    def __init__(self, hmotnost:float,prumer:float) -> None:
        self.hmotnost = hmotnost
        self.prumet_koule = math.pi * prumer**2 / 4
        self.cinitel_odporu = 0.5
     
        
class Delo:
    def __init__(self,uhel:int, pocatecni_rychlost:int) -> None:
        self.uhel = math.radians(uhel)
        self.pocatecni_rychlost = pocatecni_rychlost
        
    def natoc_delo(self, uhel:int):
        self.uhel = math.radians(uhel)
    
    def zmen_rychlost(self, rychlost:int):
        self.rychlost = rychlost
    
    
class Prostredi:
    def __init__(self, hustota_vzduchu:float) -> None:
        self.hustota_vzduchu = hustota_vzduchu
        
        
class Simulace:
    def __init__(self, casovy_krok:float,delo: Delo, koule: Koule, prostredi: Prostredi=None) -> None:
        self.casovy_krok = casovy_krok
        self.tihove_zrychleni=9.8
        self.koule = koule # do objektu vlozime objekt a abychom mohli pouzivat jeho promemy a jeho metody (agregace) 
        self.delo = delo
        self.prostredi = prostredi
        self.x = [0.0]
        self.y = [0.0]
        
    def spocitej_sikmy_vrh(self)-> Tuple[List[float], List[float]]:      
        rychlost_x= self.delo.pocatecni_rychlost * math.cos(self.delo.uhel)
        rychlost_y= self.delo.pocatecni_rychlost * math.sin(self.delo.uhel)
        
        while self.y[-1] >= 0:
            if self.prostredi:
                rychlost= math.sqrt(rychlost_x**2 + rychlost_y**2)
               
                odpor_vzduchu_x = -0.5 * self.koule.cinitel_odporu * self.koule.prumet_koule * self.prostredi.hustota_vzduchu * rychlost * rychlost_x 
                odpor_vzduchu_y = -0.5 * self.koule.cinitel_odporu * self.koule.prumet_koule * self.prostredi.hustota_vzduchu * rychlost * rychlost_y
                
                zrychleni_x = odpor_vzduchu_x / self.koule.hmotnost
                zrychleni_y = odpor_vzduchu_y / self.koule.hmotnost - self.tihove_zrychleni
                
            else:
                zrychleni_x = 0.0
                zrychleni_y = - self.tihove_zrychleni
                
            rychlost_x += zrychleni_x * self.casovy_krok
            rychlost_y += zrychleni_y * self.casovy_krok
            
            self.x.append(self.x[-1] + rychlost_x * self.casovy_krok)
            self.y.append(self.y[-1] + rychlost_y * self.casovy_krok)
            
        return self.x, self.y    
    
    def vykresli_graf(self, vysledky:List[Tuple[List[float], List[float]]]):
        plt.figure(figsize=(12, 8))
        plt.plot(self.x, self.y )
        plt.grid(True)
        plt.show()        


def main():
    uhly = [30, 45, 75]
    rychlosti = [10, 20, 30]
    pocatecni_podminky = product(uhly, rychlosti)
    
    koule= Koule(hmotnost=0.05, prumer=0.01)
    prostredi = Prostredi(hustota_vzduchu=1.2225)
    delo = Delo(uhel=30, pocatecni_rychlost=30)
    vysledky = []

    for uhel, rychlost in pocatecni_podminky:
        delo.natoc_delo(uhel=uhel)
        delo.zmen_rychlost(rychlost=rychlost)
        simulace = Simulace(casovy_krok=0.001, delo= delo, koule=koule, prostredi=prostredi)
        vysledky.append(simulace.spocitej_sikmy_vrh())
        
    simulace.vykresli_graf(vysledky=vysledky)
        

#     plt.subplot(2, 1, 1)
#     for uhel in uhly:
#         poloha_x, poloha_y = spocitej_sikmy_vrh(uhel,pocatecni_rychlost=10, odpor_prostredi=True)
#         plt.plot(poloha_x, poloha_y, label=f'{uhel}° s odporem')
#         poloha_x1, poloha_y1 = spocitej_sikmy_vrh(uhel,pocatecni_rychlost = 10, odpor_prostredi = False)
#         #print(poloha_x1,poloha_y1)
#         plt.plot(poloha_x1, poloha_y1, label=f'{uhel}° bez odporu')    
#     plt.title('Porovnani grafu s odporem vzduchu a bez, ruzne stupne ')
#     plt.xlabel('x (m)')
#     plt.ylabel('y (m)')
#     plt.legend()
#     plt.grid(True)
#     # # #2
#     plt.subplot(2, 1, 2)
#     for rychlost in rychlosti:
#         poloha_x, poloha_y = spocitej_sikmy_vrh(30, rychlost, odpor_prostredi=True)
#         plt.plot(poloha_x, poloha_y, label=f'{rychlost} m/s s odporem')
#         poloha_x1, poloha_y1 = spocitej_sikmy_vrh(30, rychlost, odpor_prostredi=False)
#         plt.plot(poloha_x1, poloha_y1, label=f'{rychlost} m/s bez odporu' )    
#     plt.title('Porovnani grafu s odporem vzduchu a bez, ruzne rychlosti ')
#     plt.xlabel('x (m)')
#     plt.ylabel('y (m)')
#     plt.legend()
#     plt.grid(True)

#     plt.tight_layout()
#     # plt.savefig('ctri.png')
#     plt.show()


if __name__ == "__main__":
    main()