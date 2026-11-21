# FHCP Challenge

**Elias de Jesus Zuñiga de Leon · Matrícula 2430085**

Trabajo en equipo con Diego Eduardo Zapata Aguilar, Junior Arturo Vázquez Leonel, César Euresti y Eder Omar Zúñiga Zavala.

El programa carga grafos HCP y busca ciclos hamiltonianos con seis familias de metaheurísticas. El costo es la cantidad de pares consecutivos sin arista, incluido el cierre. Una permutación válida no basta: el ciclo se certifica de forma independiente.

Desde la raíz de la unidad:

```powershell
python iniciar.py fhcp
python ejecutar.py fhcp --instancia graph2 --algoritmo abc --semilla 2430087 --salida nueva_busqueda
python ejecutar.py comparar --salida nueva_comparacion
```

La aplicación permite consultar instancias, ejecutar búsquedas con presupuesto, ver el certificado de referencia, revisar la comparación y exportar el resultado. El CLI admite cualquier instancia incluida, de graph1 a graph1001.

- [Cuaderno ejecutado](analisis_fhcp.ipynb).
- [Informe y conclusiones](informe.md).
- [Resultados de los 54 intentos](resultados/comparacion.json).
- [Resumen CSV](resultados/resumen.csv).
- [Certificado de referencia comprobado](resultados/referencia.json).
- [Código compartido del equipo](proyecto_equipo/src/).

Los archivos en `proyecto_equipo/` conservan la implementación compartida. La interfaz y la comparación local están en la raíz de la unidad y en `ia_unidad3`. La comparación pequeña no sustituye las campañas completas del equipo. Consulta [procedencia y atribución](../ORIGENES.md).
