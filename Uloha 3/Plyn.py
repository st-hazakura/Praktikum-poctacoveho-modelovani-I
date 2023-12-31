import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import maxwell
from matplotlib.animation import FuncAnimation, PillowWriter
from progress.bar import Bar
from typing import List, Tuple


BOLTZMANNOVA_KONSTANTA: float = 1.380649E-23
HMOTNOST_CASTICE: float = 1E-26 #kg
ROZMER_ATOMU: float = 1*1E-10   # 1 anstrem
POCET_ITERACI: int = 30000
POCET_EKVILIBRACNICH_KROKU: int = 10000
POCET_CASTIC: int = 200
TEPLOTY: int = [27, -27, -270]
POCET_GRAFU: int = 4
PRINT_MODULO: int = POCET_ITERACI / POCET_GRAFU
STATE_MODULO: int = POCET_ITERACI / 5
FONT_SIZE: int = 16


class Castice:
    def __init__(self, teplota, pocet_castic):
        self.pozice_castic =  []                                                   #posledni pozice a rychlosti vsech castic
        self.rychlosti_castic = np.array([])
        self.teplota = teplota
        self.pocet_castic = pocet_castic
        self.delka_jedne_steny = None                                              # nastavim pri vypoctech
        self.par_naim_t = None
        self.t_min = None


    def spocitat_tep_v_kelv(self):
        self.teplota = self.teplota + 273.15


    def spocitat_delku_steny(self):                                                # N/L^3 (vse v A (10^-10))= od 0.01 do 0.05 (pak prevest na metry) N>=100
        objem = int((self.pocet_castic / 0.04))
        self.delka_jedne_steny = int(objem**(1/3)) *1E-10                          # v metrech (1m = 1-10 anstrem)


    def generovani_pocatecnych_pozice_a_rychlosti(self):
        #rychlost
        sigma = np.sqrt(BOLTZMANNOVA_KONSTANTA * self.teplota / HMOTNOST_CASTICE)
        self.rychlosti_castic = np.random.normal(0, sigma, (self.pocet_castic, 3))  # ve 3 smerech x,y,z, norm rozlozeni s odhylkou sigma

        celk_rych = np.sum(self.rychlosti_castic, axis = 0)                         #sum rych[x1+x2...], [y1+y2...]...([sum.x,sum.y,sum.z])
        korekce = celk_rych / self.pocet_castic
        self.rychlosti_castic -= korekce

        posledni_korekce= np.sum(self.rychlosti_castic, axis = 0)
        self.rychlosti_castic[0] -= posledni_korekce


        #pozice
        krok = 2* ROZMER_ATOMU
        pozice_na_osu = np.arange(0, self.delka_jedne_steny/2, krok)
        for i in range(self.pocet_castic):
            for z in pozice_na_osu:
                for y in pozice_na_osu:
                    for x in pozice_na_osu:
                        self.pozice_castic.append([x,y,z])
                        if len(self.pozice_castic) == self.pocet_castic:
                            self.pozice_castic = np.array(self.pozice_castic)
                            return


    def nejmensi_cas_srazky(self):
        self.t_min= np.inf 
        for i in range(self.pocet_castic - 1):
            for j in range(i+1, self.pocet_castic):
                ri, rj = self.pozice_castic[i], self.pozice_castic[j]
                vi, vj = self.rychlosti_castic[i], self.rychlosti_castic[j]

                rij = ri - rj               # vektor
                rij = rij - self.delka_jedne_steny * np.round(rij/self.delka_jedne_steny)
                vij = vi - vj
                bij = np.dot(rij,vij)       # skalar
                if bij < 0:                 # posouvaji se k sobe
                    vij = np.dot(vij, vij)
                    rij = np.dot(rij, rij)
                    D = bij**2 - vij * (rij - ROZMER_ATOMU**2)
                    if D > 0:
                        t = (-bij - np.sqrt(D)) / (vij)
                        if 0 < t < self.t_min:
                            self.t_min = t
                            self.par_naim_t = (i,j)


    def kolize(self):
        i,j = self.par_naim_t
        ri, rj = self.pozice_castic[i], self.pozice_castic[j]
        vi, vj = self.rychlosti_castic[i], self.rychlosti_castic[j]

        rij = ri - rj
        rij = rij - self.delka_jedne_steny * np.round(rij/self.delka_jedne_steny)
        vij = vi - vj
        bij = np.dot(rij,vij)

        deltaV = (bij / ROZMER_ATOMU**2) * rij

        self.rychlosti_castic[i] -= deltaV
        self.rychlosti_castic[j] += deltaV


    def pohnout_casticema_o_tmin(self):
        for i in range(self.pocet_castic):
            self.pozice_castic[i] += self.t_min * self.rychlosti_castic[i]


            for dimenze in range(3):
                if self.pozice_castic[i][dimenze] < 0:
                    self.pozice_castic[i][dimenze] += self.delka_jedne_steny
                elif self.pozice_castic[i][dimenze] >= self.delka_jedne_steny:
                    self.pozice_castic[i][dimenze] -= self.delka_jedne_steny


    def generovat_zacatek(self):
        self.spocitat_tep_v_kelv()
        self.spocitat_delku_steny()
        self.generovani_pocatecnych_pozice_a_rychlosti()


    def mihani_castic(self, pocet_iteraci_mihani):
        for i in range(pocet_iteraci_mihani):
            self.nejmensi_cas_srazky()
            self.pohnout_casticema_o_tmin()
            self.kolize()
            if i % PRINT_MODULO == 0:
                self.porovnani_s_max_rozd(iterace=i)
            if i % STATE_MODULO == 0:
                print(f"Teplota: {self.teplota}, {round(float(i)/pocet_iteraci_mihani*100, 0)} % HOTOVO")


    def porovnani_s_max_rozd(self, iterace: int, zapis_do_souboru: bool = False) -> None:
        modul_rychlosti = np.sqrt(np.sum(self.rychlosti_castic**2, axis = 1))   #v1=[sqrt(x1^2 + y1^2)], v2=[sqrt(x2^2 + y2^2)]
        plt.figure( figsize=(10,6))
        plt.hist(modul_rychlosti, bins = 20, density= True, alpha = 0.6)

        skalovani = np.sqrt(BOLTZMANNOVA_KONSTANTA * self.teplota / HMOTNOST_CASTICE)
        sorted_rychl = np.sort(modul_rychlosti)
        plt.rc('font', size=FONT_SIZE)
        plt.xlim(0, 2600)
        plt.xlabel("v [m/s]")
        plt.ylabel("f(v)")
        plt.title(f"Rozdělení rychlosti molekul (iterace={iterace}, teplota={int(round(self.teplota, 0))})")
        hustoty_pravdepodobnosti = maxwell.pdf(sorted_rychl, scale = skalovani)
        plt.plot(sorted_rychl, hustoty_pravdepodobnosti)

        #plt.show()
        plt.savefig(f"Grafy/mb_iterace_{int(round(self.teplota, 0))}_{iterace}.jpg")
        
        if zapis_do_souboru:
            nazev_souboru = f"Grafy/mb_data_teplota_{int(round(self.teplota, 0))}_iterace_{iterace}.txt"
            self.zapis_MBdata_do_souboru(data=list(zip(sorted_rychl, hustoty_pravdepodobnosti)), nazev_souboru=nazev_souboru)
        
    def zapis_MBdata_do_souboru(self, data: List[Tuple[float, float]], nazev_souboru: str):
        with open(nazev_souboru, "w") as soubor:
            for dvojice in data:
                soubor.write(f"{dvojice[0]} {dvojice[1]}\n")


    def mihani_castic_anim(self):
        self.nejmensi_cas_srazky()
        self.pohnout_casticema_o_tmin()
        self.kolize()


    def animovat_mihani_castic(self, num_steps=200, gif_name="beznazvu.gif"):
        fig = plt.figure(figsize=(9, 12))
        ax = fig.add_subplot(111, projection='3d')

        data_poloh = np.array(self.pozice_castic)
        x, y, z = data_poloh[:,0], data_poloh[:,1], data_poloh[:,2]
        graph = ax.scatter(x, y, z)

        ax.set_xlim([0, self.delka_jedne_steny])
        ax.set_ylim([0, self.delka_jedne_steny])
        ax.set_zlim([0, self.delka_jedne_steny])


        def update(frame):
            self.mihani_castic_anim()
            data_poloh = np.array(self.pozice_castic)
            x, y, z = data_poloh[:,0], data_poloh[:,1], data_poloh[:,2]
            graph._offsets3d = (x, y, z)
            return graph,

        ani = FuncAnimation(fig, update, frames=num_steps, interval=10, blit=False)
        plt.get_current_fig_manager().window.state('zoomed')
        
        ani.save(gif_name, writer=PillowWriter())
        
        plt.show()


    def vypoc_tlak_simulace(self):
        V = self.delka_jedne_steny ** 3        
        tlak_simulace = (1 / (3*V)) * (np.sum(HMOTNOST_CASTICE * np.sum(self.rychlosti_castic**2, axis=1)))
        teor_tlak = (BOLTZMANNOVA_KONSTANTA * self.pocet_castic * self.teplota) / V   #P V = N kB T
        return tlak_simulace, teor_tlak
    
    
def main():
    for teplota in TEPLOTY:
        castice = Castice(teplota, POCET_CASTIC) #300k
        castice.generovat_zacatek()
        castice.mihani_castic(POCET_EKVILIBRACNICH_KROKU)
        castice.mihani_castic(POCET_ITERACI)
        castice.porovnani_s_max_rozd(iterace=POCET_ITERACI, zapis_do_souboru=True)
        #castice.animovat_mihani_castic(gif_name="animece_po10tisicich_kroku.gif")
        tlak_sim, teor_tlak = castice.vypoc_tlak_simulace()
        print(f"Sim tlak: {tlak_sim} teor tlak: {teor_tlak}" )


if __name__ == "__main__":
    main()

