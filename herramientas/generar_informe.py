"""Genera el informe breve a partir de los resultados medidos."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = json.loads(
        (ROOT / "01-fhcp-challenge/resultados/comparacion.json").read_text(encoding="utf-8")
    )
    rows = []
    for row in data["resumen"]:
        rows.append(
            f"| {row['nombre']} | {row['intentos']} | {row['exitos']} | {row['exitos'] / row['intentos']:.1%} | {row['costo_medio']:.3f} | {row['tiempo_medio_s']:.4f} |"
        )
    text = (
        """# Informe: ciclos hamiltonianos y metaheurísticas

**Elias de Jesus Zuñiga de Leon · Matrícula 2430085**

Trabajo en equipo con Diego Eduardo Zapata Aguilar, Junior Arturo Vázquez Leonel, César Euresti y Eder Omar Zúñiga Zavala.

## Objetivo y representación

Buscar un ciclo que visite una sola vez todos los vértices y regrese al origen. El núcleo representa grafos no dirigidos mediante adyacencia CSR inmutable; cada candidato es una permutación de índices de vértices. Las etiquetas externas originales se conservan para mostrar la solución.

El costo cuenta los pares consecutivos sin arista, incluido el cierre. El objetivo es minimizarlo hasta cero. Todo candidato de costo cero debe pasar un validador independiente que comprueba longitud, rango, repeticiones, aristas consecutivas y cierre. Los certificados de referencia se leen aparte; nunca se entregan a los solvers como candidatos iniciales.

## Algoritmos

- Genético: población de permutaciones, torneo, cruce de orden, mutación y elitismo.
- Recocido simulado: movimientos locales y aceptación probabilística, con enfriamiento.
- Colonia de hormigas: construcción de rutas guiada por feromonas y vecindad.
- Colonia de abejas: fuentes de soluciones, exploración y abandono según intentos.
- Evolución diferencial: población de claves reales que se decodifican como permutaciones.
- Enjambre de partículas: posiciones y velocidades sobre claves reales, con memoria individual y colectiva.

Se utilizaron las variantes guiadas del proyecto del equipo. Los parámetros completos y el identificador efectivo de cada variante se conservan en cada corrida de [comparacion.json](resultados/comparacion.json).

## Protocolo local

Tres instancias: graph1, graph2 y graph18; tres semillas: 2430085, 2430086 y 2430087; seis algoritmos. Son 54 intentos con un máximo de 3,000 evaluaciones y dos segundos de solver por intento. El primer límite alcanzado detiene la ejecución. La búsqueda tiene límites cooperativos: se registra cualquier sobrepaso temporal.

La ejecución fue secuencial. Los tiempos se midieron con el contador de alta resolución del solver e incluyen su validación. Pueden variar con la carga del equipo; no se presentan como un ranking definitivo. No se normalizan con los tiempos de otras máquinas ni se atribuyen a esta ejecución los resultados históricos del equipo.

## Resultados medidos

| Algoritmo | Intentos | Ciclos certificados | Tasa de éxito | Costo medio | Tiempo medio (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
"""
        + "\n".join(rows)
        + """

La colonia de abejas encontró un ciclo en graph2 con la semilla 2430087. La ruta se conserva en su registro de ejecución y se vuelve a certificar al validar la entrega. Los restantes agotamientos se mantienen en el denominador; no se eliminan para mejorar la tasa de éxito.

## Referencia externa y métricas

El FHCP Challenge Set de Flinders contiene 1,001 instancias conocidas como hamiltonianas, de 66 a 9,528 vértices. Sus soluciones públicas constituyen certificados verificables de existencia, no resultados de nuestros solvers. El certificado de graph1 se validó con sus 66 vértices y cierre correcto. Compararlo con una búsqueda fallida no convierte esa búsqueda en un éxito ni permite atribuirle el tiempo de lectura del certificado.

La tasa de éxito es el número de intentos con ciclo certificado dividido entre los intentos ejecutados. Precisión mide verdaderos positivos entre predicciones positivas; recall, verdaderos positivos entre los positivos reales; F1 es su media armónica. Sin definir un problema de clasificación con positivos y negativos no sustituyen a la tasa de éxito de este benchmark. Por eso se usan para KNN y árboles, mientras FHCP se evalúa mediante ciclos certificados, costo residual, evaluaciones y tiempo.

## Conclusiones y límites

En este presupuesto corto, varias variantes llegaron a rutas con pocas aristas ausentes, pero solo un intento completó un ciclo certificado. Un costo bajo no basta para resolver el problema. Agotar tiempo o evaluaciones tampoco demuestra que un grafo sea no hamiltoniano.

La muestra es exploratoria: tres grafos y tres semillas no permiten generalizar a las 1,001 instancias. Las seis familias están ejecutables; la campaña local no pretende sustituir las campañas grandes documentadas por el equipo. Las claves reales preservan permutaciones al decodificarse, aunque no garantizan aristas válidas; la validación final sigue siendo necesaria.

## Referencias

- Michael Haythorpe (2018), *FHCP Challenge Set: The first set of structurally difficult instances of the Hamiltonian cycle problem*, Bulletin of the ICA, 83:98–107.
- [FHCP Challenge Set y certificados oficiales](https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/fhcp-challenge-set/).
- [Proyecto original del equipo](https://github.com/ZapataFrame/FHCP-Challenge).
- [Procedencia de esta entrega](../ORIGENES.md).
"""
    )
    (ROOT / "01-fhcp-challenge/informe.md").write_text(text, encoding="utf-8")
    print("Informe generado con", len(data["corridas"]), "intentos medidos.")


if __name__ == "__main__":
    main()
