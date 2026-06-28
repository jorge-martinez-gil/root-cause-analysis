"""Explainable reasoning engine for transformer root cause analysis.

The engine applies the documented diagnostic rules to each asset, produces a
:class:`Diagnosis` carrying a full **explanation trace**, and can materialise the
inferred diagnoses back into the RDF knowledge graph with **PROV-O provenance**
so that every inferred triple is traceable to the rule and the evidence that
produced it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import pandas as pd
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import PROV, RDF, RDFS, XSD

from .ontology import ONTO, build_knowledge_graph, row_to_gas_dict
from .rules import (
    FAULT_ACTIONS,
    FAULT_SEVERITY,
    IEC60599_CITATION,
    SCREENING_RULES,
    Evidence,
    duval_triangle_coordinates,
    iec60599_diagnosis,
)

#: Severity ordering used to compute the worst-case asset status.
_SEVERITY_RANK = {"none": 0, "advisory": 1, "minor": 2, "major": 3, "critical": 4}
_STATUS_BY_SEVERITY = {
    0: "Healthy",
    1: "Investigate",
    2: "Investigate",
    3: "Action required",
    4: "Failure",
}
#: IEC fault codes that count as genuine root causes (vs. NORMAL / ND).
_ROOT_CAUSE_CODES = {"PD", "D1", "D2", "T1", "T2", "T3"}

# Ontology class for each IEC fault code (mirrors ontology.build_tbox).
_FAULT_CLASS = {
    "PD": "PartialDischarge",
    "D1": "LowEnergyDischarge",
    "D2": "HighEnergyDischarge",
    "T1": "ThermalFaultLow",
    "T2": "ThermalFaultMedium",
    "T3": "ThermalFaultHigh",
}


@dataclass(frozen=True)
class RuleActivation:
    """One rule firing, with the evidence that triggered it."""

    rule_id: str
    rule_name: str
    source: str
    conclusion: str
    severity: str
    recommended_action: str
    evidence: list[Evidence] = field(default_factory=list)
    fault_code: str | None = None


@dataclass(frozen=True)
class Diagnosis:
    """An explainable diagnosis for a single asset."""

    asset_id: str
    status: str
    root_causes: list[str]
    activations: list[RuleActivation]
    duval_coordinates: tuple[float, float, float] | None = None

    @property
    def severity(self) -> str:
        worst = max((_SEVERITY_RANK.get(a.severity, 0) for a in self.activations), default=0)
        return next(k for k, v in _SEVERITY_RANK.items() if v == worst)

    def explanation(self) -> str:
        """Return a human-readable explanation trace."""
        lines = [f"Asset {self.asset_id} — status: {self.status}"]
        if self.root_causes:
            lines.append("  Root cause(s): " + "; ".join(self.root_causes))
        else:
            lines.append("  Root cause(s): none identified")
        for act in self.activations:
            lines.append(
                f"  [{act.rule_id}] {act.rule_name} → {act.conclusion} "
                f"(severity: {act.severity}; source: {act.source})"
            )
            for ev in act.evidence:
                lines.append(f"        • {ev}")
            if act.recommended_action:
                lines.append(f"        action: {act.recommended_action}")
        if self.duval_coordinates is not None:
            ch4, c2h4, c2h2 = self.duval_coordinates
            lines.append(
                "  Duval Triangle 1 coordinates: "
                f"%CH4={ch4:.1f}, %C2H4={c2h4:.1f}, %C2H2={c2h2:.1f}"
            )
        return "\n".join(lines)


def diagnose_row(asset_id: str, row: Mapping[str, Any]) -> Diagnosis:
    """Diagnose a single asset from its measurement row."""
    activations: list[RuleActivation] = []
    root_causes: list[str] = []

    gases = row_to_gas_dict(row)
    dga = iec60599_diagnosis(gases)
    activations.append(
        RuleActivation(
            rule_id="IEC60599-DGA",
            rule_name="IEC 60599 basic gas-ratio method",
            source=IEC60599_CITATION,
            conclusion=f"{dga.code}: {dga.label}",
            severity=FAULT_SEVERITY.get(dga.code, "none"),
            recommended_action=FAULT_ACTIONS.get(dga.code, ""),
            evidence=dga.evidence,
            fault_code=dga.code,
        )
    )
    if dga.code in _ROOT_CAUSE_CODES:
        root_causes.append(f"{dga.code} — {dga.label}")

    plain = {str(k): v for k, v in row.items()}
    for rule in SCREENING_RULES:
        ev = rule.evaluate(plain)
        if ev:
            activations.append(
                RuleActivation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    source=rule.source,
                    conclusion=rule.conclusion,
                    severity=rule.severity,
                    recommended_action=rule.recommended_action,
                    evidence=ev,
                )
            )

    worst = max((_SEVERITY_RANK.get(a.severity, 0) for a in activations), default=0)
    status = _STATUS_BY_SEVERITY[worst]
    duval = duval_triangle_coordinates(gases)
    return Diagnosis(str(asset_id), status, root_causes, activations, duval)


def diagnose(measurements: pd.DataFrame, asset_column: str = "Asset") -> list[Diagnosis]:
    """Diagnose every asset (row) in a measurements table."""
    df = measurements.copy()
    if asset_column not in df.columns:
        df[asset_column] = [f"PW{101 + i}" for i in range(len(df))]
    results: list[Diagnosis] = []
    for _, row in df.iterrows():
        asset_id = str(row[asset_column])
        results.append(diagnose_row(asset_id, cast("dict[str, Any]", row.to_dict())))
    return results


# ---------------------------------------------------------------------------
# Provenance materialisation
# ---------------------------------------------------------------------------


def _asset_uri(asset_id: str) -> URIRef:
    return ONTO[str(asset_id).replace(" ", "_")]


def materialize_diagnoses(graph: Graph, diagnoses: list[Diagnosis]) -> Graph:
    """Write inferred diagnoses into ``graph`` with PROV-O provenance."""
    graph.bind("prov", PROV)
    for diag in diagnoses:
        asset = _asset_uri(diag.asset_id)
        d_uri = ONTO[f"{diag.asset_id}_diagnosis"]
        activity = ONTO[f"{diag.asset_id}_diagnosis_activity"]

        graph.add((d_uri, RDF.type, ONTO.Diagnosis))
        graph.add((d_uri, RDF.type, PROV.Entity))
        graph.add((asset, ONTO.hasDiagnosis, d_uri))
        graph.add((d_uri, ONTO.ofAsset, asset))
        graph.add((d_uri, ONTO.hasStatus, Literal(diag.status)))
        graph.add((d_uri, ONTO.hasSeverity, Literal(diag.severity)))
        graph.add((d_uri, ONTO.hasExplanation, Literal(diag.explanation())))

        # Provenance activity: the rule application that generated the diagnosis.
        graph.add((activity, RDF.type, PROV.Activity))
        graph.add((d_uri, PROV.wasGeneratedBy, activity))
        for meas in graph.objects(asset, ONTO.hasMeasurement):
            graph.add((activity, PROV.used, meas))
            graph.add((d_uri, PROV.wasDerivedFrom, meas))

        for idx, act in enumerate(diag.activations):
            rule_uri = ONTO[f"rule_{act.rule_id.replace('-', '_')}"]
            graph.add((rule_uri, RDF.type, ONTO.DiagnosticRule))
            graph.add((rule_uri, RDF.type, PROV.Agent))
            graph.add((rule_uri, RDFS.label, Literal(act.rule_name)))
            graph.add((rule_uri, RDFS.comment, Literal(act.source)))
            graph.add((d_uri, ONTO.derivedFromRule, rule_uri))
            graph.add((activity, PROV.wasAssociatedWith, rule_uri))

            if act.fault_code in _FAULT_CLASS:
                f_uri = ONTO[f"{diag.asset_id}_fault_{act.fault_code}"]
                graph.add((f_uri, RDF.type, ONTO[_FAULT_CLASS[act.fault_code]]))
                graph.add((f_uri, ONTO.faultCode, Literal(act.fault_code)))
                graph.add((d_uri, ONTO.indicatesFault, f_uri))

            if act.recommended_action:
                a_uri = ONTO[f"{diag.asset_id}_action_{act.rule_id.replace('-', '_')}"]
                graph.add((a_uri, RDF.type, ONTO.MaintenanceAction))
                graph.add((a_uri, RDFS.comment, Literal(act.recommended_action)))
                graph.add((d_uri, ONTO.recommendsAction, a_uri))

            for j, ev in enumerate(act.evidence):
                e_uri = ONTO[f"{diag.asset_id}_ev_{idx}_{j}"]
                graph.add((e_uri, RDF.type, ONTO.Evidence))
                graph.add((e_uri, RDFS.label, Literal(str(ev))))
                graph.add((e_uri, ONTO.observedProperty, ONTO[ev.parameter.replace(" ", "_")]))
                graph.add((e_uri, ONTO.hasValue, Literal(float(ev.value), datatype=XSD.double)))
                if ev.unit:
                    graph.add((e_uri, ONTO.hasUnit, Literal(ev.unit)))
                graph.add((d_uri, ONTO.supportedByEvidence, e_uri))
    return graph


def build_diagnosed_graph(
    measurements: pd.DataFrame, asset_column: str = "Asset"
) -> tuple[Graph, list[Diagnosis]]:
    """Return ``(knowledge_graph, diagnoses)`` with diagnoses materialised."""
    graph = build_knowledge_graph(measurements)
    diagnoses = diagnose(measurements, asset_column=asset_column)
    materialize_diagnoses(graph, diagnoses)
    return graph, diagnoses


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def diagnosis_report(diagnoses: list[Diagnosis]) -> str:
    """Render a Markdown diagnosis report with a summary table and traces."""
    lines = ["# Root Cause Analysis — Diagnosis Report", ""]
    lines.append(f"Assets analysed: **{len(diagnoses)}**")
    n_fault = sum(1 for d in diagnoses if d.status in {"Failure", "Action required"})
    lines.append(f"Assets requiring action: **{n_fault}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Asset | Status | Severity | Root cause(s) |")
    lines.append("|-------|--------|----------|---------------|")
    for d in diagnoses:
        rc = "; ".join(d.root_causes) if d.root_causes else "—"
        lines.append(f"| {d.asset_id} | {d.status} | {d.severity} | {rc} |")
    lines.append("")
    lines.append("## Explanation traces")
    lines.append("")
    for d in diagnoses:
        lines.append(f"### {d.asset_id}")
        lines.append("")
        lines.append("```")
        lines.append(d.explanation())
        lines.append("```")
        lines.append("")
    lines.append("---")
    lines.append(
        "*Fault codes follow IEC 60599 / IEEE C57.104. Oil-quality and health "
        "screening thresholds are advisory and configurable.*"
    )
    return "\n".join(lines)


def run_pipeline(
    measurements: pd.DataFrame,
    output_dir: str | Path | None = None,
    asset_column: str = "Asset",
) -> list[Diagnosis]:
    """End-to-end pipeline: diagnose, optionally write report + materialised KG."""
    graph, diagnoses = build_diagnosed_graph(measurements, asset_column=asset_column)
    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "diagnosis_report.md").write_text(diagnosis_report(diagnoses), encoding="utf-8")
        graph.serialize(destination=out / "knowledge_graph.ttl", format="turtle")
    return diagnoses
