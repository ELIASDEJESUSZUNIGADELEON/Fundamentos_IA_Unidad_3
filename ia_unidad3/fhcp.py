"""Acceso al proyecto de equipo y evaluación local, sin modificar sus motores."""

import re
import sys
from dataclasses import asdict
from hashlib import sha256

import numpy as np

from .common import ROOT, save_csv, save_json, timestamp

PROJECT = ROOT / "01-fhcp-challenge/proyecto_equipo"
sys.path.insert(0, str(PROJECT))
from src.algorithms.execution import Budget
from src.cli.variants import VARIANTS, effective_variant
from src.evaluation import evaluate_cost, validate_cycle
from src.graphs.readers import read_hcp, read_tour

NAMES = {
    "ga": "Genético",
    "sa": "Recocido simulado",
    "as": "Colonia de hormigas",
    "abc": "Colonia de abejas",
    "de": "Evolución diferencial",
    "pso": "Enjambre de partículas",
}
PARAMETERS = {
    "ga": {
        "population_size": 40,
        "tournament_size": 3,
        "crossover_rate": 0.85,
        "mutation_rate": 0.3,
        "elite_count": 2,
        "initialization": "greedy",
        "guided_move_rate": 0.8,
    },
    "sa": {
        "initial_temperature": 2.0,
        "cooling_factor": 0.99,
        "minimum_temperature": 0.01,
        "moves_per_temperature": 100,
        "initialization": "greedy",
        "guided_move_rate": 0.8,
        "cost_mode": "incremental",
        "incremental_check_interval": 100,
    },
    "as": {
        "ant_count": 20,
        "alpha": 1.0,
        "beta": 2.0,
        "rho": 0.2,
        "q": 1.0,
        "epsilon": 0.001,
        "initial_pheromone": 1.0,
        "pheromone_min": 0.001,
        "pheromone_max": 20.0,
        "construction": "neighbor_guided",
        "pheromone_storage": "edges",
    },
    "abc": {
        "source_count": 20,
        "limit": 30,
        "initialization": "greedy",
        "guided_move_rate": 0.8,
        "cost_mode": "incremental",
        "incremental_check_interval": 100,
    },
    "de": {
        "population_size": 24,
        "differential_weight": 0.6,
        "crossover_rate": 0.8,
        "initialization": "greedy",
    },
    "pso": {
        "swarm_size": 24,
        "inertia": 0.7,
        "cognitive_coefficient": 1.4,
        "social_coefficient": 1.4,
        "velocity_limit": 0.3,
        "initialization": "greedy",
    },
}


def load_graph(instance="graph1"):
    if not re.fullmatch(r"graph[1-9][0-9]{0,3}", instance):
        raise ValueError("Identificador de grafo inválido.")
    path = PROJECT / "data/raw/FHCPCS" / (instance + ".hcp")
    return read_hcp(
        path, source={"instance_id": instance, "sha256": sha256(path.read_bytes()).hexdigest()}
    )


def reference(instance="graph1"):
    graph = load_graph(instance)
    external = read_tour(PROJECT / "data/raw/FHCPCS_sols" / (instance + ".hcp.tou"), graph)
    route = tuple(graph.index_of(vertex) for vertex in external)
    validation = validate_cycle(graph, route)
    assert validation.valid
    return graph, route


def solve(
    instance="graph1", algorithm="sa", seed=2430085, evaluations=3000, seconds=3.0, graph=None
):
    graph = graph if graph is not None else load_graph(instance)
    spec = VARIANTS[algorithm]
    parameters = spec.resolve(PARAMETERS[algorithm])
    budget = Budget(max_elapsed_ns=int(seconds * 1e9), max_evaluations=evaluations)
    result = spec.solve(graph, parameters=parameters, seed=int(seed), budget=budget)
    if result.status == "error":
        raise RuntimeError(str(result.error))
    if result.best_route is not None:
        assert evaluate_cost(graph, result.best_route) == result.best_cost
        independent = validate_cycle(graph, result.best_route)
        assert independent.valid == (result.best_cost == 0)
    record = {
        "fecha_utc": timestamp(),
        "instancia": instance,
        "algoritmo": algorithm,
        "variante": effective_variant(spec, parameters).name,
        "parametros": parameters,
        "semilla": seed,
        "presupuesto": asdict(budget),
        "grafo_sha256": graph.source.get("sha256"),
        "vertices": graph.vertex_count(),
        "aristas": graph.edge_count(),
        "resultado": asdict(result),
    }
    return record, graph


def benchmark(
    instances=("graph1", "graph2", "graph18"),
    seeds=(2430085, 2430086, 2430087),
    evaluations=3000,
    seconds=2.0,
    progress=None,
):
    records = []
    for instance in instances:
        for algorithm in NAMES:
            for seed in seeds:
                record, _ = solve(instance, algorithm, seed, evaluations, seconds)
                records.append(record)
                if progress:
                    progress(
                        f"{len(records)}: {instance} {algorithm} semilla={seed} costo={record['resultado']['best_cost']}"
                    )
    summary = []
    for algorithm, name in NAMES.items():
        rows = [r["resultado"] for r in records if r["algoritmo"] == algorithm]
        summary.append(
            {
                "algoritmo": algorithm,
                "nombre": name,
                "intentos": len(rows),
                "exitos": sum(row["validation"]["valid"] is True for row in rows),
                "tiempo_medio_s": float(
                    np.mean([row["timing"]["solver_ns"] / 1e9 for row in rows])
                ),
                "costo_medio": float(np.mean([row["best_cost"] for row in rows])),
                "evaluaciones_medias": float(
                    np.mean([row["counters"]["evaluations_completed"] for row in rows])
                ),
            }
        )
    return {
        "fecha_utc": timestamp(),
        "instancias": list(instances),
        "semillas": list(seeds),
        "max_evaluaciones": evaluations,
        "limite_segundos": seconds,
        "corridas": records,
        "resumen": summary,
    }


def export_benchmark(folder, record):
    save_json(folder / "comparacion.json", record)
    save_csv(folder / "resumen.csv", record["resumen"])


def draw_graph(figure, graph, route=None, title="Mejor ruta del solver"):
    figure.clear()
    ax = figure.add_subplot(111)
    n = graph.vertex_count()
    angles = np.arange(n) * 2 * np.pi / n
    points = np.c_[np.cos(angles), np.sin(angles)]
    for u, v in graph.edges():
        ax.plot(points[[u, v], 0], points[[u, v], 1], color="#a0b1be", alpha=0.25, lw=0.8, zorder=1)
    if route is not None:
        for u, v in zip(route, list(route[1:]) + [route[0]]):
            valid = graph.has_edge(u, v)
            ax.plot(
                points[[u, v], 0],
                points[[u, v], 1],
                color="#258d9b" if valid else "#e35542",
                lw=1.6,
                linestyle="-" if valid else "--",
                zorder=2,
            )
    ax.scatter(points[:, 0], points[:, 1], s=32, c="#152b42", edgecolors="white", zorder=3)
    if n <= 80:
        for i, (x, y) in enumerate(points):
            ax.text(
                x * 1.08,
                y * 1.08,
                str(graph.external_label(i)),
                fontsize=7,
                ha="center",
                va="center",
            )
    ax.set_title(title)
    ax.set_aspect("equal")
    ax.axis("off")
    figure.tight_layout()
