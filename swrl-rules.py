"""Deprecated shim. Use ``rca-diagnose`` or ``root_cause_analysis.diagnose``."""

from root_cause_analysis import classify_transformers, default_transformer_measurements


def main() -> None:
    print("[deprecated] use 'rca-diagnose' or root_cause_analysis.diagnose")
    result = classify_transformers(default_transformer_measurements())
    print("Failures:", result.failures)
    print("NonFailures:", result.non_failures)


if __name__ == "__main__":
    main()
