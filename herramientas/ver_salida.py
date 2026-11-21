"""Ejecuta comprobaciones reales y muestra su salida en texto plano."""

import argparse
import json
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ACTIVIDADES = {
    "referencia": "01-1-fhcp-referencia",
    "comparacion": "01-2-fhcp-comparacion",
    "ciclo": "01-3-fhcp-ciclo",
    "peliculas": "02-peliculas",
    "knn": "03-knn",
    "iris": "04-1-iris",
    "diabetes": "04-2-diabetes",
}


def ejecutar(actividad):
    if actividad in ("referencia", "comparacion", "ciclo"):
        from ia_unidad3 import fhcp

        if actividad == "referencia":
            graph, route = fhcp.reference("graph1")
            print("FHCP - Validacion del certificado de referencia")
            print("Instancia: graph1")
            print("Vertices:", graph.vertex_count())
            print("Aristas:", graph.edge_count())
            print("Vertices diferentes en la ruta:", len(set(route)))
            print("Validacion independiente:", fhcp.validate_cycle(graph, route).valid)
            print("Costo recalculado:", fhcp.evaluate_cost(graph, route))
            print("\nEl certificado de referencia no se entrega a los solvers.")
            return
        comparison = json.loads(
            (ROOT / "01-fhcp-challenge/resultados/comparacion.json").read_text(encoding="utf-8")
        )
        if actividad == "comparacion":
            print("FHCP - Resultados guardados de la comparacion")
            print("Grafos:", ", ".join(comparison["instancias"]))
            print("Semillas:", ", ".join(map(str, comparison["semillas"])))
            print("Intentos:", len(comparison["corridas"]))
            print("Presupuesto: 3000 evaluaciones / 2 segundos por intento\n")
            print(
                f"{'Algoritmo':<12}{'Intentos':>10}{'Exitos':>9}{'Costo medio':>15}{'Tiempo (s)':>14}"
            )
            for row in comparison["resumen"]:
                print(
                    f"{row['algoritmo'].upper():<12}{row['intentos']:>10}{row['exitos']:>9}{row['costo_medio']:>15.3f}{row['tiempo_medio_s']:>14.4f}"
                )
            print("\nUn agotamiento no demuestra que no exista ciclo.")
            return
        record = next(r for r in comparison["corridas"] if r["resultado"]["validation"]["valid"])
        graph = fhcp.load_graph(record["instancia"])
        route = record["resultado"]["best_route"]
        valid = fhcp.validate_cycle(graph, route).valid
        cost = fhcp.evaluate_cost(graph, route)
        assert valid and cost == 0
        print("FHCP - Comprobacion del ciclo encontrado por el solver")
        print("Instancia:", record["instancia"])
        print("Algoritmo:", record["algoritmo"].upper(), "(colonia de abejas)")
        print("Semilla:", record["semilla"])
        print("Estado registrado:", record["resultado"]["status"])
        print("Evaluaciones:", record["resultado"]["counters"]["evaluations_completed"])
        print("Costo recalculado:", cost)
        print("Validacion independiente:", valid)
        external = [graph.external_label(i) for i in route]
        print("\nRuta (incluye regreso al inicio):")
        external.append(external[0])
        for i in range(0, len(external), 18):
            print(" -> ".join(map(str, external[i : i + 18])))
        return
    if actividad == "peliculas":
        import hashlib

        from ia_unidad3 import movies

        rows = movies.read_movies()
        stats = movies.summary(rows)
        path = ROOT / "02-dataset-peliculas/datos/peliculas.csv"
        record = json.loads(path.with_suffix(".procedencia.json").read_text(encoding="utf-8"))
        print("Dataset de peliculas - Revision del CSV recopilado")
        print("Registros:", stats["peliculas"])
        print("URL unicas:", stats["urls_unicas"])
        print("Registros con creditos:", stats["con_creditos"])
        print(
            "Huella del archivo verificada:",
            hashlib.sha256(path.read_bytes()).hexdigest() == record["csv_sha256"],
        )
        print("\nPeliculas por anio:")
        for year, count in stats["por_anio"].items():
            print(f"  {year}: {count}")
        print("\nPrimeros registros:")
        for row in rows[:6]:
            print(f"  {row['anio']}  {row['titulo']}")
        print("\nFuente: listas anuales de Wikipedia. CSV guardado en datos/.")
        return
    if actividad == "knn":
        from ia_unidad3 import knn

        record, models = knn.experiment()
        print("KNN manual - Clasificacion de semillas sinteticas")
        print("Semilla:", record["semilla"])
        for name, indices in record["indices"].items():
            print(f"{name.capitalize()}: {len(indices)}")
        print("\nResultados en prueba:")
        print(f"{'Distancia':<15}{'k':>5}{'Exactitud':>14}{'F1 macro':>12}")
        for name, row in record["resultados"].items():
            print(
                f"{name:<15}{row['k']:>5}{row['prueba']['accuracy']:>14.4f}{row['prueba']['f1_macro']:>12.4f}"
            )
        point = [6.2, 2.6]
        print("\nNuevo punto:", point)
        for name, model in models.items():
            print(f"  {name}: {knn.LABELS[model.predict_one(point)]}")
        print("\nk seleccionado con validacion; prueba reservada.")
        return
    from ia_unidad3 import trees

    name = "Iris" if actividad == "iris" else "Diabetes"
    record, _, _ = trees.experiment(name)
    print(f"Arbol de decision - {name}")
    print("Semilla:", record["semilla"])
    print("Filas:", record["filas"])
    print("Criterio:", record["criterio"])
    print("Profundidad seleccionada:", record["profundidad"])
    print("Ejemplos de prueba:", len(record["indices"]["prueba"]))
    print(f"Exactitud: {record['accuracy']:.4f}")
    print(f"F1 macro: {record['f1_macro']:.4f}")
    print("\nMatriz de confusion (filas reales, columnas predichas):")
    for row in record["confusion"]:
        print("  " + "  ".join(f"{value:3d}" for value in row))
    print("\nClases:", ", ".join(record["clases"]))
    print("\nPreparacion y evaluacion independientes para este dataset.")


def mostrar(contenido, titulo, destino=None):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
    from PySide6.QtWidgets import QApplication, QPlainTextEdit

    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    font = Path("C:/Windows/Fonts/consola.ttf")
    if font.exists():
        QFontDatabase.addApplicationFont(str(font))
    window = QPlainTextEdit()
    window.setWindowTitle("Salida de ejecucion - " + titulo)
    window.setFont(QFont("Consolas", 12))
    palette = window.palette()
    palette.setColor(QPalette.ColorRole.Base, QColor("#0c0c0c"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#eeeeee"))
    window.setPalette(palette)
    window.setReadOnly(True)
    window.setPlainText(contenido)
    window.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    window.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    height = window.fontMetrics().lineSpacing() * (contenido.count("\n") + 2) + 28
    window.resize(1180, max(300, min(760, height)))
    window.show()
    app.processEvents()
    if destino:
        assert window.grab().save(str(destino))
        window.close()
    else:
        app.exec()


def main():
    parser = argparse.ArgumentParser(description="Salida sencilla de las practicas de la unidad 3")
    parser.add_argument("actividad", choices=ACTIVIDADES)
    parser.add_argument("--ventana", action="store_true")
    args = parser.parse_args()
    if args.ventana:
        buffer = StringIO()
        with redirect_stdout(buffer):
            ejecutar(args.actividad)
        mostrar(buffer.getvalue(), args.actividad)
    else:
        ejecutar(args.actividad)


if __name__ == "__main__":
    main()
