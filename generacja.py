import pickle
import random
from wizualicacja1 import Point  # zachowujemy import klasy Point

class PopulationGenerator:
    def __init__(self):
        # Wczytaj dane z plików pickle
        self.points = pickle.load(open("obiekty.pkl", "rb"))
        self.connections = pickle.load(open("polaczenia.pkl", "rb"))
        
        # Inicjalizacja grafu połączeń
        self.graph = self.build_graph()
        self.sortownia = next((p for p in self.points if p.special), None)

    def build_graph(self):
        """Buduje graf połączeń między punktami."""
        graph = {}
        for conn in self.connections:
            idx1, idx2, _, _ = conn
            graph.setdefault(idx1, []).append(idx2)
            graph.setdefault(idx2, []).append(idx1)
        return graph

    def generate_initial_population(self, population_size=50, path_length_range=(5, 15)):
        """
        Generuje początkową populację tras.
        
        Args:
            population_size (int): Liczba tras w populacji
            path_length_range (tuple): Zakres długości tras (min, max)
            
        Returns:
            list: Lista wygenerowanych tras
        """
        population = []
        sortownia_idx = self.sortownia.index
        # Bierzemy wszystkie punkty oprócz sortowni
        all_points = [p.index for p in self.points if not p.special]

        for _ in range(population_size):
            # Rozpocznij od sortowni
            path = [sortownia_idx]
            
            # Losowa długość ścieżki z podanego zakresu
            path_length = random.randint(*path_length_range)
            
            # Generuj punkty pośrednie
            available_points = all_points.copy()
            for _ in range(path_length - 2):  # -2 bo mamy początek i koniec w sortowni
                if not available_points:
                    break
                    
                next_point = random.choice(available_points)
                path.append(next_point)
                available_points.remove(next_point)
            
            # Dodaj powrót do sortowni
            path.append(sortownia_idx)
            
            population.append(path)

        return population

    def save_population(self, population, filename="populacja.pkl"):
        """
        Zapisuje wszystkie ścieżki z populacji do jednego pliku pickle.
        """
        data = {
            "population_size": len(population),
            "paths": population
        }
        with open(filename, 'wb') as f:
            pickle.dump(data, f)

def main():
    # Utworzenie generatora
    generator = PopulationGenerator()
    
    # Generowanie populacji
    population = generator.generate_initial_population(
        population_size=50,  # możesz dostosować te parametry
        path_length_range=(5, 15)
    )
    
    # Zapisanie populacji do pliku
    generator.save_population(population)
    
    # Opcjonalnie: wyświetl informacje o wygenerowanej populacji
    print(f"Wygenerowano populację zawierającą {len(population)} tras")

if __name__ == "__main__":
    main()