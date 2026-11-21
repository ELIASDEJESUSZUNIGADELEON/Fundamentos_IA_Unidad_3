"""Verifica fuentes, datos, resultados, cuadernos, imágenes y enlaces de la entrega."""

import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import nbformat
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ia_unidad3 import fhcp, knn, movies
from ia_unidad3.common import save_json


def main():
    checks = []

    def ok(message):
        checks.append(message)
        print("OK:", message, flush=True)

    origins = json.loads((ROOT / "herramientas/origenes.json").read_text(encoding="utf-8"))
    imported = 0
    for origin in origins:
        for item in origin["archivos"]:
            assert (
                hashlib.sha256((ROOT / item["archivo"]).read_bytes()).hexdigest() == item["sha256"]
            ), item["archivo"]
            imported += 1
    assert imported == 2109
    assert len(list((fhcp.PROJECT / "data/raw/FHCPCS").glob("*.hcp"))) == 1001
    ok("2109 archivos importados verificados, incluidos los 1001 grafos FHCP y sus certificados.")

    rows = movies.read_movies()
    assert len(rows) == len({r["url"] for r in rows}) == 1000
    assert all(r["titulo"] and r["anio"] and r["equipo_y_reparto"] for r in rows)
    provenance = json.loads(
        (ROOT / "02-dataset-peliculas/datos/peliculas.procedencia.json").read_text(encoding="utf-8")
    )
    assert (
        hashlib.sha256((ROOT / "02-dataset-peliculas/datos/peliculas.csv").read_bytes()).hexdigest()
        == provenance["csv_sha256"]
    )
    assert len(provenance["paginas"]) == 3
    ok("1000 peliculas con URL unicas y creditos; CSV y procedencia del rastreo comprobados.")

    comparison = json.loads(
        (ROOT / "01-fhcp-challenge/resultados/comparacion.json").read_text(encoding="utf-8")
    )
    assert len(comparison["corridas"]) == 54
    graphs = {name: fhcp.load_graph(name) for name in comparison["instancias"]}
    success = 0
    for record in comparison["corridas"]:
        result = record["resultado"]
        graph = graphs[record["instancia"]]
        assert record["grafo_sha256"] == graph.source["sha256"]
        assert result["best_route"] is not None and result["status"] in ("success", "exhausted")
        assert result["best_cost"] == fhcp.evaluate_cost(graph, result["best_route"])
        valid = fhcp.validate_cycle(graph, result["best_route"]).valid
        assert valid == (result["status"] == "success")
        success += valid
    for row in comparison["resumen"]:
        results = [
            r["resultado"] for r in comparison["corridas"] if r["algoritmo"] == row["algoritmo"]
        ]
        assert len(results) == row["intentos"] == 9
        assert sum(r["validation"]["valid"] is True for r in results) == row["exitos"]
        assert math.isclose(np.mean([r["best_cost"] for r in results]), row["costo_medio"])
        assert math.isclose(
            np.mean([r["timing"]["solver_ns"] / 1e9 for r in results]), row["tiempo_medio_s"]
        )
    assert success == 1
    _, route = fhcp.reference("graph1")
    assert len(set(route)) == 66
    ok(
        "54 corridas FHCP recalculadas: costos, tiempos, certificados y un ciclo encontrado por el solver."
    )

    record = json.loads(
        (ROOT / "03-knn-desde-cero/resultados/experimento.json").read_text(encoding="utf-8")
    )
    parts = [set(v) for v in record["indices"].values()]
    assert set.union(*parts) == set(range(360))
    assert all(not left & right for i, left in enumerate(parts) for right in parts[i + 1 :])
    truth = np.asarray(record["y"])[record["indices"]["prueba"]]
    for metric, result in record["resultados"].items():
        recomputed = knn.scores(truth, result["predicciones"])
        assert recomputed == result["prueba"]
        assert (
            result["k"]
            == max(result["validacion"], key=lambda item: (item["f1_macro"], -item["k"]))["k"]
        )
    ok(
        "KNN: particiones sin solapamiento, k por validacion y metricas recalculadas para tres distancias."
    )
    for dataset, n in [("iris", 150), ("diabetes", 768)]:
        record = json.loads(
            (ROOT / f"04-aprendizaje-automatico/resultados/{dataset}/evaluacion.json").read_text(
                encoding="utf-8"
            )
        )
        parts = [set(v) for v in record["indices"].values()]
        assert set.union(*parts) == set(range(n))
        assert all(not left & right for i, left in enumerate(parts) for right in parts[i + 1 :])
        scores = knn.scores(record["real"], record["predicciones"], len(record["clases"]))
        assert scores["confusion"] == record["confusion"]
        assert math.isclose(scores["accuracy"], record["accuracy"])
        assert math.isclose(scores["f1_macro"], record["f1_macro"])
    ok("Iris y diabetes: particiones, matrices y metricas independientes verificadas.")

    notebooks = list(ROOT.glob("*/*.ipynb"))
    assert len(notebooks) == 4
    for path in notebooks:
        notebook = nbformat.read(path, as_version=4)
        code = [c for c in notebook.cells if c.cell_type == "code"]
        assert code and all(c.execution_count is not None for c in code)
        assert not any(o.output_type == "error" for c in code for o in c.outputs)
        assert any("image/png" in o.get("data", {}) for c in code for o in c.outputs)
    ok("Cuatro cuadernos ejecutados, sin errores y con graficas incrustadas.")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert re.findall(r"^## (\d+)\.", readme, re.MULTILINE) == ["1", "2", "3", "4"]
    assert len(re.findall(r"^!\[", readme, re.MULTILINE)) == 7
    broken = []
    for md in ROOT.rglob("*.md"):
        if "proyecto_equipo" in md.parts:
            continue
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", md.read_text(encoding="utf-8")):
            if link.startswith(("https:", "http:", "#", "mailto:")):
                continue
            if not (md.parent / unquote(link.split("#")[0])).exists():
                broken.append((str(md.relative_to(ROOT)), link))
    assert not broken, broken
    images = list((ROOT / "capturas").glob("*.png"))
    assert len(images) == 7
    for path in images:
        with Image.open(path) as im:
            assert im.width >= 1100 and im.height >= 740
            im.verify()
    ok("README con cuatro actividades, siete capturas Qt y enlaces de la entrega validos.")

    tests = 0
    for filename, expected in [("pruebas-propias.xml", 28), ("pruebas-fhcp.xml", 1258)]:
        suites = list(ET.parse(ROOT / "validacion" / filename).getroot().iter("testsuite"))
        assert sum(int(s.get("tests", "0")) for s in suites) == expected
        assert sum(int(s.get("errors", "0")) + int(s.get("failures", "0")) for s in suites) == 0
        tests += expected
    ok(f"{tests} pruebas aprobadas: 28 propias y 1258 del nucleo compartido FHCP.")
    sources = {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT / "ia_unidad3").glob("*.py")
    }
    save_json(
        ROOT / "validacion/entrega.json",
        {
            "estado": "correcto",
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "comprobaciones": checks,
            "sha256_programas": sources,
        },
    )


if __name__ == "__main__":
    main()
