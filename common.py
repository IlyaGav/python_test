from typing import List

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
    shapes = list(map(lambda e: e.shape, entries))

    min_distance = float('inf')
    nearest = None

    for shape in shapes:
        distance = shapely.distance(shape, point)

        if distance < min_distance:
            min_distance = distance
            nearest = shape

    return nearest, min_distance


def add_to_plot_box(box: BoundaryBox, color: ColorType = None):
    add_to_plot_geometry(shapely.box(box.x_min, box.y_min, box.x_max, box.y_max), color)


def plot_get_color(depth: int):
    return 'black'
    # return 'white' if depth == 0 else 'black'
    # return ['black', 'orange', 'blue', 'brown', 'violet', 'pink', 'purple', 'indigo'][depth]
