"""Tests for ontology TBox consistency and documentation completeness."""

from __future__ import annotations

from rdflib import RDFS
from rdflib.namespace import OWL, RDF

from root_cause_analysis.ontology import ONTO, build_tbox, serialize_ontology


def test_water_content_relation_is_declared() -> None:
    # Regression test for the original undeclared-property bug.
    g = build_tbox()
    assert (ONTO.relatesToWaterContent, RDF.type, OWL.ObjectProperty) in g


def test_every_class_is_documented() -> None:
    g = build_tbox()
    for cls in g.subjects(RDF.type, OWL.Class):
        assert g.value(cls, RDFS.label) is not None
        assert g.value(cls, RDFS.comment) is not None


def test_iec_fault_classes_present() -> None:
    g = build_tbox()
    for name in ("PartialDischarge", "HighEnergyDischarge", "ThermalFaultHigh"):
        assert (ONTO[name], RDF.type, OWL.Class) in g


def test_serialisation_round_trips(tmp_path) -> None:
    written = serialize_ontology(tmp_path)
    from rdflib import Graph

    reparsed = Graph()
    reparsed.parse(written["owl"])
    assert len(reparsed) > 0
