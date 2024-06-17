from __future__ import annotations

from typing import List

import shapely
from shapely import Polygon, Geometry, Point

from common import geometry_to_box, BoundaryBox, Entry, contains, get_nearest, intersection, plot_get_color, \
    add_to_plot_box
from shapely_plot import add_to_plot_geometry


class KDTreeNode(BoundaryBox):
    def __init__(self, x_min, y_min, x_max, y_max, depth):
        super().__init__(x_min, y_min, x_max, y_max)

        self.median = None
        self.entries = []
        self.depth = depth
        self.left = None
        self.right = None

    def is_leaf(self):
        return self.left is None or self.right is None


class KDTree(object):
    def __init__(self, boundary: Polygon, bucket_capacity, max_depth):
        x_min, y_min, x_max, y_max = (shapely.envelope(boundary)).bounds
        self.root = KDTreeNode(x_min, y_min, x_max, y_max, 0)

        # TODO Эти параметры учитываются только при динамическом добавлении
        self.bucket_capacity = bucket_capacity
        self.max_depth = max_depth

    def insert(self, entry: Entry):
        if not contains(self.root, entry):
            raise ValueError("ElementOutside")

        self.insert_internal(self.root, entry)

    def insert_internal(self, node: KDTreeNode, entry: Entry):
        if node.is_leaf():
            node.entries.append(entry)

            if len(node.entries) >= self.bucket_capacity:
                self.split(node)
        else:
            if contains(node.left, entry):
                self.insert_internal(node.left, entry)
            elif contains(node.right, entry):
                self.insert_internal(node.right, entry)
            else:
                node.entries.append(entry)

    def split(self, node: KDTreeNode):
        if not node.is_leaf():
            return

        k = 2  # двумерное пространство
        axis = node.depth % k

        depth = node.depth + 1

        if depth > self.max_depth:
            return

        median = find_median(node.entries, axis)

        node.median = median

        if axis == 0:
            node.left = KDTreeNode(node.x_min, node.y_min, median, node.y_max, depth)
            node.right = KDTreeNode(median, node.y_min, node.x_max, node.y_max, depth)
        else:
            node.left = KDTreeNode(node.x_min, node.y_min, node.x_max, median, depth)
            node.right = KDTreeNode(node.x_min, median, node.x_max, node.y_max, depth)

        entries = node.entries.copy()

        for entry in entries:
            if contains(node.left, entry):
                node.entries.remove(entry)
                node.left.entries.append(entry)
            elif contains(node.right, entry):
                node.entries.remove(entry)
                node.right.entries.append(entry)

    def find_nearest_neighbor(self, point: Point):
        nearest, _ = self.find_nearest_neighbor_internal(self.root, point, None, float('inf'))
        return nearest

    def find_nearest_neighbor_internal(self, node: KDTreeNode, point: Point, nearest: Geometry | None, min_distance):
        if node is None:
            return nearest, min_distance

        candidate, distance = get_nearest(node.entries, point)

        if distance < min_distance:
            nearest = candidate
            min_distance = distance

        if not node.is_leaf():
            k = 2  # двумерное пространство
            axis = node.depth % k
            point_tuple = [point.x, point.y]

            if node.median >= point_tuple[axis]:
                nearest, min_distance = self.find_nearest_neighbor_internal(node.left, point, nearest, min_distance)
                if node.median - point_tuple[axis] < min_distance:
                    nearest, min_distance = self.find_nearest_neighbor_internal(node.right, point, nearest, min_distance)
            else:
                nearest, min_distance = self.find_nearest_neighbor_internal(node.right, point, nearest, min_distance)
                if point_tuple[axis] - node.median < min_distance:
                    nearest, min_distance = self.find_nearest_neighbor_internal(node.left, point, nearest, min_distance)

        return nearest, min_distance

    def search(self, search: Geometry):
        search_box = geometry_to_box(search)

        if intersection(self.root, search_box):
            candidates = self.internal_search(self.root, search_box)
            shapes = list(map(lambda e: e.shape, candidates))
            return list(filter(lambda s: s.intersects(search), shapes))
        else:
            return None

    def internal_search(self, node: KDTreeNode, search_box: BoundaryBox) -> List[Entry]:
        search_result = list(filter(lambda n: intersection(n, search_box), node.entries))

        if not node.is_leaf():
            for child in [node.left, node.right]:
                if intersection(child, search_box):
                    search_result.extend(self.internal_search(child, search_box))

        return search_result


