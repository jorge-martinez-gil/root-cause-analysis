"""Command-line entry points."""

from __future__ import annotations

import argparse
from pathlib import Path

from .classification import classify_transformers, default_transformer_measurements
from .config import DEFAULT_ONTOLOGY_PATH
from .querying import query_transformers_by_water_level


def run_classification_cli() -> None:
    """Run the default classification workflow."""
    parser = argparse.ArgumentParser(
        description="Classify transformers using threshold-based rules."
    )
    _ = parser.parse_args()

    result = classify_transformers(default_transformer_measurements())
    print("Failures:", result.failures)
    print("NonFailures:", result.non_failures)


def run_query_cli() -> None:
    """Run ontology query workflow."""
    parser = argparse.ArgumentParser(description="Query transformers by water content threshold.")
    parser.add_argument(
        "--ontology",
        type=Path,
        default=DEFAULT_ONTOLOGY_PATH,
        help="Path to ontology file.",
    )
    parser.add_argument("--min-water-level", type=int, default=100, help="Water level threshold.")
    args = parser.parse_args()

    results = query_transformers_by_water_level(
        args.ontology,
        minimum_water_level=args.min_water_level,
    )
    for iri in results:
        print(iri)
