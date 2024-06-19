# import pickle
# import random
# import time
# import json
# from typing import List
#
# import shapely
# from matplotlib import pyplot as plt
# from shapely.geometry import Point, LineString, Polygon
#
# from fixed_grid import build_fixed_grid, fixed_grid_find_nearest_neighbor
# from fixed_grid_point import build_fixed_grid_point, fixed_grid_point_find_nearest_neighbor
# from kd_tree import build_kd_tree, kd_tree_find_nearest_neighbor
# from kd_tree_point import build_kd_tree_point, kd_tree_point_find_nearest_neighbor
# from quad_tree import build_quad_tree, quad_tree_find_nearest_neighbor
# from quad_tree_point import build_quad_tree_point, quad_tree_point_find_nearest_neighbor
# from r_plus_tree import build_r_plus_tree
#
# import numpy as np
#
# from r_tree import build_r_tree
#
#
# def generate_random_point(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, ):
#     return Point(random.uniform(min_x_coord, max_x_coord), random.uniform(min_y_coord, max_y_coord))
#
#
# class StopWatch(object):
#
#     def __init__(self):
#         self.elapsed_time = None
#         self.start_time = None
#
#     def start(self):
#         self.start_time = time.time()
#         self.elapsed_time = None
#
#     def stop(self):
#         self.elapsed_time = time.time() - self.start_time
#         return self.elapsed_time
#
#     def elapsed(self):
#         return self.elapsed_time
#
#
# seed = int(time.time())
# # seed = 1713482055
# random.seed(seed)
# print(f"random seed {seed}")
#
# boundary = shapely.box(0, 0, 10, 10)
# minx, miny, maxx, maxy = boundary.bounds
#
# max_node_capacity = 15
#
# r_tree_l_query = -1
# r_tree_q_query = -1
# kd_tree_query = -1
# quad_tree_query = -1
# grid_query = -1
#
# stopwatch = StopWatch()
#
# count = 10000
#
# points = [generate_random_point(minx, miny, maxx, maxy) for _ in range(count)]
# query_points = [generate_random_point(minx, miny, maxx, maxy) for _ in range(100)]
#
# print('building...')
#
# r_tree_l = build_r_tree(points, max_node_capacity, 'linear')
# print('build r_tree_l')
#
# r_tree_q = build_r_tree(points, max_node_capacity, 'quadratic')
# print('build r_tree_q')
#
# kd_tree = build_kd_tree_point(boundary, points)
# print('build kd_tree')
#
# quad_tree = build_quad_tree_point(boundary, points, max_node_capacity)
# print('build quad_tree')
#
# grid = build_fixed_grid_point(boundary, points, 100)
# print('build grid')
#
# print('querying')
#
# times = []
# for query_point in query_points:
#     stopwatch.start()
#     r_tree_l.find_nearest_neighbor(query_point)
#     stopwatch.stop()
#     times.append(stopwatch.elapsed())
#
# r_tree_l_query = np.mean(times)
# print('r_tree_l_query', r_tree_l_query)
#
# times = []
# for query_point in query_points:
#     stopwatch.start()
#     r_tree_q.find_nearest_neighbor(query_point)
#     stopwatch.stop()
#     times.append(stopwatch.elapsed())
#
# r_tree_q_query = np.mean(times)
# print('r_tree_q_query', r_tree_q_query)
#
# times = []
# for query_point in query_points:
#     stopwatch.start()
#     kd_tree_point_find_nearest_neighbor(kd_tree, query_point)
#     stopwatch.stop()
#     times.append(stopwatch.elapsed())
#
# kd_tree_query = np.mean(times)
# print('kd_tree_query', kd_tree_query)
#
# times = []
# for query_point in query_points:
#     stopwatch.start()
#     quad_tree_point_find_nearest_neighbor(quad_tree, query_point)
#     stopwatch.stop()
#     times.append(stopwatch.elapsed())
#
# quad_tree_query = np.mean(times)
# print('quad_tree_query', quad_tree_query)
#
# times = []
# for query_point in query_points:
#     stopwatch.start()
#     fixed_grid_point_find_nearest_neighbor(grid, query_point)
#     stopwatch.stop()
#     times.append(stopwatch.elapsed())
#
# grid_query = np.mean(times)
# print('grid_query', grid_query)
#
# print('complete')
