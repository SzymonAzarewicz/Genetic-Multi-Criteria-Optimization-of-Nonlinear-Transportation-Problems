import pygame
import math
import random

class PunktOdbioru:
    def __init__(self, id, sasiedzi, odleglosci, ilosc_paczek_do_dostarczenia, ilosc_paczek_do_odbioru):
        self.id = id
        self.sasiedzi = sasiedzi
        self.koszt_dojazdu = {sasiad: odleglosc for sasiad, odleglosc in zip(sasiedzi, odleglosci)}
        self.ilosc_paczek_do_dostarczenia = ilosc_paczek_do_dostarczenia
        self.ilosc_paczek_do_odbioru = ilosc_paczek_do_odbioru

    def __repr__(self):
        return (f"PunktOdbioru(id={self.id}, sasiedzi={self.sasiedzi}, "
                f"koszt_dojazdu={self.koszt_dojazdu})")

class Wizualizacja:
    def __init__(self, punkty, punkt_startowy, szerokosc=800, wysokosc=600):
        pygame.init()
        self.ekran = pygame.display.set_mode((szerokosc, wysokosc))
        pygame.display.set_caption("Mapa Punktów Odbioru")
        
        self.punkty = punkty
        self.punkt_startowy = punkt_startowy
        self.promien_punktu = 20
        self.czcionka = pygame.font.Font(None, 24)
        # Generujemy pozycje punktów na mapie
        self.pozycje = self._generuj_pozycje_losowo(punkty, punkt_startowy, szerokosc, wysokosc)
        self.aktywny_punkt_id = None
        
        # Inicjalizujemy pygame display
        pygame.display.flip()
    
    def _rysuj_punkty(self, pozycja_myszy):
        # Rysujemy zwykłe punkty
        for punkt in self.punkty:
            pozycja = self.pozycje[punkt.id]
            
            odleglosc = math.sqrt((pozycja[0] - pozycja_myszy[0])**2 + 
                                (pozycja[1] - pozycja_myszy[1])**2)
            kolor = (0, 150, 0) if odleglosc <= self.promien_punktu else (0, 100, 0)
            
            pygame.draw.circle(self.ekran, kolor, pozycja, self.promien_punktu)
            tekst = self.czcionka.render(str(punkt.id), True, (255, 255, 255))
            tekst_rect = tekst.get_rect(center=pozycja)
            self.ekran.blit(tekst, tekst_rect)
            
            if odleglosc <= self.promien_punktu:
                info = f"Do dostarczenia: {punkt.ilosc_paczek_do_dostarczenia}"
                info2 = f"Do odbioru: {punkt.ilosc_paczek_do_odbioru}"
                
                tekst_info = self.czcionka.render(info, True, (0, 0, 0))
                tekst_info2 = self.czcionka.render(info2, True, (0, 0, 0))
                
                self.ekran.blit(tekst_info, (pozycja[0] + 30, pozycja[1] - 20))
                self.ekran.blit(tekst_info2, (pozycja[0] + 30, pozycja[1] + 5))
        
        # Rysujemy sortownię
        pozycja = self.pozycje[self.punkt_startowy.id]
        odleglosc = math.sqrt((pozycja[0] - pozycja_myszy[0])**2 + 
                            (pozycja[1] - pozycja_myszy[1])**2)
        kolor = (200, 0, 0) if odleglosc <= self.promien_punktu else (150, 0, 0)
        
        pygame.draw.circle(self.ekran, kolor, pozycja, self.promien_punktu)
        tekst = self.czcionka.render("S", True, (255, 255, 255))
        tekst_rect = tekst.get_rect(center=pozycja)
        self.ekran.blit(tekst, tekst_rect)
        
        if odleglosc <= self.promien_punktu:
            info = "SORTOWNIA"
            tekst_info = self.czcionka.render(info, True, (0, 0, 0))
            self.ekran.blit(tekst_info, (pozycja[0] + 30, pozycja[1] - 10))

    def _generuj_pozycje_losowo(self, punkty, punkt_startowy, szerokosc, wysokosc):
        pozycje = {}
        margin = 50
        
        # Umieszczamy sortownię na środku dolnej części
        pozycje[punkt_startowy.id] = (szerokosc//2, wysokosc - margin)
        
        # Definiujemy główne arterie komunikacyjne
        arteria_y = wysokosc//2
        arteria_x = szerokosc//2
        
        # Generujemy pozycje dla pozostałych punktów
        for punkt in punkty:
            if punkt.id != punkt_startowy.id:
                while True:
                    # 40% szans na umieszczenie punktu przy głównej arterii
                    if random.random() < 0.4:
                        if random.random() < 0.5:
                            # Punkt przy arterii poziomej
                            x = random.randint(margin, szerokosc - margin)
                            y = arteria_y + random.randint(-30, 30)
                        else:
                            # Punkt przy arterii pionowej
                            x = arteria_x + random.randint(-30, 30)
                            y = random.randint(margin, wysokosc - margin)
                    else:
                        # Losowa pozycja z dala od arterii
                        x = random.randint(margin, szerokosc - margin)
                        y = random.randint(margin, wysokosc - margin)
                    
                    # Sprawdzamy czy punkt nie nakłada się z istniejącymi
                    naklada_sie = False
                    for pos in pozycje.values():
                        if math.sqrt((pos[0] - x)**2 + (pos[1] - y)**2) < self.promien_punktu * 3:
                            naklada_sie = True
                            break
                    
                    if not naklada_sie:
                        pozycje[punkt.id] = (x, y)
                        break
        return pozycje



    
    def _generuj_sciezki(self):
        """Generuje listę wszystkich bezpośrednich ścieżek między punktami"""
        sciezki = []
        wszystkie_punkty = [self.punkt_startowy] + self.punkty
        
        for punkt in wszystkie_punkty:
            for sasiad_id in punkt.sasiedzi:
                if sasiad_id > punkt.id:  # Unikamy duplikatów
                    sciezka = {
                        'punkt1_id': punkt.id,
                        'punkt2_id': sasiad_id,
                        'punkt1_pos': self.pozycje[punkt.id],
                        'punkt2_pos': self.pozycje[sasiad_id],
                        'koszt': punkt.koszt_dojazdu[sasiad_id]
                    }
                    sciezki.append(sciezka)
        
        return sciezki


    def _czy_punkt_aktywny(self, punkt_id, pozycja_myszy):
        """Sprawdza czy myszka jest nad punktem"""
        pozycja = self.pozycje[punkt_id]
        odleglosc = math.sqrt((pozycja[0] - pozycja_myszy[0])**2 + 
                            (pozycja[1] - pozycja_myszy[1])**2)
        return odleglosc <= self.promien_punktu



    def _rysuj_polaczenia(self, pozycja_myszy):
        # Aktualizujemy aktywny punkt
        self.aktywny_punkt_id = None
        for punkt in [self.punkt_startowy] + self.punkty:
            if self._czy_punkt_aktywny(punkt.id, pozycja_myszy):
                self.aktywny_punkt_id = punkt.id
                break
        
        for punkt in [self.punkt_startowy] + self.punkty:
            for sasiad_id, koszt in punkt.koszt_dojazdu.items():
                if sasiad_id > punkt.id:  # Rysujemy każdą drogę tylko raz
                    start_pos = self.pozycje[punkt.id]
                    koniec_pos = self.pozycje[sasiad_id]
                    
                    # Sprawdzamy czy ścieżka jest związana z aktywnym punktem
                    sciezka_aktywna = (self.aktywny_punkt_id is not None and 
                                     (self.aktywny_punkt_id == punkt.id or 
                                      self.aktywny_punkt_id == sasiad_id))
                    
                    # Znajdujemy punkty pośrednie
                    punkty_posrednie = self._znajdz_punkty_posrednie(start_pos, koniec_pos)
                    
                    if punkty_posrednie:
                        wszystkie_punkty = [(punkt.id, start_pos)] + \
                                         punkty_posrednie + \
                                         [(sasiad_id, koniec_pos)]
                        
                        for i in range(len(wszystkie_punkty) - 1):
                            p1 = wszystkie_punkty[i]
                            p2 = wszystkie_punkty[i + 1]
                            
                            odleglosc_calkowita = math.dist(start_pos, koniec_pos)
                            odleglosc_odcinka = math.dist(p1[1], p2[1])
                            koszt_odcinka = int(koszt * odleglosc_odcinka / odleglosc_calkowita)
                            
                            myszka_na_sciezce = self._czy_myszka_na_sciezce(p1[1], p2[1], pozycja_myszy)
                            
                            # Zmieniamy kolor w zależności od aktywności punktu
                            if sciezka_aktywna:
                                kolor = (255, 165, 0)  # Pomarańczowy dla aktywnej ścieżki
                                grubosc = 4
                            else:
                                kolor = (50, 50, 200) if myszka_na_sciezce else (100, 100, 100)
                                grubosc = 3 if myszka_na_sciezce else 2
                            
                            pygame.draw.line(self.ekran, kolor, p1[1], p2[1], grubosc)
                            
                            # Pokazujemy koszt dla aktywnej ścieżki lub gdy myszka jest nad nią
                            if sciezka_aktywna or myszka_na_sciezce:
                                srodek_x = (p1[1][0] + p2[1][0]) // 2
                                srodek_y = (p1[1][1] + p2[1][1]) // 2
                                tekst = self.czcionka.render(str(koszt_odcinka), True, (0, 0, 0))
                                self.ekran.blit(tekst, (srodek_x, srodek_y))
                    
                    else:  # Dla ścieżek bez punktów pośrednich
                        myszka_na_sciezce = self._czy_myszka_na_sciezce(start_pos, koniec_pos, pozycja_myszy)
                        
                        # Zmieniamy kolor w zależności od aktywności punktu
                        if sciezka_aktywna:
                            kolor = (255, 165, 0)  # Pomarańczowy dla aktywnej ścieżki
                            grubosc = 4
                        else:
                            kolor = (50, 50, 200) if myszka_na_sciezce else (100, 100, 100)
                            grubosc = 3 if myszka_na_sciezce else 2
                        
                        pygame.draw.line(self.ekran, kolor, start_pos, koniec_pos, grubosc)
                        
                        if sciezka_aktywna or myszka_na_sciezce:
                            srodek_x = (start_pos[0] + koniec_pos[0]) // 2
                            srodek_y = (start_pos[1] + koniec_pos[1]) // 2
                            tekst = self.czcionka.render(str(koszt), True, (0, 0, 0))
                            self.ekran.blit(tekst, (srodek_x, srodek_y))

    def _rysuj_polaczenia(self, pozycja_myszy):
        for punkt in [self.punkt_startowy] + self.punkty:
            for sasiad_id, koszt in punkt.koszt_dojazdu.items():
                # Rysujemy każdą drogę tylko raz
                if sasiad_id > punkt.id:
                    start_pos = self.pozycje[punkt.id]
                    koniec_pos = self.pozycje[sasiad_id]
                    
                    # Sprawdzamy czy myszka jest na ścieżce
                    myszka_na_sciezce = self._czy_myszka_na_sciezce(start_pos, koniec_pos, pozycja_myszy)
                    
                    # Kolor i grubość zależne od najechania myszką
                    kolor = (50, 50, 200) if myszka_na_sciezce else (100, 100, 100)
                    grubosc = 3 if myszka_na_sciezce else 2
                    
                    # Rysujemy prostą linię między punktami
                    pygame.draw.line(self.ekran, kolor, start_pos, koniec_pos, grubosc)
                    
                    # Wyświetlamy koszt, jeśli myszka jest na ścieżce
                    if myszka_na_sciezce:
                        srodek_x = (start_pos[0] + koniec_pos[0]) // 2
                        srodek_y = (start_pos[1] + koniec_pos[1]) // 2
                        tekst = self.czcionka.render(str(koszt), True, (0, 0, 0))
                        self.ekran.blit(tekst, (srodek_x, srodek_y))

    def _znajdz_punkty_posrednie(self, start_pos, koniec_pos, tolerancja=30):
        """Znajduje punkty leżące blisko ścieżki między dwoma punktami."""
        punkty_posrednie = []
        
        for punkt in self.punkty:
            pozycja = self.pozycje[punkt.id]
            # Pomijamy punkty początkowy i końcowy
            if pozycja != start_pos and pozycja != koniec_pos:
                # Używamy tej samej logiki co w _czy_myszka_na_sciezce
                x0, y0 = start_pos
                x1, y1 = koniec_pos
                x, y = pozycja
                
                # Obliczamy odległość punktu od linii
                d = abs((y1 - y0) * x - (x1 - x0) * y + x1 * y0 - y1 * x0) / \
                    ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
                
                # Sprawdzamy czy punkt jest blisko ścieżki i między punktami końcowymi
                if d <= tolerancja:
                    min_x, max_x = min(x0, x1), max(x0, x1)
                    min_y, max_y = min(y0, y1), max(y0, y1)
                    if min_x - tolerancja <= x <= max_x + tolerancja and \
                    min_y - tolerancja <= y <= max_y + tolerancja:
                        punkty_posrednie.append((punkt.id, pozycja))
        
        # Sortujemy punkty według odległości od punktu startowego
        return sorted(punkty_posrednie, 
                    key=lambda p: math.dist(start_pos, p[1]))

    def _czy_myszka_na_sciezce(self, start_pos, koniec_pos, pozycja_myszy, tolerancja=5):
        # Wyznaczanie odległości myszki od linii za pomocą geometrii
        x0, y0 = start_pos
        x1, y1 = koniec_pos
        x, y = pozycja_myszy

        # Obliczamy odległość punktu od linii
        d = abs((y1 - y0) * x - (x1 - x0) * y + x1 * y0 - y1 * x0) / ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        
        # Sprawdzamy, czy punkt myszki leży w rozsądnej odległości od linii
        if d <= tolerancja:
            # Sprawdzamy, czy myszka jest w zakresie końców linii
            min_x, max_x = min(x0, x1), max(x0, x1)
            min_y, max_y = min(y0, y1), max(y0, y1)
            if min_x - tolerancja <= x <= max_x + tolerancja and min_y - tolerancja <= y <= max_y + tolerancja:
                return True
        return False
    




    def _rysuj_polaczenia(self, pozycja_myszy):
        for punkt in [self.punkt_startowy] + self.punkty:
            for sasiad_id, koszt in punkt.koszt_dojazdu.items():
                if sasiad_id > punkt.id:  # Rysujemy każdą drogę tylko raz
                    start_pos = self.pozycje[punkt.id]
                    koniec_pos = self.pozycje[sasiad_id]
                    
                    # Znajdujemy punkty pośrednie
                    punkty_posrednie = self._znajdz_punkty_posrednie(start_pos, koniec_pos)
                    
                    # Jeśli są punkty pośrednie, rysujemy odcinki przez nie
                    if punkty_posrednie:
                        # Tworzymy listę wszystkich punktów w kolejności
                        wszystkie_punkty = [(punkt.id, start_pos)] + \
                                        punkty_posrednie + \
                                        [(sasiad_id, koniec_pos)]
                        
                        # Rysujemy odcinki między kolejnymi punktami
                        for i in range(len(wszystkie_punkty) - 1):
                            p1 = wszystkie_punkty[i]
                            p2 = wszystkie_punkty[i + 1]
                            
                            # Obliczamy część kosztu proporcjonalną do długości odcinka
                            odleglosc_calkowita = math.dist(start_pos, koniec_pos)
                            odleglosc_odcinka = math.dist(p1[1], p2[1])
                            koszt_odcinka = int(koszt * odleglosc_odcinka / odleglosc_calkowita)
                            
                            # Sprawdzamy czy myszka jest na tym odcinku
                            myszka_na_sciezce = self._czy_myszka_na_sciezce(p1[1], p2[1], pozycja_myszy)
                            
                            # Rysujemy odcinek
                            kolor = (50, 50, 200) if myszka_na_sciezce else (100, 100, 100)
                            grubosc = 3 if myszka_na_sciezce else 2
                            pygame.draw.line(self.ekran, kolor, p1[1], p2[1], grubosc)
                            
                            # Wyświetlamy koszt odcinka
                            if myszka_na_sciezce:
                                srodek_x = (p1[1][0] + p2[1][0]) // 2
                                srodek_y = (p1[1][1] + p2[1][1]) // 2
                                tekst = self.czcionka.render(str(koszt_odcinka), True, (0, 0, 0))
                                self.ekran.blit(tekst, (srodek_x, srodek_y))
                    
                    else:  # Jeśli nie ma punktów pośrednich, rysujemy jak wcześniej
                        myszka_na_sciezce = self._czy_myszka_na_sciezce(start_pos, koniec_pos, pozycja_myszy)
                        kolor = (50, 50, 200) if myszka_na_sciezce else (100, 100, 100)
                        grubosc = 3 if myszka_na_sciezce else 2
                        pygame.draw.line(self.ekran, kolor, start_pos, koniec_pos, grubosc)
                        
                        if myszka_na_sciezce:
                            srodek_x = (start_pos[0] + koniec_pos[0]) // 2
                            srodek_y = (start_pos[1] + koniec_pos[1]) // 2
                            tekst = self.czcionka.render(str(koszt), True, (0, 0, 0))
                            self.ekran.blit(tekst, (srodek_x, srodek_y))

    def uruchom(self):
        running = True
        while running:
            pozycja_myszy = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            self.ekran.fill((255, 255, 255))
            self._rysuj_polaczenia(pozycja_myszy)
            self._rysuj_punkty(pozycja_myszy)
            pygame.display.flip()
            
        pygame.quit()

def generuj_losowe_punkty(ilosc_punktow):
    # Lista wszystkich punktów (bez sortowni)
    punkty = []
    wszystkie_id = list(range(ilosc_punktow + 1))  # +1 bo mamy też sortownię (id=0)
    
    # Generujemy zwykłe punkty odbioru (od id=1 do ilosc_punktow)
    for i in range(1, ilosc_punktow + 1):
        # Każdy punkt jest połączony z sortownią (id=0) i 2-3 innymi losowymi punktami
        mozliwe_sasiedztwa = [id for id in wszystkie_id if id != i]
        ilosc_sasiadow = random.randint(2, 3)
        
        # Zawsze łączymy z sortownią (id=0)
        sasiedzi = [0]
        
        # Dodajemy losowych sąsiadów (ale nie sortownię, bo już ją dodaliśmy)
        losowi_sasiedzi = random.sample([id for id in mozliwe_sasiedztwa if id != 0], 
                                      min(ilosc_sasiadow, len(mozliwe_sasiedztwa)))
        sasiedzi.extend(losowi_sasiedzi)
        
        # Generujemy losowe odległości (50-250) dla każdego sąsiada
        odleglosci = [random.randint(50, 250) for _ in range(len(sasiedzi))]
        
        # Generujemy losową ilość paczek (1-10 dla każdego typu)
        paczki_dostarczenie = random.randint(1, 10)
        paczki_odbior = random.randint(1, 10)
        
        punkt = PunktOdbioru(i, sasiedzi, odleglosci, paczki_dostarczenie, paczki_odbior)
        punkty.append(punkt)
    
    # Tworzymy sortownię (punkt startowy)
    # Zbieramy wszystkie połączenia do sortowni
    sortownia_sasiedzi = []
    sortownia_odleglosci = []
    
    # Dodajemy połączenia zwrotne do sortowni
    for punkt in punkty:
        if 0 in punkt.sasiedzi:
            sortownia_sasiedzi.append(punkt.id)
            # Używamy tej samej odległości co w drugim kierunku
            indeks = punkt.sasiedzi.index(0)
            sortownia_odleglosci.append(punkt.koszt_dojazdu[0])
    
    sortownia = PunktOdbioru(0, sortownia_sasiedzi, sortownia_odleglosci, 0, 0)
    
    return sortownia, punkty


def wypisz_polaczenia(punkty, sortownia):
    """
    Wypisuje połączenia między wszystkimi punktami, włączając sortownię.
    
    Args:
        punkty: lista obiektów PunktOdbioru
        sortownia: obiekt PunktOdbioru reprezentujący sortownię
    """
    for punkt in [sortownia] + punkty:
        print(f"Punkt {punkt.id} ma połączenia: {punkt.koszt_dojazdu}")

# Przykład użycia
if __name__ == "__main__":
    ilosc_punktow = random.randint(15, 25)
    sortownia, punkty = generuj_losowe_punkty(ilosc_punktow)
    
    # Wywołanie poprawionej funkcji wypisz_polaczenia
    print("Lista połączeń między punktami:")
    wypisz_polaczenia(punkty, sortownia)
    
    # Inicjalizacja i uruchomienie wizualizacji
    wizualizacja = Wizualizacja(punkty, sortownia)
    wizualizacja.uruchom()