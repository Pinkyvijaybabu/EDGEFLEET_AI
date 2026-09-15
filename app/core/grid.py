from heapq import heappush, heappop
from random import Random

class WarehouseGrid:
    def __init__(self, width=18, height=18, seed=7):
        self.width, self.height = width, height
        self.rng = Random(seed)
        self.blocked = set()
        self.congestion = 0.0
        # Permanent shelving walls with cross-aisle gaps.
        for x in (4, 8, 12, 15):
            for y in range(2, height-2):
                if y not in (5, 11): self.blocked.add((x, y))

    def in_bounds(self, p):
        x, y = p
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, p):
        return self.in_bounds(p) and p not in self.blocked

    def neighbors(self, p):
        x, y = p
        for q in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if self.passable(q): yield q

    @staticmethod
    def heuristic(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def astar(self, start, goal):
        if not self.passable(start): return []
        if not self.passable(goal): return []
        frontier=[]; heappush(frontier,(0,start)); came={start:None}; cost={start:0}
        while frontier:
            _, cur=heappop(frontier)
            if cur==goal: break
            for nxt in self.neighbors(cur):
                new=cost[cur]+1+self.congestion*0.25
                if nxt not in cost or new<cost[nxt]:
                    cost[nxt]=new; came[nxt]=cur
                    heappush(frontier,(new+self.heuristic(nxt,goal),nxt))
        if goal not in came: return []
        path=[]; cur=goal
        while cur is not None: path.append(cur); cur=came[cur]
        return list(reversed(path))
