from __future__ import annotations

from typing import List

import shapely
from shapely import Polygon, Geometry

from shapely_plot import add_to_plot_geometry


def union(*boundaries: BoundaryBox):
    minx, miny, = float('inf'), float('inf')
    maxx, maxy = float('-inf'), float('-inf')

    for boundary in boundaries:
        minx, miny = min(boundary.x_min, minx), min(boundary.y_min, miny)
        maxx, maxy = max(boundary.x_max, maxx), max(boundary.y_max, maxy)

    return BoundaryBox(minx, miny, maxx, maxy)


def enlargement(boundary_1: BoundaryBox, boundary_2: BoundaryBox):
    union_bbox = union(boundary_1, boundary_2)
    return union_bbox.area() - boundary_2.area()


def split_node(node: RTreeNode) -> [RTreeNode]:
    if node.children is None:
        raise ValueError("Can not be None")

    lowIdx, highIdx = linear(node.children)

    node_1 = RTreeNode([node.children[lowIdx]], node.is_leaf)
    node_2 = RTreeNode([node.children[highIdx]], node.is_leaf)

    node.children.remove(node_1.children[0])
    node.children.remove(node_2.children[0])

    for child in node.children:
        increase_1 = enlargement(node_1, child)
        increase_2 = enlargement(node_2, child)

        if increase_1 < increase_2 or increase_1 == increase_2 and node_1.area() < node_2.area():
            node_1.add_child(child)
            node_1.updateMBR(child)
        else:
            node_2.add_child(child)
            node_2.updateMBR(child)

    return node_1, node_2


def intersection(rect1: BoundaryBox, rect2: BoundaryBox) -> bool:
    return (rect1.x_min <= rect2.x_max and
            rect1.x_max >= rect2.x_min and
            rect1.y_min <= rect2.y_max and
            rect1.y_max >= rect2.y_min)


def box_to_geometry(box: BoundaryBox):
    return shapely.box(box.x_min, box.y_min, box.x_max, box.y_max)


def geometry_to_box(shape: Geometry):
    x_min, y_min, x_max, y_max = Polygon(shapely.envelope(shape)).bounds
    return BoundaryBox(x_min, y_min, x_max, y_max)


class BoundaryBox:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def area(self) -> float:
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)


class Entry(BoundaryBox):
    def __init__(self, shape: Geometry):
        x_min, y_min, x_max, y_max = Polygon(shapely.envelope(shape)).bounds
        super().__init__(x_min, y_min, x_max, y_max)
        self.shape = shape


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


class RTree(object):
    def __init__(self, max_node_capacity=4):
        self.root = RTreeNode([], True)
        self.max_node_capacity = max_node_capacity

    def insert(self, shape: Geometry):
        entry = Entry(shape)

        self.root.children = self.internal_insert(self.root, entry)

        if len(self.root.children) > self.max_node_capacity:
            node_1, node_2 = split_node(self.root)
            self.root = RTreeNode([node_1, node_2])

    def search(self, search: Geometry):
        search_box = geometry_to_box(search)

        if intersection(self.root, search_box):
            entries = self.internal_search(self.root, search_box)
            return list(map(lambda e: box_to_geometry(e), entries))
        else:
            return None

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
                increase = enlargement(child, entry)
                if increase < min_increase:
                    min_increase = increase
                    selected_node = child
                elif increase == min_increase and child.area < selected_node.area:
                    selected_node = child

            selected_node.children = self.internal_insert(selected_node, entry)

            if len(selected_node.children) > self.max_node_capacity:
                node_1, node_2 = split_node(selected_node)
                node.children.remove(selected_node)
                node.add_child(node_1)
                node.add_child(node_2)

        node.updateMBR(entry)

        return node.children


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


def plot_r_tree(r_tree: RTree):
    plot_r_node_recursive(r_tree.root, 0)


def plot_get_color(depth: int):
    return ['orange', 'black', 'grey', 'blue'][depth]


def plot_r_node(node: RTreeNode, color: str):
    add_to_plot_geometry(shapely.box(node.x_min, node.y_min, node.x_max, node.y_max), color)


def plot_r_node_recursive(node: RTreeNode, depth: int):
    plot_r_node(node, plot_get_color(depth))

    if node.is_leaf:
        return

    for child in node.children:
        plot_r_node_recursive(child, depth + 1)
