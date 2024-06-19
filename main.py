import math
from typing import Dict, List
import json

import numpy as np
import shapely

from brute_force import BruteForce
from common import uniform_distribution, Entry, StopWatch, gaussian_distribution, generate_random_point, \
    generate_random_box, generate_random_size_box
from fixed_grid import FixedGrid
from kd_tree import KDTree
from quad_tree import Quadtree
from r_tree import RTree

import matplotlib.pyplot as plt

type = 'points'
# type = 'polygons'

times_building = 1
times_search_range = 100
times_search_nearest = 100

num_entries = 10_000
space_size = 10_000
kd_tree_node_capacity = 5
quad_tree_node_capacity = 5
r_tree_linear_node_capacity = 5
r_tree_quadratic_node_capacity = 5
kd_tree_max_depth = 14
quad_tree_max_depth = 14
grid_dimension_size = 10000

min_length_range = 1
max_length_range = 5

min_length_polygon = 1
max_length_polygon = 5

boundary = shapely.box(0, 0, space_size, space_size)

info = 'info'
count = 'count'
value = 'value'
uniform = 'uniform'
sparse = 'sparse'
tight = 'tight'

kd_tree_key = 'kd_tree'
quad_tree_key = 'quad_tree'
grid_key = 'grid'
r_tree_l_key = 'r_tree_l'
r_tree_q_key = 'r_tree_q'
brute_force_key = 'brute_force'

building_filename = f'results/building_{type}.json'
search_range_filename = f'results/search_range_{type}.json'
search_nearest_filename = f'results/search_nearest_{type}.json'


def generate_entries(distribution) -> List[Entry]:
    if type == 'points':
        points = []
        if distribution == uniform:
            points = uniform_distribution(space_size, num_entries, math.sqrt(space_size))
        elif distribution == sparse:
            points = uniform_distribution(space_size, int(math.sqrt(num_entries)), 4 * math.sqrt(space_size))
        elif distribution == tight:
            points = gaussian_distribution(space_size, 10 * num_entries, space_size / 2, space_size / 2, space_size / 5)

        return list(Entry(p) for p in points)

    if type == 'polygons':
        points = []
        if distribution == uniform:
            points = uniform_distribution(space_size, num_entries, math.sqrt(space_size))
        elif distribution == sparse:
            points = uniform_distribution(space_size, int(math.sqrt(num_entries)), 4 * math.sqrt(space_size))
        elif distribution == tight:
            points = gaussian_distribution(space_size, 10 * num_entries, space_size / 2, space_size / 2, space_size / 5)

        polygons = [generate_random_size_box(p.x, p.y, space_size, min_length_polygon, max_length_polygon) for p in
                    points]

        return list(Entry(p) for p in polygons)


def build_kd_tree(entries: List[Entry]):
    structure = KDTree(boundary, kd_tree_node_capacity, kd_tree_max_depth)
    for entry in entries:
        structure.insert(entry)
    return structure


def build_quad_tree(entries: List[Entry]):
    structure = Quadtree(boundary, quad_tree_node_capacity, quad_tree_max_depth)
    for entry in entries:
        structure.insert(entry)
    return structure


def build_fixed_grid(entries: List[Entry]):
    structure = FixedGrid(boundary, grid_dimension_size)
    for entry in entries:
        structure.insert(entry)
    return structure


def build_r_tree(entries: List[Entry], algorithm):
    structure = RTree(r_tree_linear_node_capacity, algorithm)
    for entry in entries:
        structure.insert(entry)
    return structure


def build_brute_force(entries: List[Entry]):
    structure = BruteForce()
    for entry in entries:
        structure.insert(entry)
    return structure


