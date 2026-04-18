from __future__ import annotations
# mypy: disable-error-code=call-overload

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def apply_style() -> None:
    sns.set_theme(style="whitegrid", context="talk", palette="colorblind")


FEATURE_SET_LABELS = {
    "tw_only": "TW only",
    "tw_plus_scc": "TW + SCC",
    "tw_plus_scc_plus_reuse": "TW + SCC + reuse",
    "full": "Full feature set",
}

FALLBACK_POLICY_LABELS = {
    "none": "No fallback",
    "uncertainty_gate": "Uncertainty gate",
    "uncertainty_plus_tail_guard": "Uncertainty + tail guard",
}


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

    fig2, axes = plt.subplots(
        1,
        2,
        figsize=(14, 5.6),
        gridspec_kw={"width_ratios": [1.25, 1.0]},
        constrained_layout=True,
    )
    s3 = exp02.groupby(["feature_set", "fallback_policy"], as_index=False)["regret_s"].mean()
    s3["feature_set"] = s3["feature_set"].map(FEATURE_SET_LABELS)
    s3["fallback_policy"] = s3["fallback_policy"].map(FALLBACK_POLICY_LABELS)
    feature_order = [FEATURE_SET_LABELS[key] for key in FEATURE_SET_LABELS]
    fallback_order = [FALLBACK_POLICY_LABELS[key] for key in FALLBACK_POLICY_LABELS]
    regret_grid = (
        s3.pivot(index="feature_set", columns="fallback_policy", values="regret_s")
        .reindex(index=feature_order, columns=fallback_order)
    )
    sns.heatmap(
        regret_grid,
        annot=True,
        fmt=".3f",
        cmap="Blues",
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "Mean regret (s)"},
        ax=axes[0],
    )
    axes[0].set_title("Mean Router Regret by Policy")
    axes[0].set_xlabel("Fallback policy")
    axes[0].set_ylabel("Feature set")

    best_location = regret_grid.stack().idxmin()
    best_row = feature_order.index(best_location[0])
    best_col = fallback_order.index(best_location[1])
    axes[0].add_patch(plt.Rectangle((best_col, best_row), 1, 1, fill=False, edgecolor="black", linewidth=2.0))

    s4 = exp02.groupby(["uncertainty_tau"], as_index=False).agg(
        violation_rate=("bound_violation", "mean"),
        tail_runtime_s=("tail_runtime_s", "median"),
    )
    s4["tau_label"] = s4["uncertainty_tau"].map(lambda value: f"{value:.2f}")
    ax_rate = axes[1]
    ax_tail = ax_rate.twinx()
    rate_line = ax_rate.plot(
        s4["uncertainty_tau"],
        s4["violation_rate"],
        marker="o",
        linewidth=2.2,
        color="#1f77b4",
        label="Violation rate",
    )[0]
    target_line = ax_rate.axhline(
        0.05,
        linestyle="--",
        linewidth=1.4,
        color="#4d4d4d",
        label="Target rate",
    )
    tail_line = ax_tail.plot(
        s4["uncertainty_tau"],
        s4["tail_runtime_s"],
        marker="s",
        linewidth=2.2,
        color="#e69500",
        label="Median tail runtime (s)",
    )[0]

    ax_rate.set_title("Threshold Sensitivity")
    ax_rate.set_xlabel("Uncertainty threshold $\\tau$")
    ax_rate.set_ylabel("Violation rate")
    ax_tail.set_ylabel("Median tail runtime (s)")
    ax_rate.set_xticks(s4["uncertainty_tau"], s4["tau_label"])
    ax_rate.set_ylim(0.0, max(0.62, float(s4["violation_rate"].max()) * 1.1))

    tail_min = float(s4["tail_runtime_s"].min())
    tail_max = float(s4["tail_runtime_s"].max())
    if tail_min == tail_max:
        ax_tail.set_ylim(tail_min - 0.08, tail_max + 0.08)
    else:
        padding = max(0.05, (tail_max - tail_min) * 0.2)
        ax_tail.set_ylim(tail_min - padding, tail_max + padding)

    for row in s4.itertuples(index=False):
        ax_rate.annotate(
            f"{row.violation_rate:.3f}",
            (row.uncertainty_tau, row.violation_rate),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=10,
            color="#1f77b4",
        )
        ax_tail.annotate(
            f"{row.tail_runtime_s:.2f}s",
            (row.uncertainty_tau, row.tail_runtime_s),
            textcoords="offset points",
            xytext=(0, -16),
            ha="center",
            fontsize=10,
            color="#b36b00",
        )

    axes[1].legend(
        handles=[rate_line, target_line, tail_line],
        labels=["Violation rate", "Target rate", "Median tail runtime (s)"],
        loc="center right",
        frameon=True,
    )
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
