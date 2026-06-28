"""SPARQL query helpers for transformer knowledge graphs."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pandas as pd
from rdflib import Graph

from .ontology import build_knowledge_graph

_OPERATORS = {"<", "<=", ">", ">=", "=", "!="}


def _as_graph(source: str | Path | Graph) -> Graph:
    if isinstance(source, Graph):
        return source
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Ontology file not found: {path}")
    graph = Graph()
    graph.parse(path)
    return graph


def query_transformers_by_water_level(
    source: str | Path | Graph,
    *,
    minimum_water_level: int = 100,
) -> list[str]:
    """Return transformer IRIs whose water-content measurement exceeds a level.

    ``source`` may be a path to an RDF file or an in-memory :class:`rdflib.Graph`
    that contains asset individuals (e.g. one built by
    :func:`root_cause_analysis.ontology.build_knowledge_graph`).
    """
    if minimum_water_level < 0:
        raise ValueError("minimum_water_level must be >= 0")
    graph = _as_graph(source)
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
    return [str(cast("tuple[object, ...]", row)[0]) for row in graph.query(query)]


def screen_assets(
    measurements: pd.DataFrame,
    *,
    parameter: str = "Health index",
    operator: str = "<",
    threshold: float = 80.0,
    asset_column: str = "Asset",
) -> list[tuple[str, float]]:
    """Screen assets via SPARQL over a materialised knowledge graph.

    Builds a knowledge graph from ``measurements`` and returns ``(asset_label,
    value)`` pairs for assets whose ``parameter`` satisfies ``operator threshold``.
    """
    if operator not in _OPERATORS:
        raise ValueError(f"Unsupported operator: {operator!r}")
    graph = build_knowledge_graph(measurements)
    prop_local = parameter.replace(" ", "_")
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX : <http://test.org/onto-pw#>

    SELECT ?label ?value
    WHERE {{
      ?asset :hasMeasurement ?m .
      ?asset rdfs:label ?label .
      ?m :observedProperty :{prop_local} .
      ?m :hasValue ?value .
      FILTER(?value {operator} {threshold})
    }}
    ORDER BY ?label
    """
    results: list[tuple[str, float]] = []
    for row in graph.query(query):
        label, value = cast("tuple[object, object]", row)
        results.append((str(label), float(value)))  # type: ignore[arg-type]
    return results
