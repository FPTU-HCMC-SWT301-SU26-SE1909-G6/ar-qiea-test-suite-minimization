"""Multi-objective metrics for Pareto test-suite minimization."""
from __future__ import annotations

import math
from typing import Sequence


Point = Sequence[float]


def _clean_point(point: Point) -> tuple[float, ...]:
    return tuple(max(0.0, float(v)) for v in point)


def dominates(a: Point, b: Point) -> bool:
    """Return True when point ``a`` Pareto-dominates ``b`` for maximization."""
    if len(a) != len(b):
        raise ValueError("points must have the same dimensionality")
    return all(float(x) >= float(y) for x, y in zip(a, b)) and any(
        float(x) > float(y) for x, y in zip(a, b)
    )


def constrained_dominates(
    a_objs: Point,
    a_viol: float,
    b_objs: Point,
    b_viol: float,
    eps: float = 1e-12,
) -> bool:
    """Deb's constraint-domination rule."""
    a_feasible = float(a_viol) <= eps
    b_feasible = float(b_viol) <= eps
    if a_feasible and not b_feasible:
        return True
    if not a_feasible and b_feasible:
        return False
    if not a_feasible and not b_feasible:
        return float(a_viol) < float(b_viol) - eps
    return dominates(a_objs, b_objs)


def non_dominated_filter(points: Sequence[Point]) -> list[int]:
    """Return indices of non-dominated points under maximization."""
    survivors: list[int] = []
    for i, point in enumerate(points):
        if not any(j != i and dominates(other, point) for j, other in enumerate(points)):
            survivors.append(i)
    return survivors


def crowding_distance(points: Sequence[Point]) -> list[float]:
    """NSGA-II crowding distance for maximization objectives."""
    n = len(points)
    if n == 0:
        return []
    if n <= 2:
        return [math.inf] * n

    dim = len(points[0])
    distances = [0.0] * n
    for m in range(dim):
        order = sorted(range(n), key=lambda i: float(points[i][m]))
        distances[order[0]] = math.inf
        distances[order[-1]] = math.inf
        min_v = float(points[order[0]][m])
        max_v = float(points[order[-1]][m])
        span = max_v - min_v
        if span <= 0:
            continue
        for pos in range(1, n - 1):
            if math.isinf(distances[order[pos]]):
                continue
            prev_v = float(points[order[pos - 1]][m])
            next_v = float(points[order[pos + 1]][m])
            distances[order[pos]] += (next_v - prev_v) / span
    return distances


def _unique_nondominated(points: Sequence[Point], dim: int) -> list[tuple[float, ...]]:
    cleaned = [_clean_point(p) for p in points if len(p) == dim]
    unique = list(dict.fromkeys(cleaned))
    return [unique[i] for i in non_dominated_filter(unique)]


def hypervolume_2d(points: Sequence[Point]) -> float:
    """Exact 2D hypervolume for maximization with reference point (0, 0)."""
    front = _unique_nondominated(points, 2)
    if not front:
        return 0.0

    hv = 0.0
    prev_x = 0.0
    for x, y in sorted(front, key=lambda p: p[0]):
        width = max(0.0, x - prev_x)
        hv += width * max(0.0, y)
        prev_x = max(prev_x, x)
    return float(hv)


def hypervolume_3d(points: Sequence[Point]) -> float:
    """Exact 3D hypervolume for maximization with reference point (0, 0, 0)."""
    front = _unique_nondominated(points, 3)
    if not front:
        return 0.0

    xs = sorted({p[0] for p in front})
    hv = 0.0
    prev_x = 0.0
    for x in xs:
        width = max(0.0, x - prev_x)
        active_yz = [(p[1], p[2]) for p in front if p[0] >= x]
        hv += width * hypervolume_2d(active_yz)
        prev_x = x
    return float(hv)


def hypervolume(points: Sequence[Point]) -> float:
    if not points:
        return 0.0
    dim = len(points[0])
    if dim == 2:
        return hypervolume_2d(points)
    if dim == 3:
        return hypervolume_3d(points)
    raise ValueError("hypervolume only supports 2D or 3D points")
