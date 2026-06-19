"""Basic software-testing metrics."""
from __future__ import annotations

from typing import Iterable, Sequence


def coverage_ratio(covered: Iterable[int], total_requirements: int) -> float:
    if total_requirements <= 0:
        return 1.0
    return len(set(covered)) / total_requirements


def reduction_ratio(selected_count: int, total_count: int) -> float:
    if total_count <= 0:
        return 0.0
    return 1.0 - selected_count / total_count


def apfd(ordered_fault_flags: Sequence[bool | int]) -> float:
    n = len(ordered_fault_flags)
    fault_positions = [i + 1 for i, flag in enumerate(ordered_fault_flags) if bool(flag)]
    m = len(fault_positions)
    if n == 0 or m == 0:
        return 0.0
    return 1.0 - (sum(fault_positions) / (n * m)) + (1.0 / (2 * n))
