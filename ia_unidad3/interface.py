"""Ventanas Qt de las cuatro actividades, con resultados de sus motores reales."""

import json
import sys
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QFont, QFontDatabase
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from . import fhcp, knn, movies, trees
from .common import ROOT, save_csv, save_json

STYLE = """
QWidget {font-family: 'Segoe UI'; color:#213448; font-size:13px; background:#f3f6fa;}
QFrame#navigation {background:#162c43; border:0;}
QFrame#navigation QLabel {background:transparent; color:#e4eff7;}
QFrame#navigation QPushButton {background:transparent; color:#bcd0e0; text-align:left; padding:16px; border:0; border-radius:8px;}
QFrame#navigation QPushButton:checked {background:#294b64; color:white; font-weight:600;}
QLabel#title {font-size:27px; font-weight:700;}
QLabel#muted {color:#60778b;}
QLabel#result {background:#e6f2f3; color:#176170; border-radius:8px; padding:12px; font-size:15px;}
QPushButton {background:#217e8c; color:white; border:0; border-radius:5px; padding:9px 15px;}
QPushButton:hover {background:#196a77;}
QPushButton:disabled {background:#bacbd1;}
QComboBox,QSpinBox,QDoubleSpinBox,QLineEdit {background:white; border:1px solid #c6d3df; border-radius:5px; padding:7px;}
QTableWidget {background:white; alternate-background-color:#f3f8fa; gridline-color:#e4ebf1; border:1px solid #d2dee7;}
QHeaderView::section {background:#e6edf4; color:#29475e; padding:8px; border:0; font-weight:600;}
QSplitter::handle {background:#d6e1e9; height:5px; width:5px;}
"""


def prepare_app():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    for name in ("segoeui.ttf", "seguisb.ttf", "seguisym.ttf", "consola.ttf"):
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(STYLE)
    return app


def label(text, object_name=None):
    widget = QLabel(text)
    widget.setWordWrap(True)
    if object_name:
        widget.setObjectName(object_name)
    return widget


def button(text, action, row):
    widget = QPushButton(text)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    widget.clicked.connect(action)
    row.addWidget(widget)
    return widget


def combo(items):
    widget = QComboBox()
    widget.addItems(items)
    return widget


def integer(value, minimum=1, maximum=1000000):
    widget = QSpinBox()
    widget.setRange(minimum, maximum)
    widget.setValue(value)
    return widget


def decimal(value, minimum=-100, maximum=100):
    widget = QDoubleSpinBox()
    widget.setRange(minimum, maximum)
    widget.setDecimals(2)
    widget.setValue(value)
    return widget


def field(row, name, widget):
    column = QVBoxLayout()
    column.setSpacing(4)
    column.addWidget(label(name, "muted"))
    column.addWidget(widget)
    row.addLayout(column)
    return widget


def table(headers):
    widget = QTableWidget(0, len(headers))
    widget.setHorizontalHeaderLabels(headers)
    widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    widget.setAlternatingRowColors(True)
    widget.verticalHeader().hide()
    widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return widget


def fill_table(widget, rows):
    widget.setRowCount(len(rows))
    for r, values in enumerate(rows):
        for c, value in enumerate(values):
            widget.setItem(r, c, QTableWidgetItem(str(value)))


class Plot(FigureCanvasQTAgg):
    def __init__(self):
        self.figure = Figure(figsize=(10, 6), dpi=100, facecolor="white")
        super().__init__(self.figure)
        self.setMinimumSize(400, 280)


class Worker(QThread):
    done = Signal(object)
    failed = Signal(str)
    progress = Signal(str)

    def __init__(self, function, parent=None):
        super().__init__(parent)
        self.function = function

    def run(self):
        try:
            self.done.emit(self.function(self))
        except Exception as error:
            self.failed.emit(str(error))


class Page(QWidget):
    def __init__(self, title, subtitle):
        super().__init__()
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(26, 22, 26, 22)
        self.root.setSpacing(14)
        self.root.addWidget(label(title, "title"))
        self.root.addWidget(label(subtitle, "muted"))
        self.controls = QHBoxLayout()
        self.root.addLayout(self.controls)
        self.actions = QHBoxLayout()
        self.root.addLayout(self.actions)
        self.result = label("Listo para comenzar.", "result")
        self.root.addWidget(self.result)
        self.worker = None

    def run_task(self, function, complete):
        if self.worker is not None and self.worker.isRunning():
            return
        buttons = self.findChildren(QPushButton)
        for widget in buttons:
            widget.setEnabled(False)
        self.worker = Worker(function, self)
        self.worker.done.connect(complete)
        self.worker.progress.connect(self.result.setText)
        self.worker.failed.connect(
            lambda error: QMessageBox.warning(self, "No se pudo completar", error)
        )
        self.worker.finished.connect(lambda: [widget.setEnabled(True) for widget in buttons])
        self.worker.start()

    def choose_folder(self):
        result = QFileDialog.getExistingDirectory(self, "Guardar resultados")
        return Path(result) if result else None


