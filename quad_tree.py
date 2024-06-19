from __future__ import annotations

from typing import List

import shapely
from shapely import Polygon, Geometry, Point

from common import BoundaryBox, Entry, contains, get_nearest, geometry_to_box, intersection, plot_get_color, \
    add_to_plot_box, distance, strict_contains


class QuadtreeNode(BoundaryBox):
    def __init__(self, x_min, y_min, x_max, y_max, depth):
        super().__init__(x_min, y_min, x_max, y_max)

        self.top_left: QuadtreeNode | None = None
        self.top_right: QuadtreeNode | None = None
        self.bottom_left: QuadtreeNode | None = None
        self.bottom_right: QuadtreeNode | None = None

        self.entries = []
        self.depth = depth

    def is_leaf(self):
        return (self.top_left is None or self.top_right is None or
                self.bottom_left is None or self.bottom_right is None)


def get_containing_child(node: QuadtreeNode, entry: Entry):
    if node.is_leaf():
        return None

    if strict_contains(node.top_left, entry):
        return node.top_left

    if strict_contains(node.top_right, entry):
        return node.top_right

    if strict_contains(node.bottom_left, entry):
        return node.bottom_left

    return node.bottom_right if strict_contains(node.bottom_right, entry) else None


class Quadtree(object):
    def __init__(self, boundary: Polygon, bucket_capacity: int, max_depth: int):
        x_min, y_min, x_max, y_max = (shapely.envelope(boundary)).bounds
        self.root = QuadtreeNode(x_min, y_min, x_max, y_max, 0)

        self.bucket_capacity = bucket_capacity
        self.max_depth = max_depth

    def insert(self, entry: Entry):
        if not contains(self.root, entry):
            raise ValueError("ElementOutside")

        self.insert_internal(self.root, entry)

    def insert_internal(self, node: QuadtreeNode, entry: Entry):
        if node.is_leaf():
            node.entries.append(entry)
            if len(node.entries) >= self.bucket_capacity:
                self.split(node)
        else:
            containing_child = get_containing_child(node, entry)

            if containing_child is not None:
                self.insert_internal(containing_child, entry)
            else:
                node.entries.append(entry)

    def split(self, node: QuadtreeNode):
        if not node.is_leaf():
            return

        depth = node.depth + 1

        if depth > self.max_depth:
            return

        midx, midy = (node.x_min + node.x_max) / 2, (node.y_min + node.y_max) / 2

        node.top_left = QuadtreeNode(node.x_min, midy, midx, node.y_max, depth)

        node.top_right = QuadtreeNode(midx, midy, node.x_max, node.y_max, depth)

        node.bottom_left = QuadtreeNode(node.x_min, node.y_min, midx, midy, depth)

        node.bottom_right = QuadtreeNode(midx, node.y_min, node.x_max, midy, depth)

        entries = node.entries.copy()

        for entry in entries:
            containing_child = get_containing_child(node, entry)
            if containing_child is not None:
                node.entries.remove(entry)
                containing_child.entries.append(entry)

    def find_nearest_neighbor(self, point: Point):
        nearest, _ = self.find_nearest_neighbor_internal(self.root, point, None, float('inf'))
        return nearest.shape

    def find_nearest_neighbor_internal(self, node: QuadtreeNode, point: Point, nearest: Entry | None, min_distance):
        if node is None:
            return nearest, min_distance

        candidate, candidate_distance = get_nearest(node.entries, point)

        if candidate_distance < min_distance:
            nearest = candidate
            min_distance = candidate_distance

        if not node.is_leaf():
            nodes = list(map(lambda n: [n, distance(n, point)],
                             [node.top_left, node.top_right, node.bottom_right, node.bottom_left]))
            nodes = sorted(nodes, key=lambda n: n[1])

            for node in nodes:
                if node[1] < min_distance:
                    nearest, min_distance = self.find_nearest_neighbor_internal(node[0], point, nearest, min_distance)

        return nearest, min_distance

    def search(self, search: Geometry):
        search_box = geometry_to_box(search)

        if contains(self.root, search_box):
            candidates = self.internal_search(self.root, search_box)
            shapes = list(map(lambda e: e.shape, candidates))
            return list(filter(lambda s: s.intersects(search), shapes))
        else:
            return None

    def internal_search(self, node: QuadtreeNode, search_box: BoundaryBox) -> List[Entry]:
        search_result = list(filter(lambda n: intersection(n, search_box), node.entries))

        if not node.is_leaf():
            for child in [node.top_left, node.top_right, node.bottom_right, node.bottom_left]:
                if intersection(child, search_box):
                    search_result.extend(self.internal_search(child, search_box))

        return search_result


def plot_quad_tree(tree: Quadtree):
    plot_quad_tree_internal(tree.root)


def plot_quad_tree_internal(node: QuadtreeNode):
    color = plot_get_color(node.depth)

    add_to_plot_box(node, color)

    if node.is_leaf():
        return

    plot_quad_tree_internal(node.top_left)
    plot_quad_tree_internal(node.top_right)
    plot_quad_tree_internal(node.bottom_left)
    plot_quad_tree_internal(node.bottom_right)
