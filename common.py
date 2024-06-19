import math
import random
import sys
import time
from typing import List

import numpy as np
import shapely
from matplotlib.typing import ColorType
from shapely import Geometry, Polygon, Point

from shapely_plot import add_to_plot_geometry


class BoundaryBox:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

        self.boundary = shapely.box(self.x_min, self.y_min, self.x_max, self.y_max)

    def area(self) -> float:
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)


class Entry(BoundaryBox):
    def __init__(self, shape: Geometry):
        x_min, y_min, x_max, y_max = (shapely.envelope(shape)).bounds
        super().__init__(x_min, y_min, x_max, y_max)
        self.shape = shape


class StopWatch(object):

    def __init__(self):
        self.elapsed_time = None
        self.start_time = None

    def start(self):
        self.start_time = time.time()
        self.elapsed_time = None

    def stop(self):
        self.elapsed_time = time.time() - self.start_time
        return self.elapsed_time

    def elapsed(self):
        return self.elapsed_time


def union(*boundaries: BoundaryBox):
    minx, miny, = float('inf'), float('inf')
    maxx, maxy = float('-inf'), float('-inf')

    for boundary in boundaries:
        minx, miny = min(boundary.x_min, minx), min(boundary.y_min, miny)
        maxx, maxy = max(boundary.x_max, maxx), max(boundary.y_max, maxy)

    return BoundaryBox(minx, miny, maxx, maxy)


def intersection(rect1: BoundaryBox, rect2: BoundaryBox) -> bool:
    return (rect1.x_min <= rect2.x_max and
            rect1.x_max >= rect2.x_min and
            rect1.y_min <= rect2.y_max and
            rect1.y_max >= rect2.y_min)


def contains(rect1: BoundaryBox, rect2: BoundaryBox) -> bool:
    return (rect1.x_min <= rect2.x_min and
            rect1.x_max >= rect2.x_max and
            rect1.y_min <= rect2.y_min and
            rect1.y_max >= rect2.y_max)


def strict_contains(rect1: BoundaryBox, rect2: BoundaryBox) -> bool:
    return (rect1.x_min < rect2.x_min and
            rect1.x_max > rect2.x_max and
            rect1.y_min < rect2.y_min and
            rect1.y_max > rect2.y_max)


def box_to_geometry(box: BoundaryBox):
    return shapely.box(box.x_min, box.y_min, box.x_max, box.y_max)


def geometry_to_box(shape: Geometry):
    x_min, y_min, x_max, y_max = Polygon(shapely.envelope(shape)).bounds
    return BoundaryBox(x_min, y_min, x_max, y_max)


def get_nearest(entries: List[Entry], point: Point):
    min_distance = float('inf')
    nearest = None

    for entry in entries:
        distance = shapely.distance(entry.shape, point)

        if distance < min_distance:
            min_distance = distance
            nearest = entry

    return nearest, min_distance


def distance(box: BoundaryBox, point: Point):
    nearest_x = max(box.x_min, min(point.x, box.x_max))
    nearest_y = max(box.y_min, min(point.y, box.y_max))

    return math.sqrt((nearest_x - point.x) ** 2 + (nearest_y - point.y) ** 2)


def add_to_plot_box(box: BoundaryBox, color: ColorType = None):
    add_to_plot_geometry(shapely.box(box.x_min, box.y_min, box.x_max, box.y_max), color)


def plot_get_color(depth: int):
    return 'red'
    # return 'white' if depth == 0 else 'black'
    # return ['black', 'orange', 'blue', 'brown', 'violet', 'pink', 'purple', 'indigo'][depth]


def generate_random_point(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100):
    return Point(random.uniform(min_x_coord, max_x_coord), random.uniform(min_y_coord, max_y_coord))


def generate_random_box(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, min_length: float = 1,
                        max_length: float = 15):
    width = random.uniform(min_length, max_length)
    height = random.uniform(min_length, max_length)

    ww = width / 2
    hh = height / 2

    x = random.uniform(min_x_coord + ww, max_x_coord - ww)
    y = random.uniform(min_y_coord + hh, max_y_coord - hh)

    return Polygon([(x - ww, y - hh), (x - ww, y + hh), (x + ww, y + hh), (x + ww, y - hh)])


def generate_random_size_box(center_x, center_y, space_size: float = 100, min_length: float = 1,
                             max_length: float = 15):
    width = random.uniform(min_length, max_length)
    height = random.uniform(min_length, max_length)

    # Вычисление координат углов прямоугольника
    half_width = width / 2
    half_height = height / 2

    left_x = center_x - half_width
    top_y = center_y + half_height

    right_x = center_x + half_width
    bottom_y = center_y - half_height

    # Корректировка координат, чтобы они не выходили за границы области
    left_x = max(0, left_x)
    top_y = min(space_size, top_y)
    right_x = min(space_size, right_x)
    bottom_y = max(0, bottom_y)

    top_left = (left_x, top_y)

    top_right = (right_x, top_y)

    bottom_left = (left_x, bottom_y)

    bottom_right = (right_x, bottom_y)

    return Polygon([bottom_left, top_left, top_right, bottom_right])


def uniform_distribution(size, num_points, noise_level=0.0):
    n = int(math.sqrt(num_points))

    x = np.linspace(0, size, n)
    y = np.linspace(0, size, n)

    points = [(xi + np.random.uniform(-noise_level, noise_level), yi + np.random.uniform(-noise_level, noise_level)) for
              xi in x for yi in y]

    points = list(filter(lambda p: (0 <= p[0] <= size) and (0 <= p[1] <= size), points))

    return [Point(p[0], p[1]) for p in points]


def gaussian_distribution(size, num_points, mean_x, mean_y, std_dev):
    # Генерация координат с Гауссовым распределением
    x_coords = np.random.normal(loc=mean_x, scale=std_dev, size=num_points)
    y_coords = np.random.normal(loc=mean_y, scale=std_dev, size=num_points)

    # Объединение координат в массив точек
    points = [Point(p[0], p[1]) for p in np.column_stack((x_coords, y_coords))]

    return list(filter(lambda p: (0 <= p.x <= size) and (0 <= p.y <= size), points))

# def clear_console_line():
#     # Перемещаем курсор вверх на одну строку
#     sys.stdout.write('\x1b[1A')
#     # Очищаем строку
#     sys.stdout.write('\x1b[2K')
#     sys.stdout.flush()
