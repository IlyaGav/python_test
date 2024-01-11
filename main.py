import datetime
import random
import time

import shapely.geometry
from shapely import MultiPoint, unary_union
from shapely.affinity import scale
from shapely.geometry import Point, LineString, Polygon

from kd_tree import build_kd_tree, find_nearest_neighbor
from shapely_plot import add_to_plot_geometry, show_plot


def generate_random_point(min_coord=0, max_coord=10):
    return Point(random.uniform(min_coord, max_coord), random.uniform(min_coord, max_coord))


def generate_random_line(num_points=2, min_coord=0, max_coord=10):
    points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
    return LineString([(point.x, point.y) for point in points])


def generate_random_polygon(num_points=3, min_coord=0, max_coord=10):
    points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
    return Polygon([(point.x, point.y) for point in points])


def generate_random_box(min_coord=0, max_coord=10):
    x1 = random.uniform(min_coord, max_coord)
    y1 = random.uniform(min_coord, max_coord)
    x2 = random.uniform(x1, max_coord)
    y2 = random.uniform(y1, max_coord)

    return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])


seed = int(time.time())
# seed = 1704987030
random.seed(seed)
print(f"random seed {seed}")

shapes = [generate_random_box() for _ in range(15)]

point = generate_random_point()

rec = scale(unary_union([*shapes, point]).envelope, 1.2, 1.2, 1.2)
tree = build_kd_tree(rec, shapes)

# for shape in shapes:
#     add_to_plot_geometry(shape)
#
# add_to_plot_geometry(rec, 'black')
# add_to_plot_geometry(point)
#
# show_plot()


for shape in shapes:
    add_to_plot_geometry(shape)

add_to_plot_geometry(point)

try:
    nearest_neighbor = find_nearest_neighbor(tree, point)
    add_to_plot_geometry(nearest_neighbor, 'red')
except Exception as e:
    show_plot()
    raise e

show_plot()
