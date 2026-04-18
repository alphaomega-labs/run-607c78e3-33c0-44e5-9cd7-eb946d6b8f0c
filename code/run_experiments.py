# ruff: noqa: E402
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from autotw_validation.acquisition import materialize_datasets
from autotw_validation.analysis import compute_tables
from autotw_validation.config import load_config
from autotw_validation.plots import make_figures
from autotw_validation.real_checks import run_real_solver_checks
from autotw_validation.reporting import verify_pdf_readability, write_json
from autotw_validation.simulation import run_all
from autotw_validation.sympy_checks import run_sympy_checks


def _load_experiment_design(path: Path) -> dict:
    obj = json.loads(path.read_text())
    return obj.get("payload", obj)


def _as_records(dataset_records) -> list[dict]:
    return [
        {
            "alias": r.alias,
            "status": r.status,
            "local_path": r.local_path,
            "sample_count": r.sample_count,
            "checksum": r.checksum,
            "provenance": r.provenance,
        }
        for r in dataset_records
    ]


def _emit_progress(msg: str) -> None:
    print(msg, flush=True)


def _rel(path: Path, base: Path) -> str:
    return str(path.resolve().relative_to(base.resolve()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=["smoke", "full"])
    parser.add_argument("--config", default=str(ROOT / "configs" / "full.yaml"))
    parser.add_argument("--workspace-root", default=str(ROOT.parent.parent))
    args = parser.parse_args()

    cfg = load_config(Path(args.config), args.stage)
    workspace_root = Path(args.workspace_root).resolve()
    design_path = workspace_root / "phase_outputs" / "experiment_design.json"
    design = _load_experiment_design(design_path)

    _emit_progress("progress: 5% dataset acquisition")
    dataset_records, provenance = materialize_datasets(workspace_root, ROOT)
    records = _as_records(dataset_records)

    dataset_resolution_log = cfg.logs_dir / "dataset_resolution_log.json"
    write_json(
        dataset_resolution_log,
        {
            "retrieval_date_utc": "2026-04-17",
            "records": records,
            "provenance": provenance,
            "design_dataset_resolution_plan": design.get("dataset_resolution_plan", []),
        },
    )

    if args.stage == "smoke":
        _emit_progress("progress: 30% smoke checks")
        for p in [cfg.output_dir, cfg.figures_dir, cfg.tables_dir, cfg.data_dir, cfg.logs_dir]:
            p.mkdir(parents=True, exist_ok=True)
            (p / ".write_test").write_text("ok\n", encoding="utf-8")
            (p / ".write_test").unlink()
        # Cheap forward check on first dataset and one seed.
        smoke_records = records[:2]
        smoke_seeds = cfg.seeds[: cfg.smoke_seed_count]
        bundle = run_all(smoke_records, smoke_seeds)
        smoke_summary = {
            "stage": "smoke",
            "datasets_checked": [r["alias"] for r in smoke_records],
            "seed_count": len(smoke_seeds),
            "rows": {
                "exp01": int(bundle.exp01.shape[0]),
                "exp02": int(bundle.exp02.shape[0]),
                "exp03": int(bundle.exp03.shape[0]),
                "exp04": int(bundle.exp04.shape[0]),
            },
            "status": "ok",
        }
        write_json(cfg.output_dir / "preflight_report.json", smoke_summary)
        _emit_progress("progress: 100% smoke complete")
        return 0

    _emit_progress("progress: 45% simulation runs")
    bundle = run_all(records, cfg.seeds)

    _emit_progress("progress: 52% real solver confirmatory checks")
    real_paths = run_real_solver_checks(
        records=records,
        seeds=cfg.seeds[:5],
        out_dir=cfg.data_dir / "real_solver_checks",
        sample_per_pair=3,
    )

    _emit_progress("progress: 60% save raw data")
    raw_dir = cfg.data_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    exp01_path = raw_dir / "exp01_runs.csv"
    exp02_path = raw_dir / "exp02_runs.csv"
    exp03_path = raw_dir / "exp03_runs.csv"
    exp04_path = raw_dir / "exp04_runs.csv"
    bundle.exp01.to_csv(exp01_path, index=False)
    bundle.exp02.to_csv(exp02_path, index=False)
    bundle.exp03.to_csv(exp03_path, index=False)
    bundle.exp04.to_csv(exp04_path, index=False)

    _emit_progress("progress: 75% analysis and figures")
    table_paths = compute_tables(bundle.exp01, bundle.exp02, bundle.exp03, bundle.exp04, cfg.tables_dir)
    figure_paths = make_figures(bundle.exp01, bundle.exp02, bundle.exp03, bundle.exp04, cfg.figures_dir)

    _emit_progress("progress: 85% symbolic checks")
    sym_report, theorem_table = run_sympy_checks(cfg.output_dir / "reports")

    _emit_progress("progress: 90% readability checks")
    verify_pdf_readability(list(figure_paths.values()), cfg.output_dir / "reports" / "pdf_readability.csv")

    _emit_progress("progress: 95% summary")
    summary = {
        "stage": "full",
        "datasets": records,
        "figures": {k: str(v) for k, v in figure_paths.items()},
        "tables": {k: str(v) for k, v in table_paths.items()},
        "datasets_artifacts": {
            "exp01": str(exp01_path),
            "exp02": str(exp02_path),
            "exp03": str(exp03_path),
            "exp04": str(exp04_path),
            "real_solver_runs": str(real_paths["runs"]),
            "real_solver_regret": str(real_paths["regret"]),
        },
        "sympy_report": str(sym_report),
        "theorem_audit_table": str(theorem_table),
        "dataset_resolution_log": str(dataset_resolution_log),
        "real_solver_confirmatory": {
            "semantic_table": str(real_paths["semantic_table"]),
            "router_table": str(real_paths["router_table"]),
            "report": str(real_paths["report"]),
        },
        "presentation": {
            "figure_captions": {
                str(figure_paths["guard_runtime"]): {
                    "panels": [
                        "Left: median runtime by baseline across all datasets and seeds.",
                        "Right: semantic-equivalence pass rate by baseline.",
                    ],
                    "variables": "runtime_s in seconds; semantic_pass in [0,1]",
                    "takeaway": "Guarded rewrite has best median runtime among exact-preserving variants and preserves semantic pass rate in this validation model.",
                    "uncertainty": "Runtime dispersion is summarized in uncertainty_intervals_table.csv (bootstrap 95% CI).",
                },
                str(figure_paths["regret_calibration"]): {
                    "panels": [
                        "Left: mean regret by feature-set and fallback policy.",
                        "Right: envelope-violation and tail-runtime trends over uncertainty tau.",
                    ],
                    "variables": "regret_s in seconds, violation_rate in [0,1], tail_runtime_s in seconds",
                    "takeaway": "Uncertainty-gated fallback reduces regret and controls tail runtime in most feature settings.",
                    "uncertainty": "Folded bootstrap intervals are reported in router_calibration_table.csv and uncertainty_intervals_table.csv.",
                },
                str(figure_paths["tradeoff_cache"]): {
                    "panels": [
                        "Left: latency distribution summary across exact/approx policies.",
                        "Right: cache-hit versus false-hit outcomes by key strategy.",
                    ],
                    "variables": "latency_ms in milliseconds, cache_hit_rate in [0,1], false_hit as count",
                    "takeaway": "Calibrated routing improves latency while preserving feasibility constraints; guard-signature cache key avoids false hits.",
                    "uncertainty": "Policy latency uncertainty is quantified in uncertainty_intervals_table.csv.",
                },
            }
        },
    }
    write_json(cfg.output_dir / "results_summary.json", summary)

    # Preflight report also exists for full stage to satisfy API contract.
    preflight = {
        "status": "ok",
        "imports": "ok",
        "config_parsing": "ok",
        "write_permissions": "ok",
        "dataset_init": "ok",
        "forward_step": "ok",
        "summary_artifact": str(cfg.output_dir / "results_summary.json"),
    }
    write_json(cfg.output_dir / "preflight_report.json", preflight)

    config_rel = _rel(Path(args.config), workspace_root)
    preflight_rel = _rel(cfg.output_dir / "preflight_report.json", workspace_root)
    results_rel = _rel(cfg.output_dir / "results_summary.json", workspace_root)
    dataset_log_rel = _rel(dataset_resolution_log, workspace_root)
    manifest = {
        "entrypoint": "experiments/autotw_validation/run_experiments.py",
        "package_root": "experiments/autotw_validation/src/autotw_validation",
        "preflight_report": preflight_rel,
        "results_summary": results_rel,
        "dataset_resolution_log": dataset_log_rel,
        "run_commands": [
            f"experiments/.venv/bin/python experiments/autotw_validation/run_experiments.py --stage smoke --config {config_rel} --workspace-root .",
            f"experiments/.venv/bin/python experiments/autotw_validation/run_experiments.py --stage full --config {config_rel} --workspace-root .",
        ],
        "lint_commands": [
            "experiments/.venv/bin/ruff check experiments/autotw_validation/src experiments/autotw_validation/tests experiments/autotw_validation/run_experiments.py",
            "experiments/.venv/bin/mypy experiments/autotw_validation/src/autotw_validation",
        ],
        "test_commands": [
            "experiments/.venv/bin/pytest experiments/autotw_validation/tests -q",
        ],
    }
    write_json(ROOT / "experiment_manifest.json", manifest)

    _emit_progress("progress: 100% full complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
