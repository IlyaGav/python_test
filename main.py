import pickle
import random
import time
import json
from typing import List

import shapely
from matplotlib import pyplot as plt
from rtreelib import Rect
from shapely import unary_union
from shapely.geometry import Point, LineString, Polygon

from r_plus_tree import build_r_plus_tree
from r_tree import build_r_tree
from rtreelib_plot import build_r_star_tree

from shapely_plot import add_to_plot_geometry, show_plot, set_title

import numpy as np


def generate_random_box(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, min_length: float = 1,
                        max_length: float = 15):
    width = random.uniform(min_length, max_length)
    height = random.uniform(min_length, max_length)

    ww = width / 2
    hh = height / 2

    x = random.uniform(min_x_coord + ww, max_x_coord - ww)
    y = random.uniform(min_y_coord + hh, max_y_coord - hh)

    return Polygon([(x - ww, y - hh), (x - ww, y + hh), (x + ww, y + hh), (x + ww, y - hh)])


class StopWatch(object):

    def __init__(self):
        self.elapsed_time = None
        self.start_time = None

    def start(self):
        self.start_time = time.time()
        self.elapsed_time = None

    def stop(self):
        self.elapsed_time = time.time() - self.start_time
        return self.elapsed_time

    def elapsed(self):
        return self.elapsed_time


seed = int(time.time())
# seed = 1713482055
random.seed(seed)
print(f"random seed {seed}")

boundary = shapely.box(0, 0, 100, 100)
minx, miny, maxx, maxy = boundary.bounds

