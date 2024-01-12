from functools import cmp_to_key
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


def grid_find_nearest_neighbor(grid: SpatialGrid, point: Point):
    min_distance = float('inf')
    nearest_neighbor = None

    query_x, query_y = point.x, point.y

    for level in range(0, grid.levels):
        print(f'level {level}')

        nearest_neighbor_on_level = None

        cell_width = grid.width / pow(grid.grid_size, level + 1)
        cell_height = grid.height / pow(grid.grid_size, level + 1)

        grid_x, grid_y = int(query_x // cell_width), int(query_y // cell_height)

        cell_id = z_curve.z_encode(grid_x, grid_y)

        print(f'cell_id {cell_id}')

        neighbors = grid.grids[level].get(cell_id, [])

        for neighbor in neighbors:
            # TODO Дистанцию считать от MBR
            #  Подумать:
            #  Если до MBR ближе, то и до фигуры ближе?
            #  А если точка содержится в MBR, то может быть что до другой фигуры будет ближе
            distance = shapely.distance(point, neighbor)

            if distance < min_distance:
                min_distance = distance
                nearest_neighbor_on_level = neighbor
                nearest_neighbor = neighbor

        print(f'nearest_neighbor {nearest_neighbor}')

        if nearest_neighbor_on_level is None:
            # TODO Добавить какой-то радиус? Все ячейки может быть много для последнего уровня
            cell_keys = list(grid.grids[level].keys())

            if len(cell_keys) == 0:
                continue

            if cell_id not in cell_keys:
                cell_keys.append(cell_id)

            print(f'source_keys {cell_keys}')

            cell_keys = sorted(cell_keys, key=cmp_to_key(z_curve.cmp_zorder))
            print(f'cmp_zorder_keys {cell_keys}')

            target_index = cell_keys.index(cell_id)
            cell_keys = sorted(enumerate(cell_keys), key=lambda item: abs(item[0] - target_index))

            print(f'target_order_keys {cell_keys}')

            cell_keys = list(map(lambda c: c[1], cell_keys))

            print(f'pre_output_keys {cell_keys}')

            cell_keys = cell_keys[1:]

            print(f'output_keys {cell_keys}')

            cells: List[List[Geometry]] = []

            for index, cell_key in enumerate(cell_keys):
                cell = grid.grids[level][cell_key]
                if cell is not None and len(cell) > 0:
                    cells.append(cell)
                    # Посетили ближайшие в округе
                    if index > 7:
                        break

            neighbors_2 = [cc for c in cells for cc in c]

            for neighbor in neighbors_2:
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
