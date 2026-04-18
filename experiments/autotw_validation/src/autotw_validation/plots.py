from __future__ import annotations
# mypy: disable-error-code=call-overload

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def apply_style() -> None:
    sns.set_theme(style="whitegrid", context="talk", palette="colorblind")


def make_figures(exp01: pd.DataFrame, exp02: pd.DataFrame, exp03: pd.DataFrame, exp04: pd.DataFrame, figures_dir: Path) -> dict[str, Path]:
    apply_style()
    figures_dir.mkdir(parents=True, exist_ok=True)

    fig1, axes = plt.subplots(1, 2, figsize=(15, 6), constrained_layout=True)
    s1 = exp01.groupby("baseline", as_index=False)["runtime_s"].median()
    sns.barplot(data=s1, x="baseline", y="runtime_s", ax=axes[0])
    axes[0].set_title("Runtime by Baseline")
    axes[0].set_xlabel("Baseline")
    axes[0].set_ylabel("Median Runtime (s)")
    axes[0].tick_params(axis="x", rotation=25)

    s2 = exp01.groupby("baseline", as_index=False)["semantic_pass"].mean()
    sns.barplot(data=s2, x="baseline", y="semantic_pass", ax=axes[1])
    axes[1].set_title("Semantic Equivalence Rate")
    axes[1].set_xlabel("Baseline")
    axes[1].set_ylabel("Pass Rate")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].tick_params(axis="x", rotation=25)
    p1 = figures_dir / "guard_coverage_runtime_semantics.pdf"
    fig1.savefig(p1)
    plt.close(fig1)

    fig2, axes = plt.subplots(1, 2, figsize=(15, 6), constrained_layout=True)
    s3 = (
        exp02.groupby(["feature_set", "fallback_policy"], as_index=False)["regret_s"]
        .mean()
        .sort_values("regret_s")
        .head(12)
    )
    s3["group"] = s3["feature_set"] + "|" + s3["fallback_policy"]
    sns.barplot(data=s3, x="group", y="regret_s", ax=axes[0])
    axes[0].set_title("Router Regret by Policy")
    axes[0].set_xlabel("Feature Set and Fallback")
    axes[0].set_ylabel("Mean Regret (s)")
    axes[0].tick_params(axis="x", rotation=35)

    s4 = exp02.groupby(["uncertainty_tau"], as_index=False).agg(
        violation_rate=("bound_violation", "mean"),
        tail_runtime_s=("tail_runtime_s", "median"),
    )
    sns.lineplot(data=s4, x="uncertainty_tau", y="violation_rate", marker="o", label="Violation Rate", ax=axes[1])
    sns.lineplot(data=s4, x="uncertainty_tau", y="tail_runtime_s", marker="s", label="Tail Runtime (s)", ax=axes[1])
    axes[1].set_title("Uncertainty Threshold Effects")
    axes[1].set_xlabel("Tau")
    axes[1].set_ylabel("Rate or Runtime")
    axes[1].legend(title="Series")
    p2 = figures_dir / "regret_and_calibration_panels.pdf"
    fig2.savefig(p2)
    plt.close(fig2)

    fig3, axes = plt.subplots(1, 2, figsize=(15, 6), constrained_layout=True)
    s5 = exp03.groupby("policy", as_index=False)["latency_ms"].median()
    sns.barplot(data=s5, x="policy", y="latency_ms", ax=axes[0])
    axes[0].set_title("Latency by Policy")
    axes[0].set_xlabel("Policy")
    axes[0].set_ylabel("Median Latency (ms)")
    axes[0].tick_params(axis="x", rotation=25)

    s6 = exp04.groupby("strategy", as_index=False).agg(
        cache_hit_rate=("cache_hit_rate", "mean"),
        false_hit=("false_hit", "sum"),
    )
    sns.barplot(data=s6, x="strategy", y="cache_hit_rate", ax=axes[1], label="Hit Rate")
    ax2 = axes[1].twinx()
    sns.lineplot(data=s6, x="strategy", y="false_hit", marker="o", color="black", ax=ax2, label="False Hits")
    axes[1].set_title("Cache Strategy Outcomes")
    axes[1].set_xlabel("Cache Key Strategy")
    axes[1].set_ylabel("Cache Hit Rate")
    ax2.set_ylabel("False Hit Count")
    axes[1].tick_params(axis="x", rotation=25)
    p3 = figures_dir / "tradeoff_and_cache_panels.pdf"
    fig3.savefig(p3)
    plt.close(fig3)

    return {
        "guard_runtime": p1,
        "regret_calibration": p2,
        "tradeoff_cache": p3,
    }
