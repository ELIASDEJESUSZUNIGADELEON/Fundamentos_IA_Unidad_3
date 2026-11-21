# Procedencia de proyectos y datos

## FHCP: proyecto del equipo

Integrantes: Diego Eduardo Zapata Aguilar, Junior Arturo Vázquez Leonel, César Euresti, Eder Omar Zúñiga Zavala y Elías de Jesús Zúñiga de León.

Se conservó el núcleo compartido publicado en [la unidad 3 de César](https://github.com/cesar-upv/2430233_FUNDAMENTOS_IA_UNIDAD_3/tree/59da26fbf5ef7c8b2ad9952dea61845d1d489c18/01-fhcp-challenge), revisión `59da26fbf5ef7c8b2ad9952dea61845d1d489c18`. El proyecto original del equipo es [FHCP-Challenge](https://github.com/ZapataFrame/FHCP-Challenge).

En `01-fhcp-challenge/proyecto_equipo/` se incluyen `src/`, pruebas, datos originales y documentos de decisiones. Sus 2,107 archivos importados se conservan sin modificar; las huellas SHA-256 están en [el manifiesto de procedencia](herramientas/origenes.json). No se trasladaron configuraciones de agentes ni los registros de otras campañas como si fueran ejecuciones de esta entrega.

La interfaz Qt, el adaptador `ia_unidad3/fhcp.py`, el informe y la comparación de 54 intentos corresponden a esta unidad. El adaptador utiliza variantes del proyecto con inicialización guiada y registra sus parámetros efectivos. Los certificados oficiales se leen por separado y no se suministran a las metaheurísticas.

Datos: [FHCP Challenge Set, Flinders University](https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/fhcp-challenge-set/). Referencia solicitada por sus autores: Michael Haythorpe, “FHCP Challenge Set: The first set of structurally difficult instances of the Hamiltonian cycle problem”, Bulletin of the ICA, 83:98–107, 2018.

## Recopilación de películas

El crawler y su interfaz son implementaciones de esta unidad. El CSV se generó mediante solicitudes reales a Wikipedia; no se copió el dataset de películas ni las capturas de los repositorios de referencia.

Los enlaces de atribución se conservan en cada fila del CSV y en [la procedencia del rastreo](02-dataset-peliculas/datos/peliculas.procedencia.json). Los datos se distribuyen bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Se extrajeron tablas, eliminaron referencias, normalizaron espacios y filtraron duplicados por URL. Se mantuvieron vacíos los campos que la tabla no ofrece. El detalle está en [la licencia y atribución del dataset](02-dataset-peliculas/LICENCIA_DATOS.md).

## KNN y árboles de decisión

La lógica de KNN, las particiones, el escalado, la votación, las métricas y los experimentos se implementaron en `ia_unidad3/knn.py`. Los datos de semillas son sintéticos y no representan mediciones agrícolas reales.

Las interfaces y cuadernos son propios. Los temas de las actividades se consultaron en:

- [Unidad 3 de Zapata](https://github.com/ZapataFrame/FIA-Actividades-Unidad-3/tree/f887bbaf72be04ac276ab313739aaa39432cc88e).
- [Unidad 3 de César](https://github.com/cesar-upv/2430233_FUNDAMENTOS_IA_UNIDAD_3/tree/59da26fbf5ef7c8b2ad9952dea61845d1d489c18).

Los CSV Iris y diabetes se recuperaron de `10-aprendizaje-automatico/data/` del repositorio de Zapata, con sus bytes y huellas originales. Iris corresponde al conocido conjunto de clasificación de flores; diabetes tiene las 768 filas y nueve columnas del conjunto Pima Indians Diabetes. Se conservan como datos académicos, no como una validación de uso clínico.

Los árboles se entrenan con scikit-learn, con preparación y evaluación independientes para cada dataset. KNN no utiliza un clasificador de esa biblioteca. Matplotlib dibuja las gráficas y PySide6 proporciona las ventanas. Las versiones utilizadas se conservan en [requirements de ejecución](herramientas/requirements-ejecucion.txt).
