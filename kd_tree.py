from typing import List

import shapely

#
# class Rectangle(shapely.Polygon):
#     def __new__(cls, xmin, ymin, xmax, ymax):
#         super().boundary
#         return super().__new__(cls, [(xmin, ymin), (xmax, ymax)])


class KDTree(object):
    def __init__(self, boundary: shapely.Geometry, shapes: List[shapely.Geometry], depth, left: 'KDTree' = None,
                 right: 'KDTree' = None):
        self.boundary = boundary
        self.shapes = shapes
        self.depth = depth
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None

    def insert(self, shape: shapely.Geometry):
        if self.is_leaf():
            self.shapes.append(shape)




def build_kd_tree(shapes: List[shapely.Geometry], depth=0):
    if not shapes or len(shapes) == 0:
        return None

    k = 2  # двумерное пространство
    axis = depth % k

    # points.sort(key=lambda x: x[axis])
    # median = len(points) // 2
    #
    # return Node(
    #     point=points[median],
    #     depth=depth,
    #     left=build_kd_tree(points[:median], depth + 1),
    #     right=build_kd_tree(points[median + 1:], depth + 1)
    # )


from shapely.geometry import Polygon


def position_relative_to_axes(rectangle: Polygon):
    """
    Определяет положение прямоугольника относительно осей координат.
    Возвращает строку, описывающую положение.
    """
    # Получаем вершины прямоугольника
    vertices = list(rectangle.exterior.coords)

    # Получаем координаты осей X и Y
    axis_x = 0
    axis_y = 0

    # Проверяем положение прямоугольника относительно осей
    left_of_x_axis = all(vertex[0] < axis_x for vertex in vertices)
    right_of_x_axis = all(vertex[0] > axis_x for vertex in vertices)
    above_y_axis = all(vertex[1] > axis_y for vertex in vertices)
    below_y_axis = all(vertex[1] < axis_y for vertex in vertices)

    # Формируем строку с описанием положения
    position_description = ""
    if left_of_x_axis:
        position_description += "Левее X-оси. "
    elif right_of_x_axis:
        position_description += "Правее X-оси. "

    if above_y_axis:
        position_description += "Выше Y-оси. "
    elif below_y_axis:
        position_description += "Ниже Y-оси. "

    return position_description.strip()
