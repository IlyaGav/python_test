from __future__ import annotations

from typing import List

import shapely
from shapely import Polygon, Geometry, Point

from shapely_plot import add_to_plot_geometry


class QuadtreePoint(object):
    def __init__(self, boundary: Polygon, depth: int, bucket_capacity, max_depth):
        self.boundary = boundary
        self.depth = depth

        self.bucket_capacity = bucket_capacity
        self.max_depth = max_depth

        self.top_left: QuadtreePoint | None = None
        self.top_right: QuadtreePoint | None = None
        self.bottom_left: QuadtreePoint | None = None
        self.bottom_right: QuadtreePoint | None = None

        self.points = []

        self.minx, self.miny, self.maxx, self.maxy = boundary.bounds

    def is_leaf(self):
        return (self.top_left is None or self.top_right is None or
                self.bottom_left is None or self.bottom_right is None)

    def contains(self, point: Point) -> bool:
        return (self.minx <= point.x <= self.maxx) and (self.miny <= point.y <= self.maxy)

    def insert(self, point: Point):
        if len(self.points) >= self.bucket_capacity:
            self.split()

        containing_child = self.get_containing_child(point)

        if containing_child is not None:
            containing_child.insert(point)
        else:
            self.points.append(point)

    def split(self):
        if not self.is_leaf():
            return

        depth = self.depth + 1

        if depth > self.max_depth:
            return

        minx, miny, maxx, maxy = self.boundary.bounds

        midx, midy = (minx + maxx) / 2, (miny + maxy) / 2

        self.top_left = QuadtreePoint(shapely.box(minx, midy, midx, maxy), depth, self.bucket_capacity, self.max_depth)

        self.top_right = QuadtreePoint(shapely.box(midx, midy, maxx, maxy), depth, self.bucket_capacity, self.max_depth)

        self.bottom_left = QuadtreePoint(shapely.box(minx, miny, midx, midy), depth, self.bucket_capacity,
                                         self.max_depth)

        self.bottom_right = QuadtreePoint(shapely.box(midx, miny, maxx, midy), depth, self.bucket_capacity,
                                          self.max_depth)

        points = self.points.copy()

        for point in points:
            containing_child = self.get_containing_child(point)
            if containing_child is not None:
                self.points.remove(point)
                containing_child.insert(point)

    def get_containing_child(self, point):
        if self.is_leaf():
            return None

        if self.top_left.contains(point):
            return self.top_left

        if self.top_right.contains(point):
            return self.top_right

        if self.bottom_left.contains(point):
            return self.bottom_left

        return self.bottom_right if self.bottom_right.contains(point) else None


def build_quad_tree_point(boundary: Polygon, points: List[shapely.Point], bucket_capacity: int = 8, max_depth: int = 8):
    if not points or len(points) == 0:
        return None

    tree = QuadtreePoint(boundary, 0, bucket_capacity, max_depth)

    for point in points:
        tree.insert(point)

    return tree


def quad_tree_point_find_nearest_neighbor(tree: QuadtreePoint, point: Point):
    nearest, _ = find_nearest_neighbor_internal(tree, point, None, float('inf'))
    return nearest


def find_nearest_neighbor_internal(tree: QuadtreePoint, point: Point, nearest: Geometry | None, min_distance):
    if tree is None:
        return nearest, min_distance

    candidate, distance = get_nearest(tree.points, point)

    if distance < min_distance:
        nearest = candidate
        min_distance = distance

    if not tree.is_leaf():
        nodes = list(map(lambda n: [n, shapely.distance(n.boundary, point)],
                         [tree.top_left, tree.top_right, tree.bottom_right, tree.bottom_left]))
        nodes = sorted(nodes, key=lambda n: n[1])
        for node in nodes:
            if node[1] < min_distance:
                nearest, min_distance = find_nearest_neighbor_internal(node[0], point, nearest, min_distance)

    return nearest, min_distance


def get_nearest(points: List[Point], query_point: Point):
    min_distance = float('inf')
    nearest = None

    for point in points:
        distance = shapely.distance(query_point, point)

        if distance < min_distance:
            min_distance = distance
            nearest = point

    return nearest, min_distance


def plot_quad_tree_point(tree: QuadtreePoint):
    add_to_plot_geometry(tree.boundary, 'black')

    for shape in tree.points:
        add_to_plot_geometry(shape, 'orange')

    if tree.is_leaf():
        return

    plot_quad_tree_point(tree.top_left)
    plot_quad_tree_point(tree.top_right)
    plot_quad_tree_point(tree.bottom_left)
    plot_quad_tree_point(tree.bottom_right)
