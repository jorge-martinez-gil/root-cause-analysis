"""Minimal quickstart: diagnose the built-in sample assets with explanations."""

from root_cause_analysis import diagnose, sample_transformer_measurements


def main() -> None:
    diagnoses = diagnose(sample_transformer_measurements())

    print("Asset status summary")
    print("-" * 60)
    for d in diagnoses:
        causes = "; ".join(d.root_causes) if d.root_causes else "no fault identified"
        print(f"{d.asset_id}: {d.status:16} ({causes})")

    print("\nExample explanation trace")
    print("-" * 60)
    print(diagnoses[0].explanation())


if __name__ == "__main__":
    main()
