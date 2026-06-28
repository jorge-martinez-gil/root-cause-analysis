"""Knowledge-graph-driven, explainable root cause analysis for industrial assets.

Public API
----------
* diagnose / diagnose_row  - run the explainable reasoning engine.
* Diagnosis / RuleActivation  - results with explanation traces.
* build_knowledge_graph / build_diagnosed_graph  - RDF knowledge graphs, with
  inferred diagnoses and PROV-O provenance.
* diagnosis_report / run_pipeline  - reporting and one-call pipeline.
* iec60599_diagnosis  - the underlying IEC 60599 gas-ratio classifier.
"""

from __future__ import annotations

from .classification import (
    ClassificationResult,
    classify_transformers,
    default_transformer_measurements,
)
from .datasets import reference_fault_signatures, sample_transformer_measurements
from .ontology import build_knowledge_graph, build_tbox, serialize_ontology
from .querying import query_transformers_by_water_level, screen_assets
from .reasoning import (
    Diagnosis,
    RuleActivation,
    build_diagnosed_graph,
    diagnose,
    diagnose_row,
    diagnosis_report,
    materialize_diagnoses,
    run_pipeline,
)
from .rules import Evidence, dga_significant, iec60599_diagnosis

__version__ = "0.2.0"

__all__ = [
    "ClassificationResult",
    "Diagnosis",
    "Evidence",
    "RuleActivation",
    "build_diagnosed_graph",
    "build_knowledge_graph",
    "build_tbox",
    "classify_transformers",
    "default_transformer_measurements",
    "dga_significant",
    "diagnose",
    "diagnose_row",
    "diagnosis_report",
    "iec60599_diagnosis",
    "materialize_diagnoses",
    "query_transformers_by_water_level",
    "reference_fault_signatures",
    "run_pipeline",
    "sample_transformer_measurements",
    "screen_assets",
    "serialize_ontology",
    "__version__",
]
