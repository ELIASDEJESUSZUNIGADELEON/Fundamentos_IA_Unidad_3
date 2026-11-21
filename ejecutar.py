"""Ejecuta las prácticas desde terminal y conserva los resultados."""

import argparse
from pathlib import Path

from ia_unidad3.common import save_json


def main():
    parser = argparse.ArgumentParser(description="Prácticas de Fundamentos de IA · Unidad 3")
    parser.add_argument("actividad", choices=["fhcp", "comparar", "peliculas", "knn", "arboles"])
    parser.add_argument(
        "--salida", type=Path, required=True, help="Carpeta nueva para los resultados"
    )
    parser.add_argument("--semilla", type=int, default=2430085)
    parser.add_argument("--instancia", default="graph1")
    parser.add_argument("--algoritmo", choices=["ga", "sa", "as", "abc", "de", "pso"], default="sa")
    parser.add_argument("--evaluaciones", type=int, default=3000)
    parser.add_argument("--segundos", type=float, default=2.0)
    parser.add_argument("--maximo", type=int, default=1000)
    parser.add_argument("--dataset", choices=["Iris", "Diabetes"], default="Iris")
    args = parser.parse_args()
    if args.salida.exists():
        parser.error("La carpeta de salida ya existe. Elige otra para conservar los resultados.")
    if args.evaluaciones < 1 or args.segundos <= 0 or args.semilla < 0:
        parser.error("Presupuesto o semilla fuera de rango.")
    if args.actividad == "fhcp":
        from ia_unidad3 import fhcp

        record, _ = fhcp.solve(
            args.instancia, args.algoritmo, args.semilla, args.evaluaciones, args.segundos
        )
        save_json(args.salida / "busqueda.json", record)
        print(f"Estado: {record['resultado']['status']}; costo: {record['resultado']['best_cost']}")
    elif args.actividad == "comparar":
        from ia_unidad3 import fhcp

        record = fhcp.benchmark(
            seeds=tuple(range(args.semilla, args.semilla + 3)),
            evaluations=args.evaluaciones,
            seconds=args.segundos,
            progress=print,
        )
        fhcp.export_benchmark(args.salida, record)
        print("Comparación de 54 intentos guardada.")
    elif args.actividad == "peliculas":
        from ia_unidad3.movies import crawl

        _, record = crawl(args.salida / "peliculas.csv", args.maximo, progress=print)
        print("Películas guardadas:", record["filas"])
    elif args.actividad == "knn":
        from ia_unidad3 import knn

        record, models = knn.experiment(args.semilla)
        knn.export_experiment(args.salida, record, models)
        for metric, result in record["resultados"].items():
            print(
                f"{metric}: k={result['k']}, exactitud={result['prueba']['accuracy']:.4f}, F1={result['prueba']['f1_macro']:.4f}"
            )
    else:
        from ia_unidad3 import trees

        record, model, _ = trees.experiment(args.dataset, args.semilla)
        trees.export_experiment(args.salida, record, model)
        print(
            f"{record['dataset']}: profundidad={record['profundidad']}, exactitud={record['accuracy']:.4f}, F1={record['f1_macro']:.4f}"
        )


if __name__ == "__main__":
    main()
