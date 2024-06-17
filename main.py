import random
import time

import shapely
from shapely import Point, Polygon

from common import Entry
from fixed_grid import FixedGrid, plot_fixed_grid
from kd_tree import KDTree, plot_kd_tree
from quad_tree import Quadtree, plot_quad_tree
from r_tree import RTree, plot_r_tree
from shapely_plot import add_to_plot_geometry, show_plot, set_title

seed = int(time.time())
# seed = 1718660781
# star
# seed = 1713477765

# TODO r_plus_tree
# seed = 1713477681
random.seed(seed)
print(f"random seed {seed}")

def generate_random_point(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, ):
    return Point(random.uniform(min_x_coord, max_x_coord), random.uniform(min_y_coord, max_y_coord))


def generate_random_box(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, min_length: float = 1,
                        max_length: float = 15):
    width = random.uniform(min_length, max_length)
    height = random.uniform(min_length, max_length)

    ww = width / 2
    hh = height / 2

    x = random.uniform(min_x_coord + ww, max_x_coord - ww)
    y = random.uniform(min_y_coord + hh, max_y_coord - hh)

    return Polygon([(x - ww, y - hh), (x - ww, y + hh), (x + ww, y + hh), (x + ww, y - hh)])


boundary = shapely.box(0, 0, 100, 100)
minx, miny, maxx, maxy = boundary.bounds
# polygons = [generate_random_box(minx, miny, maxx, maxy) for _ in range(50)]
# entries = list(Entry(p) for p in polygons)
points = [generate_random_point(minx, miny, maxx, maxy) for _ in range(10)]
entries = list(Entry(p) for p in points)

search_point = generate_random_point(minx, miny, maxx, maxy)
search_box = generate_random_box(minx + 20, miny + 20, maxx, maxy, 15, 30)

kd_tree = KDTree(boundary, 10, 10)
grid = FixedGrid(boundary, 10)
quad_tree = Quadtree(boundary, 10, 10)
r_tree = RTree(10, 'quadratic')

for entry in entries:
    add_to_plot_geometry(entry.shape, 'red')
    kd_tree.insert(entry)

plot_kd_tree(kd_tree)

nearest = kd_tree.find_nearest_neighbor(search_point)
add_to_plot_geometry(nearest, 'green')
add_to_plot_geometry(search_point, 'yellow')

# search_result = kd_tree.search(search_box)
# add_to_plot_geometry(search_box, 'yellow')
# if search_result is not None:
#     for r in search_result:
#         add_to_plot_geometry(r, 'green')

set_title('kd_tree')
show_plot()

for entry in entries:
    add_to_plot_geometry(entry.shape, 'red')
    grid.insert(entry)

plot_fixed_grid(grid)

nearest = grid.find_nearest_neighbor(search_point)
add_to_plot_geometry(nearest, 'green')
add_to_plot_geometry(search_point, 'yellow')

# search_result = grid.search(search_box)
# add_to_plot_geometry(search_box, 'yellow')
# if search_result is not None:
#     for r in search_result:
#         add_to_plot_geometry(r, 'green')

set_title('fixed_grid')
show_plot()
#
# for entry in entries:
#     add_to_plot_geometry(entry.shape, 'red')
#     quad_tree.insert(entry)
#
# plot_quad_tree(quad_tree)
#
# nearest = quad_tree.find_nearest_neighbor(search_point)
# add_to_plot_geometry(nearest, 'green')
# add_to_plot_geometry(search_point, 'yellow')
#
# # search_result = quad_tree.search(search_box)
# # add_to_plot_geometry(search_box, 'yellow')
# # if search_result is not None:
# #     for r in search_result:
# #         add_to_plot_geometry(r, 'green')
#
# set_title('quad_tree')
# show_plot()
#
# for entry in entries:
#     add_to_plot_geometry(entry.shape, 'red')
#     r_tree.insert(entry)
#
# plot_r_tree(r_tree)
#
# nearest = r_tree.find_nearest_neighbor(search_point)
# add_to_plot_geometry(nearest, 'green')
# add_to_plot_geometry(search_point, 'yellow')
#
# # search_result = r_tree.search(search_box)
# # add_to_plot_geometry(search_box, 'yellow')
# # if search_result is not None:
# #     for r in search_result:
# #         add_to_plot_geometry(r, 'green')
#
# set_title('r_tree')
# show_plot()

# for polygon in polygons:
#     add_to_plot_geometry(polygon, 'red')
#     r_tree_q.insert(polygon)
#
# plot_r_tree(r_tree_q)
# set_title('quadratic')
# show_plot()


# add_to_plot_geometry(search_box, 'yellow')
#
# # show_plot()
#
# # search_result = r_tree.search(search_box)
# search_result = r_plus_tree.search(search_box)
#
# print(search_result)
#
# if search_result is not None:
#     # plot_r_tree(r_tree)
#     # plot_r_plus_tree(r_plus_tree)
#     # add_to_plot_geometry(search_box, 'yellow')
#
#     for r in search_result:
#         add_to_plot_geometry(r, 'green')
#
#     show_plot()
