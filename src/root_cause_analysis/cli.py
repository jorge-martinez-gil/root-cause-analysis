"""Command-line entry points for the root cause analysis pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .classification import classify_transformers
from .datasets import default_transformer_measurements, sample_transformer_measurements
from .ontology import serialize_ontology
from .querying import screen_assets
from .reasoning import diagnosis_report, run_pipeline


def _load_measurements(path: Path | None) -> pd.DataFrame:
    if path is None:
        return sample_transformer_measurements()
    return pd.read_csv(path)


def run_diagnosis_cli() -> None:
    """Run the full explainable diagnosis pipeline (``rca-diagnose``)."""
    parser = argparse.ArgumentParser(
        description="Explainable root cause analysis for power transformers."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="CSV of measurements (defaults to the built-in sample dataset).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write diagnosis_report.md and knowledge_graph.ttl to this directory.",
    )
    parser.add_argument(
        "--format",
        choices=["trace", "markdown"],
        default="trace",
        help="Console output format.",
    )
    args = parser.parse_args()

    measurements = _load_measurements(args.input)
    diagnoses = run_pipeline(measurements, output_dir=args.output_dir)

    if args.format == "markdown":
        print(diagnosis_report(diagnoses))
    else:
        for diag in diagnoses:
            print(diag.explanation())
            print()
    if args.output_dir is not None:
        print(f"Report and knowledge graph written to: {args.output_dir}")


def run_classification_cli() -> None:
    """Run the backward-compatible classification workflow (``rca-classify``)."""
    parser = argparse.ArgumentParser(
        description="Classify transformers (failure / non-failure) via IEC 60599."
    )
    _ = parser.parse_args()
    result = classify_transformers(default_transformer_measurements())
    print("Failures:", result.failures)
    print("NonFailures:", result.non_failures)


def run_query_cli() -> None:
    """Screen assets via SPARQL over the knowledge graph (``rca-query``)."""
    parser = argparse.ArgumentParser(
        description="Screen assets by a measured parameter via SPARQL."
    )
    parser.add_argument("--input", type=Path, default=None, help="CSV of measurements.")
    parser.add_argument("--parameter", default="Health index", help="Parameter to screen.")
    parser.add_argument("--operator", default="<", help="Comparison operator.")
    parser.add_argument("--threshold", type=float, default=80.0, help="Threshold value.")
    args = parser.parse_args()

    measurements = _load_measurements(args.input)
    flagged = screen_assets(
        measurements,
        parameter=args.parameter,
        operator=args.operator,
        threshold=args.threshold,
    )
    if not flagged:
        print("No assets matched the screening condition.")
    for label, value in flagged:
        print(f"{label}: {args.parameter} = {value:g} {args.operator} {args.threshold:g}")


def run_build_ontology_cli() -> None:
    """Regenerate the ontology TBox files (``rca-build-ontology``)."""
    parser = argparse.ArgumentParser(description="Serialize the ontology TBox.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/ontology"),
        help="Directory to write onto_pw.ttl and onto_pw.owl.",
    )
    args = parser.parse_args()
    written = serialize_ontology(args.output_dir)
    for fmt, path in written.items():
        print(f"{fmt}: {path}")
