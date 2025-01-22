import pygame
import numpy as np
import random

# Inicjalizacja pygame
pygame.init()

# Ustawienia okna
TILE_SIZE = 20
TILE_MARGIN = 1
MAP_SIZE = 30
WINDOW_SIZE = MAP_SIZE * (TILE_SIZE + TILE_MARGIN) - TILE_MARGIN
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Mapa 2D - Wiele Losowych Ścieżek")

# Kolory
COLOR_GRASS = (34, 139, 34)
COLOR_ROAD = (128, 128, 128)
COLOR_START_END = (0, 0, 255)

# Tworzenie pustej mapy
map_grid = np.zeros((MAP_SIZE, MAP_SIZE), dtype=int)

# Funkcja do generowania ścieżek
def generate_paths(num_paths):
    paths = []  # Lista przechowująca wszystkie ścieżki
    start_position = MAP_SIZE // 2  # Wspólny początek
    end_position = MAP_SIZE // 2    # Wspólny koniec

    # Oznacz początek mapy
    map_grid[MAP_SIZE - 1, start_position] = 2

    for path_idx in range(num_paths):
        path = []  # Lista pozycji dla bieżącej ścieżki
        current_x = start_position
        current_y = MAP_SIZE - 1

        while current_y > 0:
            # Dodaj aktualną pozycję do ścieżki
            path.append((current_y, current_x))
            map_grid[current_y, current_x] = 1

            # Losowy ruch w pionie lub poziomie
            direction = random.choice(["up", "left", "right"])
            if direction == "up" and current_y > 0:
                current_y -= 1
            elif direction == "left" and current_x > 1 and map_grid[current_y, current_x - 1] != 1:
                current_x -= 1
            elif direction == "right" and current_x < MAP_SIZE - 2 and map_grid[current_y, current_x + 1] != 1:
                current_x += 1

        # Dodaj końcowy punkt ścieżki
        path.append((0, end_position))
        map_grid[0, end_position] = 2

        # Zapisz ścieżkę
        paths.append(path)

    return paths

# Generowanie ścieżek
num_paths = 3  # Liczba ścieżek
paths = generate_paths(num_paths)

# Główna pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rysowanie mapy
    screen.fill((0, 0, 0))
    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            if map_grid[i, j] == 0:
                color = COLOR_GRASS
            elif map_grid[i, j] == 1:
                color = COLOR_ROAD
            elif map_grid[i, j] == 2:
                color = COLOR_START_END
            pygame.draw.rect(
                screen,
                color,
                (
                    j * (TILE_SIZE + TILE_MARGIN),
                    i * (TILE_SIZE + TILE_MARGIN),
                    TILE_SIZE,
                    TILE_SIZE
                )
            )
    pygame.display.flip()

# Wyświetlanie wygenerowanych ścieżek
for idx, path in enumerate(paths):
    print(f"Ścieżka {idx + 1}: {path}")

# Zamykanie pygame
pygame.quit()
