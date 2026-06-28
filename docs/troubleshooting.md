# Troubleshooting / FAQ

## `ModuleNotFoundError: root_cause_analysis`
Install the project in editable mode:

```bash
python -m pip install -e .
```

## `rca-diagnose: command not found`
Reinstall so the console scripts are registered, and ensure your environment's
`Scripts`/`bin` directory is on `PATH`:

```bash
python -m pip install -e .
```

## A diagnosis comes back as `ND (indeterminate)`
The dissolved-gas ratios did not match a single IEC 60599 case (possible mixed faults or boundary values).
This is reported honestly rather than guessed; resample and re-evaluate.

## Screening returns no results
Lower the threshold or pick a different parameter, e.g.
`rca-query --parameter "Dielectric rigidity" --operator "<" --threshold 45`.

## Quality checks
```bash
ruff check . && ruff format --check . && mypy src && pytest
```
