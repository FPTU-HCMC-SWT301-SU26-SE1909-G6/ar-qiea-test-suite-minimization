"""Constrained binary NSGA-II baseline."""
from __future__ import annotations

from typing import Sequence

import numpy as np

from quantum_testing.algorithms.ar_qiea import ArchiveEntry
from quantum_testing.metrics_mo import constrained_dominates, crowding_distance
from quantum_testing.problems.risk_problem import MOEvaluation, RiskAwareProblem


class NSGA2:
    def __init__(
        self,
        problem: RiskAwareProblem,
        pop_size: int = 40,
        max_gen: int = 150,
        crossover_rate: float = 0.9,
        mutation_rate: float | None = None,
        seed: int | None = None,
    ):
        self.problem = problem
        self.pop_size = int(pop_size)
        self.max_gen = int(max_gen)
        self.crossover_rate = float(crossover_rate)
        self.mutation_rate = mutation_rate
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.n_bits = problem.n_tests
        if self.mutation_rate is None:
            self.mutation_rate = 1.0 / self.n_bits
        self.evaluation_count = 0

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

    def _evaluate_population(self, population: np.ndarray) -> list[ArchiveEntry]:
        self.evaluation_count += int(len(population))
        return [self._entry(row.tolist(), self.problem.evaluate(row.tolist())) for row in population]

    @staticmethod
    def _sort(entries: Sequence[ArchiveEntry]) -> list[list[int]]:
        n = len(entries)
        dominates_sets: list[list[int]] = [[] for _ in range(n)]
        dominated_counts = [0] * n
        fronts: list[list[int]] = [[]]
        for p in range(n):
            for q in range(n):
                if p == q:
                    continue
                if constrained_dominates(
                    entries[p].objectives,
                    entries[p].violation,
                    entries[q].objectives,
                    entries[q].violation,
                ):
                    dominates_sets[p].append(q)
                elif constrained_dominates(
                    entries[q].objectives,
                    entries[q].violation,
                    entries[p].objectives,
                    entries[p].violation,
                ):
                    dominated_counts[p] += 1
            if dominated_counts[p] == 0:
                fronts[0].append(p)

        i = 0
        while i < len(fronts) and fronts[i]:
            next_front: list[int] = []
            for p in fronts[i]:
                for q in dominates_sets[p]:
                    dominated_counts[q] -= 1
                    if dominated_counts[q] == 0:
                        next_front.append(q)
            if next_front:
                fronts.append(next_front)
            i += 1
        return fronts

    def _rank_and_crowding(self, entries: Sequence[ArchiveEntry]) -> tuple[list[int], list[float]]:
        fronts = self._sort(entries)
        ranks = [0] * len(entries)
        distances = [0.0] * len(entries)
        for rank, front in enumerate(fronts):
            front_points = [entries[i].objectives for i in front]
            front_distances = crowding_distance(front_points)
            for local, idx in enumerate(front):
                ranks[idx] = rank
                distances[idx] = front_distances[local]
        return ranks, distances

    def _tournament(self, ranks: Sequence[int], distances: Sequence[float]) -> int:
        a, b = self.rng.integers(0, len(ranks), size=2)
        if ranks[a] < ranks[b]:
            return int(a)
        if ranks[b] < ranks[a]:
            return int(b)
        return int(a if distances[a] >= distances[b] else b)

    def _make_offspring(self, population: np.ndarray, entries: Sequence[ArchiveEntry]) -> np.ndarray:
        ranks, distances = self._rank_and_crowding(entries)
        children: list[np.ndarray] = []
        while len(children) < self.pop_size:
            p1 = population[self._tournament(ranks, distances)].copy()
            p2 = population[self._tournament(ranks, distances)].copy()
            if self.n_bits > 1 and self.rng.random() < self.crossover_rate:
                cut = int(self.rng.integers(1, self.n_bits))
                c1 = np.concatenate([p1[:cut], p2[cut:]])
                c2 = np.concatenate([p2[:cut], p1[cut:]])
            else:
                c1, c2 = p1, p2
            for child in (c1, c2):
                flips = self.rng.random(self.n_bits) < float(self.mutation_rate)
                child[flips] = 1 - child[flips]
                children.append(child.astype(int))
                if len(children) >= self.pop_size:
                    break
        return np.asarray(children, dtype=int)

    def _select_next(self, combined: np.ndarray, entries: Sequence[ArchiveEntry]) -> np.ndarray:
        selected = self._selected_indices(entries)
        return combined[selected]

    def run(self, verbose: bool = False) -> list[ArchiveEntry]:
        self.evaluation_count = 0
        population = self.rng.integers(0, 2, size=(self.pop_size, self.n_bits), dtype=int)
        entries = self._evaluate_population(population)
        for _ in range(max(0, self.max_gen - 1)):
            offspring = self._make_offspring(population, entries)
            offspring_entries = self._evaluate_population(offspring)
            combined = np.vstack([population, offspring])
            combined_entries = [*entries, *offspring_entries]
            population = self._select_next(combined, combined_entries)
            entries = [combined_entries[i] for i in self._selected_indices(combined_entries)]
        fronts = self._sort(entries)
        first_front = [entries[i] for i in fronts[0]] if fronts else []
        return [e for e in first_front if e.violation <= 1e-12]

    def _selected_indices(self, entries: Sequence[ArchiveEntry]) -> list[int]:
        fronts = self._sort(entries)
        selected: list[int] = []
        for front in fronts:
            if len(selected) + len(front) <= self.pop_size:
                selected.extend(front)
            else:
                distances = crowding_distance([entries[i].objectives for i in front])
                order = sorted(range(len(front)), key=lambda i: distances[i], reverse=True)
                selected.extend(front[i] for i in order[: self.pop_size - len(selected)])
                break
        return selected
