"""Command-line interface for quantum-testing."""
from __future__ import annotations

import argparse
import json

from quantum_testing.algorithms import ARQIEA, NSGA2, QIEA
from quantum_testing.problems.coverage import CoverageProblem
from quantum_testing.problems.risk_problem import RiskAwareProblem


def _solve_coverage(problem: CoverageProblem, algorithm: str, seed: int) -> dict:
    if algorithm == "greedy":
        uncovered = set(range(problem.n_requirements))
        selected: list[int] = []
        while uncovered:
            best = max(
                range(problem.n_tests),
                key=lambda i: len(problem.coverage_sets[i] & uncovered),
            )
            gain = problem.coverage_sets[best] & uncovered
            if not gain:
                break
            selected.append(best)
            uncovered -= gain
        sol = [1 if i in selected else 0 for i in range(problem.n_tests)]
        return problem.report(sol).to_dict()
    if algorithm == "qiea":
        sol, _, _ = QIEA(problem.n_tests, pop_size=24, max_gen=160, evaluate_fn=problem.fitness, seed=seed).run()
        return problem.report(sol).to_dict()
    raise ValueError(f"unknown algorithm: {algorithm}")


def cmd_demo(args) -> None:
    q = QIEA(20, 12, 80, evaluate_fn=sum, seed=args.seed)
    sol, fit, _ = q.run()
    problem = CoverageProblem.synthetic(20, 15, seed=args.seed)
    print(json.dumps({"onemax": {"fitness": fit, "solution": sol}, "coverage": _solve_coverage(problem, "qiea", args.seed)}, indent=2))


def cmd_minimize(args) -> None:
    problem = CoverageProblem.load_csv(args.matrix) if args.matrix else CoverageProblem.synthetic(seed=args.seed)
    print(json.dumps(_solve_coverage(problem, args.algorithm, args.seed), indent=2))


def cmd_pareto(args) -> None:
    problem = RiskAwareProblem.from_matrix_csv(args.matrix, risk_seed=args.risk_seed, cr_threshold=args.cr_threshold)
    if args.algo == "ar-qiea":
        front = ARQIEA(problem, pop_size=args.pop, max_gen=args.gens, seed=args.seed).run()
    elif args.algo == "mo-qiea":
        front = ARQIEA(problem, pop_size=args.pop, max_gen=args.gens, seed=args.seed, risk_adaptive=False).run()
    else:
        front = NSGA2(problem, pop_size=args.pop, max_gen=args.gens, seed=args.seed).run()
    print(json.dumps({"front": [entry.__dict__ for entry in front]}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quantum-testing")
    sub = parser.add_subparsers(required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--seed", type=int, default=42)
    demo.set_defaults(func=cmd_demo)
    minimize = sub.add_parser("minimize")
    minimize.add_argument("--matrix")
    minimize.add_argument("--algorithm", choices=["qiea", "greedy"], default="qiea")
    minimize.add_argument("--seed", type=int, default=42)
    minimize.set_defaults(func=cmd_minimize)
    pareto = sub.add_parser("pareto")
    pareto.add_argument("--matrix", required=True)
    pareto.add_argument("--algo", choices=["ar-qiea", "mo-qiea", "nsga2"], default="ar-qiea")
    pareto.add_argument("--seed", type=int, default=42)
    pareto.add_argument("--risk-seed", type=int, default=12345)
    pareto.add_argument("--cr-threshold", type=float, default=0.95)
    pareto.add_argument("--pop", type=int, default=40)
    pareto.add_argument("--gens", type=int, default=150)
    pareto.set_defaults(func=cmd_pareto)
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
