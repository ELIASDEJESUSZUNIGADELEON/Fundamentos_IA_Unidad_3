"""Guarda salidas reales y captura un visor de texto sencillo, como en la unidad 1."""

import argparse
import os
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "herramientas"))
from ver_salida import ACTIVIDADES, ejecutar, mostrar


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args()
    if not args.visible:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    folder = ROOT / "capturas"
    logs = folder / "salidas"
    logs.mkdir(parents=True, exist_ok=True)
    for activity, name in ACTIVIDADES.items():
        output = StringIO()
        with redirect_stdout(output):
            ejecutar(activity)
        content = f"python herramientas/ver_salida.py {activity}\n\n" + output.getvalue()
        (logs / f"{name}.txt").write_text(content, encoding="utf-8")
        mostrar(content, activity, folder / f"{name}.png")
        app.processEvents()
        print("Captura sencilla:", name, flush=True)


if __name__ == "__main__":
    main()
