from root_cause_analysis.classification import (
    classify_transformers,
    default_transformer_measurements,
)


def test_default_classification_groups_are_consistent() -> None:
    result = classify_transformers(default_transformer_measurements())

    assert "Individual0" in result.failures
    assert "Individual4" in result.non_failures
    assert len(result.failures) == 7
    assert len(result.non_failures) == 3
