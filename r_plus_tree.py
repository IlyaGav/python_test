from __future__ import annotations

from typing import List

import shapely
from shapely import Geometry, Polygon

from shapely_plot import add_to_plot_geometry


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


class RPlusTreeNode(BoundaryBox):
    def __init__(self, children: List[RPlusTreeNode | Entry] | None = None, parent: RPlusTreeNode = None,
                 is_leaf: bool = False):
        mbr = union(*children)
        super().__init__(mbr.x_min, mbr.y_min, mbr.x_max, mbr.y_max)
        self.children = children
        self.parent = parent
        self.is_leaf = is_leaf

    def add_child(self, node: 'RPlusTreeNode' | Entry):
        self.children.append(node)


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


def _sweep(children: List[RPlusTreeNode], axis):
    temp_left = [child.x_min if axis == 0 else child.y_min for child in children]
    temp_right = [child.x_max if axis == 0 else child.y_max for child in children]

    temp_left.sort()
    temp_right.sort()

    if temp_left[0] == temp_left[-1] or temp_right[0] == temp_right[-1]:
        return float('-inf')

    cutLine = temp_left[len(children) // 2]
    if temp_left[0] == cutLine:
        for i in range(len(children) // 2 + 1, len(children)):
            if temp_left[i] != cutLine:
                cutLine = temp_left[i]
                break

    return cutLine


def _evaluate(children: List[RPlusTreeNode]):
    cutLine_x = _sweep(children, 0)
    cutLine_y = _sweep(children, 1)

    if cutLine_x == float('-inf') or cutLine_y == float('-inf'):
        return [1, cutLine_y] if cutLine_x == float('-inf') else [0, cutLine_x]

    num_cut_x = sum(1 for c in children if c.x_min < cutLine_x < c.x_max)
    num_cut_y = sum(1 for c in children if c.y_min < cutLine_y < c.y_max)

    return [0, cutLine_x] if num_cut_x < num_cut_y else [1, cutLine_y]


def _needCut(node: RPlusTreeNode, cut_info: List[int | float]):
    axis = int(cut_info[0])
    cutLine = cut_info[1]

    if (node.x_min if axis == 0 else node.y_min) < cutLine and (node.x_max if axis == 0 else node.y_max) <= cutLine:
        return 1
    elif node.x_min if axis == 0 else node.y_min >= cutLine:
        return 2
    else:
        return 0


def _partition(node: RPlusTreeNode | Entry, cut_info: List[int | float]):
    print('_partition')
    axis = cut_info[0]
    cutLine = cut_info[1]

    if not isinstance(node, Entry):
        nn = [RPlusTreeNode(node.children.copy(), None, node.is_leaf),
              RPlusTreeNode(node.children.copy(), None, node.is_leaf)]

        if axis == 0:
            nn[0].x_max = cutLine
        else:
            nn[0].y_max = cutLine
        # (nn[0].x_max if axis == 0 else nn[0].y_max) = cutLine
        # nn[0].dimensions[axis] = cutLine - nn[0].coords[axis]

        if axis == 0:
            nn[1].x_min = cutLine
        else:
            nn[1].y_min = cutLine
        # (nn[1].x_min if axis == 0 else nn[1].y_min) = cutLine
        # nn[1].coords[axis] = cutLine

        if axis == 0:
            nn[1].x_max = node.x_max
        else:
            nn[1].y_max = node.y_max
        # (nn[1].x_max if axis == 0 else nn[1].y_max) = (node.x_max if axis == 0 else node.y_max)
        # nn[1].dimensions[axis] = node.dimensions[axis] - nn[0].dimensions[axis]

        for child in node.children:
            result = _needCut(child, cut_info)
            if result == 1:
                nn[0].add_child(child)
                child.parent = nn[0]
            elif result == 2:
                nn[1].add_child(child)
                child.parent = nn[1]
            else:
                splits = _partition(child, cut_info)
                nn[0].add_child(splits[0])
                splits[0].parent = nn[0]
                nn[1].add_child(splits[1])
                splits[1].parent = nn[1]

        return nn
    else:
        ee = [Entry(node.shape), Entry(node.shape)]

        if axis == 0:
            ee[0].x_max = cutLine
        else:
            ee[0].y_max = cutLine
        # (ee[0].x_max if axis == 0 else ee[0].y_max) = cutLine
        # ee[0].dimensions[axis] = cutLine - ee[0].coords[axis]

        if axis == 0:
            ee[1].x_min = cutLine
        else:
            ee[1].y_min = cutLine
        # (ee[1].x_min if axis == 0 else ee[1].y_min) = cutLine
        # ee[1].coords[axis] = cutLine

        if axis == 0:
            ee[1].x_max = node.x_max
        else:
            ee[1].y_max = node.y_max
        # (ee[1].x_max if axis == 0 else ee[1].y_max) = (node.x_max if axis == 0 else node.y_max)
        # ee[1].dimensions[axis] = node.dimensions[axis] - ee[0].dimensions[axis]

        return ee


def _assign(node: RPlusTreeNode, cut_info: List[int | float]):
    result = _needCut(node, cut_info)

    if result == 1:
        return [node, None]
    elif result == 2:
        return [None, node]
    else:
        nn = _partition(node, cut_info)
        return nn


def _tighten(*nodes: RPlusTreeNode):
    for node in nodes:
        minx, miny, = float('inf'), float('inf')
        maxx, maxy = float('-inf'), float('-inf')

        for child in node.children:
            child.parent = node

            minx = min(minx, child.x_min)
            miny = min(miny, child.y_min)

            maxx = max(maxx, child.x_max)
            maxy = max(maxy, child.y_max)

        node.x_min, node.y_min = minx, miny
        node.x_max, node.y_max = maxx, maxy


def _splitNode(node: RPlusTreeNode):
    cc = node.children.copy()
    node.children.clear()

    nn = [node, RPlusTreeNode(node.children.copy(), node.parent, node.is_leaf)]

    if nn[1].parent is not None:
        nn[1].parent.add_child(nn[1])

    cut_info = _evaluate(cc)

    for child in cc:
        result = _assign(child, cut_info)

        if result[0] is not None:
            nn[0].add_child(result[0])
            result[0].parent = nn[0]

        if result[1] is not None:
            nn[1].add_child(result[1])
            result[1].parent = nn[1]

    _tighten(*nn)

    return nn


def _chooseLeaves(node: RPlusTreeNode, entry: Entry):
    result: List[RPlusTreeNode] | None = []

    if node.is_leaf:
        result.append(node)
    else:
        overlap = False

        for child in node.children:
            if intersection(child, entry):
                overlap = True
                result.extend(_chooseLeaves(child, entry))

        if not overlap:
            min_increase = float('inf')
            next_node = None
            for child in node.children:
                increase = enlargement(child, entry)
                if increase < min_increase:
                    min_increase = increase
                    next_node = child
                elif increase == min_increase and child.area() < next_node.area():
                    next_node = child
            result.extend(_chooseLeaves(next_node, entry))

    return result


class RPlusTree(object):
    def __init__(self, max_node_capacity=4):
        self.root = RPlusTreeNode([], None, True)
        self.max_node_capacity = max_node_capacity
        self.size = 0

    def insert(self, shape: Geometry):
        entry = Entry(shape)

        leaves = _chooseLeaves(self.root, entry)

        for leaf in leaves:
            leaf.children.append(entry)
            entry.parent = leaf

            if len(leaf.children) > self.max_node_capacity:
                splits = _splitNode(leaf)
                self._adjustTree(splits[0], splits[1])
            else:
                self._adjustTree(leaf, None)

        self.size += 1

    def _adjustTree(self, node: RPlusTreeNode, new_node: RPlusTreeNode | None):
        if node == self.root:
            if new_node is not None:
                self.root = RPlusTreeNode([], None, False)

                self.root.add_child(node)
                node.parent = self.root

                self.root.add_child(new_node)
                new_node.parent = self.root

            _tighten(self.root)
        else:
            _tighten(node)

            if new_node is not None:
                _tighten(new_node)

                if len(node.parent.children) > self.max_node_capacity:
                    splits = _splitNode(node.parent)
                    self._adjustTree(splits[0], splits[1])

            if node.parent is not None:
                self._adjustTree(node.parent, None)

    def search(self, search: Geometry):
        search_box = geometry_to_box(search)

        if intersection(self.root, search_box):
            entries = self.internal_search(self.root, search_box)
            return list(map(lambda e: box_to_geometry(e), entries))
        else:
            return None

    def internal_search(self, node: RPlusTreeNode, search_box: BoundaryBox) -> List[Entry]:
        search_result: List[Entry] | None = []

        if node.is_leaf:
            search_result = list(filter(lambda n: intersection(n, search_box), node.children))
        else:
            for child in node.children:
                if intersection(child, search_box):
                    search_result.extend(self.internal_search(child, search_box))

        return search_result


def plot_r_plus_tree(r_tree: RPlusTree):
    plot_r_plus_node_recursive(r_tree.root, 0)


def plot_get_color(depth: int):
    return ['orange', 'black', 'grey', 'blue'][depth]


def plot_r_plus_node(node: RPlusTreeNode, color: str):
    add_to_plot_geometry(shapely.box(node.x_min, node.y_min, node.x_max, node.y_max), color)


def plot_r_plus_node_recursive(node: RPlusTreeNode, depth: int):
    plot_r_plus_node(node, plot_get_color(depth))

    if node.is_leaf:
        return

    for child in node.children:
        plot_r_plus_node_recursive(child, depth + 1)
