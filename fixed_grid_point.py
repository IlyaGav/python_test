from typing import List, Dict

import shapely
from shapely import Polygon, Point

from shapely_plot import add_to_plot_geometry, show_plot


class FixedGridPoint:
    def __init__(self, boundary: Polygon, grid_size: int = 4):
        self.boundary = boundary
        self.grid_size = grid_size

        minx, miny, maxx, maxy = self.boundary.bounds

        self.width = maxx - minx
        self.height = maxy - miny

        self.cell_width = self.width / self.grid_size
        self.cell_height = self.height / self.grid_size

        self.cells: Dict[tuple[int, int], List[Point]] = {}

    def add_object(self, point: Point):
        x, y = point.x, point.y

        grid_x, grid_y = int(x // self.cell_width), int(y // self.cell_height)

        if (grid_x, grid_y) not in self.cells:
            self.cells[(grid_x, grid_y)] = []

        self.cells[(grid_x, grid_y)].append(point)

    def get_objects_in_cell(self, x, y):
        return self.cells.get((x, y), [])


def build_fixed_grid_point(boundary: Polygon, shapes: List[shapely.Point], grid_size: int = 4):
    grid = FixedGridPoint(boundary, grid_size)

    for shape in shapes:
        grid.add_object(shape)

    return grid


def fixed_grid_point_find_nearest_neighbor(grid: FixedGridPoint, query_point: Point):
    query_x, query_y = query_point.x, query_point.y

    if len(grid.cells) == 0:
        return None

    cell_x, cell_y = int(query_x // grid.cell_width), int(query_y // grid.cell_height)

    # Содержащая ячейка и ячейки вокруг нее
    nearest_cells = [(cell_x, cell_y), *circular_traversal(cell_x, cell_y, 1)]

    neighbors = list(set([cc for c in nearest_cells for cc in grid.cells.get((c[0], c[1]), [])]))

    neighbor = get_nearest(neighbors, query_point)

    if neighbor is not None:
        return neighbor

    # Если в смежных ячейках нет соседей, то бежим по остальным
    max_x_radius = max(cell_x, grid.grid_size - cell_x)
    max_y_radius = max(cell_y, grid.grid_size - cell_y)
    max_radius = max(max_x_radius, max_y_radius)

    # Бежим с 2ки, тк в ближайшее заходили выше
    for r in range(2, max_radius + 1):
        nearest_cells = circular_traversal(cell_x, cell_y, r)

        # plot_fixed_grid(grid)
        # for cc in nearest_cells:
        #     x = cc[0] * grid.cell_width
        #     y = cc[1] * grid.cell_height
        #
        #     box = shapely.box(x, y, x + grid.cell_width, y + grid.cell_height)
        #     add_to_plot_geometry(box, 'red')
        #
        # show_plot()

        neighbors = list(set([cc for c in nearest_cells for cc in grid.cells.get((c[0], c[1]), [])]))

        neighbor = get_nearest(neighbors, query_point)

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


def get_nearest(neighbors: List[Point], point: Point):
    min_distance = float('inf')
    nearest = None

    for neighbor in neighbors:

        distance = shapely.distance(point, neighbor)

        if distance < min_distance:
            min_distance = distance
            nearest = neighbor

    return nearest


def plot_fixed_grid_point(grid: FixedGridPoint):
    for i in range(grid.grid_size):
        for j in range(grid.grid_size):

            x = i * grid.cell_width
            y = j * grid.cell_height

            box = shapely.box(x, y, x + grid.cell_width, y + grid.cell_height)
            add_to_plot_geometry(box, 'black')

            cell = grid.cells.get((i, j), [])

            for point in cell:
                add_to_plot_geometry(point, 'orange')
