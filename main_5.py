# import math
# import random
# import time
#
# import shapely
# from shapely import Point, Polygon
#
# from common import Entry
# from fixed_grid import FixedGrid, plot_fixed_grid
# from kd_tree import KDTree, plot_kd_tree
# from quad_tree import Quadtree, plot_quad_tree
# from r_tree import RTree, plot_r_tree
# from shapely_plot import add_to_plot_geometry, show_plot, set_title, axis_ticks
#
# seed = int(time.time())
# # seed = 1718660781
# # star
# # seed = 1713477765
#
# # TODO r_plus_tree
# # seed = 1713477681
# random.seed(seed)
# print(f"random seed {seed}")
#
#
# def generate_random_point(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, ):
#     return Point(random.uniform(min_x_coord, max_x_coord), random.uniform(min_y_coord, max_y_coord))
#
#
# def generate_random_box(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, min_length: float = 1,
#                         max_length: float = 15):
#     width = random.uniform(min_length, max_length)
#     height = random.uniform(min_length, max_length)
#
#     ww = width / 2
#     hh = height / 2
#
#     x = random.uniform(min_x_coord + ww, max_x_coord - ww)
#     y = random.uniform(min_y_coord + hh, max_y_coord - hh)
#
#     return Polygon([(x - ww, y - hh), (x - ww, y + hh), (x + ww, y + hh), (x + ww, y - hh)])
#
#
# grid_size = 10_000
# boundary = shapely.box(0, 0, grid_size, grid_size)
# minx, miny, maxx, maxy = boundary.bounds
# # polygons = [generate_random_box(minx, miny, maxx, maxy) for _ in range(50)]
# # entries = list(Entry(p) for p in polygons)
# # points = [generate_random_point(minx, miny, maxx, maxy) for _ in range(100)]
# # entries = list(Entry(p) for p in points)
#
# import numpy as np
#
#
# def uniform_distribution(size, num_entries, noise_level=0.0):
#     n = int(math.sqrt(num_entries))
#
#     x = np.linspace(0, size, n)
#     y = np.linspace(0, size, n)
#
#     points = [(xi + np.random.uniform(-noise_level, noise_level), yi + np.random.uniform(-noise_level, noise_level)) for
#               xi in x for yi in y]
#
#     points = list(filter(lambda p: (0 <= p[0] <= size) and (0 <= p[1] <= size), points))
#
#     return [Point(p[0], p[1]) for p in points]
#
#
# def gaussian_distribution(size, num_entries, mean_x, mean_y, std_dev):
#     # Генерация координат с Гауссовым распределением
#     x_coords = np.random.normal(loc=mean_x, scale=std_dev, size=num_entries)
#     y_coords = np.random.normal(loc=mean_y, scale=std_dev, size=num_entries)
#
#     # Объединение координат в массив точек
#     points = [Point(p[0], p[1]) for p in np.column_stack((x_coords, y_coords))]
#
#     return list(filter(lambda p: (0 <= p.x <= size) and (0 <= p.y <= size), points))
#
#
# num_entries = 1000
#
# points = uniform_distribution(grid_size, num_entries, math.sqrt(grid_size))
# print('равномерные', len(points))
# for point in points:
#     add_to_plot_geometry(point, 'black')
# # set_title('равномерные')
# axis_ticks()
# show_plot()
#
# points = uniform_distribution(grid_size, int(math.sqrt(grid_size)), 4 * math.sqrt(grid_size))
# print('разреженные', len(points))
# for point in points:
#     add_to_plot_geometry(point, 'black')
# # set_title('разреженные')
# axis_ticks()
# show_plot()
#
# points = gaussian_distribution(grid_size, 5 * num_entries, grid_size / 2, grid_size / 2, grid_size / 5)
# print('плотные', len(points))
# for point in points:
#     add_to_plot_geometry(point, 'black')
# # set_title('плотные')
# axis_ticks()
# show_plot()
#
# # search_point = generate_random_point(minx, miny, maxx, maxy)
# # search_box = generate_random_box(minx + 20, miny + 20, maxx, maxy, 15, 30)
# #
# # kd_tree = KDTree(boundary, 10, 10)
# # grid = FixedGrid(boundary, 10)
# # quad_tree = Quadtree(boundary, 10, 10)
# # r_tree = RTree(10, 'quadratic')
# #
# # for entry in entries:
# #     add_to_plot_geometry(entry.shape, 'black')
# #     kd_tree.insert(entry)
# #
# # plot_kd_tree(kd_tree)
# #
# # # nearest = kd_tree.find_nearest_neighbor(search_point)
# # # add_to_plot_geometry(nearest, 'green')
# # # add_to_plot_geometry(search_point, 'yellow')
# #
# # search_result = kd_tree.search(search_box)
# # add_to_plot_geometry(search_box, 'yellow')
# # if search_result is not None:
# #     for r in search_result:
# #         add_to_plot_geometry(r, 'green')
# #
# # set_title('kd_tree')
# # show_plot()
#
# # for entry in entries:
# #     add_to_plot_geometry(entry.shape, 'red')
# #     grid.insert(entry)
# #
# # plot_fixed_grid(grid)
#
# # nearest = grid.find_nearest_neighbor(search_point)
# # add_to_plot_geometry(nearest, 'green')
# # add_to_plot_geometry(search_point, 'yellow')
#
# # search_result = grid.search(search_box)
# # add_to_plot_geometry(search_box, 'yellow')
# # if search_result is not None:
# #     for r in search_result:
# #         add_to_plot_geometry(r, 'green')
# #
# # set_title('fixed_grid')
# # show_plot()
# #
# # for entry in entries:
# #     add_to_plot_geometry(entry.shape, 'red')
# #     quad_tree.insert(entry)
# #
# # plot_quad_tree(quad_tree)
# #
# # nearest = quad_tree.find_nearest_neighbor(search_point)
# # add_to_plot_geometry(nearest, 'green')
# # add_to_plot_geometry(search_point, 'yellow')
# #
# # # search_result = quad_tree.search(search_box)
# # # add_to_plot_geometry(search_box, 'yellow')
# # # if search_result is not None:
# # #     for r in search_result:
# # #         add_to_plot_geometry(r, 'green')
# #
# # set_title('quad_tree')
# # show_plot()
# #
# # for entry in entries:
# #     add_to_plot_geometry(entry.shape, 'red')
# #     r_tree.insert(entry)
# #
# # plot_r_tree(r_tree)
# #
# # nearest = r_tree.find_nearest_neighbor(search_point)
# # add_to_plot_geometry(nearest, 'green')
# # add_to_plot_geometry(search_point, 'yellow')
# #
# # # search_result = r_tree.search(search_box)
# # # add_to_plot_geometry(search_box, 'yellow')
# # # if search_result is not None:
# # #     for r in search_result:
# # #         add_to_plot_geometry(r, 'green')
# #
# # set_title('r_tree')
# # show_plot()
#
# # for polygon in polygons:
# #     add_to_plot_geometry(polygon, 'red')
# #     r_tree_q.insert(polygon)
# #
# # plot_r_tree(r_tree_q)
# # set_title('quadratic')
# # show_plot()
#
#
# # add_to_plot_geometry(search_box, 'yellow')
# #
# # # show_plot()
# #
# # # search_result = r_tree.search(search_box)
# # search_result = r_plus_tree.search(search_box)
# #
# # print(search_result)
# #
# # if search_result is not None:
# #     # plot_r_tree(r_tree)
# #     # plot_r_plus_tree(r_plus_tree)
# #     # add_to_plot_geometry(search_box, 'yellow')
# #
# #     for r in search_result:
# #         add_to_plot_geometry(r, 'green')
# #
# #     show_plot()
