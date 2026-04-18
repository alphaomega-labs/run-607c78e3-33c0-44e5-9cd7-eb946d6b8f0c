from pathlib import Path


def test_shell_layout() -> None:
    root = Path("experiments/autotw_validation")
    assert (root / "run_experiments.py").exists()
    assert (root / "src" / "autotw_validation" / "simulation.py").exists()
    assert (root / "configs" / "full.yaml").exists()
