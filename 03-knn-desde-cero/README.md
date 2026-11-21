# K vecinos más cercanos desde cero

**Elias de Jesus Zuñiga de Leon · Matrícula 2430085**

Implementación manual de distancias, normalización, selección de vecinos, votación, matrices de confusión, exactitud, precisión, recall y F1 macro. No utiliza `KNeighborsClassifier`.

```powershell
python iniciar.py knn
python ejecutar.py knn --semilla 2430085 --salida nuevo_knn
```

Desde la raíz de la unidad. La GUI permite cambiar distancia y semilla, volver a entrenar, clasificar un punto por longitud/ancho y exportar el experimento. La estrella identifica la consulta y los círculos resaltan sus vecinos.

Se generan 360 observaciones sintéticas de Arroz, Cebada y Trigo. Hay 216 ejemplos de entrenamiento, 72 de validación y 72 de prueba. Se elige k entre 1, 3, …, 15 mediante F1 macro de validación, con preferencia por k menor en empates. El escalador de cada candidato se ajusta solo con entrenamiento. Tras elegir k se reajusta con entrenamiento más validación.

Se comparan euclidiana, Manhattan y mixta (suma de las dos anteriores). Los empates de votos se resuelven por distancia acumulada y orden de clase. Las tres seleccionaron k=13. La exactitud de prueba fue 70.83%, 72.22% y 70.83%, respectivamente.

- [Cuaderno ejecutado](knn_manual.ipynb).
- [Experimento, particiones y métricas](resultados/experimento.json).
- [Modelos y escaladores](resultados/modelos.json).
- [Predicciones de prueba](resultados/predicciones.csv).

Las clases se solapan intencionalmente. Los resultados corresponden a datos sintéticos; los votos del clasificador no son probabilidades calibradas.