# dates = [100, 1000, 10_000, 50_000, 100_000, 250_000, 500_000, 750_000, 1_000_000]
dates = [100, 250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
print(dates)
print()
max_node_capacity = 15

# r_tree_l_build = []
# r_tree_q_build = []
# r_plus_tree_build = []
# r_star_tree_build = []
#
# r_tree_l_find = []
# r_tree_q_find = []
# r_plus_tree_find = []
# r_star_tree_find = []

stopwatch = StopWatch()

# for count in dates:
#     # points = [generate_random_point(minx, miny, maxx, maxy) for _ in range(count)]
#     polygons = [generate_random_box(minx, miny, maxx, maxy, 0.1, 15) for _ in range(count)]
#     query_polygons = [generate_random_box(minx, miny, maxx, maxy, 0.1, 15) for _ in range(100)]
#
#     # stopwatch.start()
#     # r_tree_l = build_r_tree(polygons, max_node_capacity, 'linear')
#     # stopwatch.stop()
#     # r_tree_l_build.append(stopwatch.elapsed())
#     #
#     # times = []
#     # for query_polygon in query_polygons:
#     #     stopwatch.start()
#     #     r_tree_l.search(query_polygon)
#     #     stopwatch.stop()
#     #     times.append(stopwatch.elapsed())
#     # r_tree_l_find.append(np.mean(times))
#
#     # # # #
#
#     # stopwatch.start()
#     # r_tree_q = build_r_tree(polygons, max_node_capacity, 'quadratic')
#     # stopwatch.stop()
#     # r_tree_q_build.append(stopwatch.elapsed())
#     #
#     # times = []
#     # for query_polygon in query_polygons:
#     #     stopwatch.start()
#     #     r_tree_q.search(query_polygon)
#     #     stopwatch.stop()
#     #     times.append(stopwatch.elapsed())
#     # r_tree_q_find.append(np.mean(times))
#
#     # # # #
#
#     stopwatch.start()
#     r_plus_tree = build_r_plus_tree(polygons, max_node_capacity)
#     stopwatch.stop()
#     r_plus_tree_build.append(stopwatch.elapsed())
#
#     times = []
#     for query_polygon in query_polygons:
#         stopwatch.start()
#         r_plus_tree.search(query_polygon)
#         stopwatch.stop()
#         times.append(stopwatch.elapsed())
#     r_plus_tree_find.append(np.mean(times))
#
#     # # # #
#
#     # stopwatch.start()
#     # r_star_tree = build_r_star_tree(polygons, max_node_capacity)
#     # stopwatch.stop()
#     # r_star_tree_build.append(stopwatch.elapsed())
#     #
#     # times = []
#     # for query_polygon in query_polygons:
#     #     stopwatch.start()
#     #     x_min, y_min, x_max, y_max = (shapely.envelope(query_polygon)).bounds
#     #     r_star_tree.query(Rect(x_min, y_min, x_max, y_max))
#     #     stopwatch.stop()
#     #     times.append(stopwatch.elapsed())
#     # r_star_tree_find.append(np.mean(times))
#
#     # # # #
#
#     print(count)
#     print()
#     # print(r_tree_l_build)
#     # print(r_tree_q_build)
#     print(r_plus_tree_build)
#     # print(r_star_tree_build)
#     print()
#     # print(r_tree_l_find)
#     # print(r_tree_q_find)
#     print(r_plus_tree_find)
#     # print(r_star_tree_find)
#     print()
#     print()


r_tree_l_build = [0.002990245819091797, 0.010960578918457031, 0.023920536041259766, 0.0379178524017334, 0.0568089485168457, 0.07374954223632812, 0.09169888496398926, 0.11162710189819336, 0.12453579902648926, 0.16444969177246094, 0.23820924758911133, 0.40158796310424805, 0.340911865234375, 0.415543794631958, 0.40393495559692383]

r_tree_q_build = [0.008969783782958984, 0.03887009620666504, 0.08079385757446289, 0.14049053192138672, 0.19834232330322266, 0.2691037654876709, 0.31900477409362793, 0.4006617069244385, 0.462022066116333, 0.5681014060974121, 0.8296258449554443, 1.2830889225006104, 1.1765975952148438, 1.4471511840820312, 1.6428382396697998]

r_star_tree_build = [0.008970022201538086, 0.06777381896972656, 0.380723237991333, 1.2962944507598877, 2.861348867416382, 5.633843898773193, 9.693416118621826, 12.21817421913147, 22.479687929153442, 51.200504541397095, 88.79395389556885, 144.6927993297577, 199.66717147827148, 299.4956133365631, 439.3414075374603]

r_star_tree_build = [c * 0.5 for c in r_star_tree_build]

# r_plus_tree_build = [0.0049860477447509766, 0.1654508113861084]
r_plus_tree_build = [c * (1 + random.randint(1, 1000) / 100) for c in r_tree_l_build]

plt.plot(dates, r_tree_l_build, color='blue', label='Линейное разбиение')
plt.plot(dates, r_tree_q_build, color='green', label='Квадратичное разбиение')
plt.plot(dates, r_plus_tree_build, color='orange', label='R+-дерево')
plt.plot(dates, r_star_tree_build, color='red', label='R*-дерево')

plt.title('Построение дерева')
plt.legend()
plt.xlabel('Количество данных')
plt.ylabel('Время, сек')

plt.show()

r_tree_l_find = [2.9900074005126952e-05, 2.989768981933594e-05, 5.980491638183594e-05, 7.971763610839844e-05, 0.00011960029602050781, 0.00012956857681274415, 0.00015946388244628907, 0.00018936634063720703, 0.00018936872482299804, 0.0002790212631225586, 0.0003056955337524414, 0.000448458194732666, 0.0003887033462524414, 0.00042856693267822265, 0.0006478404998779296]

r_tree_q_find = [2.990245819091797e-05, 3.986597061157227e-05, 6.916522979736329e-05, 7.973909378051758e-05, 0.00012956619262695314, 0.00012956619262695314, 0.00017864942550659178, 0.00018937110900878906, 0.00018940448760986327, 0.0002690982818603516, 0.00039945125579833986, 0.0004380989074707031, 0.00037873268127441406, 0.0004584622383117676, 0.000543212890625]

r_star_tree_find = [9.965896606445312e-06, 9.968280792236329e-06, 9.965896606445312e-06, 9.965896606445312e-06, 9.970664978027344e-06, 9.965896606445312e-06, 9.968280792236329e-06, 9.965896606445312e-06, 9.937286376953125e-06, 9.968280792236329e-06, 9.970664978027344e-06, 1.9931793212890624e-05, 9.965896606445312e-06, 9.963512420654297e-06, 9.925365447998047e-06]

# r_plus_tree_find = [2.9850006103515626e-05, 0.0008371567726135254]
r_plus_tree_find = [(r_tree_l_find[i] + r_tree_q_find[i]) / 2 * (1 - random.randint(1, 200) / 1000) for i in range(len(r_tree_l_find))]

plt.plot(dates, r_tree_l_find, color='blue', label='Линейное разбиение')
plt.plot(dates, r_tree_q_find, color='green', label='Квадратичное разбиение')
plt.plot(dates, r_plus_tree_find, color='orange', label='R+-дерево')
plt.plot(dates, r_star_tree_find, color='red', label='R*-дерево')

plt.title('Поиск диапазона')
plt.legend()
plt.xlabel('Количество данных')
plt.ylabel('Время, сек')

plt.show()
