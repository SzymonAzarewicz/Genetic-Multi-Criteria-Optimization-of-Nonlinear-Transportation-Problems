import pygame
import random
import math
import pickle

# Inicjalizacja pygame
pygame.init()

# Ustawienia ekranu
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Łączenie Punktów z Sortownią, Korkami, Paczkami i Sąsiadami")

# Kolory
WHITE   = (255, 255, 255)
RED     = (255, 0, 0)
ORANGE  = (255, 150, 0)
YELLOW  = (255, 220, 0)
BLACK   = (0, 0, 0)
BLUE    = (0, 0, 255)

class Point:
    def __init__(self, x, y, index, special=False):
        """
        Jeśli special == True, punkt reprezentuje sortownię.
        """
        self.x = x
        self.y = y
        self.index = index
        self.special = special
        self.jam_index = 0  # Wartości: 1, 2 lub 3 (określające zagęszczenie ruchu)
        self.has_packages = False  # Domyślnie w punkcie nie ma paczek
        # Lista sąsiadów – każdy element to krotka: (neighbor_index, delay_factor, route_length_in_meters)
        self.neighbors = []  

    def __repr__(self):
            return (f"Point(x={self.x}, y={self.y}, index={self.index}, special={self.special}, "f"jam_index={self.jam_index}, has_packages={self.has_packages}, neighbors={self.neighbors})")
    
    def get_position(self):
        return (self.x, self.y)

