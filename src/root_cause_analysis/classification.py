"""Rule-based classification workflow inspired by the SWRL examples."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ClassificationResult:
    """Classification result with record-level labels and grouped names."""

    records: pd.DataFrame
    failures: list[str]
    non_failures: list[str]


def default_transformer_measurements() -> pd.DataFrame:
    """Return the built-in sample measurements used by the original scripts."""
    data = {
        "Hydrogen": [2845, 12886, 2820, 1099, 3210, 13500, 10200],
        "Oxigen": [5860, 61, 16400, 70, 3570, 343, 11900],
        "Nitrogen": [27842, 25041, 56300, 37520, 47900, 36500, 33700],
        "Methane": [7406, 877, 144, 545, 160, 3150, 573],
        "CO": [32, 83, 257, 184, 360, 113, 87],
        "CO2": [1344, 864, 1080, 1402, 2130, 984, 611],
        "Ethylene": [16684, 4, 206, 6, 4, 5, 0],
        "Ethane": [5467, 305, 11, 230, 43, 1230, 162],
        "Acethylene": [7, 0, 2190, 0, 4, 1, 0],
        "DBDS": [19, 45, 1, 87, 1, 1, 1],
        "Power factor": [1, 1, 1, 4.58, 0.77, 4.93, 3.53],
        "Interfacial V": [45, 45, 39, 33, 44, 37, 45],
        "Dielectric rigidity": [55, 55, 52, 49, 55, 52, 55],
        "Water content": [0, 0, 11, 5, 3, 6, 5],
        "Health index": [95.2, 85.5, 85.3, 85.3, 85.2, 75.6, 75.6],
        "Life expectation": [19, 19, 19, 6, 6, 6, 6],
    }
    return pd.DataFrame(data)


def classify_transformers(df: pd.DataFrame) -> ClassificationResult:
    """Classify transformers using the published threshold logic."""
    required_columns = {"Health index", "Power factor", "Life expectation"}
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns for classification: {missing}")

    records = df.copy()
    records.index = [f"Individual{i}" for i in range(len(records))]

    is_failure = records["Life expectation"].astype(float) < 22
    is_non_failure = (records["Health index"].astype(float) < 85) | (
        records["Power factor"].astype(float) < 1
    )

    records["is_failure"] = is_failure
    records["is_non_failure"] = is_non_failure

    failures = records.index[records["is_failure"]].to_list()
    non_failures = records.index[records["is_non_failure"]].to_list()

    return ClassificationResult(records=records, failures=failures, non_failures=non_failures)
