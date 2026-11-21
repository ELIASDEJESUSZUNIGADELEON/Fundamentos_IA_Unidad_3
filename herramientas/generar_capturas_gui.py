"""Capturas directas de las ventanas Qt: no se construyen páginas HTML."""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "01-fhcp-challenge/resultados/comparacion.json").exists():
        raise FileNotFoundError("Primero ejecuta la comparación FHCP descrita en EJECUTAR.md.")
    if not args.visible:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from ia_unidad3 import trees
    from ia_unidad3.interface import MainWindow, prepare_app

    app = prepare_app()
    window = MainWindow()
    window.resize(1500, 960)
    window.show()
    folder = ROOT / "capturas/gui"
    folder.mkdir(parents=True, exist_ok=True)

    def capture(name):
        app.processEvents()
        for plot in window.findChildren(__import__("ia_unidad3.interface", fromlist=["Plot"]).Plot):
            plot.draw()
        app.processEvents()
        assert window.grab().save(str(folder / name))
        print("Captura:", name, flush=True)

    capture("01-1-fhcp-referencia.png")
    window.pages["fhcp"].show_benchmark()
    capture("01-2-fhcp-comparacion.png")
    from ia_unidad3 import fhcp

    comparison = json.loads(
        (ROOT / "01-fhcp-challenge/resultados/comparacion.json").read_text(encoding="utf-8")
    )
    success = next(r for r in comparison["corridas"] if r["resultado"]["validation"]["valid"])
    page = window.pages["fhcp"]
    page.instance.setCurrentText(success["instancia"])
    page.algorithm.setCurrentIndex(list(fhcp.NAMES).index(success["algoritmo"]))
    page.seed.setValue(success["semilla"])
    page.seconds.setValue(comparison["limite_segundos"])
    page.apply_result((success, fhcp.load_graph(success["instancia"])))
    capture("01-3-fhcp-ciclo.png")
    window.open("peliculas")
    capture("02-peliculas.png")
    window.open("knn")
    capture("03-knn.png")
    page = window.open("arboles")
    capture("04-1-iris.png")
    page.dataset.setCurrentText("Diabetes")
    page.apply_result(trees.experiment("Diabetes"))
    page.view.setCurrentText("Confusión")
    capture("04-2-diabetes.png")
    window.close()


if __name__ == "__main__":
    main()
