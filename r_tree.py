from __future__ import annotations

import random
from typing import List, Union

import shapely
from shapely import Geometry, Point

from common import BoundaryBox, union, intersection, geometry_to_box, box_to_geometry, Entry, get_nearest
from shapely_plot import add_to_plot_geometry


class RTreeNode(BoundaryBox):
    def __init__(self, children: List[RTreeNode | Entry] | None = None, is_leaf: bool = False):
        mbr = union(*children)
        super().__init__(mbr.x_min, mbr.y_min, mbr.x_max, mbr.y_max)
        self.children = children
        self.is_leaf = is_leaf

    def add_child(self, node: RTreeNode | Entry):
        self.children.append(node)

    def updateMBR(self, box: BoundaryBox):
        mbr = union(self, box)
        self.x_min, self.y_min, self.x_max, self.y_max = mbr.x_min, mbr.y_min, mbr.x_max, mbr.y_max
        self.boundary = shapely.box(self.x_min, self.y_min, self.x_max, self.y_max)


class RTree(object):
    def __init__(self, max_node_capacity=4, algorithm: 'linear' | 'quadratic' = 'linear'):
        self.root = RTreeNode([], True)
        self.max_node_capacity = max_node_capacity
        self.algorithm = algorithm

    def insert(self, entry: Entry):
        self.root.children = self.internal_insert(self.root, entry)

        if len(self.root.children) > self.max_node_capacity:
            node_1, node_2 = self.split_node(self.root, self.algorithm)
            self.root = RTreeNode([node_1, node_2])

    def search(self, search: Geometry):
        search_box = geometry_to_box(search)

        if intersection(self.root, search_box):
            candidates = self.internal_search(self.root, search_box)
            shapes = list(map(lambda e: e.shape, candidates))
            return list(filter(lambda s: s.intersects(search), shapes))
        else:
            return None

    def find_nearest_neighbor(self, point: Point):
        nearest, _ = self.find_nearest_neighbor_internal(self.root, point, None, float('inf'))
        return nearest

    def find_nearest_neighbor_internal(self, node: RTreeNode, point: Point, nearest: Geometry | None, min_distance):
        if node.is_leaf:
            candidate, distance = get_nearest(node.children, point)

            if distance < min_distance:
                nearest = candidate
                min_distance = distance

            return nearest, min_distance

        nodes = list(map(lambda n: [n, shapely.distance(n.boundary, point)], node.children))
        nodes = sorted(nodes, key=lambda n: n[1])

        for node in nodes:
            if node[1] < min_distance:
                nearest, min_distance = self.find_nearest_neighbor_internal(node[0], point, nearest, min_distance)

        return nearest, min_distance

    def internal_search(self, node: RTreeNode, search_box: BoundaryBox) -> List[Entry]:
        search_result: List[Entry] | None = []

        if node.is_leaf:
            search_result = list(filter(lambda n: intersection(n, search_box), node.children))
        else:
            for child in node.children:
                if intersection(child, search_box):
                    search_result.extend(self.internal_search(child, search_box))

        return search_result

    def internal_insert(self, node: RTreeNode, entry: Entry) -> [RTreeNode]:
        if node.is_leaf:
            node.add_child(entry)
        else:
            min_increase = float('inf')
            selected_node = None

            for child in node.children:
                increase = union(child, entry).area() - child.area()
                if increase < min_increase:
                    min_increase = increase
                    selected_node = child
                elif increase == min_increase and child.area() < selected_node.area():
                    selected_node = child

            selected_node.children = self.internal_insert(selected_node, entry)

            if len(selected_node.children) > self.max_node_capacity:
                node_1, node_2 = self.split_node(selected_node, self.algorithm)
                node.children.remove(selected_node)
                node.add_child(node_1)
                node.add_child(node_2)

        node.updateMBR(entry)

        return node.children

    def split_node(self, node: RTreeNode, algorithm: 'linear' | 'quadratic') -> [RTreeNode]:
        if node.children is None:
            raise ValueError("Can not be None")

        lowIdx, highIdx = linear(node.children) if algorithm == 'linear' else quadratic(node.children)

        node_1 = RTreeNode([node.children[lowIdx]], node.is_leaf)
        node_2 = RTreeNode([node.children[highIdx]], node.is_leaf)

        node.children.remove(node_1.children[0])
        node.children.remove(node_2.children[0])

        while len(node.children) > 0:
            idx = next_linear(node.children) if algorithm == 'linear' else next_quadratic(node.children, node_1, node_2)
            child = node.children.pop(idx)

            increase_1 = union(node_1, child).area() - node_1.area()
            increase_2 = union(node_2, child).area() - node_2.area()

            if len(node_1.children) < self.max_node_capacity and (
                    increase_1 < increase_2 or increase_1 == increase_2 and node_1.area() < node_2.area()
                    or len(node_1.children) < len(node_2.children)
            ):
                node_1.add_child(child)
                node_1.updateMBR(child)
            else:
                node_2.add_child(child)
                node_2.updateMBR(child)

        return node_1, node_2

    def remove(self):
        # TODO
        self.split_node(None)


