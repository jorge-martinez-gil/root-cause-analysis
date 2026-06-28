"""Sample datasets for the root cause analysis pipeline.

Two datasets are provided:

* :func:`sample_transformer_measurements` — the measurement values used by the
  original publication's example, now with explicit asset identifiers. These are
  run through the *real* IEC 60599 reasoning pipeline; whatever fault codes
  emerge are reported honestly (including indeterminate cases).
* :func:`reference_fault_signatures` — a small, clearly labelled set of synthetic
  dissolved-gas signatures with a known-correct IEC 60599 fault code each. Used to
  verify the classifier and to demonstrate each fault type in tutorials.
"""

from __future__ import annotations

import pandas as pd

# Friendly measurement columns shared by the sample data.
_MEASUREMENT_COLUMNS = [
    "Hydrogen",
    "Oxygen",
    "Nitrogen",
    "Methane",
    "CO",
    "CO2",
    "Ethylene",
    "Ethane",
    "Acetylene",
    "DBDS",
    "Power factor",
    "Interfacial V",
    "Dielectric rigidity",
    "Water content",
    "Health index",
    "Life expectation",
]


def sample_transformer_measurements() -> pd.DataFrame:
    """Return the publication example measurements with asset identifiers."""
    data = {
        "Asset": ["PW101", "PW102", "PW103", "PW104", "PW105", "PW106", "PW107"],
        "Hydrogen": [2845, 12886, 2820, 1099, 3210, 13500, 10200],
        "Oxygen": [5860, 61, 16400, 70, 3570, 343, 11900],
        "Nitrogen": [27842, 25041, 56300, 37520, 47900, 36500, 33700],
        "Methane": [7406, 877, 144, 545, 160, 3150, 573],
        "CO": [32, 83, 257, 184, 360, 113, 87],
        "CO2": [1344, 864, 1080, 1402, 2130, 984, 611],
        "Ethylene": [16684, 4, 206, 6, 4, 5, 0],
        "Ethane": [5467, 305, 11, 230, 43, 1230, 162],
        "Acetylene": [7, 0, 2190, 0, 4, 1, 0],
        "DBDS": [19, 45, 1, 87, 1, 1, 1],
        "Power factor": [1, 1, 1, 4.58, 0.77, 4.93, 3.53],
        "Interfacial V": [45, 45, 39, 33, 44, 37, 45],
        "Dielectric rigidity": [55, 55, 52, 49, 55, 52, 55],
        "Water content": [0, 0, 11, 5, 3, 6, 5],
        "Health index": [95.2, 85.5, 85.3, 85.3, 85.2, 75.6, 75.6],
        "Life expectation": [19, 19, 19, 6, 6, 6, 6],
    }
    return pd.DataFrame(data)


def default_transformer_measurements() -> pd.DataFrame:
    """Backward-compatible alias returning the measurements without asset ids."""
    return sample_transformer_measurements().drop(columns=["Asset"])


def reference_fault_signatures() -> pd.DataFrame:
    """Synthetic dissolved-gas signatures with known-correct IEC 60599 codes.

    Concentrations are illustrative (μL/L) and chosen to fall unambiguously in a
    single IEC 60599 case. The ``Expected`` column is the ground-truth fault code.
    """
    rows = [
        # Asset,  H2,  CH4, C2H6, C2H4, C2H2, Expected
        ("PD-1", 1000, 50, 200, 20, 0, "PD"),
        ("D1-1", 200, 40, 30, 60, 120, "D1"),
        ("D2-1", 300, 120, 20, 100, 80, "D2"),
        ("T1-1", 200, 300, 100, 50, 0, "T1"),
        ("T2-1", 200, 400, 50, 150, 5, "T2"),
        ("T3-1", 200, 500, 30, 300, 10, "T3"),
        ("OK-1", 20, 10, 5, 5, 0, "NORMAL"),
    ]
    df = pd.DataFrame(
        rows,
        columns=["Asset", "Hydrogen", "Methane", "Ethane", "Ethylene", "Acetylene", "Expected"],
    )
    return df
