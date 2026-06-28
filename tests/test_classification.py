"""Backward-compatibility tests for the classification API."""

from __future__ import annotations

import pandas as pd

from root_cause_analysis.classification import (
    classify_transformers,
    default_transformer_measurements,
)


def test_default_classification_runs_and_flags_pw101() -> None:
    result = classify_transformers(default_transformer_measurements())

    assert isinstance(result.failures, list)
    assert isinstance(result.non_failures, list)
    assert "PW101" in result.failures  # T2 thermal fault -> action required
    assert "status" in result.records.columns
    assert "root_causes" in result.records.columns


def test_healthy_unit_is_non_failure() -> None:
    healthy = pd.DataFrame(
        {
            "Asset": ["H1"],
            "Hydrogen": [20],
            "Methane": [10],
            "Ethane": [5],
            "Ethylene": [5],
            "Acetylene": [0],
            "Health index": [99],
            "Dielectric rigidity": [60],
            "Interfacial V": [45],
            "Water content": [3],
        }
    )
    result = classify_transformers(healthy)
    assert result.failures == []
    assert "H1" in result.non_failures
