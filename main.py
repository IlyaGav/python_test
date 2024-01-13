import random
import time
from collections import namedtuple

import shapely
from shapely import unary_union
from shapely.geometry import Point, LineString, Polygon

from grid import fixed_grid_find_nearest_neighbor, plot_fixed_grid, build_fixed_grid
from kd_tree import build_kd_tree, kd_tree_find_nearest_neighbor, plot_kd_tree
from quad_tree import build_quad_tree, quad_tree_find_nearest_neighbor, plot_quad_tree
from shapely_plot import add_to_plot_geometry, show_plot, set_title


def generate_random_point(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100,):
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
    print('start build benchmark')

    min_x, min_y, max_x, max_y = 0, 0, 10_000, 10_000

    min_length, max_length = 1, 15

    count_data = 10_000

    number = 5

    boundary = shapely.box(0, 0, 10_000, 10_000)

    print('generate data')

    data_set = [[generate_random_box(min_x, min_y, max_x, max_y, min_length, max_length) for _ in range(count_data)] for
                _ in range(number)]

    def test(setup, repeat=number):
        r = []
        for i in range(repeat):
            t = timeit.Timer(lambda: setup(i)).timeit(1)
            r.append(t)

        return r

    print('start timeit')

    print(f'build_kd_tree: {test(lambda i: build_kd_tree(boundary, data_set[i]), number)}')
    print(f'build_quad_tree: {test(lambda i: build_quad_tree(boundary, data_set[i]), number)}')
    print(f'build_spatial_grid: {test(lambda i: build_fixed_grid(boundary, data_set[i]), number)}')

    print('finish build benchmark')

    print()
    print()

def benchmark_find_nearest_neighbor():


    print('start find_nearest_neighbor benchmark')

    print('build indexes')

    count_point_for_query = 10

    import numpy as np

    for i in range(number):

        kd_tree = build_kd_tree(boundary, data_set[i])
        quad_tree = build_quad_tree(boundary, data_set[i])
        fixed_grid = build_fixed_grid(boundary, data_set[i])

        query_points = [generate_random_point(min_x, min_y, max_x, max_y)] * count_point_for_query
        np.mean(test(lambda i: kd_tree_find_nearest_neighbor(kd_tree, query_points[i]), i))
        d = test(lambda i: kd_tree_find_nearest_neighbor(kd_tree, query_points[i]), i)




    test(lambda i: kd_tree_find_nearest_neighbor(kd_tree, point), number)

    point = generate_random_point()

    count_launch_nearest_neighbor = 1

    nearest_neighbor_kd_tree_timer = timeit.Timer(lambda: kd_tree_find_nearest_neighbor(kd_tree, point))
    nearest_neighbor_quad_tree_timer = timeit.Timer(lambda: quad_tree_find_nearest_neighbor(quad_tree, point))
    nearest_neighbor_fixed_grid_timer = timeit.Timer(lambda: fixed_grid_find_nearest_neighbor(fixed_grid, point))

    print('start timeit')

    print(f'nearest_neighbor_kd_tree: {nearest_neighbor_kd_tree_timer.timeit(count_launch_nearest_neighbor)}')
    print(f'nearest_neighbor_quad_tree: {nearest_neighbor_quad_tree_timer.timeit(count_launch_nearest_neighbor)}')
    print(f'nearest_neighbor_fixed_grid: {nearest_neighbor_fixed_grid_timer.timeit(count_launch_nearest_neighbor)}')

    print('finish find_nearest_neighbor benchmark')

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
