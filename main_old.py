# import pickle
# import random
# import time
# import json
# from typing import List
#
# import shapely
# from matplotlib import pyplot as plt
# from shapely import unary_union
# from shapely.geometry import Point, LineString, Polygon
#
# from fixed_grid import build_fixed_grid, plot_fixed_grid, fixed_grid_find_nearest_neighbor
# from fixed_grid_point import build_fixed_grid_point, plot_fixed_grid_point, fixed_grid_point_find_nearest_neighbor
# from hierarchical_grid import hierarchical_grid_find_nearest_neighbor
# from kd_tree import build_kd_tree, kd_tree_find_nearest_neighbor, plot_kd_tree, kd_tree_benchmark_build, \
#     kd_tree_benchmark_find_nearest_neighbor, find_nearest_neighbor_2, build_kd_tree_2, kd_tree_benchmark_build_2
# from kd_tree_point import build_kd_tree_point, plot_kd_tree_point, kd_tree_point_find_nearest_neighbor
# from quad_tree_point import build_quad_tree_point, plot_quad_tree_point, quad_tree_point_find_nearest_neighbor
# from quad_tree import build_quad_tree, quad_tree_find_nearest_neighbor, plot_quad_tree, quad_tree_benchmark_build, \
#     quad_tree_benchmark_find_nearest_neighbor
#
# from shapely_plot import add_to_plot_geometry, show_plot, set_title
#
# import numpy as np
#
#
# def generate_random_point(min_x_coord=0, min_y_coord=0, max_x_coord=100, max_y_coord=100, ):
#     return Point(random.uniform(min_x_coord, max_x_coord), random.uniform(min_y_coord, max_y_coord))
#
#
# def generate_random_line(num_points=2, min_coord=0, max_coord=100):
#     points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
#     return LineString([(point.x, point.y) for point in points])
#
#
# def generate_random_polygon(num_points=3, min_coord=0, max_coord=100):
#     points = [generate_random_point(min_coord, max_coord) for _ in range(num_points)]
#     return Polygon([(point.x, point.y) for point in points])
#
#
# def generate_random_box_2(min_coord=0, max_coord=10, max_width=2, max_height=2):
#     x1 = random.uniform(min_coord, max_coord)
#     y1 = random.uniform(min_coord, max_coord)
#     x2 = random.uniform(x1, max_coord)
#     y2 = random.uniform(y1, max_coord)
#
#     return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
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
# def generate_box(xmin, ymin, xmax, ymax):
#     return Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])
#
#
# def benchmark():
#     # min_x, min_y, max_x, max_y = 0, 0, 100_000, 100_000
#     #
#     # min_length, max_length = 1, 15
#     # count_data = 100_000
#     #
#     # print('generate data...')
#
#     # boundary = shapely.box(min_x, min_y, max_x, max_y)
#     # data_set = [generate_random_box(min_x, min_y, max_x, max_y, min_length, max_length) for _ in range(count_data)]
#
#     # print('building...')
#     #
#     # data_set = get_buildings('C:\\Users\\IlyaGav\\OneDrive\\Рабочий стол\\CFO_1.3kk.json')
#     #
#     #
#     # with open('data_set.pkl', 'wb') as file:
#     #     pickle.dump(data_set, file)
#
#     print('Загрузка экземпляра из файла...')
#
#     # Загрузка экземпляра из файла
#     with open('data_set.pkl', 'rb') as file:
#         data_set = pickle.load(file)
#
#     boundary = Polygon(unary_union([*data_set]).envelope)
#     min_x, min_y, max_x, max_y = boundary.bounds
#
#     # print('start build benchmark')
#     #
#     # print()
#     #
#     # print('kd_tree_build', kd_tree_benchmark_build(boundary, data_set))
#     # print('kd_tree_build_2', kd_tree_benchmark_build_2(boundary, data_set))
#     # print('quad_tree_build', quad_tree_benchmark_build(boundary, data_set))
#     # print('hierarchical_grid_build', hierarchical_grid_benchmark_build(boundary, data_set))
#     #
#     # print()
#     # print()
#
#     print()
#     print('start nearest_neighbor benchmark')
#     print()
#
#     stopwatch = StopWatch()
#
#     # stopwatch.start()
#     # kd_tree = build_kd_tree(boundary, data_set)
#     # stopwatch.stop()
#     # print('kd_tree_build', stopwatch.elapsed())
#     #
#     # stopwatch.start()
#     # quad_tree = build_quad_tree(boundary, data_set)
#     # stopwatch.stop()
#     # print('quad_tree_build', stopwatch.elapsed())
#     #
#     # stopwatch.start()
#     # hierarchical_grid = build_hierarchical_grid(boundary, data_set)
#     # stopwatch.stop()
#     # print('hierarchical_grid_build', stopwatch.elapsed())
#     #
#     # print()
#
#     # print('Сохранение экземпляра в файл...', stopwatch.elapsed())
#     # # Сохранение экземпляра в файл
#     # with open('kd_tree.pkl', 'wb') as file:
#     #     pickle.dump(kd_tree, file)
#     #
#     # with open('quad_tree.pkl', 'wb') as file:
#     #     pickle.dump(quad_tree, file)
#     #
#     # with open('hierarchical_grid.pkl', 'wb') as file:
#     #     pickle.dump(hierarchical_grid, file)
#
#     print('Загрузка экземпляра из файла...')
#
#     # Загрузка экземпляра из файла
#     with open('kd_tree.pkl', 'rb') as file:
#         kd_tree = pickle.load(file)
#
#     with open('quad_tree.pkl', 'rb') as file:
#         quad_tree = pickle.load(file)
#
#     with open('hierarchical_grid.pkl', 'rb') as file:
#         hierarchical_grid = pickle.load(file)
#
#     query_points = [generate_random_point(min_x, min_y, max_x, max_y) for _ in range(10)]
#
#     [() for query_point in query_points]
#
#     for _ in range(10):
#         query_point = generate_random_point(min_x, min_y, max_x, max_y)
#
#         print(query_point)
#
#         stopwatch.start()
#         n = kd_tree_find_nearest_neighbor(kd_tree, query_point)
#         stopwatch.stop()
#         print('kd_tree_nearest_neighbor', stopwatch.elapsed())
#         print(n)
#
#         stopwatch.start()
#         n = quad_tree_find_nearest_neighbor(quad_tree, query_point)
#         stopwatch.stop()
#         print('quad_tree_nearest_neighbor', stopwatch.elapsed())
#         print(n)
#
#         stopwatch.start()
#         n = hierarchical_grid_find_nearest_neighbor(hierarchical_grid, query_point)
#         stopwatch.stop()
#         print('hierarchical_grid_nearest_neighbor', stopwatch.elapsed())
#         print(n)
#
#         print()
#         print()
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
# def get_buildings(path):
#     # Открываем файл на чтение
#     with open(path, 'r', encoding='utf-8') as file:
#         # Загружаем данные из JSON файла
#         data = json.load(file)
#
#     buildings: List[List[float]] = [building["geometry"]["coordinates"][0][0] for building in data["features"]]
#
#     polygons: List[Polygon] = []
#
#     for building in buildings:
#         polygons.append(Polygon(building))
#
#     return polygons
#
#
# seed = int(time.time())
# # seed = 1705736611
# # seed = 1705687997
# random.seed(seed)
# print(f"random seed {seed}")
#
# boundary = shapely.box(0, 0, 100, 100)
# minx, miny, maxx, maxy = boundary.bounds
# # points = [generate_random_point(minx, miny, maxx, maxy) for _ in range(50)]
# # polygons = [generate_random_box(minx, miny, maxx, maxy) for _ in range(50)]
# # query_point = generate_random_point(minx, miny, maxx, maxy)
# #
# # kd = build_kd_tree(boundary, polygons)
# # quad = build_quad_tree(boundary, polygons, 1)
# # grid = build_fixed_grid(boundary, polygons, 4)
# #
# # nn = kd_tree_find_nearest_neighbor(kd, query_point)
# # plot_kd_tree(kd)
# # add_to_plot_geometry(nn, 'pink')
# # add_to_plot_geometry(query_point, 'red')
# # show_plot()
# #
# #
# # nn = quad_tree_find_nearest_neighbor(quad, query_point)
# # plot_quad_tree(quad)
# # add_to_plot_geometry(nn, 'pink')
# # add_to_plot_geometry(query_point, 'red')
# # show_plot()
# #
# # nn = fixed_grid_find_nearest_neighbor(grid, query_point)
# # plot_fixed_grid(grid)
# # add_to_plot_geometry(nn, 'pink')
# # add_to_plot_geometry(query_point, 'red')
# # show_plot()
#
# dates = [100, 1000, 10_000, 50_000, 100_000, 250_000, 500_000, 750_000, 1_000_000]
# # dates = [100, 1000, 10_000, 50_000, 100_000]
#
# # kd_tree_build = []
# # quad_tree_build = []
# # fixed_grid_build = []
# #
# # kd_tree_find = []
# # quad_tree_find = []
# # fixed_grid_find = []
# #
# # stopwatch = StopWatch()
# #
# # for count in dates:
# #     # points = [generate_random_point(minx, miny, maxx, maxy) for _ in range(count)]
# #     polygons = [generate_random_box(minx, miny, maxx, maxy, 0.1, 15) for _ in range(count)]
# #     query_points = [generate_random_point(minx, miny, maxx, maxy) for _ in range(100)]
# #
# #     stopwatch.start()
# #     kd_tree = build_kd_tree(boundary, polygons)
# #     stopwatch.stop()
# #     kd_tree_build.append(stopwatch.elapsed())
# #
# #     times = []
# #     for query_point in query_points:
# #         stopwatch.start()
# #         kd_tree_find_nearest_neighbor(kd_tree, query_point)
# #         stopwatch.stop()
# #         times.append(stopwatch.elapsed())
# #     kd_tree_find.append(np.mean(times))
# #
# #     stopwatch.start()
# #     quad_tree = build_quad_tree(boundary, polygons, 16, 16)
# #     stopwatch.stop()
# #     quad_tree_build.append(stopwatch.elapsed())
# #
# #     times = []
# #     for query_point in query_points:
# #         stopwatch.start()
# #         quad_tree_find_nearest_neighbor(quad_tree, query_point)
# #         stopwatch.stop()
# #         times.append(stopwatch.elapsed())
# #     quad_tree_find.append(np.mean(times))
# #
# #     stopwatch.start()
# #     fixed_grid = build_fixed_grid(boundary, polygons, 64)
# #     stopwatch.stop()
# #     fixed_grid_build.append(stopwatch.elapsed())
# #
# #     times = []
# #     for query_point in query_points:
# #         stopwatch.start()
# #         fixed_grid_find_nearest_neighbor(fixed_grid, query_point)
# #         stopwatch.stop()
# #         times.append(stopwatch.elapsed())
# #     fixed_grid_find.append(np.mean(times))
# #
# #     print(kd_tree_build)
# #     print(quad_tree_build)
# #     print(fixed_grid_build)
# #     print()
# #     print(kd_tree_find)
# #     print(quad_tree_find)
# #     print(fixed_grid_find)
# #     print()
# #     print()
# #
#
# # Полигоны
# kd_tree_build = [0.011964559555053711, 0.10814642906188965, 1.0454990863800049, 5.394405841827393, 10.49711298942566, 32.44301748275757, 66.53246188163757, 84.48804998397827, 111.60792779922485]
# quad_tree_build = [0.015951156616210938, 0.12306404113769531, 1.031182050704956, 4.4889326095581055, 10.916736125946045, 29.01885414123535, 55.14793801307678, 67.50932717323303, 89.40132260322571]
# fixed_grid_build = [0.0019931793212890625, 0.01494908332824707, 0.14161372184753418, 0.7264261245727539, 1.799638032913208, 4.723118782043457, 7.757278203964233, 12.115179061889648, 19.90386414527893]
#
# # Точки
# # kd_tree_build = [0.006976604461669922, 0.10018730163574219, 1.163599967956543, 6.696069717407227, 13.952640771865845, 38.041664838790894, 81.58504915237427, 126.0725245475769, 170.44739770889282]
# # quad_tree_build = [0.0029900074005126953, 0.056308746337890625, 0.820014476776123, 4.652554035186768, 10.599869966506958, 30.13180136680603, 60.431243658065796, 92.94860506057739, 129.07666420936584]
# # fixed_grid_build = [0.0009968280792236328, 0.007972955703735352, 0.08200621604919434, 0.3845491409301758, 0.7721502780914307, 1.9177398681640625, 3.8306186199188232, 6.025275468826294, 7.956989288330078]
#
#
# plt.plot(dates, kd_tree_build, color='blue',  label='K-D дерево')
# plt.plot(dates, quad_tree_build, color='green',  label='Quadtree')
# plt.plot(dates, fixed_grid_build, color='red',  label='Фиксированная сетка')
#
# plt.title('Построение индекса')
#
# plt.legend()
#
# plt.xlabel('Количество данных')
# plt.ylabel('Время, сек')
#
# plt.show()
#
# # Полигоны
# kd_tree_find = [0.0002092456817626953, 0.0013508152961730956, 0.013233613967895509, 0.06753464460372925, 0.15611129760742187, 0.4094049263000488, 0.8556482982635498, 1.0401754188537597, 1.381488242149353]
# quad_tree_find = [0.0002492523193359375, 0.001415863037109375, 0.013847110271453857, 0.06786878108978271, 0.16084574937820434, 0.4188502788543701, 0.7202358508110046, 1.0385437178611756, 1.3227689266204834]
# fixed_grid_find = [8.494615554809571e-05, 0.0005481791496276856, 0.005282940864562988, 0.025642471313476564, 0.06187274217605591, 0.17365256547927857, 0.28872740983963013, 0.4132793235778809, 0.5743201851844788]
#
# # Точки
# # kd_tree_find = [0.0002544140815734863, 0.000374910831451416, 0.00040863275527954103, 0.00043383121490478513, 0.0004834628105163574, 0.0005095958709716797, 0.0005333065986633301, 0.0005681824684143067, 0.0005758190155029297]
# # quad_tree_find = [0.00013953447341918945, 0.00020930051803588867, 0.00029072761535644533, 0.0002989983558654785, 0.0003089690208435059, 0.00033886432647705077, 0.000361781120300293, 0.00039866447448730466, 0.00041788816452026367]
# # fixed_grid_find = [2.9900074005126952e-05, 2.990245819091797e-05, 0.00019937992095947265, 0.0008719849586486816, 0.0016723394393920899, 0.004381425380706787, 0.00865976095199585, 0.01317065954208374, 0.01764293909072876]
#
# # kd_tree_find = [0.0002544140815734863, 0.000374910831451416, 0.00040863275527954103, 0.00043383121490478513, 0.0004834628105163574, 0.0005095958709716797, 0.0005333065986633301, 0.0005681824684143067, 0.0005758190155029297]
# # quad_tree_find = [0.00013953447341918945, 0.00020930051803588867, 0.00029072761535644533, 0.0002989983558654785, 0.0003089690208435059, 0.00033886432647705077, 0.000361781120300293, 0.00039866447448730466, 0.00041788816452026367]
# # fixed_grid_find = [2.9900074005126952e-05, 2.990245819091797e-05, 0.00019937992095947265, 0.0008719849586486816, 0.0016723394393920899, 0.004381425380706787, 0.00865976095199585, 0.01317065954208374, 0.01764293909072876]
#
# plt.plot(dates, kd_tree_find, color='blue',  label='K-D дерево')
# plt.plot(dates, quad_tree_find, color='green',  label='Quadtree')
# plt.plot(dates, fixed_grid_find, color='red',  label='Фиксированная сетка')
#
# plt.title('Поиск ближайшего соседа')
#
# plt.legend()
#
# plt.xlabel('Количество данных')
# plt.ylabel('Время, сек')
#
# plt.show()
#
# # add_to_plot_geometry(nearest_neighbor, 'red')
# # add_to_plot_geometry(point, 'black')
# #
# # show_plot()
#
# # shapes = get_buildings()
# # print('loaded data')
# # boundary = Polygon(unary_union([*shapes]).envelope)
# #
# # for shape in shapes:
# #     add_to_plot_geometry(shape, 'orange')
# #
# # add_to_plot_geometry(boundary, 'black')
# #
# # show_plot()
#
# # minx, miny, maxx, maxy = boundary.bounds
# # point = generate_random_point(minx, miny, maxx, maxy)
# #
# # kd_tree = build_kd_tree(boundary, shapes)
# # plot_kd_tree(kd_tree)
# # nearest_neighbor = kd_tree_find_nearest_neighbor(kd_tree, point)
# # add_to_plot_geometry(nearest_neighbor, 'red')
# # add_to_plot_geometry(point)
# # set_title('kd_tree')
# # show_plot()
#
# # kd_tree_2 = build_kd_tree_2(boundary, shapes, 8, 8)
# # plot_kd_tree(kd_tree_2)
# # nearest_neighbor = kd_tree_find_nearest_neighbor(kd_tree_2, point)
# # add_to_plot_geometry(nearest_neighbor, 'red')
# # add_to_plot_geometry(point)
# # set_title('kd_tree_2')
# # show_plot()
#
# # quad_tree = build_quad_tree(boundary, shapes, 1)
# # plot_quad_tree(quad_tree)
# # nearest_neighbor = quad_tree_find_nearest_neighbor(quad_tree, point)
# # add_to_plot_geometry(nearest_neighbor, 'red')
# # add_to_plot_geometry(point)
# # set_title('quad_tree')
# # show_plot()
#
# #
# # grid = build_hierarchical_grid(boundary, shapes)
# # plot_hierarchical_grid(grid)
# # nearest_neighbor = hierarchical_grid_find_nearest_neighbor(grid, point)
# # add_to_plot_geometry(nearest_neighbor, 'red')
# # add_to_plot_geometry(point)
# # set_title('grid')
# # show_plot()
#
# # grid_fixed = build_fixed_grid(boundary, shapes, 4)
# #
# # plot_fixed_grid(grid_fixed)
#
# # nearest_neighbor = fixed_grid_find_nearest_neighbor(grid_fixed, point)
#
# # if nearest_neighbor is not None:
# #     add_to_plot_geometry(nearest_neighbor, 'red')
# # else:
# #     print('No nearest neighbor')
# #
# # add_to_plot_geometry(point)
# #
# # set_title('fixed_grid')
#
# # show_plot()
#
# # benchmark()
