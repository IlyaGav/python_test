from typing import List

import shapely
from shapely import Polygon, Geometry, unary_union, Point, MultiPoint, LineString

from shapely_plot import add_to_plot_geometry, show_plot, set_title


class KDTree(object):
    def __init__(self, boundary: Polygon, shapes: List[Geometry], depth, left: 'KDTree' = None,
                 right: 'KDTree' = None):
        self.boundary = boundary
        self.shapes = shapes
        self.depth = depth
        self.left = left
        self.right = right

        # TODO
        # self._max_depth = 8

    def is_leaf(self):
        return self.left is None and self.right is None


def get_containing_child(tree: KDTree, boundary: shapely.Polygon):
    if tree.is_leaf:
        return None

    if tree.left.boundary.contains(boundary):
        return tree.left

    if tree.right.boundary.contains(boundary):
        return tree.right

    return None


def build_kd_tree(boundary: Polygon, shapes: List[shapely.Geometry], depth=0):
    if not shapes or len(shapes) == 0:
        return None

    k = 2  # двумерное пространство
    axis = depth % k

    median = find_median(shapes, axis)

    minx, miny, maxx, maxy = boundary.bounds

    if axis == 0:
        left_boundary = MultiPoint([(minx, miny), (median, maxy)]).envelope
        right_boundary = MultiPoint([(median, miny), (maxx, maxy)]).envelope
    else:
        left_boundary = MultiPoint([(minx, miny), (maxx, median)]).envelope
        right_boundary = MultiPoint([(minx, median), (maxx, maxy)]).envelope

    self = []
    left = []
    right = []

    for shape in shapes:
        mbr = Polygon(shapely.envelope(shape))
        vertices = list(mbr.exterior.coords)

        if all(vertex[axis] < median for vertex in vertices):
            left.append(shape)
        elif all(vertex[axis] > median for vertex in vertices):
            right.append(shape)
        else:
            self.append(shape)

    # TODO Для тестирования
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
        left=build_kd_tree(left_boundary, left, depth + 1),
        right=build_kd_tree(right_boundary, right, depth + 1)
    )

    # points.sort(key=lambda x: x[axis])
    # median = len(points) // 2
    #
    # return Node(
    #     point=points[median],
    #     depth=depth,
    #     left=build_kd_tree(points[:median], depth + 1),
    #     right=build_kd_tree(points[median + 1:], depth + 1)
    # )


def find_nearest_neighbor(tree: KDTree, point: Point):
    min_dist = min_dist_nearest_neighbor(tree, point, tree)
    return find_nearest_neighbor_from(tree, point, min_dist)


#  TODO best_dist == 0, rename var
def min_dist_nearest_neighbor(tree: KDTree, point: Point, root: KDTree):
    # TODO Вычислять всегда, вдруг попали на ось пересечения или только у листов?
    best_dist = min(map(lambda s: shapely.distance(s, point), tree.shapes)) if len(tree.shapes) > 0 else None

    # TODO Будем тогда выбирать первого (самого большого считай), кто содержит
    if best_dist == 0:
        return 0

    if tree.is_leaf():
        dist = best_dist
    elif tree.left.boundary.contains(point):
        dist = min_dist_nearest_neighbor(tree.left, point, root)
    else:
        dist = min_dist_nearest_neighbor(tree.right, point, root)

    return min(best_dist, dist) if best_dist is not None else dist

    # print(f'best_dist {best_dist}')
    #
    # add_to_plot_geometry(root.boundary, 'black')
    #
    # plot_kd_tree(root, tree.depth)
    #
    # for shape in tree.shapes:
    #     add_to_plot_geometry(shape, 'orange')
    #     shortest_line = LineString(shapely.shortest_line(shape, point))
    #     print(shortest_line.length)
    #     add_to_plot_geometry(shortest_line, 'red')
    #
    # add_to_plot_geometry(point, 'red')
    #
    # set_title(f'depth {tree.depth}')
    # show_plot()


# TODO rename
def find_nearest_neighbor_from(tree: KDTree, point: Point, radius: int):
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
        print('intersection left')
        l_nearest = find_nearest_neighbor_from(tree.left, point, radius)

    if shapely.distance(tree.right.boundary, point) <= radius:
        print('intersection right')
        r_nearest = find_nearest_neighbor_from(tree.right, point, radius)

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

# def plot_kd_tree(tree: KDTree, depth: int):
#     if tree is None or tree.depth > depth:
#         return
#
#     if tree.depth == depth:
#         # Деление плоскости
#         if tree.left is not None:
#             add_to_plot_geometry(tree.left.boundary, 'black')
#
#         add_to_plot_geometry(tree.boundary, 'red')
#     else:
#         add_to_plot_geometry(tree.boundary, 'black')
#
#     plot_kd_tree(tree.left, depth)
#
#     plot_kd_tree(tree.right, depth)
#
#     for shape in tree.shapes:
#         add_to_plot_geometry(shape, 'yellow')
