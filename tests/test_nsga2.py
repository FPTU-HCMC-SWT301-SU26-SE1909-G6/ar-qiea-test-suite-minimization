import numpy as np

from quantum_testing.algorithms.nsga2 import NSGA2
from quantum_testing.problems.risk_problem import RiskAwareProblem


def make_problem() -> RiskAwareProblem:
    coverage = np.array(
        [
            [1, 0, 0, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [1, 1, 0, 0],
            [0, 1, 1, 0],
        ],
        dtype=bool,
    )
    centrality = np.array([1.0, 2.0, 1.5, 0.5])
    mutation = np.array(
        [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 0],
            [0, 1, 1],
        ],
        dtype=bool,
    )
    return RiskAwareProblem(coverage, centrality, mutation, np.ones(5), cr_threshold=0.75)


def test_nsga2_returns_feasible_front():
    algo = NSGA2(make_problem(), pop_size=12, max_gen=12, seed=42)
    front = algo.run()
    assert front
    assert all(entry.violation == 0 for entry in front)
    assert all(len(entry.solution) == 5 for entry in front)
    assert algo.evaluation_count == 12 * 12
