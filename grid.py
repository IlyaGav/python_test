import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.pyplot as plt


class SpatialGrid:
    def __init__(self, base_grid_size, max_cells, levels):
        self.base_grid_size = base_grid_size
        self.max_cells = max_cells
        self.levels = levels
        self.grids = [{} for _ in range(levels + 1)]

    def calculate_level(self, width, height):
        max_dimension = max(width, height)
        level = 0
        while max_dimension > self.base_grid_size and level < self.levels:
            max_dimension /= 2
            level += 1
        return min(level, self.levels)

    def add_object(self, obj):
        grid_size = self.base_grid_size

        for level in range(self.levels):
            grid_x1, grid_y1 = obj['x'] // grid_size, obj['y'] // grid_size
            grid_x2, grid_y2 = (obj['x'] + obj['width']) // grid_size, (obj['y'] + obj['height']) // grid_size

            for x in range(grid_x1, grid_x2 + 1):
                for y in range(grid_y1, grid_y2 + 1):
                    cell = (x, y)

                    if cell not in self.grids[level]:
                        self.grids[level][cell] = []

                    self.grids[level][cell].append(obj)

            grid_size *= 2  # Увеличиваем размер сетки на следующем уровне вдвое

            # Если превышено максимальное количество ячеек, прекращаем добавление на более верхних уровнях
            if len(self.grids[level]) > self.max_cells:
                break

    def get_objects_in_cell(self, level, x, y):
        cell = (x, y)
        return self.grids[level].get(cell, [])

def find_nearest_neighbor_point(spatial_grid, query_point):
    min_distance = float('inf')
    nearest_neighbor = None

    query_x, query_y = query_point['x'], query_point['y']
    query_level = spatial_grid.calculate_level(1, 1)  # Размер точки равен 1x1

    for level in range(spatial_grid.levels):
        grid_size = spatial_grid.base_grid_size * (2 ** (query_level - level))

        grid_x, grid_y = int(query_x // grid_size), int(query_y // grid_size)

        neighbors = spatial_grid.get_objects_in_cell(level, grid_x, grid_y)

        for neighbor in neighbors:
            distance = ((neighbor['x'] - query_x) ** 2 + (neighbor['y'] - query_y) ** 2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                nearest_neighbor = neighbor

    return nearest_neighbor


def visualize_grid(spatial_grid, query_point=None, nearest_neighbor=None):
    fig, ax = plt.subplots(figsize=(11, 8))

    num_levels = spatial_grid.levels
    level_colors = cm.rainbow_r([i/num_levels for i in range(num_levels + 1)])

    added_legend_entries = set()  # Множество для отслеживания добавленных записей в легенду

    # Находим максимальный размер сетки (размер верхнего уровня)
    max_grid_size = spatial_grid.base_grid_size * (2 ** spatial_grid.levels) // 2 + 5

    for level in range(spatial_grid.levels):
        grid_size = spatial_grid.base_grid_size * (2 ** level)
        grid_legend_entry = f'Grid Level {level}'

        if grid_legend_entry not in added_legend_entries:
            rect = patches.Rectangle((0, 0), 0, 0, linewidth=1, edgecolor=level_colors[level], facecolor='none', alpha=0.5, label=grid_legend_entry)
            ax.add_patch(rect)
            added_legend_entries.add(grid_legend_entry)

        for cell, objects in spatial_grid.grids[level].items():
            x, y = cell
            rect = patches.Rectangle((x * grid_size, y * grid_size), grid_size, grid_size, linewidth=1, edgecolor=level_colors[level], facecolor='none', alpha=0.5)
            ax.add_patch(rect)

            obj_legend_entry = f'Objects Level {level}'

            if obj_legend_entry not in added_legend_entries:
                rect = patches.Rectangle((0, 0), 0, 0, linewidth=1, edgecolor=level_colors[level], facecolor='none', alpha=0.8, label=obj_legend_entry)
                ax.add_patch(rect)
                added_legend_entries.add(obj_legend_entry)

            for obj in objects:
                rect = patches.Rectangle((obj['x'], obj['y']), obj['width'], obj['height'], linewidth=1, edgecolor=level_colors[level], facecolor='none', alpha=0.8)
                ax.add_patch(rect)

    if query_point:
        ax.plot(query_point['x'], query_point['y'], 'go', markersize=10, label='Query Point')

    if nearest_neighbor:
        x_center = nearest_neighbor['x'] + nearest_neighbor['width'] / 2
        y_center = nearest_neighbor['y'] + nearest_neighbor['height'] / 2

        # Рисуем крестик по диагонали внутри ближайшего соседа
        ax.plot([x_center - nearest_neighbor['width'] / 2, x_center + nearest_neighbor['width'] / 2],
                [y_center - nearest_neighbor['height'] / 2, y_center + nearest_neighbor['height'] / 2], color='k', linewidth=2)
        ax.plot([x_center + nearest_neighbor['width'] / 2, x_center - nearest_neighbor['width'] / 2],
                [y_center - nearest_neighbor['height'] / 2, y_center + nearest_neighbor['height'] / 2], color='k', linewidth=2)

    ax.set_xlim(0, max_grid_size)
    ax.set_ylim(0, max_grid_size)
    ax.set_aspect('equal', adjustable='box')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()
