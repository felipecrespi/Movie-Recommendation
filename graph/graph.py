from __future__ import annotations
from typing import Any


class _Vertex:
    """A vertex in a movie review graph, used to represent a user or a movie.

    Each vertex item is either a user id or movie title. Both are represented as strings,
    even though we've kept the type annotation as Any to be consistent with lecture.

    Instance Attributes:
        - item: The data stored in this vertex, representing a user or movie.
        - kind: The type of this vertex: 'user' or 'movie'.
        - neighbours: The vertices that are adjacent to this vertex, and the
        review score between them.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'user', 'movie'}
    """
    item: Any
    kind: str
    neighbours: dict[_Vertex: int]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'user', 'movie'}
        """
        self.item = item
        self.kind = kind
        self.neighbours = {}

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    def check_connected(self, target_item: Any, visited: set[_Vertex]) -> bool:
        """Return whether this vertex is connected to a vertex corresponding to target_item,
        by a path that DOES NOT use any vertex in visited.

        Preconditions:
            - self not in visited
        """
        if self.item == target_item:
            return True
        else:
            visited.add(self)
            # new_visited = visited.union({self})
            return any(u.check_connected(target_item, visited)
                       for u in self.neighbours
                       if u not in visited)


class Graph:
    """A graph used to represent a movie review network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'user', 'movie'}
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_edge(self, item1: Any, item2: Any, score: int) -> None:
        """Add an edge between the two vertices with the given items in this graph.
        The edge will contain the review score between the movie/user.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours[v2] = score
            v2.neighbours[v1] = score
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set[tuple[Any, int]]:
        """Return a set of tuples, each containing the neighbours of the given item and
        its respective review score.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {(neighbour.item, v.neighbours[neighbour]) for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'user', 'movie'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def _get_all_paths_helper(self, start_item: Any, target_item: Any,
                              visited: set, path: list, paths_so_far: list,
                              review_score_so_far: int) -> None:
        """Mutate paths_so_far to contain the sizes (i.e. number of vertices) and
        average review scores of all the possible paths between the vertices
        corresponding to start_item and target_item.

        The average reviews score means the sum of the review scores contained in
        the edges in the path divided by the number of 'user' vertices.

        IMPORTANT NOTE: Since edge are only between distinct types of vertices, and
        both start_item and target_item correspond to 'movie' vertices, we can conclude
        that the total number of 'user' vertices is (total amount of vertices - 1) / 2.
        """

        visited.add(start_item)
        path.append(start_item)  # before the if statements to count the right num of vertices.

        if start_item == target_item:
            total_user_vertices = (len(path) - 1) / 2
            paths_so_far.append((len(path), review_score_so_far / total_user_vertices))

        elif len(path) > 5:
            return  # though still connected, vertices too distant will not be considered

        else:
            for u in self.get_neighbours(start_item):
                if not (u[0] in visited):
                    self._get_all_paths_helper(u[0], target_item, visited, path,
                                               paths_so_far, review_score_so_far + u[1])

        # Remove start_item from path and visited
        path.pop()
        visited.remove(start_item)

    def get_all_paths(self, start_item: Any, target_item: Any) -> list[tuple[int, int]]:
        """Return a list containing tuples of the sizes (i.e. number of vertices) and
        average review scores of all the possible paths between the vertices
        corresponding to start_item and target_item.
        """

        # Create a list to store all possible paths
        paths_so_far = []

        # Mutate paths_so_far with the helper function
        self._get_all_paths_helper(start_item, target_item, set(), [], paths_so_far, 0)
        return paths_so_far

    def connected(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are connected vertices
        in this graph.

        Return False if item1 or item2 do not appear as vertices
        in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]

            return v1.check_connected(item2, set())
        else:
            return False


if __name__ == '__main__':
    import doctest

    doctest.testmod()
