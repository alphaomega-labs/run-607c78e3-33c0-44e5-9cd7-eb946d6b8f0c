from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def bootstrap_ci(values: np.ndarray, n_boot: int = 400, alpha: float = 0.05) -> tuple[float, float, float]:
    rng = np.random.default_rng(123)
    if values.size == 0:
        return (float("nan"), float("nan"), float("nan"))
    means = []
    for _ in range(n_boot):
        idx = rng.integers(0, values.size, size=values.size)
        means.append(float(values[idx].mean()))
    lo = float(np.quantile(means, alpha / 2))
    hi = float(np.quantile(means, 1 - alpha / 2))
    return (float(values.mean()), lo, hi)


def compute_tables(exp01: pd.DataFrame, exp02: pd.DataFrame, exp03: pd.DataFrame, exp04: pd.DataFrame, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    t1 = (
        exp01.groupby(["baseline"], as_index=False)
        .agg(
            semantic_equivalence_rate=("semantic_pass", "mean"),
            semantic_drift_count=("semantic_drift", "sum"),
            median_runtime_s=("runtime_s", "median"),
            speedup_vs_manual_carry=("speedup_vs_manual_carry", "mean"),
        )
        .sort_values("median_runtime_s")
    )
    p1 = out_dir / "semantic_audit_table.csv"
    t1.to_csv(p1, index=False)

    t2 = (
        exp02.groupby(["feature_set", "fallback_policy", "uncertainty_tau"], as_index=False)
        .agg(
            mean_regret_s=("regret_s", "mean"),
            p95_tail_runtime_s=("tail_runtime_s", lambda x: float(np.quantile(x, 0.95))),
            violation_rate=("bound_violation", "mean"),
            fallback_activation_rate=("fallback_active", "mean"),
        )
        .sort_values(["mean_regret_s", "violation_rate"])
    )
    p2 = out_dir / "router_calibration_table.csv"
    t2.to_csv(p2, index=False)

    t3 = (
        exp03.groupby(["policy"], as_index=False)
        .agg(
            utility_gap_mean=("utility_gap", "mean"),
            feasibility_rate=("feasible", "mean"),
            latency_median_ms=("latency_ms", "median"),
            latency_p95_ms=("latency_ms", lambda x: float(np.quantile(x, 0.95))),
            exact_fallback_rate=("exact_fallback_rate", "mean"),
        )
        .sort_values("latency_median_ms")
    )
    p3 = out_dir / "exact_vs_approx_tradeoff_table.csv"
    t3.to_csv(p3, index=False)

    t4 = (
        exp04.groupby(["strategy"], as_index=False)
        .agg(
            cache_hit_rate=("cache_hit_rate", "mean"),
            false_hit_count=("false_hit", "sum"),
            counterexample_detection_rate=("counterexample_detected", "mean"),
            runtime_overhead_ms=("runtime_overhead_ms", "median"),
        )
        .sort_values("runtime_overhead_ms")
    )
    p4 = out_dir / "cache_counterexample_table.csv"
    t4.to_csv(p4, index=False)

    # Confidence interval detail table for manuscript uncertainty notes.
    ci_rows = []
    for baseline, g in exp01.groupby("baseline"):
        mean, lo, hi = bootstrap_ci(g["runtime_s"].to_numpy())
        ci_rows.append(
            {
                "metric": "runtime_s",
                "group": baseline,
                "mean": mean,
                "ci95_low": lo,
                "ci95_high": hi,
            }
        )
    for policy, g in exp03.groupby("policy"):
        mean, lo, hi = bootstrap_ci(g["latency_ms"].to_numpy())
        ci_rows.append(
            {
                "metric": "latency_ms",
                "group": policy,
                "mean": mean,
                "ci95_low": lo,
                "ci95_high": hi,
            }
        )
    p5 = out_dir / "uncertainty_intervals_table.csv"
    pd.DataFrame(ci_rows).to_csv(p5, index=False)

    return {
        "semantic_audit_table": p1,
        "router_calibration_table": p2,
        "tradeoff_table": p3,
        "cache_table": p4,
        "uncertainty_table": p5,
    }
