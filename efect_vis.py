import pygame
import pickle

from wizualicacja1 import Point  # zachowujemy import klasy Point

# Ustawienia ekranu
WIDTH, HEIGHT = 800, 800

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

def load_data():
    """Wczytuje dane z plików."""
    try:
        points = pickle.load(open('obiekty.pkl', 'rb'))
        connections = pickle.load(open('polaczenia.pkl', 'rb'))
        population_data = pickle.load(open('populacja.pkl', 'rb'))
        paths = population_data["paths"]
        return points, connections, paths
    except Exception as e:
        print(f"Błąd podczas wczytywania plików: {e}")
        return [], [], []

def draw_points(surface, points):
    """Rysuje punkty na mapie."""
    for p in points:
        if p.has_packages:
            color = GREEN
        elif p.special:
            color = BLUE
        else:
            color = BLACK
        pygame.draw.circle(surface, color, p.get_position(), 10)
        if p.special:
            label = "Sortownia"
        else:
            label = str(p.index)
        font = pygame.font.Font(None, 24)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=p.get_position())
        surface.blit(text, text_rect)

def draw_connections(surface, connections, points):
    """Rysuje połączenia między punktami."""
    for conn in connections:
        idx1, idx2, _, _ = conn
        p1 = points[idx1]
        p2 = points[idx2]
        pygame.draw.line(surface, BLACK, p1.get_position(), p2.get_position(), 2)

def draw_path(surface, path, points):
    """Rysuje aktualną ścieżkę na mapie."""
    if not path:
        return
    for i in range(len(path) - 1):
        start_index = path[i]
        end_index = path[i + 1]
        start_point = points[start_index]
        end_point = points[end_index]
        pygame.draw.line(surface, RED, start_point.get_position(), end_point.get_position(), 4)

def draw_navigation_buttons(surface):
    """Rysuje przyciski nawigacji."""
    pygame.draw.rect(surface, GRAY, (50, HEIGHT - 80, 150, 50))
    pygame.draw.rect(surface, GRAY, (WIDTH - 200, HEIGHT - 80, 150, 50))
    font = pygame.font.Font(None, 36)
    text_prev = font.render("Poprzednia", True, BLACK)
    text_next = font.render("Następna", True, BLACK)
    surface.blit(text_prev, (60, HEIGHT - 70))
    surface.blit(text_next, (WIDTH - 190, HEIGHT - 70))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wizualizacja Ścieżek")

    points, connections, paths = load_data()
    if not paths:
        print("Brak ścieżek do wyświetlenia!")
        return

    current_path_index = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 50 <= x <= 200 and HEIGHT - 80 <= y <= HEIGHT - 30:
                    current_path_index = max(0, current_path_index - 1)
                elif WIDTH - 200 <= x <= WIDTH - 50 and HEIGHT - 80 <= y <= HEIGHT - 30:
                    current_path_index = min(len(paths) - 1, current_path_index + 1)

        screen.fill(WHITE)
        draw_connections(screen, connections, points)
        draw_points(screen, points)
        draw_path(screen, paths[current_path_index], points)
        draw_navigation_buttons(screen)

        font = pygame.font.Font(None, 36)
        text = font.render(f"Ścieżka {current_path_index + 1}/{len(paths)}", True, GREEN)
        screen.blit(text, (WIDTH // 2 - 60, 20))

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()