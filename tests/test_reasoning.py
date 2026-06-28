"""Tests for the explainable IEC 60599 reasoning engine."""

from __future__ import annotations

import pytest

from root_cause_analysis.datasets import (
    reference_fault_signatures,
    sample_transformer_measurements,
)
from root_cause_analysis.reasoning import diagnose, diagnose_row
from root_cause_analysis.rules import dga_significant

_SIGNATURES = reference_fault_signatures()


@pytest.mark.parametrize("idx", range(len(_SIGNATURES)))
def test_iec60599_matches_known_signatures(idx: int) -> None:
    row = _SIGNATURES.iloc[idx]
    diag = diagnose_row(str(row["Asset"]), row.to_dict())
    assert diag.activations[0].fault_code == row["Expected"]


def test_explanation_trace_is_populated() -> None:
    diag = diagnose_row("PD-1", _SIGNATURES.iloc[0].to_dict())
    trace = diag.explanation()
    assert "IEC60599-DGA" in trace
    assert "R1 = C2H2/C2H4" in trace
    assert diag.activations[0].evidence  # at least one evidence item


def test_sample_pw101_is_thermal_fault() -> None:
    diagnoses = {d.asset_id: d for d in diagnose(sample_transformer_measurements())}
    pw101 = diagnoses["PW101"]
    assert pw101.status == "Action required"
    assert any("T2" in rc for rc in pw101.root_causes)


def test_normal_unit_has_no_root_cause() -> None:
    gases = {"Hydrogen": 20, "Methane": 10, "Ethane": 5, "Ethylene": 5, "Acetylene": 0}
    diag = diagnose_row("OK", gases)
    assert diag.status == "Healthy"
    assert diag.root_causes == []


def test_significance_gating() -> None:
    low = {"H2": 10, "CH4": 10, "C2H6": 5, "C2H4": 5, "C2H2": 0}
    significant, exceeded = dga_significant(low)
    assert significant is False
    assert exceeded == []
