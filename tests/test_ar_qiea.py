import numpy as np

from quantum_testing.algorithms.ar_qiea import ARQIEA, ArchiveEntry
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


def test_ar_qiea_returns_feasible_archive_entries():
    front = ARQIEA(make_problem(), pop_size=12, max_gen=20, seed=42, archive_size=10).run()
    assert front
    assert all(isinstance(entry, ArchiveEntry) for entry in front)
    assert all(entry.violation == 0 for entry in front)
    assert all(len(entry.objectives) == 3 for entry in front)


def test_mo_qiea_ablation_mode_runs():
    front = ARQIEA(make_problem(), pop_size=10, max_gen=15, seed=3, risk_adaptive=False).run()
    assert all(entry.violation == 0 for entry in front)
