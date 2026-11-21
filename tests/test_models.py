import numpy as np
import pytest

from ia_unidad3 import knn, trees


@pytest.mark.parametrize(
    "metric,expected", [("Euclidiana", 5.0), ("Manhattan", 7.0), ("Mixta", 12.0)]
)
def test_distance_definitions(metric, expected):
    assert knn.distances([0, 0], [[3, 4]], metric)[0] == expected


def test_vote_tie_uses_distance_then_class_order():
    model = knn.ManualKNN(2).fit([[-1], [1]], [2, 0])
    assert model.predict_one([0]) == 0
    assert model.predict_one([0.5]) == 0


def test_scaler_is_fitted_only_with_training():
    model = knn.ManualKNN(1).fit([[0, 5], [2, 5]], [0, 1])
    before = model.mean.copy()
    model.predict([[1000, 1000]])
    np.testing.assert_equal(model.mean, before)
    np.testing.assert_equal(model.mean, [1, 5])
    np.testing.assert_equal(model.scale, [1, 1])


@pytest.mark.parametrize("k", [0, -1, 3])
def test_invalid_k(k):
    with pytest.raises(ValueError):
        knn.ManualKNN(k).fit([[0], [1]], [0, 1])


def test_query_shape_and_nonfinite_values():
    model = knn.ManualKNN(1).fit([[0, 1], [1, 1]], [0, 1])
    for query in ([0], [float("nan"), 1]):
        with pytest.raises(ValueError):
            model.predict_one(query)


def assert_partitions(indices, size):
    sets = [set(values) for values in indices.values()]
    assert len(set.union(*sets)) == size
    assert all(not a & b for i, a in enumerate(sets) for b in sets[i + 1 :])


def test_knn_experiment_is_reproducible_without_test_selection():
    first, models = knn.experiment()
    second, _ = knn.experiment()
    assert first["resultados"] == second["resultados"]
    assert_partitions(first["indices"], 360)
    combined = first["indices"]["entrenamiento"] + first["indices"]["validacion"]
    for name, result in first["resultados"].items():
        best = max(result["validacion"], key=lambda item: (item["f1_macro"], -item["k"]))
        assert best["k"] == result["k"]
        np.testing.assert_allclose(models[name].mean, np.asarray(first["x"])[combined].mean(axis=0))
        truth = np.asarray(first["y"])[first["indices"]["prueba"]]
        expected = np.mean(truth == result["predicciones"])
        assert expected == result["prueba"]["accuracy"]


def test_confusion_metrics_hand_calculated():
    result = knn.scores([0, 0, 1, 2], [0, 1, 1, 2])
    assert result["confusion"] == [[1, 1, 0], [0, 1, 0], [0, 0, 1]]
    assert result["accuracy"] == 0.75
    assert result["f1_macro"] == pytest.approx(7 / 9)


@pytest.mark.parametrize("name,size", [("Iris", 150), ("Diabetes", 768)])
def test_tree_holdout_and_median_imputation(name, size):
    record, model, frame = trees.experiment(name)
    assert_partitions(record["indices"], size)
    assert len(record["indices"]["prueba"]) in (30, 154)
    selected = max(record["seleccion"], key=lambda row: (row["f1_macro"], -row["profundidad"]))
    assert selected["profundidad"] == record["profundidad"]
    combined = record["indices"]["entrenamiento"] + record["indices"]["validacion"]
    np.testing.assert_allclose(model[0].statistics_, frame.iloc[combined].median().to_numpy())
    truth, prediction = np.array(record["real"]), np.array(record["predicciones"])
    assert float(np.mean(truth == prediction)) == record["accuracy"]
    assert sum(map(sum, record["confusion"])) == len(truth)


def test_diabetes_zero_replacement_is_limited_to_physiological_columns():
    frame, _, _ = trees.load_data("Diabetes")
    assert frame["Insulin"].isna().any()
    assert (frame["Pregnancies"] == 0).any()
    assert not frame["Pregnancies"].isna().any()
