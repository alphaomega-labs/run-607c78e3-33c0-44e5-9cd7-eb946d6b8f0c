# AutoTW Validation Package

This package implements the `validation_simulation` phase execution shell for AutoTW-ASP.

## Goals
- Materialize benchmark datasets using the experiment design plan.
- Execute smoke and full experiment stages with fixed seeds.
- Produce reproducible figures, tables, data dumps, and symbolic checks.

## Layout
- `run_experiments.py`: stable entrypoint (`--stage smoke|full`).
- `src/autotw_validation/`: acquisition, simulation, analysis, plotting, symbolic checks.
- `configs/`: stage configs.
- `tests/`: shell-level package tests.
- `outputs/`: generated reports and summaries.

## Commands
- Smoke: `experiments/.venv/bin/python experiments/autotw_validation/run_experiments.py --stage smoke --config experiments/autotw_validation/configs/full.yaml --workspace-root .`
- Full: `experiments/.venv/bin/python experiments/autotw_validation/run_experiments.py --stage full --config experiments/autotw_validation/configs/full.yaml --workspace-root .`
- Lint: `experiments/.venv/bin/ruff check experiments/autotw_validation && experiments/.venv/bin/mypy experiments/autotw_validation/src/autotw_validation`
- Tests: `experiments/.venv/bin/pytest experiments/autotw_validation/tests -q`

## Provenance
- Real benchmark assets are sourced from `https://github.com/azreasoners/NeurASP` at a pinned commit recorded in `logs/dataset_resolution_log.json`.
- Additional benchmark families are materialized from deterministic local generators with fixed seeds and checksums.
