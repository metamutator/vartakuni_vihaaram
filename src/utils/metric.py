import networkx as nx
from typing import Dict

def build_metric_closure(graph: nx.Graph) -> nx.Graph:
    """Return the metric closure (complete graph with shortest-path weights).

    For each pair of distinct nodes (u, v) the closure contains an edge whose
    weight is the shortest-path travel time between u and v in the original
    graph. Assumes original edge weights are non-negative.
    """
    closure = nx.Graph()
    nodes = list(graph.nodes())
    for source in nodes:
        lengths: Dict[str, float] = nx.single_source_dijkstra_path_length(
            graph, source, weight='weight'
        )
        for target, dist in lengths.items():
            if source == target:
                continue
            # Keep minimum distance if already present (should be identical)
            if closure.has_edge(source, target):
                if dist < closure[source][target]['weight']:
                    closure[source][target]['weight'] = dist
            else:
                closure.add_edge(source, target, weight=dist)
    return closure
