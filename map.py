import pygame
import numpy as np

# Inicjalizacja pygame
pygame.init()

# Ustawienia okna
TILE_SIZE = 20  # Wielkość kwadratu (w pikselach)
TILE_MARGIN = 1  # Margines między kwadratami
MAP_SIZE = 30   # Nowy rozmiar mapy (30x30)
WINDOW_SIZE = MAP_SIZE * (TILE_SIZE + TILE_MARGIN) - TILE_MARGIN
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Mapa 2D - Połączone Ścieżki")

# Kolory
COLOR_GRASS = (34, 139, 34)  # Zielony (trawa)
COLOR_ROAD = (128, 128, 128)  # Szary (droga)
COLOR_START_END = (0, 0, 255)  # Niebieski (punkt startowy i końcowy)

# Tworzenie macierzy mapy: 0 - trawa, 1 - droga
map_grid = np.zeros((MAP_SIZE, MAP_SIZE), dtype=int)

def generate_connected_paths(map_grid):
    # Punkt startowy (środek dolnej krawędzi mapy)
    start_x = MAP_SIZE // 2
    start_y = MAP_SIZE - 1

    # Punkt końcowy (środek górnej krawędzi mapy)
    end_x = MAP_SIZE // 2
    end_y = 0

    # Lista punktów startowych dla rozgałęzień
    connections = [(start_x, start_y), (end_x, end_y)]

    def add_path(x, y, target_x, target_y):
        while x != target_x or y != target_y:
            map_grid[y, x] = 1  # Ustaw ścieżkę
            if x < target_x:
                x += 1
            elif x > target_x:
                x -= 1
            elif y < target_y:
                y += 1
            elif y > target_y:
                y -= 1

    # Tworzenie głównej ścieżki
    add_path(start_x, start_y, end_x, end_y)

    # Tworzenie rozgałęzień i łączenie ich z innymi ścieżkami
    for _ in range(5):  # Liczba rozgałęzień
        branch_x = np.random.randint(1, MAP_SIZE - 1)
        branch_y = np.random.randint(1, MAP_SIZE - 1)
        target_x, target_y = connections[np.random.randint(len(connections))]
        add_path(branch_x, branch_y, target_x, target_y)
        connections.append((branch_x, branch_y))

    # Łączenie pozostałych punktów
    for i in range(len(connections)):
        for j in range(i + 1, len(connections)):
            if np.random.rand() > 0.5:  # Losowe połączenia
                add_path(connections[i][0], connections[i][1], connections[j][0], connections[j][1])

    return map_grid, start_x, start_y, end_x, end_y

# Generowanie połączonych dróg
map_grid, start_x, start_y, end_x, end_y = generate_connected_paths(map_grid)

# Główna pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rysowanie mapy
    screen.fill((0, 0, 0))  # Czarny kolor tła
    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            if (j, i) == (start_x, start_y) or (j, i) == (end_x, end_y):
                color = COLOR_START_END  # Niebieski dla punktu startowego i końcowego
            else:
                color = COLOR_GRASS if map_grid[i, j] == 0 else COLOR_ROAD
            pygame.draw.rect(
                screen,
                color,
                (
                    j * (TILE_SIZE + TILE_MARGIN),  # Pozycja X z marginesem
                    i * (TILE_SIZE + TILE_MARGIN),  # Pozycja Y z marginesem
                    TILE_SIZE,                      # Szerokość kwadratu
                    TILE_SIZE                       # Wysokość kwadratu
                )
            )

    # Aktualizacja ekranu
    pygame.display.flip()

# Zamykanie pygame
pygame.quit()
