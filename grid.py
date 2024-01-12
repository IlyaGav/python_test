import pyzorder
from typing import List, Dict

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm
import shapely
from shapely import Geometry, Polygon, Point

import z_curve
from shapely_plot import add_to_plot_geometry, show_plot

class SpatialGrid:
    def __init__(self, boundary: Polygon, grid_size: int = 4, limit_cells: int = 16, levels: int = 4):
        self.boundary = boundary
        self.grid_size = grid_size

        minx, miny, maxx, maxy = boundary.bounds

        self.width = maxx - minx
        self.height = maxy - miny

        self.limit_cells = limit_cells
        self.levels = levels
        # TODO не выделять сразу память (мб тогда словарь использовать)
        # self.grids: List[List[List[Geometry] | None]] = [[None] * pow(grid_size, pow(l + 1, 2)) for l in range(levels)]
        self.grids: List[Dict[int, List[Geometry]]] = [{} for _ in range(levels)]

    # def calculate_level(self, width, height):
    #     max_dimension = max(width, height)
    #     level = 0
    #     while max_dimension > self.base_grid_size and level < self.levels:
    #         max_dimension /= 2
    #         level += 1
    #     return min(level, self.levels - 1)

    def add_object(self, obj: Geometry):
        minx, miny, maxx, maxy = Polygon(shapely.envelope(obj)).bounds

        for level in range(self.levels):

            cell_width = self.width / pow(self.grid_size, level + 1)
            cell_height = self.height / pow(self.grid_size, level + 1)

            grid_x1_on_next = int(minx // (cell_width / self.grid_size))
            grid_y1_on_next = int(miny // (cell_height / self.grid_size))
            grid_x2_on_next = int(maxx // (cell_width / self.grid_size))
            grid_y2_on_next = int(maxy // (cell_height / self.grid_size))

            covered_on_next = (grid_x2_on_next - grid_x1_on_next + 1) * (grid_y2_on_next - grid_y1_on_next + 1)

            # print(f' l = {level}, (w, h) = {(cell_width, cell_height)}, covered_next = {covered_on_next}')

            # Если след уровнь превышает ограничение, то останавливаемся на текущем
            if covered_on_next >= self.limit_cells or level == self.levels - 1:

                grid_x1, grid_y1 = int(minx // cell_width), int(miny // cell_height)
                grid_x2, grid_y2 = int(maxx // cell_width), int(maxy // cell_height)

                for x in range(grid_x1, grid_x2 + 1):
                    for y in range(grid_y1, grid_y2 + 1):
                        cell_id = z_curve.z_encode(x, y)
                        if cell_id not in self.grids[level]:
                            self.grids[level][cell_id] = []

                        self.grids[level][cell_id].append(obj)

                break

    def get_objects_in_cell(self, level, cell_id):
        return self.grids[level].get(cell_id, [])


def grid_find_nearest_neighbor(grid, point: Point):
    min_distance = float('inf')
    nearest_neighbor = None

    query_x, query_y = point.x, point.y

    for level in range(0, grid.levels):
        cell_width = grid.width / pow(grid.grid_size, level + 1)
        cell_height = grid.height / pow(grid.grid_size, level + 1)

        grid_x, grid_y = int(query_x // cell_width), int(query_y // cell_height)

        cell_id = z_curve.z_encode(grid_x, grid_y)

        neighbors = grid.get_objects_in_cell(level, cell_id)

        for neighbor in neighbors:

            # TODO Дистанцию считать от MBR
            #  Подумать:
            #  Если до MBR ближе, то и до фигуры ближе?
            #  А если точка содержится в MBR, то может быть что до другой фигуры будет ближе
            distance = shapely.distance(point, neighbor)

            if distance < min_distance:
                min_distance = distance
                nearest_neighbor = neighbor

    return nearest_neighbor


def visualize_grid(grid: SpatialGrid):
    for level in range(grid.levels):
        cells = grid.grids[level]
        for cell in cells:
            xmin, ymin = z_curve.z_decode(cell)

            width = grid.width / pow(grid.grid_size, level + 1)
            height = grid.height / pow(grid.grid_size, level + 1)
            xmin = xmin * width
            ymin = ymin * height

            box = shapely.box(xmin, ymin, xmin + width, ymin + height)
            add_to_plot_geometry(box, 'black')


def print_grid(spatial_grid):
    for level in range(spatial_grid.levels):
        print(f"Grid Level {level}:")

        for cell, objects in spatial_grid.grids[level].items():
            x, y = cell
            print(f"Cell ({x}, {y}): {len(objects)} objects")

            for obj in objects:
                print(obj)

        print("\n")
