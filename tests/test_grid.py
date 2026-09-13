from app.core.grid import WarehouseGrid

def test_astar_finds_path():
    g = WarehouseGrid()
    path = g.astar((1,1),(20,12))
    assert path
    assert path[0] == (1,1)
    assert path[-1] == (20,12)

def test_block_changes_walkability():
    g = WarehouseGrid()
    g.add_block((2,2))
    assert not g.walkable((2,2))
