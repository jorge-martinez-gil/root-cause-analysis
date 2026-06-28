"""Tests for knowledge-graph materialisation and PROV-O provenance."""

from __future__ import annotations

from root_cause_analysis.datasets import sample_transformer_measurements
from root_cause_analysis.reasoning import build_diagnosed_graph

_COUNT_DIAGNOSES = """
PREFIX : <http://test.org/onto-pw#>
SELECT (COUNT(?d) AS ?n) WHERE { ?d a :Diagnosis . }
"""

_PW101_FAULT = """
PREFIX : <http://test.org/onto-pw#>
SELECT ?code WHERE {
  ?d a :Diagnosis ; :ofAsset :PW101 ; :indicatesFault ?f .
  ?f :faultCode ?code .
}
"""

_PROVENANCE = """
PREFIX : <http://test.org/onto-pw#>
PREFIX prov: <http://www.w3.org/ns/prov#>
ASK {
  ?d a :Diagnosis ; prov:wasGeneratedBy ?act .
  ?act prov:used ?m ; prov:wasAssociatedWith ?rule .
}
"""


def test_all_assets_get_a_diagnosis() -> None:
    graph, diagnoses = build_diagnosed_graph(sample_transformer_measurements())
    (row,) = list(graph.query(_COUNT_DIAGNOSES))
    assert int(row[0]) == len(diagnoses) == 7


def test_pw101_fault_is_materialised_as_t2() -> None:
    graph, _ = build_diagnosed_graph(sample_transformer_measurements())
    codes = {str(r[0]) for r in graph.query(_PW101_FAULT)}
    assert "T2" in codes


def test_provenance_chain_exists() -> None:
    graph, _ = build_diagnosed_graph(sample_transformer_measurements())
    assert bool(graph.query(_PROVENANCE).askAnswer)
