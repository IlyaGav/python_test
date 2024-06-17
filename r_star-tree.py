# from __future__ import annotations
#
# import math
# from typing import List, Optional, Dict, Tuple, Iterable, Union, Callable, Any
#
# import shapely
# from shapely import Geometry, Polygon
#
# EPSILON = 1e-5
#
#
# class BoundaryBox:
#     def __init__(self, x_min, y_min, x_max, y_max):
#         self.x_min = x_min
#         self.y_min = y_min
#         self.x_max = x_max
#         self.y_max = y_max
#
#     def area(self) -> float:
#         return (self.x_max - self.x_min) * (self.y_max - self.y_min)
#
#     def perimeter(self) -> float:
#         return 2 * ((self.x_max - self.x_min) + (self.y_max - self.y_min))
#
#     def centroid(self) -> (float, float):
#         cx = (self.x_min + self.x_max) / 2
#         cy = (self.y_min + self.y_max) / 2
#         return cx, cy
#
#
# class Entry(BoundaryBox):
#     def __init__(self, shape: Geometry):
#         x_min, y_min, x_max, y_max = (shapely.envelope(shape)).bounds
#         super().__init__(x_min, y_min, x_max, y_max)
#         self.shape = shape
#
#
# class RStarTreeNode(BoundaryBox):
#     def __init__(self, children: List[RStarTreeNode | Entry] | None = None, parent: RStarTreeNode = None,
#                  is_leaf: bool = False):
#         mbr = union(*children)
#         super().__init__(mbr.x_min, mbr.y_min, mbr.x_max, mbr.y_max)
#         self.children = children
#         self.parent = parent
#         self.is_leaf = is_leaf
#
#     def add_child(self, node: RStarTreeNode | Entry):
#         self.children.append(node)
#
#
# def union(*boundaries: BoundaryBox):
#     minx, miny, = float('inf'), float('inf')
#     maxx, maxy = float('-inf'), float('-inf')
#
#     for boundary in boundaries:
#         minx, miny = min(boundary.x_min, minx), min(boundary.y_min, miny)
#         maxx, maxy = max(boundary.x_max, maxx), max(boundary.y_max, maxy)
#
#     return BoundaryBox(minx, miny, maxx, maxy)
#
#
# def intersection(rect1: BoundaryBox, rect2: BoundaryBox) -> bool:
#     return (rect1.x_min <= rect2.x_max and
#             rect1.x_max >= rect2.x_min and
#             rect1.y_min <= rect2.y_max and
#             rect1.y_max >= rect2.y_min)
#
#
# def box_to_geometry(box: BoundaryBox):
#     return shapely.box(box.x_min, box.y_min, box.x_max, box.y_max)
#
#
# def geometry_to_box(shape: Geometry):
#     x_min, y_min, x_max, y_max = Polygon(shapely.envelope(shape)).bounds
#     return BoundaryBox(x_min, y_min, x_max, y_max)
#
#
# def choose_leaf(node: RStarTreeNode, entry: Entry):
#     if node.is_leaf:
#         return node
#
#     if all(map(lambda n: n.is_leaf, node.children)):
#         return least_overlap_enlargement(node.children, entry)
#     else:
#         return least_area_enlargement(node.children, entry)
#
#
# def _fix_children(node: RStarTreeNode) -> None:
#     if not node.is_leaf:
#         for entry in node.children:
#             entry.child.parent = node
#
#
# def perform_node_split(node: RStarTreeNode, group1: List[RStarTreeNode | Entry],
#                        group2: List[RStarTreeNode | Entry]) \
#         -> RStarTreeNode:
#     """
#     Splits a given node into two nodes. The original node will have the entries specified in group1, and the
#     newly-created split node will have the entries specified in group2. Both the original and split node will
#     have their children nodes adjusted so they have the correct parent.
#     :param node: Original node to split
#     :param group1: Entries to assign to the original node
#     :param group2: Entries to assign to the newly-created split node
#     :return: The newly-created split node
#     """
#     node.entries = group1
#     split_node = RStarTreeNode(group2, node.parent, node.is_leaf)
#     _fix_children(node)
#     _fix_children(split_node)
#     return split_node
#
#
# class RStarTree(object):
#     def __init__(self, max_node_capacity=4):
#         self.root = RStarTreeNode([], None, True)
#         self.max_node_capacity = max_node_capacity
#         self.min_node_capacity = 1
#
#     def insert(self, shape: Geometry):
#         entry = Entry(shape)
#
#         node = choose_leaf(self.root, entry)
#         node.add_child(entry)
#
#         split_node = None
#         if len(node.children) > self.max_node_capacity:
#             split_node = self.overflow_strategy(node)
#
#         self.adjust_tree(kd_tree, node, split_node)
#
#     def overflow_strategy(self, node: RStarTreeNode) -> RStarTreeNode:
#         """
#         R* overflow treatment. The outer method initializes a cache to store information about the kd_tree's current state,
#         including the current state of the nodes at every level of the kd_tree, as well as a dictionary of which levels we
#         have performed a force reinsert on.
#         :param kd_tree: R-kd_tree instance
#         :param node: Overflowing node
#         :return: New node resulting from a split, or None
#         """
#         if not self._cache:
#             self._cache = RStarCache()
#
#         if not self._cache.levels:
#             self._cache.levels = self.get_levels()
#
#         levels_from_leaf = _get_levels_from_leaf(kd_tree._cache.levels, node)
#
#         return self._rstar_overflow(node, levels_from_leaf)
#
#     def _rstar_overflow(self, node: RStarTreeNode, levels_from_leaf: int) -> Optional[RStarTreeNode]:
#         # If the level is not the root level and this is the first call of _rstar_overflow on the given level, then
#         # perform a forced reinsert of a subset of the entries in the node. Otherwise, do a regular node split.
#         if node == self.root or self._cache.reinsert.get(levels_from_leaf, False):
#             split_node = self.rstar_split(node)
#             self.adjust_tree(node, split_node)
#         else:
#             self.reinsert(node, levels_from_leaf)
#         return None
#
#     # noinspection PyProtectedMember
#     def reinsert(self, node: RStarTreeNode, levels_from_leaf: int):
#         """
#         Performs a forced reinsert on a subset of the entries in the given node.
#         :param kd_tree: R-kd_tree instance
#         :param node: Overflowing node
#         :param levels_from_leaf: Level of the node in the kd_tree (starting with the leaf level being 0). Forced reinsert is
#             done at most once per level during an insert operation. The inverse level (with leaf level being 0, rather than
#             the root level being 0) is used because a split can cause the kd_tree to grow in the middle of the reinsert
#             operation, which would cause the level (in the normal sense, with root being 0) to change, whereas
#             levels_from_leaf would stay the same.
#         """
#         # Indicate that we have performed a forced reinsert at the current level. Forced reinsert is done at most once per
#         # level during an insert operation.
#         self._cache.reinsert[levels_from_leaf] = True
#
#         # Sort the entries in order of increasing distance from the node's centroid
#         node_centroid = node.centroid()
#         sorted_entries = sorted(node.entries, key=lambda e: _dist(e.rect.centroid(), node_centroid))
#
#         # Get the subset of entries to reinsert. Per the paper, reinserting the closest 30% yields the best performance.
#         p = math.ceil(0.3 * len(sorted_entries))
#         entries_to_reinsert = sorted_entries[:p]
#
#         # Remove entries that will be reinserted from the node and adjust the node's bounding rectangle to
#         # fit the remaining entries.
#         node.entries = [e for e in node.entries if e not in entries_to_reinsert]
#         node.parent_entry.rect = union_all([entry.rect for entry in node.entries])
#
#         # Reinsert the entries at the same level in the kd_tree.
#         for e in entries_to_reinsert:
#             _reinsert_entry(kd_tree, e, levels_from_leaf)
#
#     def _adjustTree(self, node: RStarTreeNode, new_node: RStarTreeNode | None):
#         raise Exception('Not implemented')
#
#     def search(self, search: Geometry):
#         raise Exception('Not implemented')
#
#     def rstar_split(self, node: RStarTreeNode) -> RStarTreeNode:
#         """
#         Split an overflowing node. The R*-Tree implementation first determines the optimum split axis (minimizing overall
#         perimeter), then chooses the best split index along the chosen axis (based on minimum overlap).
#         :param node: RTreeNode[T]: Overflowing node that needs to be split.
#         :return: Newly-created split node whose entries are a subset of the original node's entries.
#         """
#         stat = get_rstar_stat(node.children, self.min_node_capacity, self.max_node_capacity)
#         axis = choose_split_axis(stat)
#         distributions = stat.get_axis_unique_distributions(axis)
#         i = choose_split_index(distributions)
#         distribution = distributions[i]
#         d1 = list(distribution.set1)
#         d2 = list(distribution.set2)
#         return perform_node_split(node, d1, d2)
#
#
# EntryDivision = Tuple[Iterable[RStarTreeNode | Entry], Iterable[RStarTreeNode | Entry]]
# EntryOrdering = Tuple[RStarTreeNode | Entry]
#
#
# def _dist(p1, p2):
#     x1, y1 = p1
#     x2, y2 = p2
#     return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
#
#
# def choose_split_axis(stat: RStarStat) -> Axis:
#     """
#     Determines the axis perpendicular to which the entries should be split, based on the one with the smallest overall
#     perimeter after determining all possible divisions of the entries that satisfy min_entries and max_entries.
#     :param stat: RStarStat instance (as returned by get_rstar_stat)
#     :return: Best split axis ('x' or 'y')
#     """
#     perimeter_x = stat.get_axis_perimeter('x')
#     perimeter_y = stat.get_axis_perimeter('y')
#     return 'x' if perimeter_x <= perimeter_y else 'y'
#
#
# def choose_split_index(distributions: List[EntryDistribution]) -> int:
#     """
#     Chooses the best split index based on minimum overlap (or minimum area in case of tie).
#     :param distributions: List of possible distributions of entries along the best split axis.
#     :return: Index of the best distribution among the list of possible distributions.
#     """
#     division_rects = [d.get_rects() for d in distributions]
#     division_overlaps = [get_intersection_area(r1, r2) for r1, r2 in division_rects]
#     min_overlap = min(division_overlaps)
#     indices = [i for i, v in enumerate(division_overlaps) if math.isclose(v, min_overlap, rel_tol=EPSILON)]
#     # If a single index is a clear winner, choose that index.
#     if len(indices) == 1:
#         return indices[0]
#     else:
#         # Resolve ties by choosing the distribution with minimum area
#         min_area = None
#         split_index = None
#         for i in indices:
#             r1, r2 = division_rects[i]
#             area = r1.area() + r2.area()
#             if min_area is None or area < min_area:
#                 min_area = area
#                 split_index = i
#         return split_index
#
#
# def get_rstar_stat(entries: List[RStarTreeNode | Entry], min_entries: int, max_entries: int) -> RStarStat:
#     sort_divisions: Dict[EntryOrdering, List[EntryDivision]] = {}
#     stat = RStarStat()
#     for axis in ['x', 'y']:
#         for dimension in ['min', 'max']:
#             sorted_entries = tuple(sorted(entries, key=_get_sort_key(axis, dimension)))
#             divisions = sort_divisions.get(sorted_entries, None)
#             if divisions is None:
#                 divisions = get_possible_divisions(sorted_entries, min_entries, max_entries)
#                 sort_divisions[sorted_entries] = divisions
#             for division in divisions:
#                 stat.add_distribution(axis, dimension, division)
#     return stat
#
#
# def _get_sort_key(axis: Axis, dimension: Dimension) -> Callable[[RStarTreeNode | Entry], Any]:
#     if axis == 'x' and dimension == 'min':
#         return lambda e: e.rect.min_x
#     if axis == 'x' and dimension == 'max':
#         return lambda e: e.rect.max_x
#     if axis == 'y' and dimension == 'min':
#         return lambda e: e.rect.min_y
#     if axis == 'y' and dimension == 'max':
#         return lambda e: e.rect.max_y
#
#
# def get_possible_divisions(entries: Iterable[RStarTreeNode | Entry], min_entries: int, max_entries: int) -> List[
#     EntryDivision]:
#     """
#     Returns a list of all possible divisions of a sorted list of entries into two groups (preserving order), where each
#     group has at least min_entries number of entries.
#     :param entries: List of entries, sorted by some criteria.
#     :param min_entries: Minimum number of entries in each group.
#     :param max_entries: Maximum number of entries in each group. It is assumed that the entries list contains one
#         greater than the maximum number of entries (i.e., the entries list corresponds to a node that is now overflowing
#         after the insertion of a new entry).
#     :return: List of tuples representing the possible divisions.
#     """
#     m = min_entries
#     return [(entries[:(m - 1 + k)], entries[(m - 1 + k):]) for k in range(1, max_entries - 2 * m + 3)]
#
#
# Axis = Union['x', 'y']
# Dimension = Union['min', 'max']
#
#
# class EntryDistribution:
#     """
#     Represents a distribution of entries into two groups, where the order of entries in each group is not relevant.
#     This class is similar to the EntryDivision type alias, but contains additional helper methods for working with
#     the distribution (e.g., getting bounding rectangles for each group), as well as equality and hash operators so
#     the list of distributions can be used as part of a set (as required by RStarStat).
#     """
#
#     def __init__(self, division: EntryDivision):
#         """
#         Creates an RStarDistribution from an EntryDivision.
#         :param division: Entry division. Note that an EntryDivision is nothing more than a type alias for a tuple
#             containing two lists of entries.
#         """
#         self.division = division
#         self.set1 = set(division[0])
#         self.set2 = set(division[1])
#         r1 = union(*[e for e in division[0]])
#         r2 = union(*[e for e in division[1]])
#         self.overlap = get_intersection_area(r1, r2)
#         self.perimeter = r1.perimeter() + r2.perimeter()
#
#     def is_division_equivalent(self, division: EntryDivision) -> bool:
#         """
#         Returns True if the given entry division may be considered equivalent (i.e., its two groups contain the same
#         entries, independent of the order of both the groups themselves, as well as the entries in each group).
#         :param division: Entry division
#         :return: True if the entry division may be considered equivalent to this distribution
#         """
#         set1 = set(division[0])
#         set2 = set(division[1])
#         return (self.set1 == set1 and self.set2 == set2) or (self.set1 == set2 and self.set2 == set1)
#
#     def get_rects(self) -> Tuple[BoundaryBox, BoundaryBox]:
#         """Returns the two rectangles corresponding to the bounding boxes of each group in the distribution."""
#         r1 = union(*[e for e in self.division[0]])
#         r2 = union(*[e for e in self.division[1]])
#         return r1, r2
#
#     def __eq__(self, other):
#         if isinstance(other, self.__class__):
#             return (self.set1 == other.set1 and self.set2 == other.set2) \
#                 or (self.set1 == other.set2 and self.set2 == other.set1)
#         return False
#
#     def __ne__(self, other):
#         return not self == other
#
#     def __hash__(self):
#         return hash(frozenset([frozenset(self.set1), frozenset(self.set2)]))
#
#     def __repr__(self):
#         return f'RStarDistribution({[e.shape for e in self.set1]}, {[e.shape for e in self.set2]})'
#
#
# class RStarStat:
#     """
#     Class used for caching metrics as part of the R*-Tree split algorithm. These metrics are primarily the list of
#     possible entry distributions along each axis ('x' or 'y') and dimension ('min' or 'max'), which are required by
#     multiple steps of the split algorithm. In particular, the algorithm first requires selecting the optimum split axis
#     (based on minimum total perimeter of all possible distributions along that axis), and then the optimum split index
#     of all possible distributions along the optimum axis (based on minimum overlap). To avoid having to recompute the
#     list of possible distributions, this class is used to cache them so they can be calculated once, and then used for
#     both steps. This class also provides some helper methods for getting the total perimeter and unique distributions
#     along a given axis.
#     """
#
#     def __init__(self):
#         self.stat: Dict[Axis, Dict[Dimension, List[EntryDistribution]]] = {
#             'x': {
#                 'min': [],
#                 'max': []
#             },
#             'y': {
#                 'min': [],
#                 'max': []
#             }
#         }
#         self.unique_distributions: List[EntryDistribution] = []
#
#     def add_distribution(self, axis: Axis, dimension: Dimension, division: EntryDivision):
#         """
#         Adds a distribution of entries for the given axis and dimension.
#         :param axis: Axis ('x' or 'y')
#         :param dimension: Dimension ('min' or 'max')
#         :param division: Entry division
#         """
#         distribution = next((d for d in self.unique_distributions if d.is_division_equivalent(division)), None)
#         if distribution is None:
#             distribution = EntryDistribution(division)
#             self.unique_distributions.append(distribution)
#         self.stat[axis][dimension].append(distribution)
#
#     def get_axis_perimeter(self, axis: Axis):
#         """
#         Returns the total overall perimeter of all distributions along the given axis (sorted by both min and max).
#         :param axis: Axis ('x' or 'y')
#         :return: Total overall perimeter for all distributions along the axis
#         """
#         distributions_min = self.stat[axis]['min']
#         distributions_max = self.stat[axis]['max']
#         return sum([d.perimeter for d in (distributions_min + distributions_max)])
#
#     def get_axis_unique_distributions(self, axis: Axis) -> List[EntryDistribution]:
#         """
#         Returns a list of all unique entry distributions for a given axis
#         :param axis: Axis ('x' or 'y')
#         :return: List of unique entry distributions for the given axis
#         """
#         # Use dict.fromkeys() to preserve order. Though order is not technically relevant, it helps to keep the
#         # split algorithm deterministic (and reduces flakiness in unit tests).
#         distributions = self.stat[axis]['min'] + self.stat[axis]['max']
#         return list(dict.fromkeys(distributions).keys())
#
#
# def least_overlap_enlargement(nodes: List[RStarTreeNode], entry: Entry) -> RStarTreeNode:
#     overlaps = [overlap(e, [e2 for e2 in without(nodes, e)]) for e in nodes]
#     overlap_enlargements = [
#         overlap(union(e, entry), [e2 for e2 in without(nodes, e)]) - overlaps[i]
#         for i, e in enumerate(nodes)]
#     min_enlargement = min(overlap_enlargements)
#     indices = [i for i, v in enumerate(overlap_enlargements) if
#                math.isclose(v, min_enlargement, rel_tol=EPSILON)]
#     # If a single entry is a clear winner, choose that entry.
#     if len(indices) == 1:
#         return nodes[indices[0]]
#     else:
#         # If multiple entries have the same overlap enlargement, use least area enlargement strategy as a tie-breaker.
#         entries = [nodes[i] for i in indices]
#         return least_area_enlargement(entries, entry)
#
#
# def least_area_enlargement(nodes: List[RStarTreeNode], entry: Entry) -> RStarTreeNode:
#     areas = [child.area() for child in nodes]
#     enlargements = [union(child, entry).area() - areas[i] for i, child in enumerate(nodes)]
#     min_enlargement = min(enlargements)
#     indices = [i for i, v in enumerate(enlargements) if math.isclose(v, min_enlargement, rel_tol=EPSILON)]
#     # If a single entry is a clear winner, choose that entry. Otherwise, if there are multiple entries having the
#     # same enlargement, choose the entry having the smallest area as a tie-breaker.
#     if len(indices) == 1:
#         return nodes[indices[0]]
#     else:
#         min_area = min([areas[i] for i in indices])
#         i = areas.index(min_area)
#         return nodes[i]
#
#
# def without(items: List[RStarTreeNode], item: RStarTreeNode) -> List[RStarTreeNode]:
#     """Returns all items in a list except the given item."""
#     return [i for i in items if i != item]
#
#
# def overlap(rect: BoundaryBox, rects: List[BoundaryBox]) -> float:
#     """
#     Returns the total overlap area of one rectangle with respect to the others. Any common areas where multiple
#     rectangles intersect will be counted multiple times.
#     """
#     return sum([get_intersection_area(rect, r) for r in rects])
#
#
# def get_intersection_area(rect1: BoundaryBox, rect2: BoundaryBox) -> float:
#     x_overlap = max(0.0, min(rect1.x_max, rect2.x_max) - max(rect1.x_min, rect2.x_min))
#     y_overlap = max(0.0, min(rect1.y_max, rect2.y_max) - max(rect1.y_min, rect2.y_min))
#     return x_overlap * y_overlap
