'''     
Trabalho-2 de Teoria dos Grafos

Alunos: 
* Carlos Gabriel de Oliveira Frazão - 22.1.8100
* Patrick Peres Nicolini - 22.1.8103

'''

import heapq
from PIL import Image
from collections import deque
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ImageGraph:
    def __init__(self, image_paths):
        
        self.images = [Image.open(image_path) for image_path in image_paths]
        self.width, self.height = self.images[0].size
        self.graph = {}
        self.number_of_edges = 0
        self.number_of_nodes = 0
        self.green_pixels = []
        self.red_pixel = None
        self.red_pixels = []
        self.rotations = []
        self.red_area_height = 0
        self.red_area_width = 0

    def build_graph(self):
        for z, image in enumerate(self.images):
            for x in range(self.width):
                for y in range(self.height):
                    color = image.getpixel((x, y))
                    if color == (0, 255, 0):
                        self.green_pixels.append((x, y, z))
                    elif color == (255, 0, 0):
                        self.red_pixel = (x, y, z)
                        self.red_pixels.append((x, y, z))
                    
                    if color != (0, 0, 0):
                        self.graph[(x, y, z)] = {}
                        self.number_of_nodes += 1

        for z, image in enumerate(self.images):
            for x in range(self.width):
                for y in range(self.height):
                    color = image.getpixel((x, y))
                    if color != (0, 0, 0):
                        neighbors = [(x-1, y, z), (x+1, y, z), (x, y-1, z), (x, y+1, z), (x, y, z-1), (x, y, z+1)]
                        for neighbor in neighbors:
                            if neighbor in self.graph and image.getpixel((x, y)) != (0, 0, 0):
                                weight = self.calculate_weight(color, image.getpixel((neighbor[0], neighbor[1])), z != neighbor[2])
                                self.graph[(x, y, z)][neighbor] = weight
                                self.number_of_edges += 1

        self.red_area(self.red_pixel)

    def calculate_weight(self, color1, color2, different_floor):
        if different_floor:
            return 5
        elif color2 == (128, 128, 128):
            return 4
        elif color2 == (196, 196, 196):
            return 2
        else:
            return 1

    def red_area(self,node):
        decrease_x = 1
        increase_y = 1

        x, y = node[0], node[1]

        while(1):
            if self.images[node[2]].getpixel((x-decrease_x, y)) == (255, 0, 0):
                decrease_x += 1
                self.red_area_width += 1
            else:
                break

        x, y = node[0], node[1]

        while(1):
            if self.images[node[2]].getpixel((x, y-increase_y)) == (255, 0, 0):
                increase_y += 1
                self.red_area_height += 1
            else:
                break

        self.red_area_width += 1
        self.red_area_height += 1
                            

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
    
    def dijkstra(self, s):
        dist = {node: float("inf") for node in self.graph}
        pred = {node: None for node in self.graph}
        dist[s] = 0
        Q = [(dist[s], s)]
        u = None
        while Q:
            dist_u, u = heapq.heappop(Q)
            if u in self.green_pixels:
                return dist, pred, u
            for v in self.graph[u]:

                if not self.is_valid_area(v):
                    continue


                if dist[v] > dist_u + self.graph[u][v]:
                    dist[v] = dist_u + self.graph[u][v]
                    heapq.heappush(Q, (dist[v], v))
                    pred[v] = u
        return dist, pred, None
    
    def is_valid_area(self, v):
        # given a v node, tests if the pixels around it are not black
        for i in range(v[0], v[0] - self.red_area_width, -1):
            for j in range(v[1], v[1] - self.red_area_height, -1):
                if self.images[v[2]].getpixel((i, j)) == (0, 0, 0):
                    return False
                if i > self.width or i < 0 or j > self.height or j < 0:
                    return False
        # checks below the pixel imedialety below the node
        if self.images[v[2]].getpixel((v[0], v[1] - 1)) == (0, 0, 0):
            return False
        return True
    
    def rotate(self):
        temp = self.red_area_width
        self.red_area_width = self.red_area_height
        self.red_area_height = temp

    def is_valid_area_with_rotation(self, v):
        if not self.is_valid_area(v):
            self.rotate()
        if not self.is_valid_area(v):
            self.rotate()
            return False
        return True
