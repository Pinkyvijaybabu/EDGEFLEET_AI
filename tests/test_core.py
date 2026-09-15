from app.core.grid import WarehouseGrid

def test_astar_avoids_block():
    g=WarehouseGrid(10,10)
    start=(0,0); goal=(9,9); path=g.astar(start,goal)
    assert path[0]==start and path[-1]==goal
    g.blocked.add((1,0)); path=g.astar(start,goal)
    assert path and (1,0) not in path
