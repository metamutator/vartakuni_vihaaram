"""Utilities for expanding a TSP tour into a physical metro route.

Functions here convert an abstract tour (list of station IDs visited
exactly once) into the full physical traversal through the underlying
metro graph using shortest paths between successive tour stations.

The graph edges are expected to include a `connection_type` attribute
with one of:
    - 'train'
    - 'walk_transfer'
    - 'walk_between_stations'

Any other value (or missing attribute) is categorized as 'unknown'.

Returned data structures are lightweight dataclasses for downstream
analysis or formatting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import networkx as nx  # type: ignore


@dataclass(frozen=True)
class RouteMove:
    index: int
    from_station: str
    to_station: str
    connection_type: str
    weight: float
    from_line: str
    to_line: str
    from_name: str
    to_name: str


@dataclass(frozen=True)
class RouteStats:
    total_visits: int
    unique_stations: int
    train_connections: int
    walk_transfers: int
    walk_between: int
    other_connections: int
    total_train_time: float
    total_walk_time: float
    total_time: float
    num_line_segments: int
    unique_lines: List[str]


def _classify_connection(edge_data: dict) -> str:
    """Return standardized connection type from edge attributes."""
    ct = edge_data.get('connection_type')
    if not ct:
        # Fallback names if ever used elsewhere
        ct = edge_data.get('type') or edge_data.get('kind') or edge_data.get('mode') or 'unknown'
    return ct


def build_physical_route(graph: nx.Graph, tour: List[str]) -> Tuple[List[str], RouteStats, List[RouteMove]]:
    """Expand an abstract tour into the full physical route.

    Args:
        graph: NetworkX graph of the metro network.
        tour: Ordered list of station IDs (each exactly once) forming a cycle.

    Returns:
        full_path: List of station IDs encountered following shortest paths
                   between successive tour stations (includes revisits and
                   intermediate stations; ends with start station).
        stats: RouteStats summary object.
        moves: List of RouteMove objects (each edge traversal in full_path).
    """
    if not tour:
        raise ValueError("Tour is empty")

    full_path: List[str] = []
    for i in range(len(tour)):
        start = tour[i]
        end = tour[(i + 1) % len(tour)]
        segment = nx.shortest_path(graph, start, end, weight='weight')
        if i == 0:
            full_path.extend(segment)
        else:
            full_path.extend(segment[1:])

    moves: List[RouteMove] = []
    total_train_time = 0.0
    total_walk_time = 0.0
    total_time = 0.0
    train_connections = 0
    walk_transfers = 0
    walk_between = 0
    other_connections = 0

    for i in range(len(full_path) - 1):
        u = full_path[i]
        v = full_path[i + 1]
        edge_data = graph[u][v]
        raw_type = _classify_connection(edge_data)
        weight = edge_data['weight']
        total_time += weight

        if raw_type == 'train':
            train_connections += 1
            total_train_time += weight
            normalized = 'train'
        elif raw_type == 'walk_transfer':
            walk_transfers += 1
            total_walk_time += weight
            normalized = 'walk_transfer'
        elif raw_type == 'walk_between_stations':
            walk_between += 1
            total_walk_time += weight
            normalized = 'walk_between_stations'
        else:
            other_connections += 1
            normalized = raw_type or 'unknown'

        moves.append(RouteMove(
            index=i + 1,
            from_station=u,
            to_station=v,
            connection_type=normalized,
            weight=weight,
            from_line=graph.nodes[u].get('line_code', ''),
            to_line=graph.nodes[v].get('line_code', ''),
            from_name=graph.nodes[u].get('name', u),
            to_name=graph.nodes[v].get('name', v)
        ))

    # Line segments (consecutive run on same line)
    line_segments: List[str] = []
    current_line = None
    for station in full_path:
        lc = graph.nodes[station].get('line_code', '')
        if lc != current_line:
            if current_line is not None:
                line_segments.append(current_line)
            current_line = lc
    if current_line is not None:
        line_segments.append(current_line)

    stats = RouteStats(
        total_visits=len(full_path),
        unique_stations=len(tour),
        train_connections=train_connections,
        walk_transfers=walk_transfers,
        walk_between=walk_between,
        other_connections=other_connections,
        total_train_time=total_train_time,
        total_walk_time=total_walk_time,
        total_time=total_time,
        num_line_segments=len(line_segments),
        unique_lines=sorted(set(line_segments))
    )

    return full_path, stats, moves


def format_route_move(move: RouteMove) -> str:
    """Return a human-readable string for a single move."""
    t = move.connection_type
    if t == 'train':
        symbol, arrow, label = '🚇', '→', ''
    elif t == 'walk_transfer':
        symbol, arrow, label = '🚶', '⟿', ' TRANSFER'
    elif t == 'walk_between_stations':
        symbol, arrow, label = '🚶', '⤍', ' WALK'
    else:
        symbol, arrow, label = '❓', '→', f' {t}'
    return (
        f"{move.index:4d}. {symbol} {move.from_station:5s} ({move.from_line:2s}) "
        f"{move.from_name[:28]:28s} {arrow} {move.to_station:5s} ({move.to_line:2s}) "
        f"{move.to_name[:28]:28s} [{move.weight:.1f}min{label}]"
    )


def print_physical_route(graph: nx.Graph, tour: List[str], show_all: bool = True) -> None:
    """Convenience printer for a physical route expansion."""
    full_path, stats, moves = build_physical_route(graph, tour)  # full_path kept for potential external use
    print("=" * 90)
    print("PHYSICAL ROUTE")
    print("=" * 90)
    print(f"Start: {tour[0]} -> Cycle length (unique): {stats.unique_stations}")
    print(f"Total station visits (expanded): {stats.total_visits}")
    print()
    print(f"Train connections: {stats.train_connections}  Walk transfers: {stats.walk_transfers}  "
          f"Walk between: {stats.walk_between}  Other: {stats.other_connections}")
    print(f"Total time: {stats.total_time:.2f} min (train {stats.total_train_time:.2f} | walk {stats.total_walk_time:.2f})")
    print(f"Lines used ({len(stats.unique_lines)}): {', '.join(stats.unique_lines)}")
    print()
    print("Moves:")
    if show_all:
        iterable = moves
    else:
        head = moves[:50]
        tail = moves[-10:] if len(moves) > 60 else []
        iterable = head + (["... omitted ..."] if tail else []) + tail
    for m in iterable:
        if isinstance(m, str):
            print(m)
        else:
            print(format_route_move(m))
    print()
    print("Legend: 🚇 train  🚶⟿ transfer  🚶⤍ walk between  ❓ other")


__all__ = [
    'RouteMove',
    'RouteStats',
    'build_physical_route',
    'format_route_move',
    'print_physical_route'
]
