from __future__ import annotations

import timeit
from typing import List

import shapely
from shapely import Polygon, Geometry, Point, MultiPoint

from shapely_plot import add_to_plot_geometry


class KDTree(object):
    def __init__(self, boundary: Polygon, shapes: List[Geometry], depth, bucket_capacity, max_depth,
                 median: float = None, left: 'KDTree' = None, right: 'KDTree' = None):
        self.median = median
        self.boundary = boundary
        self.shapes = shapes
        self.depth = depth
        self.left = left
        self.right = right

        # TODO Эти параметры учитываются только при динамическом добавлении
        self.bucket_capacity = bucket_capacity
        self.max_depth = max_depth

    def is_leaf(self):
        return self.left is None or self.right is None

    def insert(self, shape: Geometry):
        if not self.boundary.contains(shapely.envelope(shape)):
            raise ValueError("ElementOutside")

        if len(self.shapes) >= self.bucket_capacity:
            self.split()

        containing_child = self.get_containing_child(shape)
        if containing_child is not None:
            containing_child.insert(shape)
        else:
            self.shapes.append(shape)

    def split(self):
        if not self.is_leaf():
            return

        k = 2  # двумерное пространство
        axis = self.depth % k

        depth = self.depth + 1

        if depth > self.max_depth:
            return

        median = find_median(self.shapes, axis)

        minx, miny, maxx, maxy = self.boundary.bounds

        self.median = median

        if axis == 0:
            self.left = KDTree(MultiPoint([(minx, miny), (median, maxy)]).envelope, [], depth, self.bucket_capacity,
                               self.max_depth)
            self.right = KDTree(MultiPoint([(median, miny), (maxx, maxy)]).envelope, [], depth, self.bucket_capacity,
                                self.max_depth)
        else:
            self.left = KDTree(MultiPoint([(minx, miny), (maxx, median)]).envelope, [], depth, self.bucket_capacity,
                               self.max_depth)
            self.right = KDTree(MultiPoint([(minx, median), (maxx, maxy)]).envelope, [], depth, self.bucket_capacity,
                                self.max_depth)

        shapes = self.shapes.copy()

        for shape in shapes:
            containing_child = self.get_containing_child(shapely.envelope(shape))
            if containing_child is not None:
                self.shapes.remove(shape)
                containing_child.insert(shape)

    def get_containing_child(self: KDTree, shape: Geometry):
        if self.is_leaf():
            return None

        boundary = shapely.envelope(shape)

        if self.left.boundary.contains(boundary):
            return self.left

        if self.right.boundary.contains(boundary):
            return self.right

        return None


def build_kd_tree_2(boundary: Polygon, shapes: List[shapely.Geometry], bucket_capacity: int = 8, max_depth: int = 8):
    if not shapes or len(shapes) == 0:
        return None

    tree = KDTree(boundary, [], 0, bucket_capacity, max_depth)

    for shape in shapes:
        tree.insert(shape)

    return tree


def build_kd_tree(boundary: Polygon, shapes: List[shapely.Geometry], depth=0):
    if not shapes or len(shapes) == 0:
        return KDTree(
            boundary=boundary,
            shapes=[],
            depth=depth,
            # TODO Эти параметры не учитываются в этой функции добавления
            bucket_capacity=8,
            max_depth=8)

    k = 2  # двумерное пространство
    axis = depth % k

    median = find_median(shapes, axis)

    minx, miny, maxx, maxy = boundary.bounds

    if axis == 0:
        left_boundary = shapely.box(minx, miny, median, maxy)
        right_boundary = shapely.box(median, miny, maxx, maxy)
    else:
        left_boundary = shapely.box(minx, miny, maxx, median)
        right_boundary = shapely.box(minx, median, maxx, maxy)

    self = []
    left = []
    right = []

    for shape in shapes:
        mbr = Polygon(shapely.envelope(shape))
        vertices = list(mbr.exterior.coords)
        # TODO Сравнивать не каждую координату, а только противоположенные
        if all(vertex[axis] <= median for vertex in vertices):
            left.append(shape)
        elif all(vertex[axis] > median for vertex in vertices):
            right.append(shape)
        else:
            self.append(shape)

    # TODO Для тестирования и визуализации шагов
    # add_to_plot_geometry(left_boundary, 'red')
    # add_to_plot_geometry(right_boundary, 'green')
    # add_to_plot_geometry(boundary, 'blue')
    #
    # for shape in self:
    #     add_to_plot_geometry(shape, 'yellow')
    #
    # for shape in left:
    #     add_to_plot_geometry(shape, 'purple')
    #
    # for shape in right:
    #     add_to_plot_geometry(shape, 'brown')
    #
    # show_plot()

    return KDTree(
        boundary=boundary,
        shapes=self,
        depth=depth,
        # TODO Эти параметры не учитываются в этой функции добавления
        bucket_capacity=8,
        max_depth=8,
        median=median,
        left=build_kd_tree(left_boundary, left, depth + 1),
        right=build_kd_tree(right_boundary, right, depth + 1)
    )


def kd_tree_find_nearest_neighbor(tree: KDTree, point: Point):
    nearest, _ = find_nearest_neighbor_internal(tree, point, None, float('inf'))
    return nearest


