import numpy as np
import pytest

from quantum_testing.analyzers.centrality import frequency_centrality_proxy
from quantum_testing.analyzers.mutation import synthetic_mutation_matrix
from quantum_testing.problems.risk_problem import RiskAwareProblem


def make_problem() -> RiskAwareProblem:
    coverage = np.array(
        [
            [1, 0, 1],
            [0, 1, 0],
            [1, 1, 0],
        ],
        dtype=bool,
    )
    centrality = np.array([1.0, 2.0, 3.0])
    mutation = np.array(
        [
            [1, 0],
            [0, 1],
            [1, 1],
        ],
        dtype=bool,
    )
    exec_times = np.array([2.0, 3.0, 5.0])
    return RiskAwareProblem(coverage, centrality, mutation, exec_times, cr_threshold=0.95)


def test_evaluate_all_zero_solution():
    ev = make_problem().evaluate([0, 0, 0])
    assert ev.cr == 0.0
    assert ev.objectives == pytest.approx((0.0, 0.0, 1.0))
    assert ev.violation == pytest.approx(0.95)
    assert ev.selected_count == 0


def test_evaluate_vectorized_objectives():
    ev = make_problem().evaluate([1, 0, 1])
    assert ev.cr == pytest.approx(1.0)
    assert ev.violation == 0.0
    assert ev.objectives[0] == pytest.approx(1.0)
    assert ev.objectives[1] == pytest.approx(1.0)
    assert ev.objectives[2] == pytest.approx(0.3)
    assert ev.rop > 0.0


def test_no_killed_mutants_degenerate_msr():
    coverage = np.eye(2, dtype=bool)
    problem = RiskAwareProblem(coverage, np.ones(2), np.zeros((2, 2), dtype=bool), np.ones(2))
    assert problem.evaluate([1, 0]).objectives[0] == pytest.approx(1.0)


def test_risk_scores_are_normalized():
    risk = make_problem().test_risk_scores()
    assert risk.shape == (3,)
    assert np.all(risk >= 0)
    assert np.all(risk <= 1)


def test_synthetic_analyzers_are_seeded():
    coverage = np.array([[1, 0], [1, 1]], dtype=bool)
    assert np.allclose(frequency_centrality_proxy(coverage, 123), frequency_centrality_proxy(coverage, 123))
    assert np.array_equal(synthetic_mutation_matrix(coverage, 123), synthetic_mutation_matrix(coverage, 123))


def test_matrix_csv_loader_with_header_and_ids(tmp_path):
    matrix = tmp_path / "matrix.csv"
    matrix.write_text("test_id,r0,r1\nt0,1,0\nt1,0,1\n", encoding="utf-8")
    problem = RiskAwareProblem.from_matrix_csv(matrix, risk_seed=7)
    assert problem.coverage.shape == (2, 2)
    assert problem.test_ids == ["t0", "t1"]
    assert problem.requirements == ["r0", "r1"]


def test_matrix_csv_loader_numeric_only(tmp_path):
    matrix = tmp_path / "matrix.csv"
    matrix.write_text("1,0,1\n0,1,0\n", encoding="utf-8")
    problem = RiskAwareProblem.from_matrix_csv(matrix, risk_seed=7)
    assert problem.coverage.shape == (2, 3)
    assert problem.test_ids == ["t0", "t1"]
    assert problem.requirements == ["r0", "r1", "r2"]


def test_invalid_empty_matrix_raises():
    with pytest.raises(ValueError):
        RiskAwareProblem(np.array([]), np.array([]), np.array([]), np.array([]))
