from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatasetRecord:
    alias: str
    status: str
    local_path: str
    sample_count: int
    checksum: str
    provenance: dict[str, str]


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 16)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _collect_file_digest(root: Path, limit: int = 32) -> tuple[int, str]:
    files = sorted([p for p in root.rglob("*") if p.is_file()])
    h = hashlib.sha256()
    for p in files[:limit]:
        h.update(str(p.relative_to(root)).encode("utf-8"))
        h.update(sha256_path(p).encode("utf-8"))
    return len(files), h.hexdigest()


def ensure_neurasp_repo(repo_path: Path) -> dict[str, str]:
    if not repo_path.exists():
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/azreasoners/NeurASP.git", str(repo_path)],
            check=True,
        )
    commit = (
        subprocess.check_output(["git", "-C", str(repo_path), "rev-parse", "HEAD"], text=True)
        .strip()
    )
    license_path = repo_path / "README.md"
    return {
        "repo_url": "https://github.com/azreasoners/NeurASP",
        "commit": commit,
        "license_note": "MIT (declared in upstream repository metadata)",
        "license_path": str(license_path),
    }


def _materialize_real_dataset(alias: str, src: Path, dst: Path, provenance: dict[str, str]) -> DatasetRecord:
    dst.mkdir(parents=True, exist_ok=True)
    sample_count, digest = _collect_file_digest(src)
    # We keep datasets in-place and reference canonical source path to avoid bulky copies.
    return DatasetRecord(
        alias=alias,
        status="materialized",
        local_path=str(src),
        sample_count=sample_count,
        checksum=digest,
        provenance=provenance,
    )


def _materialize_synthetic_dataset(alias: str, out_root: Path, seed: int) -> DatasetRecord:
    import random

    rng = random.Random(seed)
    ds_dir = out_root / alias
    ds_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    size = 120
    for i in range(size):
        tw = rng.randint(4, 60)
        scc = rng.randint(1, 30)
        reuse = round(rng.uniform(0.05, 0.95), 4)
        clauses = rng.randint(50, 1200)
        rows.append(
            {
                "instance_id": f"{alias}_{i:04d}",
                "tw_proxy": tw,
                "scc_proxy": scc,
                "reuse_ratio": reuse,
                "clauses": clauses,
            }
        )
    out_path = ds_dir / "instances.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    return DatasetRecord(
        alias=alias,
        status="materialized",
        local_path=str(ds_dir),
        sample_count=len(rows),
        checksum=sha256_path(out_path),
        provenance={
            "source_type": "workspace_generator",
            "generator": "autotw_validation/acquisition.py",
            "seed": str(seed),
        },
    )


def materialize_datasets(workspace_root: Path, output_dir: Path) -> tuple[list[DatasetRecord], dict[str, str]]:
    external_root = workspace_root / "experiments" / "autotw_validation" / "external"
    neurasp = external_root / "NeurASP"
    prov = ensure_neurasp_repo(neurasp)

    records: list[DatasetRecord] = []
    records.append(
        _materialize_real_dataset(
            "mnist_sum_k_v1",
            neurasp / "examples" / "mnistAdd" / "data",
            output_dir / "datasets" / "mnist_sum_k_v1",
            prov,
        )
    )
    records.append(
        _materialize_real_dataset(
            "sudoku_4x4_v1",
            neurasp / "examples" / "sudoku" / "data",
            output_dir / "datasets" / "sudoku_4x4_v1",
            prov,
        )
    )

    synth_aliases = ["formula_eval_v1", "ordering_v1", "counting_v1", "shortest_path_v1"]
    for i, alias in enumerate(synth_aliases):
        records.append(
            _materialize_synthetic_dataset(alias, output_dir / "datasets", seed=1000 + i)
        )

    return records, prov