class FHCPPage(Page):
    def __init__(self):
        super().__init__(
            "01  /  Ciclos hamiltonianos",
            "Explora el proyecto del equipo: seis metaheurísticas y validación independiente de las rutas.",
        )
        self.instance = field(
            self.controls,
            "Instancia FHCP",
            combo(
                [
                    "graph1",
                    "graph2",
                    "graph18",
                    "graph58",
                    "graph268",
                    "graph48",
                    "graph175",
                    "graph74",
                    "graph479",
                    "graph1001",
                ]
            ),
        )
        self.algorithm = field(self.controls, "Metaheurística", combo(list(fhcp.NAMES.values())))
        self.algorithm.setCurrentIndex(1)
        self.seed = field(self.controls, "Semilla", integer(2430085, 0, 2147483647))
        self.evaluations = field(
            self.controls, "Máximo de evaluaciones", integer(3000, 40, 1000000)
        )
        self.seconds = field(self.controls, "Límite (segundos)", decimal(3, 0.1, 60))
        button("Ejecutar búsqueda", self.start, self.actions)
        button("Ver certificado de referencia", self.show_reference, self.actions)
        button("Comparación guardada", self.show_benchmark, self.actions)
        button("Exportar resultado", self.export, self.actions)
        self.plot = Plot()
        self.root.addWidget(self.plot, 1)
        self.record = None
        self.show_reference()

    def start(self):
        args = (
            self.instance.currentText(),
            list(fhcp.NAMES)[self.algorithm.currentIndex()],
            self.seed.value(),
            self.evaluations.value(),
            self.seconds.value(),
        )
        self.result.setText("Buscando una ruta dentro del presupuesto…")
        self.run_task(lambda worker: fhcp.solve(*args), self.apply_result)

    def apply_result(self, pair):
        self.record, graph = pair
        result = self.record["resultado"]
        state = "Ciclo certificado" if result["validation"]["valid"] else "Presupuesto agotado"
        self.result.setText(
            f"{state}  ·  Costo: {result['best_cost']} aristas ausentes  ·  Evaluaciones: {result['counters']['evaluations_completed']}  ·  Tiempo: {result['timing']['solver_ns'] / 1e9:.3f} s"
        )
        fhcp.draw_graph(
            self.plot.figure,
            graph,
            result["best_route"],
            f"{self.record['instancia']} · {fhcp.NAMES[self.record['algoritmo']]} · mejor ruta del solver",
        )
        self.plot.draw()

    def show_reference(self):
        graph, route = fhcp.reference(self.instance.currentText())
        self.result.setText(
            f"Certificado oficial validado: {len(route)} vértices, una visita por vértice y cierre correcto. Esta ruta no proviene del solver."
        )
        fhcp.draw_graph(
            self.plot.figure,
            graph,
            route,
            f"{self.instance.currentText()} · certificado de referencia FHCP",
        )
        self.plot.draw()

    def show_benchmark(self):
        path = ROOT / "01-fhcp-challenge/resultados/comparacion.json"
        if not path.exists():
            QMessageBox.information(
                self, "Comparación", "Primero ejecuta la comparación desde ejecutar.py comparar."
            )
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        self.plot.figure.clear()
        left, right = self.plot.figure.subplots(1, 2)
        names = [r["algoritmo"].upper() for r in data["resumen"]]
        left.bar(names, [r["costo_medio"] for r in data["resumen"]], color="#258d9b")
        left.set(title="Aristas ausentes: menor es mejor", ylabel="Costo medio")
        right.bar(names, [r["tiempo_medio_s"] for r in data["resumen"]], color="#eead4b")
        right.set(title="Tiempo medido por intento", ylabel="Segundos")
        self.plot.figure.tight_layout()
        self.plot.draw()
        successes = sum(r["exitos"] for r in data["resumen"])
        self.result.setText(
            f"{len(data['corridas'])} intentos reales · {len(data['instancias'])} grafos · {len(data['semillas'])} semillas · {successes} ciclos certificados. Agotar el presupuesto no demuestra que no exista ciclo."
        )

    def export(self):
        folder = self.choose_folder()
        if folder:
            if self.record:
                save_json(folder / "busqueda_fhcp.json", self.record)
            self.plot.figure.savefig(folder / "fhcp.png", dpi=150)


