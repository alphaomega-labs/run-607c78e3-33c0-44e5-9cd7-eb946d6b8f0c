from __future__ import annotations
# mypy: disable-error-code="import-untyped,call-overload,arg-type"

import json
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class SolverRun:
    dataset: str
    seed: int
    instance_id: str
    tw_proxy: int
    backend: str
    runtime_s: float
    model_count: int
    semantic_pass: int


def _build_program(n_items: int, mod_guard: int, rewritten: bool) -> str:
    base = [
        f"item(1..{n_items}).",
        f"bad(I) :- item(I), I \\ {mod_guard} == 0.",
    ]
    if rewritten:
        body = [
            "allowed(I) :- item(I), not bad(I).",
            "1 { pick(I): allowed(I) } 1.",
        ]
    else:
        body = [
            "1 { pick(I): item(I) } 1.",
            ":- pick(I), bad(I).",
        ]
    tail = [
        "#show pick/1.",
    ]
    return "\n".join(base + body + tail) + "\n"


def _run_clingo(program_path: Path, config_name: str) -> tuple[float, list[str]]:
    cmd = [
        sys.executable,
        "-m",
        "clingo",
        str(program_path),
        "--outf=2",
        "--models=0",
        "--configuration",
        config_name,
    ]
    start = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    elapsed = time.perf_counter() - start
    parsed = json.loads(proc.stdout)
    calls = parsed.get("Call", [])
    if not calls:
        return elapsed, []
    witnesses = calls[0].get("Witnesses", [])
    models = []
    for w in witnesses:
        values = sorted(w.get("Value", []))
        models.append(" ".join(values))
    return elapsed, models


def run_real_solver_checks(records: list[dict], seeds: list[int], out_dir: Path, sample_per_pair: int) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(94721)
    runs: list[SolverRun] = []
    regret_rows: list[dict] = []

    # Bounded real checks: execute clingo on generated ASP programs derived from dataset aliases and seeds.
    for rec in records:
        alias = rec["alias"]
        for seed in seeds:
            local_rng = random.Random(seed + sum(ord(c) for c in alias))
            for idx in range(sample_per_pair):
                n_items = local_rng.randint(10, 22)
                mod_guard = local_rng.randint(2, 6)
                tw_proxy = local_rng.randint(5, 55)
                instance_id = f"{alias}_{seed}_{idx:03d}"

                naive_path = out_dir / f"{instance_id}_naive.lp"
                rewrite_path = out_dir / f"{instance_id}_rewrite.lp"
                naive_path.write_text(_build_program(n_items, mod_guard, rewritten=False), encoding="utf-8")
                rewrite_path.write_text(_build_program(n_items, mod_guard, rewritten=True), encoding="utf-8")

                enum_time, enum_models = _run_clingo(naive_path, "frumpy")
                comp_time, _ = _run_clingo(naive_path, "trendy")
                rewrite_time, rewrite_models = _run_clingo(rewrite_path, "frumpy")
                semantic_pass = int(enum_models == rewrite_models)

                runs.append(
                    SolverRun(
                        dataset=alias,
                        seed=seed,
                        instance_id=instance_id,
                        tw_proxy=tw_proxy,
                        backend="enum_frumpy",
                        runtime_s=enum_time,
                        model_count=len(enum_models),
                        semantic_pass=semantic_pass,
                    )
                )
                runs.append(
                    SolverRun(
                        dataset=alias,
                        seed=seed,
                        instance_id=instance_id,
                        tw_proxy=tw_proxy,
                        backend="enum_rewrite_frumpy",
                        runtime_s=rewrite_time,
                        model_count=len(rewrite_models),
                        semantic_pass=semantic_pass,
                    )
                )
                runs.append(
                    SolverRun(
                        dataset=alias,
                        seed=seed,
                        instance_id=instance_id,
                        tw_proxy=tw_proxy,
                        backend="comp_trendy_proxy",
                        runtime_s=comp_time,
                        model_count=len(enum_models),
                        semantic_pass=semantic_pass,
                    )
                )

                best = min(enum_time, comp_time)
                # Router proxy intentionally simple and deterministic for auditability.
                choose_comp = (tw_proxy <= 25) or (rng.random() < 0.1)
                chosen = comp_time if choose_comp else enum_time
                regret_rows.append(
                    {
                        "dataset": alias,
                        "seed": seed,
                        "instance_id": instance_id,
                        "tw_proxy": tw_proxy,
                        "chosen_backend": "comp_trendy_proxy" if choose_comp else "enum_frumpy",
                        "regret_s": chosen - best,
                        "bound_violation": int((chosen - best) > 0.03),
                        "semantic_pass": semantic_pass,
                    }
                )

    runs_df = pd.DataFrame([r.__dict__ for r in runs])
    regret_df = pd.DataFrame(regret_rows)

    runs_path = out_dir / "real_solver_runs.csv"
    runs_df.to_csv(runs_path, index=False)
    regret_path = out_dir / "real_solver_regret.csv"
    regret_df.to_csv(regret_path, index=False)

    sem_table = (
        runs_df[runs_df["backend"].isin(["enum_frumpy", "enum_rewrite_frumpy"])]
        .groupby(["dataset", "backend"], as_index=False)
        .agg(
            median_runtime_s=("runtime_s", "median"),
            semantic_equivalence_rate=("semantic_pass", "mean"),
            model_count_mean=("model_count", "mean"),
        )
        .sort_values(["dataset", "backend"])
    )
    sem_path = out_dir / "real_solver_semantic_table.csv"
    sem_table.to_csv(sem_path, index=False)

    route_table = (
        regret_df.groupby("dataset", as_index=False)
        .agg(
            mean_regret_s=("regret_s", "mean"),
            p95_regret_s=("regret_s", lambda x: float(np.quantile(x, 0.95))),
            violation_rate=("bound_violation", "mean"),
        )
        .sort_values("mean_regret_s")
    )
    route_path = out_dir / "real_solver_router_table.csv"
    route_table.to_csv(route_path, index=False)

    report_lines = [
        "# Real Solver Confirmatory Report",
        "",
        "This report captures bounded real clingo executions for semantic-equivalence and routing-regret checks.",
        "",
        "## Protocol",
        "- Backend A: `clingo --configuration=frumpy` (enumeration-oriented baseline).",
        "- Backend B: `clingo --configuration=trendy` (proxy for alternate exact solver policy).",
        "- Semantic check: compare full model sets between naive and rewritten encodings.",
        "- Regret check: compare deterministic router choice against per-instance best backend runtime.",
        "",
        "## Caveats",
        "- Backend B is a clingo policy proxy, not a full compilation backend.",
        "- These checks are confirmatory and do not replace larger benchmark sweeps.",
        "",
        f"- Total real solver invocations: {int(runs_df.shape[0])}.",
        f"- Mean regret (all instances): {float(regret_df['regret_s'].mean()):.6f} s.",
        f"- Semantic pass rate (all instances): {float(runs_df['semantic_pass'].mean()):.4f}.",
    ]
    report_path = out_dir / "real_solver_confirmatory_report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return {
        "runs": runs_path,
        "regret": regret_path,
        "semantic_table": sem_path,
        "router_table": route_path,
        "report": report_path,
    }
