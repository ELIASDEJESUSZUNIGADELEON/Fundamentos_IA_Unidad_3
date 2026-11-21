# Dataset de películas

**Elias de Jesus Zuñiga de Leon · Matrícula 2430085**

Crawler propio y aplicación para revisar películas, filtrar por año o buscar títulos/créditos y exportar los registros seleccionados.

```powershell
python iniciar.py peliculas
python ejecutar.py peliculas --maximo 1000 --salida nuevo_dataset
```

Los comandos se ejecutan desde la raíz de la unidad. El crawler recorre listas anuales de Wikipedia, descarga su HTML, interpreta tablas con celdas combinadas, extrae enlaces de películas y elimina repeticiones. Continúa con la siguiente lista hasta alcanzar el máximo o agotar los años elegidos. No requiere API ni credenciales.

El [CSV incluido](datos/peliculas.csv) contiene 1,000 URL únicas: 420 películas de 2024, 308 de 2023 y 272 de 2022. Incluye `titulo`, `anio`, `generos`, `compania`, `equipo_y_reparto`, `url` y `lista_origen`. Las listas usadas no proporcionan géneros; ese campo se conserva vacío. No se incluyen sinopsis ni se infieren datos ausentes.

El rastreo respeta robots.txt, espera al menos 1.1 segundos entre solicitudes y se detiene ante errores. El archivo de destino debe ser nuevo. La GUI puede usar el dataset incluido sin Internet.

- [Cuaderno ejecutado con revisión del dataset](analisis_dataset.ipynb).
- [Procedencia, páginas y huellas](datos/peliculas.procedencia.json).
- [Licencia y atribución de datos](LICENCIA_DATOS.md).
- Implementación: `ia_unidad3/movies.py` e `ia_unidad3/interface.py`, en la raíz de la unidad.

El muestreo está limitado a listas de estrenos estadounidenses y a las páginas consultadas; no representa la distribución de toda la producción cinematográfica.
