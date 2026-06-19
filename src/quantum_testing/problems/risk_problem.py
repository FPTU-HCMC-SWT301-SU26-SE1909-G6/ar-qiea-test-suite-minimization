"""Risk-aware multi-objective test-suite minimization problem."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from quantum_testing.analyzers.centrality import frequency_centrality_proxy
from quantum_testing.analyzers.mutation import synthetic_mutation_matrix


@dataclass(frozen=True)
class MOEvaluation:
    objectives: tuple[float, float, float]
    cr: float
    violation: float
    rop: float
    selected_count: int
    total_time: float


class RiskAwareProblem:
    def __init__(
        self,
        coverage: np.ndarray,
        centrality: np.ndarray,
        mutation: np.ndarray,
        exec_times: np.ndarray,
        cr_threshold: float = 0.95,
        test_ids: Sequence[str] | None = None,
        requirements: Sequence[str] | None = None,
    ):
        self.coverage = np.asarray(coverage, dtype=bool)
        self.centrality = np.asarray(centrality, dtype=float)
        self.mutation = np.asarray(mutation, dtype=bool)
        self.exec_times = np.asarray(exec_times, dtype=float)
        self.cr_threshold = float(cr_threshold)

        if self.coverage.ndim != 2 or self.coverage.size == 0:
            raise ValueError("coverage must be a non-empty 2D matrix")
        self.n_tests, self.n_requirements = self.coverage.shape
        if self.n_tests == 0 or self.n_requirements == 0:
            raise ValueError("coverage must include at least one test and one requirement")
        if self.centrality.shape != (self.n_requirements,):
            raise ValueError("centrality must have shape (n_requirements,)")
        if self.mutation.ndim != 2 or self.mutation.shape[0] != self.n_tests:
            raise ValueError("mutation must have shape (n_tests, n_mutants)")
        if self.exec_times.shape != (self.n_tests,):
            raise ValueError("exec_times must have shape (n_tests,)")
        if np.any(self.centrality < 0):
            raise ValueError("centrality weights must be non-negative")
        if np.any(self.exec_times <= 0):
            raise ValueError("exec_times must be positive")
        if not 0.0 <= self.cr_threshold <= 1.0:
            raise ValueError("cr_threshold must be in [0, 1]")

        self.test_ids = list(test_ids) if test_ids is not None else [f"t{i}" for i in range(self.n_tests)]
        self.requirements = (
            list(requirements) if requirements is not None else [f"r{j}" for j in range(self.n_requirements)]
        )

        self._covered_by_original = self.coverage.any(axis=0)
        self._killed_by_original = self.mutation.any(axis=0) if self.mutation.shape[1] else np.zeros(0, dtype=bool)
        self._cov_den = int(self._covered_by_original.sum())
        self._killed_den = int(self._killed_by_original.sum())
        self._cgcc_den = float(self.centrality[self._covered_by_original].sum())
        self._time_den = float(self.exec_times.sum())

    @classmethod
    def from_matrix_csv(
        cls,
        path,
        risk_seed: int = 12345,
        cr_threshold: float = 0.95,
        n_mutants_factor: float = 2.0,
        kill_prob: float = 0.6,
        cost_exponent: float = 1.3,
        noise_sigma: float = 0.3,
    ) -> "RiskAwareProblem":
        coverage, test_ids, requirements = _load_matrix_csv(path)
        centrality = frequency_centrality_proxy(coverage, seed=risk_seed, noise_sigma=noise_sigma)
        mutation = synthetic_mutation_matrix(
            coverage,
            seed=risk_seed,
            n_mutants_factor=n_mutants_factor,
            kill_prob=kill_prob,
        )
        rng = np.random.default_rng(risk_seed)
        cover_counts = np.maximum(1, coverage.sum(axis=1).astype(float))
        exec_times = (cover_counts**cost_exponent) * rng.lognormal(mean=0.0, sigma=noise_sigma, size=coverage.shape[0])
        exec_times = np.maximum(exec_times, 1e-9)
        return cls(
            coverage=coverage,
            centrality=centrality,
            mutation=mutation,
            exec_times=exec_times,
            cr_threshold=cr_threshold,
            test_ids=test_ids,
            requirements=requirements,
        )

    def evaluate(self, solution: Sequence[int]) -> MOEvaluation:
        sel = np.asarray(solution, dtype=bool)
        if sel.shape[0] != self.n_tests:
            raise ValueError("solution length must equal number of tests")

        selected_count = int(sel.sum())
        if selected_count:
            covered = self.coverage[sel].any(axis=0)
            killed = self.mutation[sel].any(axis=0) if self.mutation.shape[1] else np.zeros(0, dtype=bool)
            hits = self.coverage[sel].sum(axis=0)
        else:
            covered = np.zeros(self.n_requirements, dtype=bool)
            killed = np.zeros(self.mutation.shape[1], dtype=bool)
            hits = np.zeros(self.n_requirements, dtype=int)

        cr = float(covered[self._covered_by_original].sum() / self._cov_den) if self._cov_den else 1.0
        violation = max(0.0, self.cr_threshold - cr)
        msr = float(killed[self._killed_by_original].sum() / self._killed_den) if self._killed_den else 1.0
        cgcc = float(self.centrality[covered].sum() / self._cgcc_den) if self._cgcc_den > 0 else 1.0
        selected_time = float(self.exec_times[sel].sum())
        etr = 1.0 - selected_time / self._time_den if self._time_den > 0 else 0.0
        total_hits = int(hits.sum())
        rop = float(np.maximum(0, hits - 1).sum() / max(1, total_hits))
        return MOEvaluation(
            objectives=(_clip01(msr), _clip01(cgcc), _clip01(etr)),
            cr=_clip01(cr),
            violation=float(violation),
            rop=_clip01(rop),
            selected_count=selected_count,
            total_time=selected_time,
        )

    def test_risk_scores(self) -> np.ndarray:
        centrality_mass = self.coverage.astype(float) @ self.centrality
        mutation_mass = self.mutation.sum(axis=1).astype(float) if self.mutation.shape[1] else np.zeros(self.n_tests)
        risk = 0.5 * _normalize(centrality_mass) + 0.5 * _normalize(mutation_mass)
        return np.clip(risk, 0.0, 1.0)


def _clip01(value: float) -> float:
    return float(min(1.0, max(0.0, value)))


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    max_v = float(values.max()) if values.size else 0.0
    if max_v <= 0:
        return np.zeros_like(values, dtype=float)
    return values / max_v


def _is_bool_token(cell: str) -> bool:
    return cell.strip().lower() in {"0", "1", "true", "false", "t", "f"}


def _bool_value(cell: str) -> bool:
    token = cell.strip().lower()
    if token in {"1", "true", "t"}:
        return True
    if token in {"0", "false", "f"}:
        return False
    raise ValueError(f"invalid coverage value: {cell!r}")


def _load_matrix_csv(path: str | Path) -> tuple[np.ndarray, list[str], list[str]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [row for row in csv.reader(f) if row]
    if not rows:
        raise ValueError("matrix CSV is empty")

    first = rows[0]
    first_is_data = all(_is_bool_token(c) for c in first) or (
        len(first) > 1 and not _is_bool_token(first[0]) and all(_is_bool_token(c) for c in first[1:])
    )
    has_header = not first_is_data
    header = first if has_header else []
    data_rows = rows[1:] if has_header else rows
    if not data_rows:
        raise ValueError("matrix CSV has no data rows")

    data: list[list[bool]] = []
    test_ids: list[str] = []
    data_width: int | None = None
    for i, row in enumerate(data_rows):
        if not row:
            continue
        has_id = not _is_bool_token(row[0])
        cells = row[1:] if has_id else row
        if data_width is None:
            data_width = len(cells)
        elif len(cells) != data_width:
            raise ValueError("matrix CSV rows have inconsistent widths")
        data.append([_bool_value(c) for c in cells])
        test_ids.append(row[0] if has_id else f"t{i}")

    if not data or data_width is None or data_width == 0:
        raise ValueError("matrix CSV contains no coverage values")
    requirements = header[1:] if has_header and len(header) == data_width + 1 else header[:data_width]
    if not requirements:
        requirements = [f"r{j}" for j in range(data_width)]
    return np.asarray(data, dtype=bool), test_ids, requirements
