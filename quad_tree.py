from __future__ import annotations

from typing import List

import shapely
from shapely import Polygon, Geometry, Point

from shapely_plot import add_to_plot_geometry


class Quadtree(object):
    def __init__(self, boundary: Polygon, depth: int, bucket_capacity=8, max_depth=8):
        self.boundary = boundary
        self.depth = depth

        self.bucket_capacity = bucket_capacity
        self.max_depth = max_depth

        self.top_left: Quadtree | None = None
        self.top_right: Quadtree | None = None
        self.bottom_left: Quadtree | None = None
        self.bottom_right: Quadtree | None = None

        self.shapes = []

    def is_leaf(self):
        return (self.top_left is None or self.top_right is None or
                self.bottom_left is None or self.bottom_right is None)

    def insert(self, shape: Geometry):
        if not self.boundary.contains(shapely.envelope(shape)):
            raise ValueError("ElementOutsideQuadtreeBounds")

        if len(self.shapes) >= self.bucket_capacity:
            self.split()

        containing_child = self.get_containing_child(shape)

        if containing_child is not None:
            containing_child.insert(shape)
        else:
            self.shapes.append(shape)

    # def Remove(self, element):
    #     containing_child = self.GetContainingChild(element.Bounds)
    #     removed = containing_child.Remove(element) if containing_child else self._elements.remove(element)
    #
    #     if removed and self.CountElements() <= self._bucket_capacity:
    #         self.Merge()
    #
    #     return removed

    # def Intersects(self, element):
    #     nodes = Queue()
    #     collisions = []
    #
    #     nodes.put(self)
    #
    #     while not nodes.empty():
    #         node = nodes.get()
    #
    #         if not element.Intersects(node.Bounds):
    #             continue
    #
    #         collisions.extend(
    #             e for e in node._elements if e.Bounds.Intersects(element)
    #         )
    #
    #         if not node.IsLeaf:
    #             nodes.put(node._top_left)
    #             nodes.put(node._top_right)
    #             nodes.put(node._bottom_left)
    #             nodes.put(node._bottom_right)
    #
    #     return collisions
    #
    # def Contains(self, element):
    #     nodes = Queue()
    #     contained = []
    #
    #     nodes.put(self)
    #
    #     while not nodes.empty():
    #         node = nodes.get()
    #
    #         if not node.Bounds.Contains(element):
    #             continue
    #
    #         contained.extend(
    #             e for e in node._elements if e.Bounds.Contains(element)
    #         )
    #
    #         if not node.IsLeaf:
    #             nodes.put(node._top_left)
    #             nodes.put(node._top_right)
    #             nodes.put(node._bottom_left)
    #             nodes.put(node._bottom_right)
    #
    #     return contained

    # def CountElements(self):
    #     count = len(self._elements)
    #
    #     if not self.IsLeaf:
    #         count += self._top_left.CountElements()
    #         count += self._top_right.CountElements()
    #         count += self._bottom_left.CountElements()
    #         count += self._bottom_right.CountElements()
    #
    #     return count

    # def GetElements(self):
    #     children = []
    #     nodes = Queue()
    #
    #     nodes.put(self)
    #
    #     while not nodes.empty():
    #         node = nodes.get()
    #
    #         if not node.IsLeaf:
    #             nodes.put(node._top_left)
    #             nodes.put(node._top_right)
    #             nodes.put(node._bottom_left)
    #             nodes.put(node._bottom_right)
    #
    #         children.extend(node._elements)
    #
    #     return children

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

    # def Merge(self):
    #     if self.IsLeaf:
    #         return
    #
    #     self._elements.extend(self._top_left._elements)
    #     self._elements.extend(self._top_right._elements)
    #     self._elements.extend(self._bottom_left._elements)
    #     self._elements.extend(self._bottom_right._elements)
    #
    #     self._top_left = self._top_right = self._bottom_left = self._bottom_right = None

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


def build_quad_tree(boundary: Polygon, shapes: List[shapely.Geometry]):
    if not shapes or len(shapes) == 0:
        return None

    tree = Quadtree(boundary, 0, 4, 8)

    for shape in shapes:
        tree.insert(shape)

    return tree


def quad_tree_find_nearest_neighbor(tree: Quadtree, point: Point):
    return find_nearest_neighbor_internal(tree, point, None)


# TODO Много дублирования
def find_nearest_neighbor_internal(tree: Quadtree, point: Point, best: Geometry = None):
    if tree is None:
        return best

    shapes = tree.shapes.copy()
    shapes.sort(key=lambda s: shapely.distance(s, point))

    _best = shapes[0] if len(shapes) > 0 else None

    if best is None or shapely.distance(_best, point) < shapely.distance(best, point):
        best = _best

    if not tree.is_leaf():
        nodes = [tree.top_left, tree.top_right, tree.bottom_right, tree.bottom_left]
        for i in range(len(nodes)):
            if nodes[i].boundary.contains(point):
                best = find_nearest_neighbor_internal(nodes[i], point, best)
                for j in filter(lambda jj: jj != i, range(len(nodes))):
                    if best is None or shapely.distance(nodes[j].boundary, point) < shapely.distance(best, point):
                        best = find_nearest_neighbor_internal(nodes[j], point, best)

    return best


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
