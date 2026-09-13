from __future__ import annotations

from heapq import heappush, heappop
from typing import Iterable

Point = tuple[int, int]

class WarehouseGrid:
    def __init__(self, width: int = 22, height: int = 14):
        self.width = width
        self.height = height
        self.blocked: set[Point] = set()
        self._build_static_obstacles()

    def _build_static_obstacles(self):
        # Warehouse shelves form corridors and two choke points.
        shelves = [
            (4, 2, 4, 9),
            (9, 4, 9, 12),
            (14, 1, 14, 9),
            (18, 4, 18, 12),
        ]
        for x1, y1, x2, y2 in shelves:
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    self.blocked.add((x, y))
        # Open selected gaps in shelves.
        for p in [(4, 5), (4, 10), (9, 2), (9, 8), (14, 6), (14, 10), (18, 7)]:
            self.blocked.discard(p)

    def in_bounds(self, p: Point) -> bool:
        x, y = p
        return 0 <= x < self.width and 0 <= y < self.height

    def walkable(self, p: Point) -> bool:
        return self.in_bounds(p) and p not in self.blocked

    def neighbors(self, p: Point) -> Iterable[Point]:
        x, y = p
        for q in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if self.walkable(q):
                yield q

    @staticmethod
    def heuristic(a: Point, b: Point) -> int:
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def astar(self, start: Point, goal: Point) -> list[Point]:
        if not self.walkable(start) or not self.walkable(goal):
            return []
        frontier: list[tuple[int, Point]] = []
        heappush(frontier, (0, start))
        came_from: dict[Point, Point | None] = {start: None}
        cost = {start: 0}

        while frontier:
            _, current = heappop(frontier)
            if current == goal:
                break
            for nxt in self.neighbors(current):
                new_cost = cost[current] + 1
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    priority = new_cost + self.heuristic(nxt, goal)
                    heappush(frontier, (priority, nxt))
                    came_from[nxt] = current

        if goal not in came_from:
            return []

        path = []
        cur: Point | None = goal
        while cur is not None:
            path.append(cur)
            cur = came_from[cur]
        return list(reversed(path))

    def add_block(self, p: Point) -> bool:
        if not self.in_bounds(p):
            return False
        self.blocked.add(p)
        return True

    def remove_block(self, p: Point):
        self.blocked.discard(p)
