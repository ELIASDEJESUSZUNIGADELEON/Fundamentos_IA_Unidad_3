# Ejecutar las actividades

## En este equipo

Desde PowerShell en `C:\Users\elias\Downloads\Said - github`:

```powershell
.\.venv-u3\Scripts\python.exe .\Fundamentos_IA_Unidad_3\iniciar.py
```

La ventana reúne las cuatro actividades. Para abrir una directamente, agrega `fhcp`, `peliculas`, `knn` o `arboles` al comando.

## Preparar otro equipo

Desde la raíz del repositorio, con Python 3.12 o posterior:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe iniciar.py knn
```

En Linux y macOS, el ejecutable equivalente es `.venv/bin/python`. Las aplicaciones de escritorio necesitan una sesión gráfica. No se requieren claves de API; el crawler sí necesita Internet.

## Ejecución desde terminal

Los siguientes ejemplos utilizan carpetas nuevas para conservar las ejecuciones anteriores:

```powershell
python ejecutar.py fhcp --instancia graph2 --algoritmo abc --semilla 2430087 --salida resultados_busqueda
python ejecutar.py comparar --salida resultados_comparacion
python ejecutar.py peliculas --maximo 1000 --salida resultados_peliculas
python ejecutar.py knn --salida resultados_knn
python ejecutar.py arboles --dataset Iris --salida resultados_iris
python ejecutar.py arboles --dataset Diabetes --salida resultados_diabetes
```

Usa el ejecutable del entorno virtual en lugar de `python` si no lo activaste. `--help` muestra todos los parámetros. Para FHCP están disponibles `ga`, `sa`, `as`, `abc`, `de` y `pso`; `--evaluaciones` y `--segundos` controlan el presupuesto. Las 1,001 instancias están en `01-fhcp-challenge/proyecto_equipo/data/raw/FHCPCS`.

El crawler solo visita las listas anuales configuradas de Wikipedia. Consulta robots.txt, realiza una petición a la vez con intervalo mínimo de 1.1 segundos y conserva la procedencia y la huella del CSV. Ante una respuesta de error se detiene; no intenta evadir restricciones. La GUI permite cargar el CSV incluido sin conexión.

## Cuadernos

Los cuatro archivos `.ipynb` contienen sus salidas y gráficas. Para volver a ejecutarlos desde un editor con Jupyter, selecciona el intérprete de este entorno y ejecuta todas las celdas. Conserva el repositorio completo: los cuadernos importan `ia_unidad3` y utilizan los datos locales.

El cuaderno FHCP analiza la comparación guardada y vuelve a validar los ciclos. El de películas verifica el CSV existente; no hace un rastreo nuevo. KNN y árboles vuelven a entrenar y exportan en `resultados/cuaderno/` dentro de sus actividades.

## Capturas y comprobaciones

```powershell
python herramientas/generar_capturas.py
python herramientas/validar_entrega.py
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Las siete capturas principales muestran salidas reales en un visor de texto plano, con el mismo formato sencillo de la unidad 1. Los TXT se conservan en `capturas/salidas/`; la comparación FHCP se lee de los resultados guardados y los ciclos se validan de nuevo. `--visible` muestra el visor durante la captura. Los registros de pruebas y de integridad están en `validacion/`.

Para consultar una salida en la terminal o abrirla en una ventana sencilla:

```powershell
python herramientas/ver_salida.py ciclo
python herramientas/ver_salida.py knn --ventana
```

Las capturas de las interfaces están en `capturas/gui/`. Se pueden regenerar con `python herramientas/generar_capturas_gui.py`. La interfaz adicional FHCP y los experimentos locales están separados del código original del equipo en `01-fhcp-challenge/proyecto_equipo/`, que se conserva sin modificar.

Las aplicaciones y los cuadernos se ejecutaron con Python 3.12. El núcleo original FHCP también se comprobó con Python 3.14, su versión de referencia. Para repetir esas pruebas desde `01-fhcp-challenge/proyecto_equipo`, utiliza Python 3.14 con NumPy y pytest:

```powershell
python -m pytest -q tests/test_graph.py tests/test_readers.py tests/test_routes.py tests/test_cycle_validation.py tests/test_cost.py tests/test_genetic.py tests/test_annealing.py tests/test_ant_system.py tests/test_abc.py tests/test_differential.py tests/test_particle_swarm.py tests/test_real_keys.py tests/test_permutation_operators.py tests/test_graph_guidance.py tests/test_search_enhancements.py
```

Esta selección comprueba grafos, operadores, seis familias de búsqueda y validación; no ejecuta las campañas históricas del equipo.
