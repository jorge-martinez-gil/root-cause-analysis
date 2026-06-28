"""Backward-compatible classification API built on the real reasoning engine.

The original ``classify_transformers`` applied ad-hoc thresholds. It now delegates
to the standards-grounded :mod:`root_cause_analysis.reasoning` engine and exposes
the same lightweight result shape for existing callers.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .datasets import default_transformer_measurements
from .reasoning import diagnose

__all__ = [
    "ClassificationResult",
    "classify_transformers",
    "default_transformer_measurements",
]


@dataclass(frozen=True)
class ClassificationResult:
    """Classification result with record-level labels and grouped asset ids."""

    records: pd.DataFrame
    failures: list[str]
    non_failures: list[str]


def classify_transformers(df: pd.DataFrame) -> ClassificationResult:
    """Classify assets via the IEC 60599 reasoning engine.

    ``failures`` are assets whose worst severity requires action; ``non_failures``
    are assets with no abnormal findings. Assets that only warrant investigation
    appear in neither list (they remain visible in ``records['status']``).
    """
    diagnoses = diagnose(df)
    failures = [d.asset_id for d in diagnoses if d.status in {"Failure", "Action required"}]
    non_failures = [d.asset_id for d in diagnoses if d.status == "Healthy"]

    records = df.copy()
    records["asset"] = [d.asset_id for d in diagnoses]
    records["status"] = [d.status for d in diagnoses]
    records["root_causes"] = ["; ".join(d.root_causes) or "-" for d in diagnoses]

    return ClassificationResult(records=records, failures=failures, non_failures=non_failures)
