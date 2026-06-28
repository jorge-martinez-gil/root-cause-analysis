"""Deprecated shim.

The original ad-hoc ``owlready2`` reimplementation has been superseded by the
standards-grounded engine in :mod:`root_cause_analysis.reasoning`. This wrapper
remains so existing commands keep working; it prints explanation traces for the
built-in sample assets.
"""

from root_cause_analysis import diagnose, sample_transformer_measurements


def main() -> None:
    print("[deprecated] use 'rca-diagnose' or root_cause_analysis.diagnose")
    for diag in diagnose(sample_transformer_measurements()):
        print(diag.explanation())
        print()


if __name__ == "__main__":
    main()
