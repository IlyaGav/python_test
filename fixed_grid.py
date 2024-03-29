from typing import List, Dict

import shapely
from shapely import Geometry, Polygon, Point

from shapely_plot import add_to_plot_geometry


class FixedGrid:
    def __init__(self, boundary: Polygon, grid_size: int = 4):
        self.boundary = boundary
        self.grid_size = grid_size

        minx, miny, maxx, maxy = self.boundary.bounds

        self.width = maxx - minx
        self.height = maxy - miny

        self.cell_width = self.width / self.grid_size
        self.cell_height = self.height / self.grid_size

        self.cells: Dict[tuple[int, int], List[Geometry]] = {}

    def add_object(self, obj: Geometry):
        minx, miny, maxx, maxy = Polygon(shapely.envelope(obj)).bounds

        grid_x1, grid_y1 = int(minx // self.cell_width), int(miny // self.cell_height)
        grid_x2, grid_y2 = int(maxx // self.cell_width), int(maxy // self.cell_height)

        for x in range(grid_x1, grid_x2 + 1):
            for y in range(grid_y1, grid_y2 + 1):
                if (x, y) not in self.cells:
                    self.cells[(x, y)] = []

                self.cells[(x, y)].append(obj)

    def get_objects_in_cell(self, x, y):
        return self.cells.get((x, y), [])


def build_fixed_grid(boundary: Polygon, shapes: List[shapely.Geometry], grid_size: int = 64):
    grid = FixedGrid(boundary, grid_size)

    for shape in shapes:
        grid.add_object(shape)

    return grid


def fixed_grid_find_nearest_neighbor(grid: FixedGrid, point: Point):
    query_x, query_y = point.x, point.y

    if len(grid.cells) == 0:
        return None

    cell_x, cell_y = int(query_x // grid.cell_width), int(query_y // grid.cell_height)

    # Содержащая ячейка и ячейки вокруг нее
    nearest_cells = [(cell_x, cell_y), *circular_traversal(cell_x, cell_y, 1)]

    neighbors = list(set([cc for c in nearest_cells for cc in grid.cells.get((c[0], c[1]), [])]))

    neighbor = get_nearest(neighbors, point)

    if neighbor is not None:
        return neighbor

    nearest_neighbor = None

    # Если в смежных ячейках нет соседей, то бежим по остальным
    max_x_radius = max(cell_x, grid.grid_size - cell_x)
    max_y_radius = max(cell_y, grid.grid_size - cell_y)
    max_radius = max(max_x_radius, max_y_radius)

    # Бежим с 2ки, тк в ближайшее заходили выше
    for r in range(2, max_radius + 1):
        nearest_cells = circular_traversal(cell_x, cell_y, r)

        neighbors = list(set([cc for c in nearest_cells for cc in grid.cells.get((c[0], c[1]), [])]))

        neighbor = get_nearest(neighbors, point)

        # Ближайших на этом уровне, дальше можно не искать
        if neighbor is not None:
            return neighbor

    return None


def circular_traversal(x_c, y_c, r):
    x = 0
    y = r
    delta = 3 - 2 * y

    cells = []

    while x <= y:
        cells.append((x_c + x, y_c + y))
        cells.append((x_c + x, y_c - y))
        cells.append((x_c - x, y_c + y))
        cells.append((x_c - x, y_c - y))
        cells.append((x_c + y, y_c + x))
        cells.append((x_c + y, y_c - x))
        cells.append((x_c - y, y_c + x))
        cells.append((x_c - y, y_c - x))

        delta += 4 * x + 6 if delta < 0 else 4 * (x - y - 1) + 10
        x += 1

    return cells


def get_nearest(neighbors: List[Geometry], point: Point):
    min_distance = float('inf')
    nearest = None

    for neighbor in neighbors:
        # TODO Дистанцию считать от MBR
        #  Подумать:
        #  Если до MBR ближе, то и до фигуры ближе?
        #  А если точка содержится в MBR, то может быть что до другой фигуры будет ближе
        distance = shapely.distance(point, neighbor)

        if distance < min_distance:
            min_distance = distance
            nearest = neighbor

    return nearest


def plot_fixed_grid(grid: FixedGrid):
    for i in range(grid.grid_size):
        for j in range(grid.grid_size):

            x = i * grid.cell_width
            y = j * grid.cell_height

            box = shapely.box(x, y, x + grid.cell_width, y + grid.cell_height)
            add_to_plot_geometry(box, 'black')

            cell = grid.cells.get((i, j), [])

            for shape in cell:
                add_to_plot_geometry(shape, 'orange')
