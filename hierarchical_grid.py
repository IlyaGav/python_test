import timeit
from typing import List, Dict

import shapely
from shapely import Geometry, Polygon, Point

import z_curve
from shapely_plot import add_to_plot_geometry


# TODO Наверное стоит избавиться от z_curve
# TODO rename? spatial grid, hierarchical grid
class HierarchicalGrid:
    def __init__(self, boundary: Polygon, grid_size: int = 4, limit_cells: int = 16, levels: int = 4):
        self.boundary = boundary
        self.grid_size = grid_size

        minx, miny, maxx, maxy = boundary.bounds

        self.width = maxx - minx
        self.height = maxy - miny

        self.limit_cells = limit_cells
        self.levels = levels
        self.grids: List[Dict[int, List[Geometry]]] = [{} for _ in range(levels)]

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

            # Если след уровень превышает ограничение, то останавливаемся на текущем
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


def build_hierarchical_grid(boundary: Polygon, shapes: List[shapely.Geometry], grid_size: int = 4, limit_cells: int = 16,
                     levels: int = 4):
    grid = HierarchicalGrid(boundary, grid_size, limit_cells, levels)

    for shape in shapes:
        grid.add_object(shape)

    return grid


def hierarchical_grid_find_nearest_neighbor(grid: HierarchicalGrid, point: Point):
    min_distance = float('inf')
    nearest_neighbor = None

    query_x, query_y = point.x, point.y

    for level in range(0, grid.levels):

        if len(grid.grids[level]) == 0:
            continue

        cell_width = grid.width / pow(grid.grid_size, level + 1)
        cell_height = grid.height / pow(grid.grid_size, level + 1)

        cell_x, cell_y = int(query_x // cell_width), int(query_y // cell_height)

        # Содержащая ячейка и ячейки вокруг нее
        nearest_cells = [(cell_x, cell_y), *circular_traversal(cell_x, cell_y, 1)]

        # TODO Нужен distinct ???

        neighbors = [cc for c in nearest_cells for cc in grid.grids[level].get(z_curve.z_encode(c[0], c[1]), [])]

        neighbor, distance = get_nearest(neighbors, point)

        if distance < min_distance:
            nearest_neighbor = neighbor
            min_distance = distance

        # TODO Подумать
        #  Перебор ближайших
        #  Возможно полный перебор будет быстрее (см ниже полный перебор)

        # Если в смежных ячейках нет соседей, то бежим по остальным
        if neighbor is None:

            max_x_radius = max(cell_x, pow(grid.grid_size, level + 1) - cell_x)
            max_y_radius = max(cell_y, pow(grid.grid_size, level + 1) - cell_y)
            max_radius = max(max_x_radius, max_y_radius)

            # Бежим с 2ки, тк в ближайшее заходили выше
            for r in range(2, max_radius + 1):
                # Если расстояние до след ячеек уже больше чем до ближайшего соседа
                if max(r * cell_width, r * cell_height) > min_distance:
                    break

                nearest_cells = circular_traversal(cell_x, cell_y, r)

                neighbors = [cc for c in nearest_cells for cc in
                             grid.grids[level].get(z_curve.z_encode(c[0], c[1]), [])]

                neighbor, distance = get_nearest(neighbors, point)

                # Ближайших на этом уровне, дальше можно не искать
                if neighbor is not None:

                    if distance < min_distance:
                        nearest_neighbor = neighbor
                        min_distance = distance

                    break

        # TODO Подумать
        #  Полный перебор:
        #  Может он выгоднее? Бегать только по ячейкам в которых есть записи
        #  Без него в получения в самой удаленной точке будет хуже
        #  Да и если ячейки в БД, то может проще сразу все получить, их не так много
        # if neighbor is None:
        #
        #     c_cell_x = cell_x + cell_width / 2
        #     c_cell_y = cell_y + cell_height / 2
        #
        #     nearest_cells = []
        #
        #     square_min_distance = float('inf')
        #
        #     # TODO Подумать
        #     #  Добавить какой-то радиус? Все ячейки может быть много для последнего уровня
        #     #  Сначала в этом радиусе получать, а потом увеличивать?
        #     for (key, cell) in grid.grids[level].items():
        #         (x, y) = z_curve.z_decode(key)
        #         c_x = x + cell_width / 2
        #         c_y = y + cell_height / 2
        #
        #         distance = square_distance(c_cell_x, c_cell_y, c_x, c_y)
        #
        #         if distance < square_min_distance:
        #             square_min_distance = distance
        #             nearest_cells = [cell]
        #
        #         if distance == square_min_distance:
        #             nearest_cells.append(cell)
        #
        #     if len(nearest_cells) == 0:
        #         continue
        #
        #     neighbors = [cc for c in nearest_cells for cc in c]
        #
        #     neighbor, distance = get_nearest(neighbors, point)
        #
        #     if distance < min_distance:
        #         nearest_neighbor = neighbor
        #         min_distance = distance

    return nearest_neighbor


def square_distance(x1, y1, x2, y2):
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


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

    return nearest, min_distance


def plot_hierarchical_grid(grid: HierarchicalGrid):
    for level in range(grid.levels):
        cells = grid.grids[level]
        for (key, cell) in cells.items():
            xmin, ymin = z_curve.z_decode(key)

            width = grid.width / pow(grid.grid_size, level + 1)
            height = grid.height / pow(grid.grid_size, level + 1)
            xmin = xmin * width
            ymin = ymin * height

            box = shapely.box(xmin, ymin, xmin + width, ymin + height)
            add_to_plot_geometry(box, 'black')

            for shape in cell:
                add_to_plot_geometry(shape, 'orange')
