import random
import time

import pyzorder
import shapely
from pyzorder import pymorton
from shapely import unary_union
from shapely.affinity import scale
from shapely.geometry import Point, LineString, Polygon

import z_curve
from grid import SpatialGrid, grid_find_nearest_neighbor, visualize_grid, print_grid
from kd_tree import build_kd_tree, kd_tree_find_nearest_neighbor, plot_kd_tree
from quad_tree import build_quad_tree, quad_tree_find_nearest_neighbor, plot_quad_tree
from shapely_plot import add_to_plot_geometry, show_plot






# Ваша функция encodeComponent также должна быть переведена на Python
# def encode_component(mask, bits, dim, bit_pos_mod_dim):
#     # Ваша реализация encodeComponent


from pyzorder import ZOrderIndexer

from test_z import ZCurve

zi = ZOrderIndexer((0, 0), (7, 7))

z_2_2 = zi.zindex(2, 2)
# z_2_2 = 12

print(zi.next_zorder_index(z_2_2))

print('-------------')

zz = ZCurve(2, 32)

b = zz.encode([5, 3])

print(zz.big_min(60 , 24, 31))



print('-------------')

def generate_random_point(min_coord=0, max_coord=10):
    return Point(random.uniform(min_coord, max_coord), random.uniform(min_coord, max_coord))


def generate_random_line(num_points=2, min_coord=0, max_coord=10):
    points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
    return LineString([(point.x, point.y) for point in points])


def generate_random_polygon(num_points=3, min_coord=0, max_coord=10):
    points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
    return Polygon([(point.x, point.y) for point in points])


def generate_random_box_2(min_coord=0, max_coord=10, max_width=2, max_height=2):
    x1 = random.uniform(min_coord, max_coord)
    y1 = random.uniform(min_coord, max_coord)
    x2 = random.uniform(x1, max_coord)
    y2 = random.uniform(y1, max_coord)

    return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])


def generate_random_box(min_coord=0, max_coord=100, min_length=0.5, max_length=8):
    width = random.uniform(min_length, max_length)
    height = random.uniform(min_length, max_length)

    ww = width / 2
    hh = height / 2

    x = random.uniform(min_coord + ww, max_coord - ww)
    y = random.uniform(min_coord + hh, max_coord - hh)

    return Polygon([(x - ww, y - hh), (x - ww, y + hh), (x + ww, y + hh), (x + ww, y - hh)])


seed = int(time.time())
# seed = 1705066752
# seed = 1705051400
random.seed(seed)
print(f"random seed {seed}")

shapes = [generate_random_box() for _ in range(5)]

point = generate_random_point()

print(point)

# rec = scale(unary_union([*shapes, point]).envelope, 1.2, 1.2, 1.2)
boundary = shapely.box(0, 0, 100, 100)

# kd_tree = build_kd_tree(rec, shapes)
# plot_kd_tree(kd_tree)
#
# # for shape in shapes:
# #     add_to_plot_geometry(shape)
#
# nearest_neighbor = kd_tree_find_nearest_neighbor(kd_tree, point)
# add_to_plot_geometry(nearest_neighbor, 'red')
# add_to_plot_geometry(point)
# set_title('kd_tree')
# show_plot()

# quad_tree = build_quad_tree(rec, shapes)
#
# plot_quad_tree(quad_tree)
#
# nearest_neighbor = quad_tree_find_nearest_neighbor(quad_tree, point)
# add_to_plot_geometry(nearest_neighbor, 'red')
# add_to_plot_geometry(point)
# set_title('quad_tree')
# show_plot()

# Пример использования
grid = SpatialGrid(boundary)

for shape in shapes:
    grid.add_object(shape)

# nearest_neighbor = grid_find_nearest_neighbor(grid, point)

add_to_plot_geometry(boundary, 'red')

for shape in shapes:
    add_to_plot_geometry(shape)

# add_to_plot_geometry(point)

# add_to_plot_geometry(nearest_neighbor)

visualize_grid(grid)

show_plot()

# Вывод сетки на консоль
# print_grid(grid)

# Выводим результат
# print(f"Nearest neighbor (query rect):", nearest_neighbor)
