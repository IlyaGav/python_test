from typing import List, Dict

import shapely
from shapely import Polygon, Point, Geometry

from common import Entry, get_nearest, geometry_to_box, intersection, BoundaryBox, contains
from shapely_plot import add_to_plot_geometry


class FixedGrid(BoundaryBox):
    def __init__(self, boundary: Polygon, grid_size: int = 4):
        x_min, y_min, x_max, y_max = (shapely.envelope(boundary)).bounds
        super().__init__(x_min, y_min, x_max, y_max)

        self.grid_size = grid_size

        self.width = x_max - x_min
        self.height = y_max - y_min

        self.cell_width = self.width / self.grid_size
        self.cell_height = self.height / self.grid_size

        self.cells: Dict[tuple[int, int], List[Entry]] = {}

    def insert(self, entry: Entry):
        if not contains(self, entry):
            raise ValueError("ElementOutside")

        grid_x1, grid_y1 = int(entry.x_min // self.cell_width), int(entry.y_min // self.cell_height)
        grid_x2, grid_y2 = int(entry.x_max // self.cell_width), int(entry.y_max // self.cell_height)

        for x in range(grid_x1, grid_x2 + 1):
            for y in range(grid_y1, grid_y2 + 1):
                if (x, y) not in self.cells:
                    self.cells[(x, y)] = []

                self.cells[(x, y)].append(entry)

    def find_nearest_neighbor(self, point: Point):
        query_x, query_y = point.x, point.y

        cell_x, cell_y = int(query_x // self.cell_width), int(query_y // self.cell_height)

        # Содержащая ячейка
        neighbors = self.get_objects_in_cell(cell_x, cell_y)
        nearest = get_nearest_entry(neighbors, point)

        if nearest is not None:
            return nearest.shape

        # Если в ячейке нет соседей, то бежим по остальным
        max_x_radius = max(cell_x, self.grid_size - cell_x + 1)
        max_y_radius = max(cell_y, self.grid_size - cell_y + 1)
        max_radius = max(max_x_radius, max_y_radius)

        for r in range(1, max_radius + 1):
            nearest_cells = circular_traversal(cell_x, cell_y, r, self.grid_size)
            neighbors = list(set([cc for c in nearest_cells for cc in self.get_objects_in_cell(c[0], c[1])]))
            nearest = get_nearest_entry(neighbors, point)

            # Если ближайший найден, то нужен поиск еще по одному кругу
            if nearest is not None:
                if r < max_radius:
                    nearest_cells = circular_traversal(cell_x, cell_y, r + 1, self.grid_size)
                    neighbors = list(set([cc for c in nearest_cells for cc in self.get_objects_in_cell(c[0], c[1])]))
                    nearest = get_nearest_entry([*neighbors, nearest], point)

                return nearest.shape

        return None

    def search(self, search: Geometry):
        search_box = geometry_to_box(search)

        if contains(self, search_box):
            x_min, y_min, x_max, y_max = search_box.x_min, search_box.y_min, search_box.x_max, search_box.y_max

            cell_min_x, cell_min_y = int(x_min // self.cell_width), int(y_min // self.cell_height)
            cell_max_x, cell_max_y = int(x_max // self.cell_width), int(y_max // self.cell_height)

            candidates = []

            for x in range(cell_min_x, cell_max_x + 1):
                for y in range(cell_min_y, cell_max_y + 1):
                    entries = list(filter(lambda e: intersection(e, search_box), self.get_objects_in_cell(x, y)))
                    candidates.extend(entries)

            shapes = list(map(lambda e: e.shape, set(candidates)))
            return list(filter(lambda s: s.intersects(search), shapes))
        else:
            return None

    def get_objects_in_cell(self, x, y) -> List[Entry]:
        return self.cells.get((x, y), [])


def get_nearest_entry(entries: List[Entry], point: Point):
    nearest, _ = get_nearest(entries, point)
    return nearest


def circular_traversal(x_c, y_c, r, grid_size):
    def circle_points(x, y):
        return [
            (x_c + x, y_c + y),
            (x_c + x, y_c - y),
            (x_c - x, y_c + y),
            (x_c - x, y_c - y),
            (x_c + y, y_c + x),
            (x_c + y, y_c - x),
            (x_c - y, y_c + x),
            (x_c - y, y_c - x),
        ]

    x, y = 0, r
    delta = 3 - 2 * r
    cells = []

    while x <= y:
        cells.extend(filter(lambda c: (0 <= c[0] < grid_size) and (0 <= c[1] < grid_size), circle_points(x, y)))

        if delta < 0:
            delta += 4 * x + 6
        else:
            delta += 4 * (x - y) + 10

        x += 1

    return set(cells)


def plot_fixed_grid(grid: FixedGrid):
    for i in range(grid.grid_size):
        for j in range(grid.grid_size):
            x = i * grid.cell_width
            y = j * grid.cell_height

            box = shapely.box(x, y, x + grid.cell_width, y + grid.cell_height)
            add_to_plot_geometry(box, 'black')