def building(new: bool = False):
    print('start building...')

    print()
    print('type:', type)
    if type == 'polygons':
        print('min_length_polygon:', min_length_polygon)
        print('max_length_polygon:', max_length_polygon)
    print('times:', times_building)
    print('grid_size:', space_size)
    print('num_entries:', num_entries)
    print('kd_tree_node_capacity:', kd_tree_node_capacity)
    print('kd_tree_max_depth:', kd_tree_max_depth)
    print('quad_tree_node_capacity:', quad_tree_node_capacity)
    print('quad_tree_max_depth:', quad_tree_max_depth)
    print('r_tree_linear_node_capacity:', r_tree_linear_node_capacity)
    print('r_tree_quadratic_node_capacity:', r_tree_quadratic_node_capacity)
    print('grid_dimension_size:', grid_dimension_size)
    print()

    if new:
        results = {
            info: {
                'type': type,

                'kd_tree_node_capacity': kd_tree_node_capacity,
                'quad_tree_node_capacity': quad_tree_node_capacity,
                'r_tree_linear_node_capacity': r_tree_linear_node_capacity,
                'r_tree_quadratic_node_capacity': r_tree_quadratic_node_capacity,

                'grid_dimension_size': grid_dimension_size,

                'kd_tree_max_depth': kd_tree_max_depth,
                'quad_tree_max_depth': quad_tree_max_depth,

                'space_size': space_size,
                'num_entries': num_entries,
            },
            uniform: {
                count: 0,
                value: {}
            },
            sparse: {
                count: 0,
                value: {}
            },
            tight: {
                count: 0,
                value: {}
            },
        }

        if type == 'polygons':
            results[info]['min_length_polygon'] = min_length_polygon
            results[info]['max_length_polygon'] = max_length_polygon
    else:
        with open(building_filename, 'r') as f:
            results = json.load(f)

    def building_iteration(entries: List[Entry]) -> Dict[str, float]:
        result = {}
        stopwatch = StopWatch()

        print('kd_tree building...')
        stopwatch.start()
        build_kd_tree(entries)
        result[kd_tree_key] = stopwatch.stop()
        print('kd_tree build', stopwatch.elapsed())
        print()

        print('quad_tree building...')
        stopwatch.start()
        build_quad_tree(entries)
        result[quad_tree_key] = stopwatch.stop()
        print('quad_tree build', stopwatch.elapsed())
        print()

        print('grid building...')
        stopwatch.start()
        build_fixed_grid(entries)
        result[grid_key] = stopwatch.stop()
        print('grid build', stopwatch.elapsed())
        print()

        print('r_tree_linear building...')
        stopwatch.start()
        build_r_tree(entries, 'linear')
        result[r_tree_l_key] = stopwatch.stop()
        print('r_tree_linear build', stopwatch.elapsed())
        print()

        print('r_tree_quadratic building...')
        stopwatch.start()
        build_r_tree(entries, 'quadratic')
        result[r_tree_q_key] = stopwatch.stop()
        print('r_tree_quadratic build', stopwatch.elapsed())
        print()

        print('brute_force building...')
        stopwatch.start()
        build_brute_force(entries)
        result[brute_force_key] = stopwatch.stop()
        print('brute_force build', stopwatch.elapsed())
        print()

        return result

    def launch(distribution):
        print(f'{distribution} distribution')
        for i in range(times_building - results[distribution][count]):
            print('#', i + 1)
            entries = generate_entries(distribution)
            print('count', len(entries))

            result = building_iteration(entries)
            print(result)
            calc_mean(distribution, results, result)

            save(results, building_filename)

        print(f'{distribution} distribution end')

    launch(uniform)
    launch(sparse)
    launch(tight)

    print()

    # def mean(distribution, structure):
    #     return np.mean([r[structure] for r in results_50_16[distribution]])
    #
    # data = {
    #     kd_tree_key: mean(uniform, kd_tree_key),
    #     quad_tree_key: mean(uniform, quad_tree_key),
    #     grid_key: mean(uniform, grid_key),
    #     r_tree_l_key: mean(uniform, r_tree_l_key),
    #     r_tree_q_key: mean(uniform, r_tree_q_key),
    # }
    #
    # print(data)
    #
    # plot(data)

    print('end building!')


