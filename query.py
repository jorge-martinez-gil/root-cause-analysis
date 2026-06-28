"""Deprecated shim. Use ``rca-query`` or ``root_cause_analysis.screen_assets``.

Kept for backward compatibility; screens the built-in sample assets by health
index and prints the flagged asset labels.
"""

from root_cause_analysis import sample_transformer_measurements, screen_assets


def main() -> None:
    print("[deprecated] use 'rca-query' or root_cause_analysis.screen_assets")
    for label, value in screen_assets(
        sample_transformer_measurements(),
        parameter="Health index",
        operator="<",
        threshold=80.0,
    ):
        print(f"{label}: Health index = {value:g}")


if __name__ == "__main__":
    main()
