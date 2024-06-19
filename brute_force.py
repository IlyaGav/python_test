from typing import List

from shapely import Point, Geometry

from common import Entry, get_nearest, geometry_to_box, intersection


class BruteForce():
    def __init__(self):
        self.entries: List[Entry] = []

    def insert(self, entry: Entry):
        self.entries.append(entry)

    def find_nearest_neighbor(self, point: Point):
        nearest, distance = get_nearest(self.entries, point)
        return nearest

    def search(self, search: Geometry):
        search_box = geometry_to_box(search)

        candidates = list(filter(lambda e: intersection(e, search_box), self.entries))
        shapes = list(map(lambda e: e.shape, set(candidates)))

        return list(filter(lambda s: s.intersects(search), shapes))