from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RunConfig:
    experiment_id: str
    stage: str
    output_dir: Path
    figures_dir: Path
    tables_dir: Path
    data_dir: Path
    logs_dir: Path
    seeds: list[int]
    smoke_seed_count: int


def load_config(path: Path, stage: str) -> RunConfig:
    raw = yaml.safe_load(path.read_text())
    out_root = Path(raw["output_dir"])
    figures_dir = Path(raw["figures_dir"])
    tables_dir = Path(raw["tables_dir"])
    data_dir = Path(raw["data_dir"])
    logs_dir = out_root / "logs"
    for p in (out_root, figures_dir, tables_dir, data_dir, logs_dir):
        p.mkdir(parents=True, exist_ok=True)
    seeds = [int(x) for x in raw["seeds"]]
    smoke_seed_count = int(raw.get("smoke_seed_count", 2))
    return RunConfig(
        experiment_id=str(raw["experiment_id"]),
        stage=stage,
        output_dir=out_root,
        figures_dir=figures_dir,
        tables_dir=tables_dir,
        data_dir=data_dir,
        logs_dir=logs_dir,
        seeds=seeds,
        smoke_seed_count=smoke_seed_count,
    )


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
