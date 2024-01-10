import shapely
from matplotlib import pyplot as plt
from matplotlib.typing import ColorType
from shapely import Point, LineString, Polygon, MultiPoint


def add_to_plot_geometry(geometry: shapely.Geometry, color: ColorType = None):
    """
    Рисует геометрические объекты из библиотеки Shapely на одном графике.
    """
    if isinstance(geometry, Point):
        x, y = geometry.x, geometry.y
        plt.plot(x, y, 'o', color=color if color is not None else 'red', label='Point')

    elif isinstance(geometry, LineString):
        x, y = geometry.xy
        plt.plot(x, y, color=color if color is not None else 'blue', label='LineString')

    elif isinstance(geometry, Polygon):
        x, y = geometry.exterior.xy
        plt.plot(x, y, color=color if color is not None else 'green', label='Polygon Exterior')
        for interior in geometry.interiors:
            x, y = interior.xy
            plt.plot(x, y, color=color if color is not None else 'orange', label='Polygon Interior')

    elif isinstance(geometry, MultiPoint):
        for point in geometry.geoms:
            x, y = point.x, point.y
            plt.plot(x, y, 'o', color=color if color is not None else 'red', label='MultiPoint')
    else:
        raise ValueError("Unsupported Shapely geometry type")


def show_plot():
    plt.show()
