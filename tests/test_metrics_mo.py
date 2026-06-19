import pytest

from quantum_testing.metrics_mo import (
    constrained_dominates,
    dominates,
    hypervolume,
    hypervolume_2d,
    hypervolume_3d,
)


def test_dominates_maximization():
    assert dominates((1, 1, 1), (1, 1, 0.5))
    assert not dominates((1, 0), (0, 1))


def test_constrained_dominance_prefers_feasible():
    assert constrained_dominates((0, 0, 0), 0.0, (1, 1, 1), 0.1)
    assert constrained_dominates((0, 0, 0), 0.1, (1, 1, 1), 0.2)


def test_hypervolume_2d_examples():
    assert hypervolume_2d([(1, 1)]) == pytest.approx(1.0)
    assert hypervolume_2d([(1, 0.5), (0.5, 1)]) == pytest.approx(0.75)


def test_hypervolume_3d_examples():
    assert hypervolume_3d([(1, 1, 1)]) == pytest.approx(1.0)
    assert hypervolume_3d([(1, 0.5, 0.5), (0.5, 1, 0.5)]) == pytest.approx(0.375)


def test_dominated_points_do_not_increase_hypervolume():
    front = [(1, 0.5), (0.5, 1)]
    assert hypervolume_2d([*front, (0.25, 0.25)]) == pytest.approx(hypervolume_2d(front))
    front3 = [(1, 0.5, 0.5), (0.5, 1, 0.5)]
    assert hypervolume_3d([*front3, (0.25, 0.25, 0.25)]) == pytest.approx(hypervolume_3d(front3))


def test_hypervolume_dispatch_and_empty():
    assert hypervolume([]) == 0.0
    assert hypervolume([(1, 1)]) == pytest.approx(1.0)
