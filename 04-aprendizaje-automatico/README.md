# Aprendizaje automático: árboles de decisión

**Elias de Jesus Zuñiga de Leon · Matrícula 2430085**

Análisis de Iris y diabetes con árboles de clasificación. La GUI permite cambiar dataset, criterio y máxima profundidad, entrenar, consultar el árbol, la matriz de confusión y las importancias, y exportar resultados.

```powershell
python iniciar.py arboles
python ejecutar.py arboles --dataset Iris --salida nuevo_iris
python ejecutar.py arboles --dataset Diabetes --salida nuevo_diabetes
```

Se ejecutan desde la raíz de la unidad. La partición estratificada es 60/20/20. La profundidad se selecciona entre 2 y 6 por F1 macro de validación, favoreciendo el árbol más pequeño. Se refita con entrenamiento más validación y se evalúa una sola vez en prueba. Las métricas y predicciones se calculan por separado para cada dataset.

En diabetes, los ceros de `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin` y `BMI` se consideran faltantes y se imputan mediante medianas del entrenamiento. Los ceros de `Pregnancies` se conservan. El árbol usa las ocho variables del archivo.

- Iris: 150 filas, profundidad elegida 2 y exactitud de prueba 93.33% sobre 30 ejemplos.
- Diabetes: 768 filas, profundidad elegida 4 y exactitud de prueba 73.38% sobre 154 ejemplos.

[Cuaderno ejecutado](arboles_decision.ipynb) · [Resultados de Iris](resultados/iris/evaluacion.json) · [Resultados de diabetes](resultados/diabetes/evaluacion.json).

Cada carpeta de resultados contiene la estructura del árbol, medianas de imputación, predicciones, índices de las particiones y métricas por clase. El cuaderno añade revisión de faltantes, duplicados, correlaciones y las gráficas de ambos árboles.