def search_range(new: bool = False):
    print('start search range...')

    print()
    print('type:', type)
    if type == 'polygons':
        print('min_length_polygon:', min_length_polygon)
        print('max_length_polygon:', max_length_polygon)
    print('times:', times_search_range)
    print('grid_size:', space_size)
    print('num_entries:', num_entries)
    print('kd_tree_node_capacity:', kd_tree_node_capacity)
    print('kd_tree_max_depth:', kd_tree_max_depth)
    print('quad_tree_node_capacity:', quad_tree_node_capacity)
    print('quad_tree_max_depth:', quad_tree_max_depth)
    print('r_tree_linear_node_capacity:', r_tree_linear_node_capacity)
    print('r_tree_quadratic_node_capacity:', r_tree_quadratic_node_capacity)
    print('grid_dimension_size:', grid_dimension_size)
    print()

    if new:
        results = {
            info: {
                'type': type,
                'min_length_range': min_length_range,
                'max_length_range': max_length_range,

                'kd_tree_node_capacity': kd_tree_node_capacity,
                'quad_tree_node_capacity': quad_tree_node_capacity,
                'r_tree_linear_node_capacity': r_tree_linear_node_capacity,
                'r_tree_quadratic_node_capacity': r_tree_quadratic_node_capacity,

                'grid_dimension_size': grid_dimension_size,

                'kd_tree_max_depth': kd_tree_max_depth,
                'quad_tree_max_depth': quad_tree_max_depth,

                'space_size': space_size,
                'num_entries': num_entries,
            },
            uniform: {
                count: 0,
                value: {}
            },
            sparse: {
                count: 0,
                value: {}
            },
            tight: {
                count: 0,
                value: {}
            },
        }

        if type == 'polygons':
            results[info]['min_length_polygon'] = min_length_polygon
            results[info]['max_length_polygon'] = max_length_polygon
    else:
        with open(search_range_filename, 'r') as f:
            results = json.load(f)

    stopwatch = StopWatch()

    def launch(distribution):
        print(f'{distribution} distribution')

        times = times_search_range - results[distribution][count]

        if times == 0:
            return

        entries = generate_entries(distribution)
        print('count', len(entries))

        query_ranges = [generate_random_box(0, 0, space_size, space_size, min_length_range, max_length_range) for _ in
                        range(times)]

        result = {}

        def iteration(structure, query_ranges):
            query_result = []
            for query_range in query_ranges:
                stopwatch.start()
                structure.search(query_range)
                stopwatch.stop()
                query_result.append(stopwatch.elapsed())

            return np.mean(query_result)

        print('kd_tree building...')
        structure = build_kd_tree(entries)
        print('start kd_tree search range...')
        result[kd_tree_key] = iteration(structure, query_ranges)
        print(f'end kd_tree search range {result[kd_tree_key]}')
        print()

        print('quad_tree building...')
        structure = build_quad_tree(entries)
        print('start quad_tree search range...')
        result[quad_tree_key] = iteration(structure, query_ranges)
        print(f'end quad_tree search {result[quad_tree_key]}')
        print()

        print('fixed_grid building...')
        structure = build_fixed_grid(entries)
        print('start fixed_grid search range...')
        result[grid_key] = iteration(structure, query_ranges)
        print(f'end fixed_grid search range {result[grid_key]}')
        print()

        print('r_tree_linear building...')
        structure = build_r_tree(entries, 'linear')
        print('start r_tree_linear search range...')
        result[r_tree_l_key] = iteration(structure, query_ranges)
        print(f'end r_tree_linear search range {result[r_tree_l_key]}')
        print()

        print('r_tree_quadratic building...')
        structure = build_r_tree(entries, 'quadratic')
        print('start r_tree_quadratic search range...')
        result[r_tree_q_key] = iteration(structure, query_ranges)
        print(f'end r_tree_quadratic search range {result[r_tree_q_key]}')
        print()

        print('brute_force building...')
        structure = build_brute_force(entries)
        print('start brute_force search range...')
        result[brute_force_key] = iteration(structure, query_ranges)
        print(f'end brute_force search range {result[brute_force_key]}')
        print()

        curr_count = results[distribution][count]
        for (k, v) in result.items():
            curr_mean = results[distribution][value].get(k, None)
            if curr_mean is None:
                if curr_count > 1:
                    raise ValueError("Неверные данные")
                curr_mean = 0

            results[distribution][value][k] = (curr_count * curr_mean + times * v) / (curr_count + times)
        results[distribution][count] = (curr_count + times)

        save(results, search_range_filename)

        print(f'{distribution} distribution end')
        print()

    launch(uniform)
    launch(sparse)
    launch(tight)

    print('end search range!')


