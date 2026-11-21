"""Abre las aplicaciones de escritorio de la unidad 3."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Fundamentos de IA · Unidad 3")
    parser.add_argument(
        "actividad", nargs="?", default="fhcp", choices=["fhcp", "peliculas", "knn", "arboles"]
    )
    args = parser.parse_args()
    from ia_unidad3.interface import MainWindow, prepare_app

    app = prepare_app()
    window = MainWindow(args.actividad)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
