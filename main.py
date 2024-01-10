import random
from shapely.geometry import Point, LineString, Polygon

from shapely_plot import add_to_plot_geometry, show_plot


def is_left_of_line(geometry, line):
    """
    Проверяет, лежит ли геометрическая фигура слева относительно прямой.
    """
    # Получаем точку начала и конца прямой
    start_point, end_point = line.xy

    # Создаем вектор прямой
    line_vector = (end_point[0] - start_point[0], end_point[1] - start_point[1])

    # Создаем вектор от начала прямой до центральной точки фигуры
    if isinstance(geometry, Point):
        point_vector = (geometry.x - start_point[0], geometry.y - start_point[1])
    else:
        # Для линии или полигона берем центр масс
        point_vector = (geometry.centroid.x - start_point[0], geometry.centroid.y - start_point[1])

    # Вычисляем векторное произведение
    cross_product = line_vector[0] * point_vector[1] - line_vector[1] * point_vector[0]

    # Если векторное произведение положительно, то фигура лежит слева от прямой
    return cross_product > 0

def generate_random_point(min_coord=0, max_coord=10):
    """
    Генерирует случайную точку в прямоугольнике (min_coord, max_coord) x (min_coord, max_coord).
    """
    return Point(random.uniform(min_coord, max_coord), random.uniform(min_coord, max_coord))

def generate_random_line(num_points=2, min_coord=0, max_coord=10):
    """
    Генерирует случайную линию, соединяющую указанное количество случайных точек.
    """
    points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
    return LineString([(point.x, point.y) for point in points])

def generate_random_polygon(num_points=3, min_coord=0, max_coord=10):
    """
    Генерирует случайный полигон, соединяющий указанное количество случайных точек.
    """
    points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
    return Polygon([(point.x, point.y) for point in points])

# Пример использования
line = LineString([(5, 0), (5, 5)])

random_point = generate_random_point()
random_line = generate_random_line(num_points=3)
random_polygon = generate_random_polygon(num_points=4)

print("Точка левее прямой:", is_left_of_line(random_point, line))
print("Линия левее прямой:", is_left_of_line(random_line, line))
print("Полигон левее прямой:", is_left_of_line(random_polygon, line))

add_to_plot_geometry(line, 'red')
add_to_plot_geometry(line.envelope, 'blue')

show_plot()
# Находим медиану для списка фигур
# median_geometry = unary_union(geometries)
