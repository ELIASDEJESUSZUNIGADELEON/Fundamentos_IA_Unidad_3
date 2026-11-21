"""KNN manual: escalado, distancias, voto, particiones y evaluación."""

from collections import Counter

import numpy as np

from .common import save_csv, save_json, timestamp

METRICS = ("Euclidiana", "Manhattan", "Mixta")
LABELS = ["Arroz", "Cebada", "Trigo"]


def distances(query, training, metric="Euclidiana"):
    delta = np.abs(np.asarray(training, dtype=float) - np.asarray(query, dtype=float))
    euclidean = np.sqrt(np.sum(delta**2, axis=-1))
    manhattan = delta.sum(axis=-1)
    if metric == "Euclidiana":
        return euclidean
    if metric == "Manhattan":
        return manhattan
    if metric == "Mixta":
        return euclidean + manhattan
    raise ValueError("Distancia desconocida.")


class ManualKNN:
    def __init__(self, k=5, metric="Euclidiana"):
        self.k, self.metric = k, metric

    def fit(self, x, y):
        x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=int)
        if x.ndim != 2 or len(x) != len(y) or not np.isfinite(x).all():
            raise ValueError("Se requieren observaciones finitas y etiquetas alineadas.")
        if not isinstance(self.k, int) or not 1 <= self.k <= len(x):
            raise ValueError("k debe estar entre 1 y el tamaño del entrenamiento.")
        if self.metric not in METRICS:
            raise ValueError("Distancia desconocida.")
        self.mean = x.mean(axis=0)
        self.scale = x.std(axis=0)
        self.scale[self.scale == 0] = 1
        self.x = (x - self.mean) / self.scale
        self.raw_x, self.y = x.copy(), y.copy()
        return self

    def neighbors(self, query):
        query = np.asarray(query, dtype=float)
        if query.shape != self.mean.shape or not np.isfinite(query).all():
            raise ValueError("La consulta debe tener las mismas variables y valores finitos.")
        d = distances((query - self.mean) / self.scale, self.x, self.metric)
        selected = np.argsort(d, kind="stable")[: self.k]
        return selected, d[selected]

    def predict_one(self, query):
        selected, d = self.neighbors(query)
        counts = Counter(self.y[selected].tolist())
        return min(counts, key=lambda c: (-counts[c], float(d[self.y[selected] == c].sum()), c))

    def predict(self, queries):
        return np.array([self.predict_one(q) for q in queries])


def scores(y_true, y_pred, classes=3):
    matrix = np.zeros((classes, classes), dtype=int)
    for a, b in zip(y_true, y_pred):
        matrix[int(a), int(b)] += 1
    per_class = []
    for i in range(classes):
        tp = int(matrix[i, i])
        precision = tp / int(matrix[:, i].sum()) if matrix[:, i].sum() else 0.0
        recall = tp / int(matrix[i].sum()) if matrix[i].sum() else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class.append({"precision": precision, "recall": recall, "f1": f1})
    return {
        "accuracy": float(np.trace(matrix) / matrix.sum()),
        "f1_macro": float(np.mean([s["f1"] for s in per_class])),
        "confusion": matrix.tolist(),
        "por_clase": per_class,
    }


def synthetic(seed=2430085, per_class=120):
    rng = np.random.default_rng(seed)
    means = [(5.2, 1.9), (7.1, 3.1), (6.1, 2.9)]
    x = np.vstack([rng.multivariate_normal(m, [[0.6, 0.2], [0.2, 0.22]], per_class) for m in means])
    y = np.repeat(np.arange(3), per_class)
    return x, y


def split_indices(y, seed=2430085):
    rng = np.random.default_rng(seed)
    parts = [[], [], []]
    for label in np.unique(y):
        indices = rng.permutation(np.flatnonzero(y == label))
        a, b = int(len(indices) * 0.6), int(len(indices) * 0.8)
        for part, chunk in zip(parts, np.split(indices, [a, b])):
            part.extend(chunk.tolist())
    return [np.array(rng.permutation(p), dtype=int) for p in parts]


