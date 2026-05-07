from pathlib import Path

import pytest

from root_cause_analysis.querying import query_transformers_by_water_level

ONTOLOGY_PATH = Path("data/ontology/onto_pw.owl")


def test_query_returns_transformer_above_threshold() -> None:
    results = query_transformers_by_water_level(ONTOLOGY_PATH, minimum_water_level=100)

    assert any(result.endswith("PW101") for result in results)
    assert all("PW102" not in result for result in results)


def test_query_rejects_invalid_threshold() -> None:
    with pytest.raises(ValueError, match="must be >= 0"):
        query_transformers_by_water_level(ONTOLOGY_PATH, minimum_water_level=-1)