# def build_kd_tree(boundary: Polygon, shapes: List[shapely.Geometry], depth=0):
#     if not shapes or len(shapes) == 0:
#         return KDTree(
#             boundary=boundary,
#             shapes=[],
#             depth=depth,
#             # TODO Эти параметры не учитываются в этой функции добавления
#             bucket_capacity=8,
#             max_depth=8)
#
#     k = 2  # двумерное пространство
#     axis = depth % k
#
#     median = find_median(shapes, axis)
#
#     minx, miny, maxx, maxy = boundary.bounds
#
#     if axis == 0:
#         left_boundary = shapely.box(minx, miny, median, maxy)
#         right_boundary = shapely.box(median, miny, maxx, maxy)
#     else:
#         left_boundary = shapely.box(minx, miny, maxx, median)
#         right_boundary = shapely.box(minx, median, maxx, maxy)
#
#     self = []
#     left = []
#     right = []
#
#     for shape in shapes:
#         mbr = Polygon(shapely.envelope(shape))
#         vertices = list(mbr.exterior.coords)
#         # TODO Сравнивать не каждую координату, а только противоположенные
#         if all(vertex[axis] <= median for vertex in vertices):
#             left.append(shape)
#         elif all(vertex[axis] > median for vertex in vertices):
#             right.append(shape)
#         else:
#             self.append(shape)
#
#     # TODO Для тестирования и визуализации шагов
#     # add_to_plot_geometry(left_boundary, 'red')
#     # add_to_plot_geometry(right_boundary, 'green')
#     # add_to_plot_geometry(boundary, 'blue')
#     #
#     # for shape in self:
#     #     add_to_plot_geometry(shape, 'yellow')
#     #
#     # for shape in left:
#     #     add_to_plot_geometry(shape, 'purple')
#     #
#     # for shape in right:
#     #     add_to_plot_geometry(shape, 'brown')
#     #
#     # show_plot()
#
#     return KDTree(
#         boundary=boundary,
#         shapes=self,
#         depth=depth,
#         # TODO Эти параметры не учитываются в этой функции добавления
#         bucket_capacity=8,
#         max_depth=8,
#         median=median,
#         left=build_kd_tree(left_boundary, left, depth + 1),
#         right=build_kd_tree(right_boundary, right, depth + 1)
#     )
#
#


# Поиск с минимальным расстоянием
# Сначала ищем минимальное расстояние в листе
# Потом заходим только в узлы до которых расстояние меньше найденного
# В этих узлах ищем самый близкий элемент
# def find_nearest_neighbor_2(kd_tree: KDTree, point: Point):
#     min_dist = min_dist_nearest_neighbor_2(kd_tree, point, kd_tree)
#     return find_nearest_neighbor_2_internal(kd_tree, point, min_dist)
#
#
# #  TODO best_dist == 0, rename var
# def min_dist_nearest_neighbor_2(kd_tree: KDTree, point: Point, root: KDTree):
#     # TODO Вычислять всегда, вдруг попали на ось пересечения или только у листов?
#     best_dist = min(map(lambda s: shapely.distance(s, point), kd_tree.shapes)) if len(kd_tree.shapes) > 0 else None
#
#     # TODO Будем тогда выбирать первого (самого большого считай), кто содержит
#     if best_dist == 0:
#         return 0
#
#     if kd_tree.is_leaf():
#         dist = best_dist
#     elif kd_tree.left.boundary.contains(point):
#         dist = min_dist_nearest_neighbor_2(kd_tree.left, point, root)
#     else:
#         dist = min_dist_nearest_neighbor_2(kd_tree.right, point, root)
#
#     return min(best_dist, dist) if best_dist is not None else dist
#
#
# # TODO rename, refactor, .distance
# def find_nearest_neighbor_2_internal(kd_tree: KDTree, point: Point, radius: int):
#     # TODO Или пересечение или расстояние меньше радиуса
#     shapes = list(filter(lambda s: shapely.distance(s, point) <= radius, kd_tree.shapes))
#     shapes.sort(key=lambda s: shapely.distance(s, point))
#
#     best = None
#
#     if len(shapes) > 0:
#         best = shapes[0]
#
#     if kd_tree.is_leaf():
#         return best
#
#     l_nearest = None
#     r_nearest = None
#
#     if shapely.distance(kd_tree.left.boundary, point) <= radius:
#         l_nearest = find_nearest_neighbor_2_internal(kd_tree.left, point, radius)
#
#     if shapely.distance(kd_tree.right.boundary, point) <= radius:
#         r_nearest = find_nearest_neighbor_2_internal(kd_tree.right, point, radius)
#
#     l = list(filter(lambda n: n is not None, [l_nearest, r_nearest, best]))
#     l.sort(key=lambda n: shapely.distance(n, point))
#
#     return l[0] if len(l) > 0 else None


def find_median(entries: List[Entry], axes):
    all_coords = [[(minx, miny), (maxx, maxy)] for minx, miny, maxx, maxy in map(lambda e: e.boundary.bounds, entries)]
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
    color = plot_get_color(0)

    add_to_plot_box(tree.root, color)

    plot_kd_tree_internal(tree.root)


def plot_kd_tree_internal(node: KDTreeNode):
    if node.is_leaf():
        return

    k = 2  # двумерное пространство
    axis = node.depth % k
    color = plot_get_color(node.depth)

    if axis == 0:
        line = shapely.geometry.LineString([(node.median, node.y_min), (node.median, node.y_max)])
    else:
        line = shapely.geometry.LineString([(node.x_min, node.median), (node.x_max, node.median)])

    add_to_plot_geometry(line, color)
    plot_kd_tree_internal(node.left)
    plot_kd_tree_internal(node.right)
