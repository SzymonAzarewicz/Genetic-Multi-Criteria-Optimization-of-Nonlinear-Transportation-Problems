import pickle
import random
from wizualicacja1 import Point

class PopulationGenerator:
    def __init__(self):
        self.points = pickle.load(open("obiekty.pkl", "rb"))
        self.connections = pickle.load(open("polaczenia.pkl", "rb"))
        self.graph = self._build_graph()
        self.sortownia_idx = next(p.index for p in self.points if p.special)

    def _build_graph(self):
        """Buduje graf sąsiedztwa na podstawie połączeń."""
        graph = {}
        for idx1, idx2, _, _ in self.connections:
            graph.setdefault(idx1, []).append(idx2)
            graph.setdefault(idx2, []).append(idx1)
        return graph

    def generate_initial_population(self, population_size=50, min_path_length=10, max_path_length=20):
        """
        Generuje populację początkową spełniającą:
        - Dokładnie `population_size` ścieżek
        - Każda ścieżka zaczyna i kończy się w sortowni
        - Długość ścieżki w zakresie [min_path_length, max_path_length]
        - Unikanie zbyt wczesnego powrotu do sortowni
        """
        population = []
        attempts = 0
        max_attempts = population_size * 10  # Zabezpieczenie przed nieskończoną pętlą

        while len(population) < population_size and attempts < max_attempts:
            path = [self.sortownia_idx]
            current_node = self.sortownia_idx
            visited = set([current_node])

            # Generuj ścieżkę do osiągnięcia max długości lub powrotu
            while len(path) < max_path_length:
                neighbors = [
                    n for n in self.graph[current_node]
                    if n not in visited or (n == self.sortownia_idx and len(path) >= min_path_length - 1)
                ]
                
                if not neighbors:
                    break
                
                next_node = random.choice(neighbors)
                path.append(next_node)
                
                if next_node == self.sortownia_idx:
                    if len(path) >= min_path_length:
                        population.append(path)
                    break
                
                current_node = next_node
                visited.add(current_node)
            
            attempts += 1

        if len(population) < population_size:
            print(f"Uwaga: Wygenerowano tylko {len(population)} poprawnych tras z {population_size} prób")
        return population

    def save_population(self, population, filename="populacja.pkl"):
        with open(filename, 'wb') as f:
            pickle.dump({"paths": population}, f)

if __name__ == "__main__":
    generator = PopulationGenerator()
    population = generator.generate_initial_population(population_size=50, min_path_length=10, max_path_length=20)
    generator.save_population(population)
    print(f"Wygenerowano {len(population)} poprawnych tras")