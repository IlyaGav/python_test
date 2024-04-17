import random
import time

import shapely
from shapely import Point, Polygon

from r_plus_tree import RPlusTree, plot_r_plus_tree
from r_tree import RTree, plot_r_tree
from shapely_plot import add_to_plot_geometry, show_plot, set_title

# seed = int(time.time())
seed = 1713392961
random.seed(seed)
print(f"random seed {seed}")


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
polygons = [generate_random_box(minx, miny, maxx, maxy) for _ in range(20)]
# search_box = generate_random_box(minx + 20, miny + 20, maxx, maxy)
search_box = shapely.box(20, 20, 80, 80)

# r_tree = RTree(4)
r_plus_tree = RPlusTree(4)

# for i, polygon in enumerate(polygons):
#
#     # r_tree.insert(polygon)
#     r_plus_tree.insert(polygon)
#
#     # plot_r_tree(r_tree)
#     plot_r_plus_tree(r_plus_tree)
#
#     for p in polygons[0:i + 1]:
#         add_to_plot_geometry(p, 'red')
#
#     set_title(i)
#     show_plot()

for polygon in polygons:
    add_to_plot_geometry(polygon, 'red')
    # r_tree.insert(polygon)
    r_plus_tree.insert(polygon)

# plot_r_tree(r_tree)
plot_r_plus_tree(r_plus_tree)

add_to_plot_geometry(search_box, 'yellow')

# show_plot()

# search_result = r_tree.search(search_box)
search_result = r_plus_tree.search(search_box)

print(search_result)

if search_result is not None:
    # plot_r_tree(r_tree)
    # plot_r_plus_tree(r_plus_tree)
    # add_to_plot_geometry(search_box, 'yellow')

    for r in search_result:
        add_to_plot_geometry(r, 'green')

    show_plot()
