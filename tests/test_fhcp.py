from itertools import combinations

import pytest
from src.graphs import Graph

from ia_unidad3 import fhcp


@pytest.mark.parametrize("algorithm", list(fhcp.NAMES))
def test_six_solvers_and_independent_certification_on_complete_graph(algorithm):
    graph = Graph(range(6), list(combinations(range(6), 2)))
    record, _ = fhcp.solve("sintetico", algorithm, 2430085, 100, 2.0, graph=graph)
    result = record["resultado"]
    assert result["status"] == "success"
    assert result["best_cost"] == 0
    route = result["best_route"]
    assert sorted(route) == list(range(6))
    assert all(graph.has_edge(u, v) for u, v in zip(route, route[1:] + (route[0],)))


def test_official_certificate_and_no_path_traversal():
    graph, route = fhcp.reference("graph1")
    assert len(route) == graph.vertex_count() == 66
    assert len(set(route)) == 66
    assert all(graph.has_edge(u, v) for u, v in zip(route, route[1:] + (route[0],)))
    with pytest.raises(ValueError):
        fhcp.load_graph("../graph1")
