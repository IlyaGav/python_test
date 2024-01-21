from __future__ import annotations

import timeit
from typing import List

import shapely
from shapely import Polygon, Geometry, Point

from shapely_plot import add_to_plot_geometry


class Quadtree(object):
    def __init__(self, boundary: Polygon, depth: int, bucket_capacity, max_depth):
        self.boundary = boundary
        self.depth = depth

        self.bucket_capacity = bucket_capacity
        self.max_depth = max_depth

        self.top_left: Quadtree | None = None
        self.top_right: Quadtree | None = None
        self.bottom_left: Quadtree | None = None
        self.bottom_right: Quadtree | None = None

        self.shapes = []
        self.minx, self.miny, self.maxx, self.maxy = boundary.bounds

    def is_leaf(self):
        return (self.top_left is None or self.top_right is None or
                self.bottom_left is None or self.bottom_right is None)

    def contains(self, point: Point) -> bool:
        return (self.minx <= point.x <= self.maxx) and (self.miny <= point.y <= self.maxy)

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

        depth = self.depth + 1

        if depth > self.max_depth:
            return

        minx, miny, maxx, maxy = self.boundary.bounds

        midx, midy = (minx + maxx) / 2, (miny + maxy) / 2

        self.top_left = Quadtree(shapely.box(minx, midy, midx, maxy), depth, self.bucket_capacity, self.max_depth)

        self.top_right = Quadtree(shapely.box(midx, midy, maxx, maxy), depth, self.bucket_capacity, self.max_depth)

        self.bottom_left = Quadtree(shapely.box(minx, miny, midx, midy), depth, self.bucket_capacity, self.max_depth)

        self.bottom_right = Quadtree(shapely.box(midx, miny, maxx, midy), depth, self.bucket_capacity, self.max_depth)

        shapes = self.shapes.copy()

        for shape in shapes:
            containing_child = self.get_containing_child(shape)
            if containing_child is not None:
                self.shapes.remove(shape)
                containing_child.insert(shape)

    def get_containing_child(self, shape):
        if self.is_leaf():
            return None

        boundary = shapely.envelope(shape)

        if self.top_left.boundary.contains(boundary):
            return self.top_left

        if self.top_right.boundary.contains(boundary):
            return self.top_right

        if self.bottom_left.boundary.contains(boundary):
            return self.bottom_left

        return self.bottom_right if self.bottom_right.boundary.contains(boundary) else None


def build_quad_tree(boundary: Polygon, shapes: List[shapely.Geometry], bucket_capacity: int = 8, max_depth: int = 8):
    if not shapes or len(shapes) == 0:
        return None

    tree = Quadtree(boundary, 0, bucket_capacity, max_depth)

    for shape in shapes:
        tree.insert(shape)

    return tree


def quad_tree_find_nearest_neighbor(tree: Quadtree, point: Point):
    nearest, _ = find_nearest_neighbor_internal(tree, point, None, float('inf'))
    return nearest


def find_nearest_neighbor_internal(tree: Quadtree, point: Point, nearest: Geometry | None, min_distance):
    if tree is None:
        return nearest, min_distance

    candidate, distance = get_nearest(tree.shapes, point)

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


def get_nearest(shapes: List[Geometry], point: Point):
    min_distance = float('inf')
    nearest = None

    for shape in shapes:
        distance = shapely.distance(point, shape)

        if distance < min_distance:
            min_distance = distance
            nearest = shape

    return nearest, min_distance


def plot_quad_tree(tree: Quadtree):
    add_to_plot_geometry(tree.boundary, 'black')

    for shape in tree.shapes:
        add_to_plot_geometry(shape, 'orange')

    if tree.is_leaf():
        return

    plot_quad_tree(tree.top_left)
    plot_quad_tree(tree.top_right)
    plot_quad_tree(tree.bottom_left)
    plot_quad_tree(tree.bottom_right)


def quad_tree_benchmark_build(boundary: Polygon, shapes: List[shapely.Geometry], bucket_capacity=8, max_depth=8):
    return timeit.Timer(lambda: build_quad_tree(boundary, shapes, bucket_capacity, max_depth)).timeit(1)


def quad_tree_benchmark_find_nearest_neighbor(tree: Quadtree, query_point: Point):
    return timeit.Timer(lambda: quad_tree_find_nearest_neighbor(tree, query_point)).timeit(1)
