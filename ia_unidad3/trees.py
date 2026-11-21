"""Árboles de clasificación con selección por validación y prueba reservada."""

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier, plot_tree

from .common import ROOT, save_csv, save_json, timestamp


def load_data(name="Iris"):
    folder = ROOT / "04-aprendizaje-automatico/datos"
    if name == "Iris":
        frame = pd.read_csv(
            folder / "iris.data.csv",
            header=None,
            names=["Largo sépalo", "Ancho sépalo", "Largo pétalo", "Ancho pétalo", "Clase"],
        )
        names = sorted(frame["Clase"].unique())
        y = frame.pop("Clase").map({label: i for i, label in enumerate(names)}).to_numpy(dtype=int)
    elif name == "Diabetes":
        frame = pd.read_csv(folder / "diabetes.csv")
        y = frame.pop("Outcome").to_numpy(dtype=int)
        names = ["Sin diabetes", "Con diabetes"]
        for column in ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]:
            frame[column] = frame[column].replace(0, np.nan)
    else:
        raise ValueError("Selecciona Iris o Diabetes.")
    return frame, y, names


def experiment(name="Iris", seed=2430085, criterion="entropy", depths=(2, 3, 4, 5, 6)):
    if criterion not in ("gini", "entropy") or not depths or any(d < 1 for d in depths):
        raise ValueError("Criterio o profundidad inválidos.")
    frame, y, names = load_data(name)
    indices = np.arange(len(frame))
    trainval, test = train_test_split(indices, test_size=0.2, stratify=y, random_state=seed)
    train, validation = train_test_split(
        trainval, test_size=0.25, stratify=y[trainval], random_state=seed
    )
    candidates = []
    for depth in depths:
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            DecisionTreeClassifier(
                max_depth=int(depth), criterion=criterion, random_state=seed, min_samples_leaf=3
            ),
        )
        model.fit(frame.iloc[train], y[train])
        prediction = model.predict(frame.iloc[validation])
        candidates.append(
            {
                "profundidad": int(depth),
                "f1_macro": float(
                    f1_score(y[validation], prediction, average="macro", zero_division=0)
                ),
            }
        )
    selected = max(candidates, key=lambda row: (row["f1_macro"], -row["profundidad"]))[
        "profundidad"
    ]
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        DecisionTreeClassifier(
            max_depth=selected, criterion=criterion, random_state=seed, min_samples_leaf=3
        ),
    )
    model.fit(frame.iloc[trainval], y[trainval])
    prediction = model.predict(frame.iloc[test])
    record = {
        "fecha_utc": timestamp(),
        "dataset": name,
        "semilla": seed,
        "filas": len(frame),
        "variables": list(frame.columns),
        "clases": names,
        "criterio": criterion,
        "profundidad": selected,
        "faltantes_por_variable": frame.isna().sum().astype(int).to_dict(),
        "indices": {
            "entrenamiento": train.tolist(),
            "validacion": validation.tolist(),
            "prueba": test.tolist(),
        },
        "seleccion": candidates,
        "accuracy": float(accuracy_score(y[test], prediction)),
        "f1_macro": float(f1_score(y[test], prediction, average="macro", zero_division=0)),
        "confusion": confusion_matrix(y[test], prediction, labels=list(range(len(names)))).tolist(),
        "reporte": classification_report(
            y[test],
            prediction,
            labels=list(range(len(names))),
            target_names=names,
            output_dict=True,
            zero_division=0,
        ),
        "real": y[test].tolist(),
        "predicciones": prediction.tolist(),
        "importancias": model[-1].feature_importances_.tolist(),
    }
    return record, model, frame


def export_experiment(folder, record, model):
    save_json(folder / "evaluacion.json", record)
    save_csv(
        folder / "predicciones.csv",
        [
            {"indice": index, "real": real, "prediccion": prediction}
            for index, real, prediction in zip(
                record["indices"]["prueba"], record["real"], record["predicciones"]
            )
        ],
    )
    estimator = model[-1]
    tree = estimator.tree_
    save_json(
        folder / "arbol.json",
        {
            "variables": record["variables"],
            "clases": record["clases"],
            "imputacion_mediana": model[0].statistics_.tolist(),
            "hijos_izquierdos": tree.children_left.tolist(),
            "hijos_derechos": tree.children_right.tolist(),
            "variable": tree.feature.tolist(),
            "umbral": tree.threshold.tolist(),
            "valor": tree.value.tolist(),
        },
    )


def draw(figure, record, model, view="Árbol"):
    figure.clear()
    ax = figure.add_subplot(111)
    if view == "Árbol":
        plot_tree(
            model[-1],
            feature_names=record["variables"],
            class_names=record["clases"],
            filled=True,
            rounded=True,
            fontsize=7 if record["dataset"] == "Diabetes" else 10,
            ax=ax,
        )
        ax.set_title(
            f"{record['dataset']} · profundidad {record['profundidad']} · criterio {record['criterio']}"
        )
    elif view == "Confusión":
        matrix = np.array(record["confusion"])
        ax.imshow(matrix, cmap="YlGnBu")
        for (r, c), value in np.ndenumerate(matrix):
            ax.text(
                c,
                r,
                str(value),
                ha="center",
                va="center",
                fontsize=18,
                color="white" if value > matrix.max() * 0.5 else "#152b42",
            )
        ax.set(
            xticks=range(len(record["clases"])),
            yticks=range(len(record["clases"])),
            xticklabels=record["clases"],
            yticklabels=record["clases"],
            xlabel="Predicción",
            ylabel="Real",
            title=f"Prueba reservada · exactitud {record['accuracy']:.1%} · F1 macro {record['f1_macro']:.3f}",
        )
    else:
        ax.barh(record["variables"], record["importancias"], color="#258d9b")
        ax.set(xlabel="Importancia", title="Variables utilizadas por el árbol")
    figure.tight_layout()