class DimStats:
    def __init__(self):
        self.minLow = float('inf')
        self.maxLow = float('-inf')
        self.minHigh = float('inf')
        self.maxHigh = float('-inf')
        self.lowIndex = 0
        self.highIndex = 0

    @staticmethod
    def farest(s):
        return abs(s.maxHigh - s.minLow)

    @staticmethod
    def nearest(s):
        return abs(s.minHigh - s.maxLow)


def compute_dim(s, lo, hi, i):
    s.minLow = min(s.minLow, lo)
    s.maxHigh = max(s.maxHigh, hi)
    if lo > s.maxLow:
        s.maxLow = lo
        s.lowIndex = i
    if hi < s.minHigh:
        s.minHigh = hi
        s.highIndex = i


def linear(entries: List[BoundaryBox]):
    dx = DimStats()
    dy = DimStats()

    if len(entries) > 2:
        for i, e in enumerate(entries):
            compute_dim(dx, e.x_min, e.x_max, i)
            compute_dim(dy, e.y_min, e.y_max, i)

    farX, farY = DimStats.farest(dx), DimStats.farest(dy)
    nearX, nearY = DimStats.nearest(dx), DimStats.nearest(dy)
    normX, normY = nearX / farX, nearY / farY
    lowIdx, highIdx = (dx.lowIndex, dx.highIndex) if normX > normY else (dy.lowIndex, dy.highIndex)

    cmp = lowIdx - highIdx
    if cmp < 0:
        return lowIdx, highIdx
    elif cmp > 0:
        return highIdx, lowIdx
    elif lowIdx == 0:
        return 0, 1
    else:
        return 0, highIdx


def quadratic(entries: List[BoundaryBox]):
    x = 0
    y = 1
    max_diff = float('-inf')

    if len(entries) > 2:
        for i in range(len(entries)):
            for j in range(1, len(entries)):
                combined = union(entries[i], entries[j])
                diff = combined.area() - entries[i].area() - entries[j].area()

                if diff > max_diff:
                    max_diff = diff
                    x = i
                    y = j

    return x, y


def select_group(rect1: BoundaryBox, rect2: BoundaryBox, len1: int, len2: int, diff1: float, diff2: float):
    if diff1 < diff2:
        return 0
    elif diff2 < diff1:
        return 1
    elif rect1.area() < rect2.area():
        return 0
    elif rect2.area() < rect1.area():
        return 1
    elif len1 < len2:
        return 0
    elif len2 < len1:
        return 1
    else:
        return 0


def next_quadratic(entries: List[BoundaryBox], rect1: BoundaryBox, rect2: BoundaryBox):
    idx = 0

    max_preference_diff = float('-inf')

    for i, e in enumerate(entries):
        pref1 = union(rect1, e).area() - rect1.area()
        pref2 = union(rect2, e).area() - rect2.area()
        preference_diff = abs(pref1 - pref2)

        if max_preference_diff <= preference_diff:
            max_preference_diff = preference_diff
            idx = i

    return idx


def next_linear(entries: List[BoundaryBox]):
    return random.randint(0, len(entries) - 1)


def plot_r_tree(r_tree: RTree):
    plot_r_node_recursive(r_tree.root, 0)


def plot_get_color(depth: int):
    return 'white' if depth == 0 else 'black'
    # return ['orange', 'black', 'grey', 'blue', 'brown', 'violet', 'pink', 'purple', 'indigo'][depth]


def plot_r_node(node: RTreeNode, color: str):
    add_to_plot_geometry(shapely.box(node.x_min, node.y_min, node.x_max, node.y_max), color)


def plot_r_node_recursive(node: RTreeNode, depth: int):
    plot_r_node(node, plot_get_color(depth))

    if node.is_leaf:
        return

    for child in node.children:
        plot_r_node_recursive(child, depth + 1)


TypeAlgorithm = Union['linear', 'quadratic']


def build_r_tree(entries: List[Geometry], max_node_capacity, algorithm: TypeAlgorithm):
    tree = RTree(max_node_capacity, algorithm)

    for entry in entries:
        tree.insert(entry)

    return tree


def distance_func(shape: Geometry, point: Point):
    return shapely.distance(point, shape)

