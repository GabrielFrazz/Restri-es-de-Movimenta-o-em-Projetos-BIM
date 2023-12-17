'''     
Trabalho-1 de Teoria dos Grafos

Alunos: 
* Carlos Gabriel de Oliveira Frazão - 22.1.8100
* Patrick Peres Nicolini - 22.1.8103

'''

from PIL import Image
from collections import deque

class ImageGraph:
    def __init__(self, image_path):
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size
        self.graph = {}
        self.number_of_edges = 0
        self.number_of_nodes = 0
        self.green_pixel = None
        self.red_pixel = None

    def build_graph(self):
        for x in range(self.width):
            for y in range(self.height):
                color = self.image.getpixel((x, y))
                if color == (0, 255, 0):
                    self.green_pixel = (x, y)
                elif color == (255, 0, 0):
                    self.red_pixel = (x, y)
                    
                if color != (0, 0, 0):
                    self.graph[(x, y)] = []
                    self.number_of_nodes += 1

        for x in range(self.width):
            for y in range(self.height):
                color = self.image.getpixel((x, y))
                if color != (0, 0, 0):
                    neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                    for neighbor in neighbors:
                        if neighbor in self.graph and self.image.getpixel(neighbor) != (0, 0, 0):
                            self.graph[(x, y)].append(neighbor)
                            self.number_of_edges += 1

    def find_path(self, start, end):
        queue = deque([start])
        visited = {start: True}
        predecessors = {start: None}
        distances = {start: 0}

        while queue:
            current_point = queue.popleft()
            if current_point == end:
                path = []
                while current_point != start:
                    path.append(current_point)
                    current_point = predecessors[current_point]
                path.append(start)
                path.reverse()
                return path

            for neighbor in self.graph[current_point]:
                if neighbor not in visited:
                    visited[neighbor] = True
                    predecessors[neighbor] = current_point
                    distances[neighbor] = distances[current_point] + 1
                    queue.append(neighbor)

        return None
