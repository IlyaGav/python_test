import random
import time
from collections import namedtuple

import shapely
from shapely import unary_union
from shapely.geometry import Point, LineString, Polygon

from fixed_grid import fixed_grid_find_nearest_neighbor, plot_fixed_grid, build_fixed_grid, fixed_grid_benchmark_build, \
    fixed_grid_benchmark_find_nearest_neighbor
from kd_tree import build_kd_tree, kd_tree_find_nearest_neighbor, plot_kd_tree, kd_tree_benchmark_build, \
    kd_tree_benchmark_find_nearest_neighbor
from quad_tree import build_quad_tree, quad_tree_find_nearest_neighbor, plot_quad_tree, quad_tree_benchmark_build, \
    quad_tree_benchmark_find_nearest_neighbor
from shapely_plot import add_to_plot_geometry, show_plot, set_title


def generate_random_point(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, ):
    return Point(random.uniform(min_x_coord, max_x_coord), random.uniform(min_y_coord, max_y_coord))


def generate_random_line(num_points=2, min_coord=0, max_coord=100):
    points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
    return LineString([(point.x, point.y) for point in points])


def generate_random_polygon(num_points=3, min_coord=0, max_coord=100):
    points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
    return Polygon([(point.x, point.y) for point in points])


def generate_random_box_2(min_coord=0, max_coord=10, max_width=2, max_height=2):
    x1 = random.uniform(min_coord, max_coord)
    y1 = random.uniform(min_coord, max_coord)
    x2 = random.uniform(x1, max_coord)
    y2 = random.uniform(y1, max_coord)

    return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])


def generate_random_box(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, min_length=1, max_length=15):
    width = random.uniform(min_length, max_length)
    height = random.uniform(min_length, max_length)

    ww = width / 2
    hh = height / 2

    x = random.uniform(min_x_coord + ww, max_x_coord - ww)
    y = random.uniform(min_y_coord + hh, max_y_coord - hh)

    return Polygon([(x - ww, y - hh), (x - ww, y + hh), (x + ww, y + hh), (x + ww, y - hh)])


def generate_box(xmin, ymin, xmax, ymax):
    return Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])


seed = int(time.time())
# seed = 1705134058
# seed = 1705094261
random.seed(seed)
print(f"random seed {seed}")

# boundary = shapely.box(0, 0, 100, 100)


import timeit


def d(setup):
    pass


def benchmark():
    min_x, min_y, max_x, max_y = 0, 0, 1_000_000, 1_000_000

    min_length, max_length = 1, 15

    count_data = 100_000_000

    boundary = shapely.box(min_x, min_y, max_x, max_y)

    print('generate data...')

    data_set = [generate_random_box(min_x, min_y, max_x, max_y, min_length, max_length) for _ in range(count_data)]

    print('start build benchmark')

    print()

    print('kd_tree_build', kd_tree_benchmark_build(boundary, data_set))
    print('quad_tree_build', quad_tree_benchmark_build(boundary, data_set))
    print('fixed_grid_build', fixed_grid_benchmark_build(boundary, data_set))

    print()
    print()

    print('start nearest_neighbor benchmark')

    print('building...')

    point = generate_random_point(min_x, min_y, max_x, max_y)

    kd_tree = build_kd_tree(boundary, data_set)
    quad_tree = build_quad_tree(boundary, data_set)
    fixed_grid = build_fixed_grid(boundary, data_set)

    print()

    print('kd_tree_nearest_neighbor', kd_tree_benchmark_find_nearest_neighbor(kd_tree, point))
    print('quad_tree_nearest_neighbor', quad_tree_benchmark_find_nearest_neighbor(quad_tree, point))
    print('fixed_grid_nearest_neighbor', fixed_grid_benchmark_find_nearest_neighbor(fixed_grid, point))

    print()
    print()


benchmark()

# shapes = [generate_random_box() for _ in range(100)]
# # shapes = []
# # shapes.append(generate_box(1, 1, 30, 30))
# # shapes.append(generate_box(10, 52, 35, 80))
#
# boundary = shapely.box(0, 0, 100, 100)
#
# point = generate_random_point()
# # point = Point(4, 48)
#
# kd_tree = build_kd_tree(boundary, shapes)
# plot_kd_tree(kd_tree)
# nearest_neighbor = kd_tree_find_nearest_neighbor(kd_tree, point)
# add_to_plot_geometry(nearest_neighbor, 'red')
# add_to_plot_geometry(point)
# set_title('kd_tree')
# show_plot()
#
# quad_tree = build_quad_tree(boundary, shapes)
# plot_quad_tree(quad_tree)
# nearest_neighbor = quad_tree_find_nearest_neighbor(quad_tree, point)
# add_to_plot_geometry(nearest_neighbor, 'red')
# add_to_plot_geometry(point)
# set_title('quad_tree')
# show_plot()
#
# grid = build_grid(boundary, shapes)
# plot_grid(grid)
# nearest_neighbor = grid_find_nearest_neighbor(grid, point)
# add_to_plot_geometry(nearest_neighbor, 'red')
# add_to_plot_geometry(point)
# set_title('grid')
# show_plot()

# x, y, r = 5, 5, 3
#
# for p in list(set(circular_traversal(x, y, r))):
#     add_to_plot_geometry(Point(p[0], p[1]), 'red')
# set_title('circular_traversal')
# show_plot()
#
#
# for p in list(set(circular_traversal_2(x, y, r))):
#     add_to_plot_geometry(Point(p[0], p[1]), 'red')
# set_title('circular_traversal_2')
# show_plot()
#
# for p in list(set(circular_traversal_3(x, y, r))):
#     add_to_plot_geometry(Point(p[0], p[1]), 'red')
# set_title('circular_traversal_3')
# show_plot()


# Вывод сетки на консоль
# print_grid(grid)

# Выводим результат
# print(f"Nearest neighbor (query rect):", nearest_neighbor)
