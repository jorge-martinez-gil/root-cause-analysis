# Contributing

Thanks for considering a contribution.

## Development setup

```bash
python -m pip install -e .[dev]
```

## Quality checks

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

## Pull requests

- Keep changes scoped and reproducible.
- Add or update tests for behavior changes.
- Update documentation when user-facing behavior changes.
