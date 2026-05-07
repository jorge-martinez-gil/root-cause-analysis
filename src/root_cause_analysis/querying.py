"""Ontology query helpers for transformer diagnostics."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from rdflib import Graph


def query_transformers_by_water_level(
    ontology_path: str | Path,
    *,
    minimum_water_level: int = 100,
) -> list[str]:
    """Return transformer IRIs with water level above the threshold."""
    if minimum_water_level < 0:
        raise ValueError("minimum_water_level must be >= 0")

    path = Path(ontology_path)
    if not path.exists():
        raise FileNotFoundError(f"Ontology file not found: {path}")

    graph = Graph()
    graph.parse(path)
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX : <http://test.org/onto-pw#>

    SELECT ?transformer
    WHERE {{
      ?transformer rdf:type :Transformer .
      ?transformer :relatesToWaterContent ?waterContent .
      ?waterContent :hasWaterLevel ?level .
      FILTER(?level > {minimum_water_level})
    }}
    """
    return [str(cast(tuple[object, ...], row)[0]) for row in graph.query(query)]
