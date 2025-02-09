import pygame
import random
import math


# Inicjalizacja pygame
pygame.init()

# Ustawienia ekranu
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Łączenie Punktów")

# Kolory
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
ORANGE = (255,150,0)
YELLOW = (255,220,0)
BLACK = (100,100,100)

# Klasa reprezentująca punkt
class Point:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.index = index
        self.jam_index=0


# Funkcja rysująca punkt
def draw_point(point, screen, font, radius):
    if point.jam_index==3:
        pygame.draw.circle(screen, RED, (point.x, point.y), radius)
    elif point.jam_index==2:
        pygame.draw.circle(screen, ORANGE, (point.x, point.y), radius)
    else:
        pygame.draw.circle(screen, YELLOW, (point.x, point.y), radius)
    text_surface = font.render(str(point.index), True, WHITE)
    text_rect = text_surface.get_rect(center=(point.x, point.y))
    screen.blit(text_surface, text_rect)

# Funkcja sprawdzająca minimalny dystans
def is_too_close(new_x, new_y, points, min_distance):
    for point in points:
        distance = math.sqrt((new_x - point.x) ** 2 + (new_y - point.y) ** 2)
        if distance < min_distance:
            return True
    return False

# Funkcja obliczająca dystans między dwoma punktami
def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

# Funkcja obliczająca odległość punktu od odcinka
def distance_from_point_to_line(px, py, x1, y1, x2, y2):
    """Oblicza minimalną odległość od punktu (px, py) do odcinka (x1, y1)-(x2, y2)."""
    line_len = calculate_distance(Point(x1, y1, -1), Point(x2, y2, -1))
    if line_len == 0:
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len**2))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)

# Funkcja sprawdzająca, czy dwa odcinki się przecinają
def orientation(p, q, r):
    """Sprawdza orientację trzech punktów: p, q, r."""
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val == 0:
        return 0  # punkty współliniowe
    return 1 if val > 0 else 2  # 1 -> zgodnie z ruchem wskazówek zegara, 2 -> przeciwnie

def do_segments_intersect(p1, q1, p2, q2):
    """Sprawdza, czy odcinki (p1, q1) i (p2, q2) się przecinają."""
    # Ignoruj przypadek, gdy odcinki mają wspólny punkt końcowy
    if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
        return False

    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # Ogólny przypadek
    if o1 != o2 and o3 != o4:
        return True

    # Specjalne przypadki: sprawdzanie współliniowości
    if o1 == 0 and is_on_segment(p1, p2, q1):
        return True
    if o2 == 0 and is_on_segment(p1, q2, q1):
        return True
    if o3 == 0 and is_on_segment(p2, p1, q2):
        return True
    if o4 == 0 and is_on_segment(p2, q1, q2):
        return True

    return False

def is_on_segment(p, q, r):
    """Sprawdza, czy punkt q leży na odcinku pr (zakładając współliniowość)."""
    if q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y):
        return True
    return False

# Funkcja sprawdzająca, czy linia przechodzi przez inne punkty
def line_passes_through_other_points(p1, p2):
    """Sprawdza, czy linia (p1, p2) przechodzi przez środek innych punktów."""
    for point in points:
        if point == p1 or point == p2:
            continue
        distance = distance_from_point_to_line(point.x, point.y, p1.x, p1.y, p2.x, p2.y)
        if distance < radius:  # Jeśli linia przechodzi przez "koło" punktu
            return True
    return False

def calculate_centroid(points):
    """Oblicza środek ciężkości wszystkich punktów."""
    if not points:
        return None  # Jeśli lista punktów jest pusta, zwróć None
    
    sum_x = sum(point.x for point in points)
    sum_y = sum(point.y for point in points)
    num_points = len(points)
    
    centroid_x = sum_x / num_points
    centroid_y = sum_y / num_points
    
    return centroid_x, centroid_y  # Tworzymy punkt dla środka ciężkości

def find_max_distance_from_centroid(points, centroid_x, centroid_y):
    """Znajduje największą odległość od centroidu do najdalszego punktu."""
    if not points:
        return None  # Jeśli lista punktów jest pusta, zwróć None
    
    max_distance = 0
    
    for point in points:
        # Oblicz odległość punktu od centroidu
        distance = math.sqrt((point.x - centroid_x) ** 2 + (point.y - centroid_y) ** 2)
        
        # Sprawdź, czy odległość jest większa niż aktualne max
        if distance > max_distance:
            max_distance = distance
    
    return max_distance

def coloring_points(points):
    centroid_x, centroid_y = calculate_centroid(points)
    radius = find_max_distance_from_centroid(points, centroid_x, centroid_y)

    for point in points:
        distance = math.sqrt((point.x - centroid_x) ** 2 + (point.y - centroid_y) ** 2)
        if distance <= 0.35*radius:
            point.jam_index = 3
        elif distance <=0.7*radius:
            point.jam_index = 2
        else:
            point.jam_index = 1

# Funkcja dodająca połączenia między punktami
def connect_points():
    global connections
    added = True
    while added:
        added = False
        for point in points:
            closest_working_point = None
            closest_working_point_distance = float('inf')
            for other_point in points:
                if point == other_point:
                    continue

                # Sprawdź, czy linia już istnieje
                if (point.index, other_point.index) in connections or (other_point.index, point.index) in connections:
                    continue

                # Sprawdź, czy nowa linia przecina istniejące lub przechodzi przez inne punkty
                new_line_valid = True
                for connection in connections:
                    existing_point1 = points[connection[0]]
                    existing_point2 = points[connection[1]]
                    if do_segments_intersect(point, other_point, existing_point1, existing_point2):
                        new_line_valid = False
                        break
                if new_line_valid and line_passes_through_other_points(point, other_point):
                    new_line_valid = False

                # Dodaj linię, jeśli jest poprawna
                if new_line_valid:
                    distance = math.sqrt((point.x - other_point.x) ** 2 + (point.y - other_point.y) ** 2)
                    if distance < closest_working_point_distance:
                        closest_working_point = other_point
                        closest_working_point_distance = distance
                    added = True

            if closest_working_point is not None:
                connections.append((point.index, closest_working_point.index))


# Generowanie 20 losowych punktów z minimalnym dystansem
num_points = 35
radius = 20
min_distance = radius * 4
points = []

for i in range(num_points):
    while True:
        x = random.randint(radius, WIDTH - radius)
        y = random.randint(radius, HEIGHT - radius)
        if not is_too_close(x, y, points, min_distance):
            points.append(Point(x, y, i))
            break

# Czcionka do numerów
font = pygame.font.Font(None, 24)

# Lista połączeń między punktami
connections = []
# Pętla gry
running = True
connect_points()  # Wygeneruj połączenia na początku
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rysowanie linii między punktami
    for connection in connections:
        point1 = points[connection[0]]
        point2 = points[connection[1]]
        pygame.draw.line(screen, BLACK, (point1.x, point1.y), (point2.x, point2.y), 2)

    coloring_points(points)
    # Rysowanie punktów
    for point in points:
        draw_point(point, screen, font, radius)

    # Aktualizacja ekranu
    pygame.display.flip()

# Zakończenie pygame
pygame.quit()