def experiment(seed=2430085):
    x, y = synthetic(seed)
    train, validation, test = split_indices(y, seed)
    results = {}
    models = {}
    for metric in METRICS:
        candidates = []
        for k in range(1, 16, 2):
            model = ManualKNN(k, metric).fit(x[train], y[train])
            candidates.append(
                {
                    "k": k,
                    "f1_macro": scores(y[validation], model.predict(x[validation]))["f1_macro"],
                }
            )
        best = max(candidates, key=lambda row: (row["f1_macro"], -row["k"]))
        final = ManualKNN(best["k"], metric).fit(
            x[np.r_[train, validation]], y[np.r_[train, validation]]
        )
        prediction = final.predict(x[test])
        results[metric] = {
            "k": best["k"],
            "validacion": candidates,
            "prueba": scores(y[test], prediction),
            "predicciones": prediction.tolist(),
        }
        models[metric] = final
    record = {
        "fecha_utc": timestamp(),
        "semilla": seed,
        "clases": LABELS,
        "datos_sinteticos": True,
        "variables": ["Longitud (mm)", "Ancho (mm)"],
        "x": x.tolist(),
        "y": y.tolist(),
        "indices": {
            "entrenamiento": train.tolist(),
            "validacion": validation.tolist(),
            "prueba": test.tolist(),
        },
        "resultados": results,
    }
    return record, models


def export_experiment(folder, record, models):
    save_json(folder / "experimento.json", record)
    save_json(
        folder / "modelos.json",
        {
            metric: {
                "k": model.k,
                "media": model.mean.tolist(),
                "escala": model.scale.tolist(),
                "x": model.raw_x.tolist(),
                "y": model.y.tolist(),
            }
            for metric, model in models.items()
        },
    )
    test = record["indices"]["prueba"]
    save_csv(
        folder / "predicciones.csv",
        [
            {
                "indice": i,
                "real": record["y"][i],
                **{m: record["resultados"][m]["predicciones"][j] for m in METRICS},
            }
            for j, i in enumerate(test)
        ],
    )


def draw_regions(figure, record, models, query=None, metric=None):
    figure.clear()
    x, y = np.asarray(record["x"]), np.asarray(record["y"])
    metrics = [metric] if metric else list(METRICS)
    colors = ["#258d9b", "#f2b84c", "#945fbe"]
    from matplotlib.colors import ListedColormap

    xx, yy = np.meshgrid(
        np.linspace(x[:, 0].min() - 0.5, x[:, 0].max() + 0.5, 85),
        np.linspace(x[:, 1].min() - 0.4, x[:, 1].max() + 0.4, 65),
    )
    for n, name in enumerate(metrics, 1):
        ax = figure.add_subplot(1, len(metrics), n)
        model = models[name]
        predicted = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        ax.contourf(
            xx, yy, predicted, levels=[-0.5, 0.5, 1.5, 2.5], cmap=ListedColormap(colors), alpha=0.16
        )
        for label, color in enumerate(colors):
            mask = y == label
            ax.scatter(x[mask, 0], x[mask, 1], s=12, c=color, alpha=0.7, label=LABELS[label])
        if query is not None:
            selected, _ = model.neighbors(query)
            ax.scatter(
                model.raw_x[selected, 0],
                model.raw_x[selected, 1],
                s=90,
                facecolors="none",
                edgecolors="#152b42",
                linewidths=1.5,
            )
            ax.scatter(*query, marker="*", s=230, c="#e35542", edgecolors="white", zorder=5)
        score = record["resultados"][name]["prueba"]["accuracy"]
        ax.set(
            title=f"{name} · k={model.k} · acierto={score:.1%}",
            xlabel="Longitud (mm)",
            ylabel="Ancho (mm)",
        )
        ax.legend(fontsize=8, loc="upper left")
    figure.tight_layout()
