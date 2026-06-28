"""Tests for SPARQL querying / screening helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from root_cause_analysis.datasets import sample_transformer_measurements
from root_cause_analysis.ontology import build_knowledge_graph
from root_cause_analysis.querying import (
    query_transformers_by_water_level,
    screen_assets,
)


def test_screen_assets_by_health_index() -> None:
    flagged = dict(
        screen_assets(
            sample_transformer_measurements(),
            parameter="Health index",
            operator="<",
            threshold=80.0,
        )
    )
    assert "PW106" in flagged
    assert "PW107" in flagged
    assert "PW101" not in flagged


def test_query_transformers_by_water_level_on_graph() -> None:
    df = pd.DataFrame({"Asset": ["WET", "DRY"], "Water content": [105, 10]})
    graph = build_knowledge_graph(df)
    hits = query_transformers_by_water_level(graph, minimum_water_level=100)
    assert any(h.endswith("WET") for h in hits)
    assert all("DRY" not in h for h in hits)


def test_query_rejects_invalid_threshold() -> None:
    df = pd.DataFrame({"Asset": ["A"], "Water content": [10]})
    graph = build_knowledge_graph(df)
    with pytest.raises(ValueError, match="must be >= 0"):
        query_transformers_by_water_level(graph, minimum_water_level=-1)
