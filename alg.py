import random

class AlgorytmGenetyczny:
    def __init__(self, sortownia, punkty, rozmiar_populacji=100, liczba_pokolen=50):
        self.sortownia = sortownia
        self.punkty = punkty
        self.rozmiar_populacji = rozmiar_populacji
        self.liczba_pokolen = liczba_pokolen
        self.wszystkie_punkty = {punkt.id: punkt for punkt in [sortownia] + punkty}
        
    def generuj_losowa_sciezke(self):
        sciezka = [0]  # Rozpoczynamy od sortowni (id=0)
        dostepne_punkty = set(punkt.id for punkt in self.punkty)
        
        while dostepne_punkty:
            aktualny = sciezka[-1]
            punkt = self.wszystkie_punkty[aktualny]
            
            # Znajdujemy dostępnych sąsiadów
            dostepni_sasiedzi = [s for s in punkt.sasiedzi if s in dostepne_punkty]
            
            if not dostepni_sasiedzi:
                # Jeśli nie ma dostępnych sąsiadów, próbujemy wrócić do sortowni
                if 0 in punkt.sasiedzi:
                    sciezka.append(0)
                    break
                return None  # Ścieżka niemożliwa
            
            # Wybieramy losowego sąsiada
            nastepny = random.choice(dostepni_sasiedzi)
            sciezka.append(nastepny)
            dostepne_punkty.remove(nastepny)
            
        # Sprawdzamy, czy kończymy w sortowni
        if sciezka[-1] != 0:
            if 0 in self.wszystkie_punkty[sciezka[-1]].sasiedzi:
                sciezka.append(0)
            else:
                return None
                
        return sciezka if self._czy_sciezka_poprawna(sciezka) else None

    def _czy_sciezka_poprawna(self, sciezka):
        if not sciezka or sciezka[0] != 0 or sciezka[-1] != 0:
            return False
            
        for i in range(len(sciezka) - 1):
            punkt_aktualny = self.wszystkie_punkty[sciezka[i]]
            if sciezka[i+1] not in punkt_aktualny.sasiedzi:
                return False
        return True

    def oblicz_koszt_sciezki(self, sciezka):
        if not sciezka:
            return float('inf')
            
        koszt = 0
        # Sprawdzamy czy wszystkie punkty z paczkami są obsłużone
        punkty_z_paczkami = set(punkt.id for punkt in self.punkty 
                              if punkt.ilosc_paczek_do_dostarczenia > 0 or punkt.ilosc_paczek_do_odbioru > 0)
        punkty_odwiedzone = set(sciezka)
        
        if not punkty_z_paczkami.issubset(punkty_odwiedzone):
            return float('inf')  # Kara za nieodwiedzenie punktu z paczkami
            
        # Obliczamy koszt trasy
        for i in range(len(sciezka) - 1):
            punkt = self.wszystkie_punkty[sciezka[i]]
            koszt += punkt.koszt_dojazdu[sciezka[i+1]]
            
        return koszt

    def krzyzuj(self, rodzic1, rodzic2):
        if len(rodzic1) < 3:
            return rodzic1
            
        punkt_krzyzowania = random.randint(1, len(rodzic1) - 2)
        potomek = rodzic1[:punkt_krzyzowania]
        
        for gen in rodzic2[punkt_krzyzowania:]:
            if gen not in potomek:
                potomek.append(gen)
                
        if potomek[-1] != 0:
            potomek.append(0)
            
        return potomek if self._czy_sciezka_poprawna(potomek) else None

    def mutuj(self, sciezka):
        if len(sciezka) < 4:  # Potrzebujemy co najmniej 4 punktów (start, 2 do zamiany, koniec)
            return sciezka
            
        punkty_do_mutacji = range(1, len(sciezka) - 1)
        if len(punkty_do_mutacji) < 2:
            return sciezka
            
        indeks1, indeks2 = random.sample(list(punkty_do_mutacji), 2)
        nowa_sciezka = sciezka.copy()
        nowa_sciezka[indeks1], nowa_sciezka[indeks2] = nowa_sciezka[indeks2], nowa_sciezka[indeks1]
        
        return nowa_sciezka if self._czy_sciezka_poprawna(nowa_sciezka) else sciezka

    def znajdz_najlepsza_trase(self):
        # Generowanie początkowej populacji
        populacja = []
        while len(populacja) < self.rozmiar_populacji:
            sciezka = self.generuj_losowa_sciezke()
            if sciezka:
                populacja.append(sciezka)

        najlepsza_sciezka = None
        najlepszy_koszt = float('inf')

        for pokolenie in range(self.liczba_pokolen):
            # Obliczanie przystosowania
            przystosowanie = [(sciezka, self.oblicz_koszt_sciezki(sciezka)) for sciezka in populacja]
            przystosowanie.sort(key=lambda x: x[1])
            
            # Aktualizacja najlepszego rozwiązania
            if przystosowanie[0][1] < najlepszy_koszt:
                najlepsza_sciezka = przystosowanie[0][0]
                najlepszy_koszt = przystosowanie[0][1]
                # Wydruk szczegółów trasy
                print("\nSzczegóły trasy:")
                for i in range(len(najlepsza_sciezka)-1):
                    punkt_start = najlepsza_sciezka[i]
                    punkt_koniec = najlepsza_sciezka[i+1]
                    koszt_odcinka = self.wszystkie_punkty[punkt_start].koszt_dojazdu[punkt_koniec]
                    print(f"Punkt {punkt_start} -> Punkt {punkt_koniec}, koszt: {koszt_odcinka}")
                print(f"Całkowity koszt: {najlepszy_koszt}")

            # Selekcja najlepszych osobników
            nowa_populacja = [p[0] for p in przystosowanie[:10]]  # Elitaryzm
            
            # Krzyżowanie i mutacja
            while len(nowa_populacja) < self.rozmiar_populacji:
                rodzic1, rodzic2 = random.sample(nowa_populacja[:50], 2)
                potomek = self.krzyzuj(rodzic1, rodzic2)
                if potomek and random.random() < 0.1:  # 10% szans na mutację
                    potomek = self.mutuj(potomek)
                if potomek:
                    nowa_populacja.append(potomek)
            
            populacja = nowa_populacja

        return najlepsza_sciezka, najlepszy_koszt

# Przykład użycia:
if __name__ == "__main__":
    from map2 import generuj_losowe_punkty, Wizualizacja
    
    sortownia, punkty = generuj_losowe_punkty(15)
    
    algorytm = AlgorytmGenetyczny(sortownia, punkty)
    najlepsza_sciezka, najlepszy_koszt = algorytm.znajdz_najlepsza_trase()
    
    print(f"Najlepsza znaleziona trasa: {najlepsza_sciezka}")
    print(f"Koszt trasy: {najlepszy_koszt}")
    
    wizualizacja = Wizualizacja(punkty, sortownia)
    wizualizacja.wizualizuj_trase(najlepsza_sciezka)