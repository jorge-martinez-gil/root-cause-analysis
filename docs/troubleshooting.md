# Troubleshooting / FAQ

## `ModuleNotFoundError: root_cause_analysis`
Install the project in editable mode:

```bash
python -m pip install -e .
```

## Query returns no results
- Verify ontology path exists.
- Lower threshold, e.g. `--min-water-level 50`.

## Lint/type/test checks
Run:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```
