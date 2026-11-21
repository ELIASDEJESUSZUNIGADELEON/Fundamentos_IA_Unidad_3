import pytest

from ia_unidad3 import movies

HTML = """<table class="wikitable"><tr><th colspan="2">Opening</th><th>Title</th><th>Company credits</th><th>Cast and crew</th></tr>
<tr><td rowspan="2">January</td><td>1</td><td><i><a href="/wiki/Film_A">Film A</a></i><sup class="reference">[1]</sup></td><td>Studio</td><td>Person (director)</td></tr>
<tr><td>2</td><td><i><a href="/wiki/Film_B">Film B</a></i></td><td>Studio B</td><td>Other person</td></tr>
<tr><td>Feb</td><td>1</td><td><i><a href="/wiki/Film_A">Film A</a></i></td><td>Studio</td><td>Same</td></tr>
<tr><td>Feb</td><td>2</td><td><i><a href="https://other.example/movie">External</a></i></td><td>Other</td><td>Other</td></tr></table>"""


def test_rowspan_deduplication_and_source_fields():
    rows = movies.parse_list(HTML, "https://en.wikipedia.org/wiki/Example", 2024)
    assert [row["titulo"] for row in rows] == ["Film A", "Film B"]
    assert rows[0]["compania"] == "Studio"
    assert rows[1]["equipo_y_reparto"] == "Other person"
    assert rows[0]["generos"] == ""
    assert rows[0]["url"] == "https://en.wikipedia.org/wiki/Film_A"
    assert "[1]" not in rows[0]["titulo"]


def test_preserves_existing_csv(tmp_path):
    path = tmp_path / "original.csv"
    path.write_text("original", encoding="utf-8")
    with pytest.raises(FileExistsError):
        movies.crawl(path)
    assert path.read_text() == "original"


def test_list_with_missing_month_cell_keeps_film_and_credits():
    html = '<table class="wikitable"><tr><th>Opening</th><th>Opening</th><th>Title</th><th>Company credits</th><th>Cast and crew</th></tr><tr><td>30</td><td><i><a href="/wiki/Film_C">Film C</a></i></td><td><a href="/wiki/Studio">Studio</a></td><td>A director</td></tr></table>'
    rows = movies.parse_list(html, "https://en.wikipedia.org/wiki/Example", 2024)
    assert len(rows) == 1
    assert rows[0]["titulo"] == "Film C"
    assert rows[0]["compania"] == "Studio"
    assert rows[0]["equipo_y_reparto"] == "A director"


@pytest.mark.parametrize("limit", [0, -1, 1001])
def test_crawler_rejects_bad_limit_without_network(limit, tmp_path):
    with pytest.raises(ValueError):
        movies.crawl(tmp_path / "new.csv", limit)


def test_actual_dataset_has_unique_sources_and_required_metadata():
    rows = movies.read_movies()
    assert len(rows) == 1000
    assert len({row["url"] for row in rows}) == 1000
    assert all(
        row["titulo"] and row["anio"] and row["equipo_y_reparto"] and row["lista_origen"]
        for row in rows
    )
    assert all(row["url"].startswith("https://en.wikipedia.org/wiki/") for row in rows)