def search_nearest(new: bool = False):
    print('search_nearest search...')

    print()
    print('type:', type)
    if type == 'polygons':
        print('min_length_polygon:', min_length_polygon)
        print('max_length_polygon:', max_length_polygon)
    print('times:', times_search_nearest)
    print('grid_size:', space_size)
    print('num_entries:', num_entries)
    print('kd_tree_node_capacity:', kd_tree_node_capacity)
    print('kd_tree_max_depth:', kd_tree_max_depth)
    print('quad_tree_node_capacity:', quad_tree_node_capacity)
    print('quad_tree_max_depth:', quad_tree_max_depth)
    print('r_tree_linear_node_capacity:', r_tree_linear_node_capacity)
    print('r_tree_quadratic_node_capacity:', r_tree_quadratic_node_capacity)
    print('grid_dimension_size:', grid_dimension_size)
    print()

    if new:
        results = {
            info: {
                'type': type,

                'kd_tree_node_capacity': kd_tree_node_capacity,
                'quad_tree_node_capacity': quad_tree_node_capacity,
                'r_tree_linear_node_capacity': r_tree_linear_node_capacity,
                'r_tree_quadratic_node_capacity': r_tree_quadratic_node_capacity,

                'grid_dimension_size': grid_dimension_size,

                'kd_tree_max_depth': kd_tree_max_depth,
                'quad_tree_max_depth': quad_tree_max_depth,

                'space_size': space_size,
                'num_entries': num_entries,
            },
            uniform: {
                count: 0,
                value: {}
            },
            sparse: {
                count: 0,
                value: {}
            },
            tight: {
                count: 0,
                value: {}
            },
        }

        if type == 'polygons':
            results[info]['min_length_polygon'] = min_length_polygon
            results[info]['max_length_polygon'] = max_length_polygon
    else:
        with open(search_nearest_filename, 'r') as f:
            results = json.load(f)

    stopwatch = StopWatch()

    def launch(distribution):
        print(f'{distribution} distribution')

        times = times_search_nearest - results[distribution][count]

        if times == 0:
            return

        entries = generate_entries(distribution)
        print('count', len(entries))

        query_points = [generate_random_point(0, 0, space_size, space_size) for _ in range(times)]

        result = {}

        def iteration(structure, query_points):
            query_result = []
            for query_range in query_points:
                stopwatch.start()
                structure.find_nearest_neighbor(query_range)
                stopwatch.stop()
                query_result.append(stopwatch.elapsed())

            return np.mean(query_result)

        print('kd_tree building...')
        structure = build_kd_tree(entries)
        print('start kd_tree search nearest...')
        result[kd_tree_key] = iteration(structure, query_points)
        print(f'end kd_tree search nearest {result[kd_tree_key]}')
        print()

        print('quad_tree building...')
        structure = build_quad_tree(entries)
        print('start quad_tree search nearest...')
        result[quad_tree_key] = iteration(structure, query_points)
        print(f'end quad_tree search nearest {result[quad_tree_key]}')
        print()

        print('fixed_grid building...')
        structure = build_fixed_grid(entries)
        print('start fixed_grid search nearest...')
        result[grid_key] = iteration(structure, query_points)
        print(f'end fixed_grid search nearest {result[grid_key]}')
        print()

        print('r_tree_linear building...')
        structure = build_r_tree(entries, 'linear')
        print('start r_tree_linear search nearest...')
        result[r_tree_l_key] = iteration(structure, query_points)
        print(f'end r_tree_linear search nearest {result[r_tree_l_key]}')
        print()

        print('r_tree_quadratic building...')
        structure = build_r_tree(entries, 'quadratic')
        print('start r_tree_quadratic search nearest...')
        result[r_tree_q_key] = iteration(structure, query_points)
        print(f'end r_tree_quadratic search nearest {result[r_tree_q_key]}')
        print()

        print('brute_force building...')
        structure = build_brute_force(entries)
        print('start brute_force search nearest...')
        result[brute_force_key] = iteration(structure, query_points)
        print(f'end brute_force search nearest {result[brute_force_key]}')
        print()

        curr_count = results[distribution][count]
        for (k, v) in result.items():
            curr_mean = results[distribution][value].get(k, None)
            if curr_mean is None:
                if curr_count > 1:
                    raise ValueError("Неверные данные")
                curr_mean = 0

            results[distribution][value][k] = (curr_count * curr_mean + times * v) / (curr_count + times)
        results[distribution][count] = (curr_count + times)

        save(results, search_nearest_filename)

        print(f'{distribution} distribution end')
        print()

    launch(uniform)
    launch(sparse)
    launch(tight)

    print('end search!')


def plot(data: Dict[str, float]):
    labels = [i for (i, _) in enumerate(data.keys())]
    values = [*data.values()]

    # Список цветов для каждого столбца
    colors = ['yellow', 'blue', 'green', 'brown', 'orange']

    # Создание горизонтальной столбчатой диаграммы с разными цветами
    bars = plt.barh(labels, values, color=colors, edgecolor='black', linewidth=1.5)

    # Добавление значений на сами столбцы
    for (i, bar) in enumerate(bars):
        width = bar.get_width()
        plt.text(-10, bar.get_y() + bar.get_height() / 2, list(data.keys())[i], va='center', ha='left')

    # Добавление заголовка и меток осей
    plt.title('Горизонтальная столбчатая диаграмма')
    plt.xlabel('Значения')
    plt.ylabel('Категории')

    # Добавление сетки
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.gca().set_yticks([])

    # Отображение диаграммы
    plt.show()


def save(dict, filename):
    with open(filename, 'w') as f:
        json.dump(dict, f)


def calc_mean(distribution, results, result):
    c = results[distribution][count] + 1
    for (k, v) in result.items():
        mean = results[distribution][value].get(k, None)
        if mean is None:
            if c > 1:
                raise ValueError("Неверные данные")
            mean = 0
        results[distribution][value][k] = mean + (v - mean) / c

    results[distribution][count] = c

# building(True)

search_range(True)

search_nearest(True)