def find_nearest_neighbor_internal(tree: KDTree, point: Point, nearest: Geometry | None, min_distance):
    if tree is None or tree.is_leaf():
        return nearest, min_distance

    candidate, distance = get_nearest(tree.shapes, point)

    if distance < min_distance:
        nearest = candidate
        min_distance = distance

    k = 2  # двумерное пространство
    axis = tree.depth % k
    point_tuple = [point.x, point.y]

    if tree.median >= point_tuple[axis]:
        nearest, min_distance = find_nearest_neighbor_internal(tree.left, point, nearest, min_distance)
        if tree.median - point_tuple[axis] < min_distance:
            nearest, min_distance = find_nearest_neighbor_internal(tree.right, point, nearest, min_distance)
    else:
        nearest, min_distance = find_nearest_neighbor_internal(tree.right, point, nearest, min_distance)
        if point_tuple[axis] - tree.median < min_distance:
            nearest, min_distance = find_nearest_neighbor_internal(tree.left, point, nearest, min_distance)

    return nearest, min_distance


def get_nearest(shapes: List[Geometry], point: Point):
    min_distance = float('inf')
    nearest = None

    for shape in shapes:
        distance = shapely.distance(point, shape)

        if distance < min_distance:
            min_distance = distance
            nearest = shape

    return nearest, min_distance


# Поиск с минимальным расстоянием
# Сначала ищем минимальное расстояние в листе
# Потом заходим только в узлы до которых расстояние меньше найденного
# В этих узлах ищем самый близкий элемент
def find_nearest_neighbor_2(tree: KDTree, point: Point):
    min_dist = min_dist_nearest_neighbor_2(tree, point, tree)
    return find_nearest_neighbor_2_internal(tree, point, min_dist)


#  TODO best_dist == 0, rename var
def min_dist_nearest_neighbor_2(tree: KDTree, point: Point, root: KDTree):
    # TODO Вычислять всегда, вдруг попали на ось пересечения или только у листов?
    best_dist = min(map(lambda s: shapely.distance(s, point), tree.shapes)) if len(tree.shapes) > 0 else None

    # TODO Будем тогда выбирать первого (самого большого считай), кто содержит
    if best_dist == 0:
        return 0

    if tree.is_leaf():
        dist = best_dist
    elif tree.left.boundary.contains(point):
        dist = min_dist_nearest_neighbor_2(tree.left, point, root)
    else:
        dist = min_dist_nearest_neighbor_2(tree.right, point, root)

    return min(best_dist, dist) if best_dist is not None else dist


# TODO rename, refactor, .distance
def find_nearest_neighbor_2_internal(tree: KDTree, point: Point, radius: int):
    # TODO Или пересечение или расстояние меньше радиуса
    shapes = list(filter(lambda s: shapely.distance(s, point) <= radius, tree.shapes))
    shapes.sort(key=lambda s: shapely.distance(s, point))

    best = None

    if len(shapes) > 0:
        best = shapes[0]

    if tree.is_leaf():
        return best

    l_nearest = None
    r_nearest = None

    if shapely.distance(tree.left.boundary, point) <= radius:
        l_nearest = find_nearest_neighbor_2_internal(tree.left, point, radius)

    if shapely.distance(tree.right.boundary, point) <= radius:
        r_nearest = find_nearest_neighbor_2_internal(tree.right, point, radius)

    l = list(filter(lambda n: n is not None, [l_nearest, r_nearest, best]))
    l.sort(key=lambda n: shapely.distance(n, point))

    return l[0] if len(l) > 0 else None


def find_median(geometries: List[Geometry], axes):
    all_coords = [[(minx, miny), (maxx, maxy)] for minx, miny, maxx, maxy in map(lambda g: g.bounds, geometries)]
    all_coords = [cc[axes] for c in all_coords for cc in c]
    all_coords.sort()

    if len(all_coords) % 2 == 1:
        # Нечетное количество элементов, возвращаем одну точку
        return all_coords[len(all_coords) // 2]
    else:
        # Четное количество элементов, возвращаем две точки
        median_1 = all_coords[len(all_coords) // 2 - 1]
        median_2 = all_coords[len(all_coords) // 2]
        return (median_1 + median_2) / 2


def plot_kd_tree(tree: KDTree):
    if tree.depth == 0:
        add_to_plot_geometry(tree.boundary, 'black')

    if tree.is_leaf():
        return

    k = 2  # двумерное пространство
    axis = tree.depth % k

    minx, miny, maxx, maxy = tree.boundary.bounds

    if axis == 0:
        add_to_plot_geometry(shapely.geometry.LineString([(tree.median, miny), (tree.median, maxy)]), 'black')
    else:
        add_to_plot_geometry(shapely.geometry.LineString([(minx, tree.median), (maxx, tree.median)]), 'black')

    for shape in tree.shapes:
        add_to_plot_geometry(shape, 'orange')

    plot_kd_tree(tree.left)
    plot_kd_tree(tree.right)


def kd_tree_benchmark_build(boundary: Polygon, shapes: List[shapely.Geometry]):
    return timeit.Timer(lambda: build_kd_tree(boundary, shapes)).timeit(1)


def kd_tree_benchmark_build_2(boundary: Polygon, shapes: List[shapely.Geometry]):
    return timeit.Timer(lambda: build_kd_tree_2(boundary, shapes)).timeit(1)


def kd_tree_benchmark_find_nearest_neighbor(tree: KDTree, query_point: Point):
    return timeit.Timer(lambda: kd_tree_find_nearest_neighbor(tree, query_point)).timeit(1)
