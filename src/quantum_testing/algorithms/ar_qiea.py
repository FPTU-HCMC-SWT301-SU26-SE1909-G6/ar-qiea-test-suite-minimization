"""Adaptive risk-aware quantum-inspired evolutionary algorithm."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np

from quantum_testing.metrics_mo import constrained_dominates, crowding_distance, hypervolume
from quantum_testing.problems.risk_problem import MOEvaluation, RiskAwareProblem


@dataclass(frozen=True)
class ArchiveEntry:
    solution: list[int]
    objectives: tuple[float, float, float]
    violation: float
    cr: float
    rop: float
    selected_count: int
    total_time: float


class ARQIEA:
    def __init__(
        self,
        problem: RiskAwareProblem,
        pop_size: int = 40,
        max_gen: int = 150,
        rotation_angle: float = 0.01 * math.pi,
        risk_alpha: float = 1.0,
        risk_adaptive: bool = True,
        archive_size: int = 50,
        seed: int | None = None,
        risk_shuffled: bool = False,
    ):
        self.problem = problem
        self.pop_size = int(pop_size)
        self.max_gen = int(max_gen)
        self.rotation_angle = float(rotation_angle)
        self.risk_alpha = float(risk_alpha)
        self.risk_adaptive = bool(risk_adaptive)
        self.archive_size = int(archive_size)
        self.seed = seed
        self.risk_shuffled = bool(risk_shuffled)
        self.rng = np.random.default_rng(seed)
        self.n_bits = problem.n_tests
        self.population = self._init_population()
        self.history_hv: list[float] = []

    def _init_population(self) -> np.ndarray:
        amp = 1.0 / math.sqrt(2)
        return np.full((self.pop_size, self.n_bits, 2), amp, dtype=float)

    def _observe_population(self) -> list[list[int]]:
        probabilities = self.population[:, :, 1] ** 2
        return (self.rng.random(probabilities.shape) < probabilities).astype(int).tolist()

    @staticmethod
    def _entry(solution: Sequence[int], evaluation: MOEvaluation) -> ArchiveEntry:
        return ArchiveEntry(
            solution=list(map(int, solution)),
            objectives=evaluation.objectives,
            violation=evaluation.violation,
            cr=evaluation.cr,
            rop=evaluation.rop,
            selected_count=evaluation.selected_count,
            total_time=evaluation.total_time,
        )

    @staticmethod
    def constrained_non_dominated(entries: Sequence[ArchiveEntry]) -> list[ArchiveEntry]:
        dedup: dict[tuple[int, ...], ArchiveEntry] = {}
        for entry in entries:
            key = tuple(entry.solution)
            existing = dedup.get(key)
            if existing is None or constrained_dominates(
                entry.objectives,
                entry.violation,
                existing.objectives,
                existing.violation,
            ):
                dedup[key] = entry
        unique = list(dedup.values())
        survivors: list[ArchiveEntry] = []
        for i, entry in enumerate(unique):
            dominated = False
            for j, other in enumerate(unique):
                if i != j and constrained_dominates(
                    other.objectives,
                    other.violation,
                    entry.objectives,
                    entry.violation,
                ):
                    dominated = True
                    break
            if not dominated:
                survivors.append(entry)
        return survivors

    def _prune_archive(self, archive: list[ArchiveEntry]) -> list[ArchiveEntry]:
        if len(archive) <= self.archive_size:
            return archive
        distances = crowding_distance([e.objectives for e in archive])
        order = sorted(range(len(archive)), key=lambda i: distances[i], reverse=True)
        return [archive[i] for i in order[: self.archive_size]]

    def _rotate_toward(self, i: int, q: int, observed_bit: int, guide_bit: int, delta: float) -> None:
        if observed_bit == guide_bit:
            return
        theta = delta if observed_bit == 0 and guide_bit == 1 else -delta
        alpha, beta = self.population[i, q]
        new_alpha = alpha * math.cos(theta) - beta * math.sin(theta)
        new_beta = alpha * math.sin(theta) + beta * math.cos(theta)
        norm = math.sqrt(new_alpha * new_alpha + new_beta * new_beta)
        if norm > 0:
            self.population[i, q, 0] = new_alpha / norm
            self.population[i, q, 1] = new_beta / norm

    def _inject_diversity(self) -> None:
        count = max(1, int(math.ceil(0.25 * self.pop_size)))
        indices = self.rng.choice(self.pop_size, size=count, replace=False)
        amp = 1.0 / math.sqrt(2)
        self.population[indices, :, :] = amp

    def run(self, verbose: bool = False) -> list[ArchiveEntry]:
        self.population = self._init_population()
        self.history_hv = []
        archive: list[ArchiveEntry] = []
        risk = self.problem.test_risk_scores()
        if self.risk_shuffled:
            risk = self.rng.permutation(risk)

        for gen in range(self.max_gen):
            solutions = self._observe_population()
            new_entries = [self._entry(sol, self.problem.evaluate(sol)) for sol in solutions]
            archive = self.constrained_non_dominated([*archive, *new_entries])
            archive = self._prune_archive(archive)
            feasible_points = [e.objectives for e in archive if e.violation <= 1e-12]
            self.history_hv.append(hypervolume(feasible_points) if feasible_points else 0.0)

            if not archive:
                continue
            decay = 1.0 - 0.5 * gen / max(1, self.max_gen)
            for i in range(self.pop_size):
                guide = archive[int(self.rng.integers(0, len(archive)))]
                for q in range(self.n_bits):
                    if solutions[i][q] != guide.solution[q]:
                        multiplier = 1.0 + self.risk_alpha * risk[q] if self.risk_adaptive else 1.0
                        self._rotate_toward(i, q, solutions[i][q], guide.solution[q], self.rotation_angle * decay * multiplier)
                    if self.rng.random() < 1.0 / self.n_bits:
                        self.population[i, q, 0], self.population[i, q, 1] = (
                            self.population[i, q, 1],
                            self.population[i, q, 0],
                        )
            if gen > 0 and gen % 20 == 0 and float(np.std(self.population[:, :, 0])) < 0.05:
                self._inject_diversity()

        final = [e for e in self.constrained_non_dominated(archive) if e.violation <= 1e-12]
        return self._prune_archive(final)