class Game:
    def __init__(self, num_points=35, point_radius=20, min_distance_multiplier=4):
        self.num_points = num_points
        self.point_radius = point_radius
        self.min_distance = point_radius * min_distance_multiplier
        self.points = []       
        # Każda trasa zapisywana jest jako krotka:
        # (indeks punktu1, indeks punktu2, losowy czynnik, długość_odcinka_w_metrach)
        self.connections = []  
        self.font = pygame.font.Font(None, 24)
        # Przelicznik: 1 piksel = 0.5 m, ale chcemy wynik 5 razy większy
        self.pixel_to_meter = 0.5  
        self.scale_factor = 5  # skala długości
        # Szansa na to, że w punkcie (poza sortownią) będą paczki.
        self.package_probability = 0.4
        
        # Kolejność: generujemy punkty, dodajemy sortownię, a następnie łączymy wszystkie punkty.
        self.generate_points()
        self.create_sortownia()
        self.connect_points()

    def generate_points(self):
        """Generuje zwykłe punkty z zachowaniem minimalnej odległości między nimi.
           Dla każdego punktu (poza sortownią) ustawia flagę has_packages zgodnie z package_probability.
        """
        for i in range(self.num_points):
            while True:
                x = random.randint(self.point_radius, WIDTH - self.point_radius)
                y = random.randint(self.point_radius, HEIGHT - self.point_radius)
                if not self.is_too_close(x, y):
                    point = Point(x, y, i)
                    # Ustawiamy, czy w punkcie są paczki – szansa określona przez package_probability
                    if random.random() < self.package_probability:
                        point.has_packages = True
                    self.points.append(point)
                    break

    def is_too_close(self, x, y):
        """Sprawdza, czy punkt (x, y) jest zbyt blisko któregokolwiek z już wygenerowanych punktów."""
        for p in self.points:
            if math.hypot(x - p.x, y - p.y) < self.min_distance:
                return True
        return False

    def calculate_distance(self, p1, p2):
        """Oblicza odległość między dwoma punktami (w pikselach)."""
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def distance_from_point_to_line(self, px, py, x1, y1, x2, y2):
        """
        Oblicza minimalną odległość od punktu (px, py) do odcinka (x1, y1)-(x2, y2).
        """
        line_len = self.calculate_distance(Point(x1, y1, -1), Point(x2, y2, -1))
        if line_len == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len**2)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return math.hypot(px - proj_x, py - proj_y)

    def orientation(self, p, q, r):
        """Oblicza orientację trzech punktów."""
        val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
        if val == 0:
            return 0  # punkty współliniowe
        return 1 if val > 0 else 2

    def is_on_segment(self, p, q, r):
        """Sprawdza, czy punkt q leży na odcinku pr (przy założeniu współliniowości)."""
        return (min(p.x, r.x) <= q.x <= max(p.x, r.x) and
                min(p.y, r.y) <= q.y <= max(p.y, r.y))

    def do_segments_intersect(self, p1, q1, p2, q2):
        """
        Sprawdza, czy odcinki (p1, q1) i (p2, q2) się przecinają.
        Ignorujemy przypadki, gdy końce odcinków pokrywają się.
        """
        if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
            return False

        o1 = self.orientation(p1, q1, p2)
        o2 = self.orientation(p1, q1, q2)
        o3 = self.orientation(p2, q2, p1)
        o4 = self.orientation(p2, q2, q1)

        if o1 != o2 and o3 != o4:
            return True

        if o1 == 0 and self.is_on_segment(p1, p2, q1):
            return True
        if o2 == 0 and self.is_on_segment(p1, q2, q1):
            return True
        if o3 == 0 and self.is_on_segment(p2, p1, q2):
            return True
        if o4 == 0 and self.is_on_segment(p2, q1, q2):
            return True

        return False

    def line_passes_through_other_points(self, p1, p2):
        """
        Sprawdza, czy linia łącząca p1 i p2 przechodzi przez obszar innych punktów.
        Używamy promienia punktu jako marginesu.
        """
        for p in self.points:
            if p == p1 or p == p2:
                continue
            if self.distance_from_point_to_line(p.x, p.y, p1.x, p1.y, p2.x, p2.y) < self.point_radius:
                return True
        return False

    def calculate_centroid(self):
        """
        Oblicza środek ciężkości punktów zwykłych 
        (sortownia nie wpływa na obliczenia).
        """
        regular_points = [p for p in self.points if not p.special]
        if not regular_points:
            return (0, 0)
        sum_x = sum(p.x for p in regular_points)
        sum_y = sum(p.y for p in regular_points)
        return (sum_x / len(regular_points), sum_y / len(regular_points))

    def find_max_distance_from_centroid(self, centroid):
        """Znajduje największą odległość od centroidu (dla punktów zwykłych)."""
        regular_points = [p for p in self.points if not p.special]
        if not regular_points:
            return 0
        return max(math.hypot(p.x - centroid[0], p.y - centroid[1]) for p in regular_points)

    def color_points(self):
        """
        Koloruje zwykłe punkty w zależności od ich odległości od środka ciężkości.
        Sortownia pozostaje niezmieniona (będzie rysowana na niebiesko).
        """
        centroid = self.calculate_centroid()
        max_dist = self.find_max_distance_from_centroid(centroid)
        for p in self.points:
            if p.special:
                continue
            dist = math.hypot(p.x - centroid[0], p.y - centroid[1])
            if dist <= 0.35 * max_dist:
                p.jam_index = 3
            elif dist <= 0.7 * max_dist:
                p.jam_index = 2
            else:
                p.jam_index = 1

    def create_sortownia(self):
        """
        Tworzy specjalny punkt reprezentujący sortownię,
        umieszczony na dolnej krawędzi (granicy miasta).
        (Sortownia nie otrzymuje paczek.)
        """
        x = random.randint(self.point_radius, WIDTH - self.point_radius)
        y = HEIGHT - self.point_radius
        sortownia_index = len(self.points)
        sortownia = Point(x, y, sortownia_index, special=True)
        self.points.append(sortownia)

    def connection_exists(self, idx1, idx2):
        """Sprawdza, czy trasa między dwoma punktami już istnieje."""
        for conn in self.connections:
            if (conn[0] == idx1 and conn[1] == idx2) or (conn[0] == idx2 and conn[1] == idx1):
                return True
        return False

    def connect_points(self):
        """
        Łączy wszystkie punkty (wraz z sortownią) liniami, które nie przecinają się
        oraz nie przechodzą przez inne punkty. Dodatkowo przy tworzeniu trasy
        obliczany jest współczynnik "korków" równy:
            współczynnik = (średnia jam_index obu punktów) * (losowy czynnik z [0.9, 1.1])
        oraz zapisywana jest przeskalowana długość odcinka (w metrach).
        
        Po dodaniu połączenia aktualizujemy listy sąsiadów obu punktów – dla każdego sąsiada zapisujemy:
            (neighbor_index, delay_factor, route_length_in_meters)
        """
        added = True
        while added:
            added = False
            for point in self.points:
                closest_point = None
                closest_distance = float('inf')
                for other in self.points:
                    if other == point:
                        continue
                    if self.connection_exists(point.index, other.index):
                        continue
                    valid_line = True
                    for conn in self.connections:
                        p_existing = self.points[conn[0]]
                        q_existing = self.points[conn[1]]
                        if self.do_segments_intersect(point, other, p_existing, q_existing):
                            valid_line = False
                            break
                    if valid_line and self.line_passes_through_other_points(point, other):
                        valid_line = False
                    if valid_line:
                        distance = self.calculate_distance(point, other)
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_point = other
                        added = True
                if closest_point:
                    # Losowy czynnik ±10%
                    factor = random.uniform(0.9, 1.1)
                    # Obliczamy długość odcinka w pikselach, a następnie przeliczamy na metry
                    length_pixels = self.calculate_distance(point, closest_point)
                    length_meters = length_pixels * self.pixel_to_meter * self.scale_factor
                    self.connections.append((point.index, closest_point.index, factor, length_meters))
                    # Aktualizujemy listę sąsiadów dla obu punktów
                    # Każdy sąsiad zapisujemy jako: (neighbor_index, delay_factor, route_length_in_meters)
                    self.points[point.index].neighbors.append((closest_point.index, factor, length_meters))
                    self.points[closest_point.index].neighbors.append((point.index, factor, length_meters))

    def get_connection_color(self, coefficient):
        """
        Wybiera kolor trasy na podstawie obliczonego współczynnika korków.
        (Funkcja pozostaje, ale przy rysowaniu linii nie jest używana, gdyż wszystkie linie są czarne).
        Przyjmujemy następujące progi:
          - coefficient < 1.5  => YELLOW (małe zagęszczenie)
          - 1.5 <= coefficient < 2.5  => ORANGE (średnie)
          - coefficient >= 2.5  => RED (duże zagęszczenie)
        """
        if coefficient < 1.5:
            return YELLOW
        elif coefficient < 2.5:
            return ORANGE
        else:
            return RED

    def draw_points(self, surface):
        """
        Rysuje punkty – zwykłe oraz sortownię.
        Dla punktów (poza sortownią), jeśli w punkcie są paczki, tekst (etykieta) będzie renderowany na czarno.
        """
        for p in self.points:
            if p.special:
                color = BLUE  # sortownia
            else:
                if p.jam_index == 3:
                    color = RED
                elif p.jam_index == 2:
                    color = ORANGE
                else:
                    color = YELLOW
            pygame.draw.circle(surface, color, p.get_position(), self.point_radius)
            if p.special:
                label = "Sortownia"
                text_color = WHITE
            else:
                label = f"{p.index} {'P' if p.has_packages else ''}"
                text_color = BLACK if p.has_packages else WHITE
            text_surface = self.font.render(label, True, text_color)
            text_rect = text_surface.get_rect(center=p.get_position())
            surface.blit(text_surface, text_rect)

    def draw_connections(self, surface):
        """
        Rysuje trasy między punktami.
        Linie są rysowane zawsze czarnym kolorem.
        Dla każdej trasy (przy najechaniu myszy) wyświetlamy współczynnik korków
        oraz zapisany wcześniej (przeskalowany) wynik długości odcinka w metrach.
        """
        mouse_pos = pygame.mouse.get_pos()
        hover_threshold = 5  # próg w pikselach

        for conn in self.connections:
            # Połączenie jako krotka 4-elementowa: (idx1, idx2, factor, stored_length)
            idx1, idx2, factor, stored_length = conn
            p1 = self.points[idx1]
            p2 = self.points[idx2]
            avg_jam = (p1.jam_index + p2.jam_index) / 2
            coefficient = avg_jam * factor

            # Rysujemy linię na czarno
            pygame.draw.line(surface, BLACK, p1.get_position(), p2.get_position(), 2)
            
            # Sprawdzamy, czy mysz znajduje się w pobliżu linii
            dist_to_line = self.distance_from_point_to_line(
                mouse_pos[0], mouse_pos[1],
                p1.x, p1.y,
                p2.x, p2.y
            )
            if dist_to_line < hover_threshold:
                mid_x = (p1.x + p2.x) / 2
                mid_y = (p1.y + p2.y) / 2
                coeff_text = self.font.render(f"C: {coefficient:.2f}", True, BLACK)
                length_text = self.font.render(f"L: {stored_length:.2f} m", True, BLACK)
                surface.blit(coeff_text, (mid_x, mid_y))
                surface.blit(length_text, (mid_x, mid_y + 20))

    def print_points_and_routes(self):
        """
        Wypisuje do terminala informacje o wszystkich punktach oraz trasach.
        Dodatkowo dla każdego punktu wypisuje listę sąsiadów wraz z informacjami o opóźnieniu i długości trasy.
        """
        self.color_points()  # aby mieć zaktualizowane jam_index
        print("Punkty:")
        for p in self.points:
            print(f"Index: {p.index}, x: {p.x}, y: {p.y}, jam_index: {p.jam_index}, "
                  f"has_packages: {p.has_packages}, special: {p.special}, neighbors: {p.neighbors}")
        print("\nTrasy:")
        for conn in self.connections:
            idx1, idx2, factor, stored_length = conn
            p1 = self.points[idx1]
            p2 = self.points[idx2]
            avg_jam = (p1.jam_index + p2.jam_index) / 2
            coefficient = avg_jam * factor
            print(f"Z {idx1} do {idx2}, factor: {factor:.2f}, długość: {stored_length:.2f} m, "
                  f"współczynnik: {coefficient:.2f}")
    

    def run(self):
        """Główna pętla gry."""
        running = True
        clock = pygame.time.Clock()
        while running:
            clock.tick(60)  # 60 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.color_points()
            screen.fill(WHITE)
            self.draw_connections(screen)
            self.draw_points(screen)
            pygame.display.flip()



        pygame.quit()


if __name__ == '__main__':
    game = Game()
    # Wypisujemy do terminala wszystkie dane o punktach, sąsiadach i trasach
    game.print_points_and_routes()
    game.run()

    with open('obiekty.pkl', 'wb') as plik:  # 'wb' oznacza zapis binarny
        pickle.dump(game.points, plik)

    with open('polaczenia.pkl', 'wb') as plik:  # 'wb' oznacza zapis binarny
        pickle.dump(game.connections, plik)