class MoviesPage(Page):
    def __init__(self):
        super().__init__(
            "02  /  Colección de películas",
            "Crawler de Wikipedia con deduplicación, procedencia y exportación a CSV. Datos reales de listas anuales.",
        )
        self.search = field(self.controls, "Buscar título o créditos", QLineEdit())
        self.year = field(
            self.controls, "Año", combo(["Todos", "2024", "2023", "2022", "2021", "2020", "2019"])
        )
        self.limit = field(self.controls, "Máximo de películas", integer(1000, 1, 1000))
        button("Crear un CSV nuevo", self.start, self.actions)
        button("Abrir CSV", self.open_csv, self.actions)
        button("Exportar selección", self.export, self.actions)
        button("Ver artículo", self.open_article, self.actions)
        self.table = table(["Título", "Año", "Compañía", "Equipo y reparto"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 240)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(1, 60)
        self.root.addWidget(self.table, 1)
        self.rows = (
            movies.read_movies()
            if (ROOT / "02-dataset-peliculas/datos/peliculas.csv").exists()
            else []
        )
        self.search.textChanged.connect(self.refresh)
        self.year.currentTextChanged.connect(self.refresh)
        self.refresh()

    def refresh(self):
        term, year = self.search.text().casefold(), self.year.currentText()
        self.filtered = [
            row
            for row in self.rows
            if (year == "Todos" or str(row["anio"]) == year)
            and term in (row["titulo"] + " " + row["equipo_y_reparto"]).casefold()
        ]
        fill_table(
            self.table,
            [
                [row["titulo"], row["anio"], row["compania"], row["equipo_y_reparto"]]
                for row in self.filtered
            ],
        )
        stats = movies.summary(self.rows)
        self.result.setText(
            f"{stats['peliculas']} películas  ·  {stats['urls_unicas']} URL únicas  ·  {len(self.filtered)} visibles  ·  Años: {', '.join(stats['por_anio'])}"
        )

    def start(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Nuevo dataset", "peliculas_nuevas.csv", "CSV (*.csv)"
        )
        if not path:
            return
        limit = self.limit.value()

        def work(worker):
            return movies.crawl(
                path, limit, progress=worker.progress.emit, stop=worker.isInterruptionRequested
            )

        def complete(pair):
            self.rows = pair[0]
            self.refresh()

        self.run_task(work, complete)

    def open_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Dataset de esta actividad", "", "CSV (*.csv)")
        if path:
            try:
                rows = movies.read_movies(path)
                if rows and not set(movies.FIELDS) <= rows[0].keys():
                    raise ValueError("El CSV no tiene las columnas de esta actividad.")
                self.rows = rows
                self.refresh()
            except Exception as error:
                QMessageBox.warning(self, "CSV inválido", str(error))

    def export(self):
        if not self.filtered:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar selección", "seleccion.csv", "CSV (*.csv)"
        )
        if path:
            save_csv(path, self.filtered, movies.FIELDS)

    def open_article(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.filtered):
            url = self.filtered[row]["url"]
            if url.startswith("https://en.wikipedia.org/wiki/"):
                QDesktopServices.openUrl(QUrl(url))


class KNNPage(Page):
    def __init__(self):
        super().__init__(
            "03  /  Vecinos más cercanos",
            "Clasificación manual de semillas sintéticas. Elige una distancia y consulta un nuevo punto.",
        )
        self.metric_choice = field(self.controls, "Distancia", combo(knn.METRICS))
        self.seed = field(self.controls, "Semilla", integer(2430085, 0, 2147483647))
        self.length_input = field(self.controls, "Longitud (mm)", decimal(6.2, 1, 12))
        self.width_input = field(self.controls, "Ancho (mm)", decimal(2.6, 0.1, 8))
        button("Entrenar y comparar", self.start, self.actions)
        button("Clasificar punto", self.show_query, self.actions)
        button("Exportar experimento", self.export, self.actions)
        self.plot = Plot()
        self.root.addWidget(self.plot, 1)
        self.table = table(
            ["Distancia", "k por validación", "Exactitud de prueba", "F1 macro de prueba"]
        )
        self.table.setMaximumHeight(145)
        self.root.addWidget(self.table)
        self.metric_choice.currentTextChanged.connect(lambda: self.show_query())
        self.apply_result(knn.experiment())

    def start(self):
        seed = self.seed.value()
        self.run_task(lambda worker: knn.experiment(seed), self.apply_result)

    def apply_result(self, pair):
        self.record, self.models = pair
        fill_table(
            self.table,
            [
                [
                    name,
                    row["k"],
                    f"{row['prueba']['accuracy']:.1%}",
                    f"{row['prueba']['f1_macro']:.3f}",
                ]
                for name, row in self.record["resultados"].items()
            ],
        )
        self.show_query()

    def show_query(self):
        if not hasattr(self, "models"):
            return
        metric = self.metric_choice.currentText()
        query = [self.length_input.value(), self.width_input.value()]
        model = self.models[metric]
        predicted = model.predict_one(query)
        selected, _ = model.neighbors(query)
        votes = np.bincount(model.y[selected], minlength=3)
        self.result.setText(
            f"Punto ({query[0]:.2f}, {query[1]:.2f}) → {knn.LABELS[predicted]}  ·  k={model.k}  ·  Votos: {', '.join(f'{name} {n}' for name, n in zip(knn.LABELS, votes))}  ·  360 observaciones sintéticas"
        )
        knn.draw_regions(self.plot.figure, self.record, self.models, query, metric)
        self.plot.draw()

    def export(self):
        folder = self.choose_folder()
        if folder:
            knn.export_experiment(folder, self.record, self.models)
            self.plot.figure.savefig(folder / "consulta.png", dpi=150)


