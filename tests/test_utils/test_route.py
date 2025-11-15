import networkx as nx  # type: ignore
from src.utils import build_physical_route, RouteStats, RouteMove


def make_sample_graph():
    G = nx.Graph()
    # Add minimal node attributes
    for sid, name, line in [
        ('A', 'Alpha', 'L1'),
        ('B', 'Beta', 'L1'),
        ('C', 'Gamma', 'L2'),
        ('D', 'Delta', 'L2')
    ]:
        G.add_node(sid, name=name, line_code=line)

    # Edges with connection types
    G.add_edge('A', 'B', weight=1.0, connection_type='train')
    G.add_edge('B', 'C', weight=0.5, connection_type='walk_transfer')
    G.add_edge('C', 'D', weight=2.0, connection_type='train')
    G.add_edge('D', 'A', weight=3.0, connection_type='walk_between_stations')
    return G


def test_build_physical_route_basic():
    G = make_sample_graph()
    tour = ['A', 'B', 'C', 'D']
    full_path, stats, moves = build_physical_route(G, tour)

    # full_path should close cycle: A->B->C->D->A
    assert full_path == ['A', 'B', 'C', 'D', 'A']

    # Stats validation
    assert isinstance(stats, RouteStats)
    assert stats.unique_stations == 4
    assert stats.total_visits == 5
    assert stats.train_connections == 2  # A-B, C-D
    assert stats.walk_transfers == 1     # B-C
    assert stats.walk_between == 1       # D-A
    assert stats.other_connections == 0

    # Time aggregations
    assert stats.total_train_time == 1.0 + 2.0
    assert stats.total_walk_time == 0.5 + 3.0
    assert abs(stats.total_time - (1.0 + 2.0 + 0.5 + 3.0)) < 1e-9

    # Moves list
    assert len(moves) == 4
    assert all(isinstance(m, RouteMove) for m in moves)
    types = [m.connection_type for m in moves]
    assert types == ['train', 'walk_transfer', 'train', 'walk_between_stations']


def test_build_physical_route_empty_tour():
    import pytest  # type: ignore
    G = make_sample_graph()
    with pytest.raises(ValueError):
        build_physical_route(G, [])


def test_build_physical_route_repeated_shortest_path():
    G = make_sample_graph()
    # Add alternate path with lower weight forcing shortest path deviation
    G.add_node('X', name='Aux', line_code='Lx')
    G.add_edge('B', 'X', weight=0.1, connection_type='train')
    G.add_edge('X', 'C', weight=0.1, connection_type='train')

    tour = ['A', 'B', 'C']
    full_path, stats, moves = build_physical_route(G, tour)

    # Shortest paths:
    # A->B direct
    # B->C uses B->X->C (0.1+0.1 vs direct 0.5)
    # C->A uses C->X->B->A (0.1+0.1+1.0 = 1.2 vs C->B->A 0.5+1.0 = 1.5)
    # Thus X appears twice in the expanded route.
    assert full_path == ['A', 'B', 'X', 'C', 'X', 'B', 'A']
    assert stats.total_visits == 7
    # Moves: A-B, B-X, X-C, C-X, X-B, B-A
    assert len(moves) == 6
    # Ensure train classification present
    assert all(m.connection_type == 'train' for m in moves)
