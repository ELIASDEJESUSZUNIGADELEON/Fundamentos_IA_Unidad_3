"""Crawler acotado a listas anuales de Wikipedia, sin claves de API."""

import csv
import hashlib
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from .common import ROOT, save_csv, save_json, timestamp

BASE = "https://en.wikipedia.org"
USER_AGENT = (
    "Unidad3Educational/1.0 (https://github.com/ELIASDEJESUSZUNIGADELEON/Fundamentos_IA_Unidad_3)"
)
FIELDS = ["titulo", "anio", "generos", "compania", "equipo_y_reparto", "url", "lista_origen"]


def text(cell):
    return re.sub(r"\s+", " ", cell.get_text(" ", strip=True)).strip()


def table_rows(table):
    """Expande rowspan/colspan para conservar la columna del título."""
    occupied = {}
    for row_number, row in enumerate(table.find_all("tr")):
        cells = row.find_all(["th", "td"], recursive=False)
        col = 0
        for cell in cells:
            while (row_number, col) in occupied:
                col += 1
            width = int(cell.get("colspan", 1))
            height = int(cell.get("rowspan", 1))
            for dr in range(height):
                for dc in range(width):
                    occupied[row_number + dr, col + dc] = cell
            col += width
        indices = sorted(c for r, c in occupied if r == row_number)
        yield [occupied[row_number, c] for c in indices]
        for key in [(r, c) for r, c in occupied if r == row_number]:
            del occupied[key]


def parse_list(html, source, year):
    soup = BeautifulSoup(html, "html.parser")
    for ref in soup.select("sup.reference"):
        ref.decompose()
    films = {}
    for table in soup.select("table.wikitable"):
        rows = iter(table_rows(table))
        header = next(rows, [])
        names = [text(cell).lower() for cell in header]
        if "title" not in names or not any("cast" in name for name in names):
            continue
        expected_title = names.index("title")

        def field(row, word, offset):
            index = next((i for i, name in enumerate(names) if word in name), None)
            if index is not None:
                index += offset
            return text(row[index]) if index is not None and index < len(row) else ""

        for row in rows:
            title_index = next(
                (i for i, cell in enumerate(row) if cell.select_one("i a[href]")), None
            )
            if title_index is None:
                continue
            title = row[title_index]
            link = title.select_one("i a[href]")
            offset = title_index - expected_title
            if link is None:
                continue
            href = link.get("href", "")
            url = urldefrag(urljoin(BASE, href))[0]
            parsed = urlsplit(url)
            if (
                parsed.netloc != "en.wikipedia.org"
                or not parsed.path.startswith("/wiki/")
                or parsed.query
                or ":" in unquote(parsed.path[6:])
            ):
                continue
            name = text(title)
            if not name or name.lower() == "title" or "redlink" in href:
                continue
            films.setdefault(
                url,
                dict(
                    zip(
                        FIELDS,
                        [
                            name,
                            year,
                            field(row, "genre", offset),
                            field(row, "company", offset)
                            or field(row, "production", offset)
                            or field(row, "distributor", offset),
                            field(row, "cast", offset),
                            url,
                            source,
                        ],
                    )
                ),
            )
    return list(films.values())


def crawl(output, limit=1000, years=(2024, 2023, 2022, 2021, 2020, 2019), progress=None, stop=None):
    if not 1 <= limit <= 1000:
        raise ValueError("El máximo debe estar entre 1 y 1000 películas.")
    output = Path(output)
    if output.exists():
        raise FileExistsError("Elige un archivo nuevo para conservar el dataset anterior.")
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"})
    robots_response = session.get(BASE + "/robots.txt", timeout=40)
    robots_response.raise_for_status()
    robots = RobotFileParser()
    robots.parse(robots_response.text.splitlines())
    films, pages, seen = [], [], set()
    last_request = time.monotonic()
    if progress:
        progress("robots.txt recibido; comenzando listas anuales.")
    for year in years:
        if stop and stop():
            break
        if type(year) is not int or not 1900 <= year <= 2025:
            raise ValueError("Año fuera del rango permitido: 1900–2025.")
        url = f"{BASE}/wiki/List_of_American_films_of_{year}"
        if not robots.can_fetch(USER_AGENT, url):
            raise PermissionError("robots.txt no permite consultar esta lista.")
        time.sleep(max(0, 1.1 - (time.monotonic() - last_request)))
        response = session.get(url, timeout=50, allow_redirects=False)
        last_request = time.monotonic()
        response.raise_for_status()
        if response.status_code != 200:
            raise RuntimeError(
                f"Respuesta inesperada {response.status_code}; se detuvo el rastreo."
            )
        rows = parse_list(response.text, url, year)
        if not rows:
            raise ValueError(
                f"No se reconoció la tabla de {year}; no se guardará un dataset vacío."
            )
        pages.append(
            {
                "url": url,
                "sha256_html": hashlib.sha256(response.content).hexdigest(),
                "candidatas": len(rows),
            }
        )
        for row in rows:
            if row["url"] not in seen:
                seen.add(row["url"])
                films.append(row)
                if len(films) == limit:
                    break
        if progress:
            progress(f"{year}: {len(rows)} candidatas; {len(films)}/{limit} películas únicas.")
        if len(films) == limit:
            break
    if not films:
        raise ValueError("El rastreo terminó sin registros; no se creó un CSV.")
    save_csv(output, films, FIELDS)
    record = {
        "fecha_utc": timestamp(),
        "maximo_solicitado": limit,
        "filas": len(films),
        "licencia_datos": "CC BY-SA 4.0",
        "intervalo_minimo_segundos": 1.1,
        "paginas": pages,
        "csv_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "observacion": "Listas anuales de estrenos estadounidenses. Géneros vacíos si la tabla no los ofrece; créditos conservados como texto. No se descargan sinopsis ni artículos individuales.",
    }
    save_json(output.with_suffix(".procedencia.json"), record)
    return films, record


def read_movies(path=None):
    path = Path(path or ROOT / "02-dataset-peliculas/datos/peliculas.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def summary(rows):
    return {
        "peliculas": len(rows),
        "urls_unicas": len({row["url"] for row in rows}),
        "por_anio": dict(sorted(Counter(str(row["anio"]) for row in rows).items())),
        "con_genero": sum(bool(row["generos"]) for row in rows),
        "con_creditos": sum(bool(row["equipo_y_reparto"]) for row in rows),
    }
