"""Mutation-data utilities."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np


def synthetic_mutation_matrix(
    coverage: np.ndarray,
    seed: int,
    n_mutants_factor: float = 2.0,
    kill_prob: float = 0.6,
) -> np.ndarray:
    """Generate a seeded synthetic kill matrix coupled to requirement coverage."""
    cov = np.asarray(coverage, dtype=bool)
    if cov.ndim != 2 or cov.size == 0:
        raise ValueError("coverage must be a non-empty 2D matrix")
    if n_mutants_factor < 0:
        raise ValueError("n_mutants_factor must be non-negative")
    if not 0.0 <= kill_prob <= 1.0:
        raise ValueError("kill_prob must be in [0, 1]")

    rng = np.random.default_rng(seed)
    n_tests, n_reqs = cov.shape
    n_mutants = max(1, int(round(n_mutants_factor * n_reqs)))
    coverable_reqs = np.flatnonzero(cov.any(axis=0))
    if coverable_reqs.size == 0:
        return np.zeros((n_tests, n_mutants), dtype=bool)

    mutant_reqs = rng.choice(coverable_reqs, size=n_mutants, replace=True)
    kills = np.zeros((n_tests, n_mutants), dtype=bool)
    for k, req in enumerate(mutant_reqs):
        eligible = cov[:, req]
        kills[:, k] = eligible & (rng.random(n_tests) < kill_prob)
    return kills


def run_major_mutation(project: str, bug: int, tests: list[str], workdir: str) -> np.ndarray:
    """Run Defects4J/Major per-test mutation and parse a coarse kill matrix.

    This wrapper is intentionally conservative. It executes the expected command
    for each test and records whether any mutant was killed. Full Major
    kill-matrix parsing is project-layout dependent and should be cached by the
    caller for paper runs.
    """
    kills = np.zeros((len(tests), 1), dtype=bool)
    for i, test_id in enumerate(tests):
        cmd = ["wsl.exe", "defects4j", "mutation", "-w", workdir, "-t", test_id]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30 * 60, check=False)
        output = result.stdout + result.stderr
        kills[i, 0] = "killed" in output.lower() or "KILLED" in output
        cache_dir = Path(workdir) / ".quantum_testing_mutation_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / f"{project}-{bug}-{i}.log").write_text(output, encoding="utf-8")
    return kills