class TreesPage(Page):
    def __init__(self):
        super().__init__(
            "04  /  Árboles de decisión",
            "Análisis de Iris y diabetes: selección de profundidad por validación y evaluación en prueba reservada.",
        )
        self.dataset = field(self.controls, "Dataset", combo(["Iris", "Diabetes"]))
        self.criterion = field(self.controls, "Criterio", combo(["entropy", "gini"]))
        self.max_depth_input = field(
            self.controls, "Profundidad máxima a comparar", integer(6, 2, 10)
        )
        self.view = field(self.controls, "Vista", combo(["Árbol", "Confusión", "Importancias"]))
        button("Entrenar y evaluar", self.start, self.actions)
        button("Exportar resultados", self.export, self.actions)
        self.plot = Plot()
        self.root.addWidget(self.plot, 1)
        self.view.currentTextChanged.connect(self.redraw)
        self.apply_result(trees.experiment())

    def start(self):
        name, criterion, depth = (
            self.dataset.currentText(),
            self.criterion.currentText(),
            self.max_depth_input.value(),
        )
        self.run_task(
            lambda worker: trees.experiment(
                name, criterion=criterion, depths=tuple(range(2, depth + 1))
            ),
            self.apply_result,
        )

    def apply_result(self, result):
        self.record, self.model, self.frame = result
        r = self.record
        self.result.setText(
            f"{r['dataset']}  ·  {r['filas']} filas  ·  Profundidad elegida: {r['profundidad']}  ·  Exactitud de prueba: {r['accuracy']:.1%}  ·  F1 macro: {r['f1_macro']:.3f}  ·  {len(r['indices']['prueba'])} ejemplos de prueba"
        )
        self.redraw()

    def redraw(self):
        if hasattr(self, "record"):
            trees.draw(self.plot.figure, self.record, self.model, self.view.currentText())
            self.plot.draw()

    def export(self):
        folder = self.choose_folder()
        if folder:
            trees.export_experiment(folder, self.record, self.model)
            self.plot.figure.savefig(folder / "vista.png", dpi=150)


PAGES = {"fhcp": FHCPPage, "peliculas": MoviesPage, "knn": KNNPage, "arboles": TreesPage}


class MainWindow(QMainWindow):
    def __init__(self, activity="fhcp"):
        super().__init__()
        self.setWindowTitle("Fundamentos de IA · Unidad 3 · Elias · 2430085")
        self.resize(1450, 920)
        self.setMinimumSize(1100, 740)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        nav = QFrame()
        nav.setObjectName("navigation")
        nav.setFixedWidth(210)
        column = QVBoxLayout(nav)
        column.setContentsMargins(14, 28, 14, 24)
        column.addWidget(label("FUNDAMENTOS\nDE IA"))
        title = label("Unidad 3")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        column.addWidget(title)
        column.addSpacing(28)
        self.buttons = {}
        for key, text in [
            ("fhcp", "01  Ciclos FHCP"),
            ("peliculas", "02  Películas"),
            ("knn", "03  KNN manual"),
            ("arboles", "04  Árboles"),
        ]:
            control = button(text, lambda checked=False, name=key: self.open(name), column)
            control.setCheckable(True)
            self.buttons[key] = control
        column.addStretch()
        column.addWidget(label("Elias de Jesus\nZuñiga de Leon\n\nMatrícula 2430085"))
        layout.addWidget(nav)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(container)
        self.pages = {}
        self.open(activity)

    def open(self, name):
        if name not in self.pages:
            self.pages[name] = PAGES[name]()
            self.stack.addWidget(self.pages[name])
        self.stack.setCurrentWidget(self.pages[name])
        for key, control in self.buttons.items():
            control.setChecked(key == name)
        return self.pages[name]

    def closeEvent(self, event):
        for page in self.pages.values():
            if page.worker is not None and page.worker.isRunning():
                page.worker.requestInterruption()
                if not page.worker.wait(60000):
                    event.ignore()
                    return
        event.accept()
