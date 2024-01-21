from __future__ import annotations

from typing import List

import shapely
from shapely import Polygon, Geometry, Point

from shapely_plot import add_to_plot_geometry


class KDTreePoint(object):
    def __init__(self, boundary: Polygon, point: Point | None, depth, left: 'KDTreePoint' = None,
                 right: 'KDTreePoint' = None):
        self.boundary = boundary
        self.point = point
        self.depth = depth
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None or self.right is None


def build_kd_tree_point(boundary: Polygon, points: List[shapely.geometry.Point], depth=0):
    if not points or len(points) == 0:
        return None

    k = 2  # двумерное пространство
    axis = depth % k

    sorted_points = sorted(points, key=lambda p: (p.x, p.y)[axis])

    median_index = len(sorted_points) // 2
    median = sorted_points[median_index]

    minx, miny, maxx, maxy = boundary.bounds

    if axis == 0:
        left_boundary = shapely.box(minx, miny, median.x, maxy)
        right_boundary = shapely.box(median.x, miny, maxx, maxy)
    else:
        left_boundary = shapely.box(minx, miny, maxx, median.y)
        right_boundary = shapely.box(minx, median.y, maxx, maxy)

    left = []
    right = []

    for (index, point) in enumerate(sorted_points):
        if index < median_index:
            left.append(point)
        elif index > median_index:
            right.append(point)

    return KDTreePoint(
        boundary=boundary,
        point=median,
        depth=depth,
        left=build_kd_tree_point(left_boundary, left, depth + 1),
        right=build_kd_tree_point(right_boundary, right, depth + 1)
    )


def kd_tree_point_find_nearest_neighbor(tree: KDTreePoint, point: Point):
    nearest, _ = find_nearest_neighbor_internal(tree, point, None, float('inf'))
    return nearest


def find_nearest_neighbor_internal(tree: KDTreePoint, point: Point, nearest: Geometry | None, min_distance):
    if tree is None:
        return nearest, min_distance

    distance = shapely.distance(tree.point, point)

    if distance < min_distance:
        nearest = tree.point
        min_distance = distance

    k = 2  # двумерное пространство
    axis = tree.depth % k
    median_tuple = [tree.point.x, tree.point.y]
    point_tuple = [point.x, point.y]

    if point_tuple[axis] <= median_tuple[axis]:
        nearest, min_distance = find_nearest_neighbor_internal(tree.left, point, nearest, min_distance)
        if (median_tuple[axis] - point_tuple[axis]) < min_distance:
            nearest, min_distance = find_nearest_neighbor_internal(tree.right, point, nearest, min_distance)
    else:
        nearest, min_distance = find_nearest_neighbor_internal(tree.right, point, nearest, min_distance)
        if (point_tuple[axis] - median_tuple[axis]) < min_distance:
            nearest, min_distance = find_nearest_neighbor_internal(tree.left, point, nearest, min_distance)

    return nearest, min_distance


def plot_kd_tree_point(tree: KDTreePoint):
    if tree is None:
        return

    if tree.depth == 0:
        add_to_plot_geometry(tree.boundary, 'black')

    k = 2  # двумерное пространство
    axis = tree.depth % k

    minx, miny, maxx, maxy = tree.boundary.bounds

    if axis == 0:
        add_to_plot_geometry(shapely.geometry.LineString([(tree.point.x, miny), (tree.point.x, maxy)]), 'black')
    else:
        add_to_plot_geometry(shapely.geometry.LineString([(minx, tree.point.y), (maxx, tree.point.y)]), 'black')

    add_to_plot_geometry(tree.point, 'orange')

    plot_kd_tree_point(tree.left)
    plot_kd_tree_point(tree.right)

