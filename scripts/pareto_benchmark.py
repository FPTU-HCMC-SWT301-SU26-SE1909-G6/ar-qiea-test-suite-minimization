"""Run Pareto benchmarks for risk-aware test-suite minimization."""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from statistics import mean, pstdev
from typing import Iterable

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from quantum_testing.algorithms.ar_qiea import ARQIEA, ArchiveEntry
from quantum_testing.algorithms.nsga2 import NSGA2
from quantum_testing.metrics_mo import constrained_dominates, dominates, hypervolume
from quantum_testing.problems.risk_problem import RiskAwareProblem


def entry_to_dict(entry: ArchiveEntry) -> dict:
    return {
        "solution": entry.solution,
        "objectives": list(entry.objectives),
        "violation": entry.violation,
        "cr": entry.cr,
        "rop": entry.rop,
        "selected_count": entry.selected_count,
        "total_time": entry.total_time,
    }


def stats(values: Iterable[float]) -> dict:
    data = [float(v) for v in values]
    if not data:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": mean(data),
        "std": pstdev(data) if len(data) > 1 else 0.0,
        "min": min(data),
        "max": max(data),
    }


def constrained_front(entries: list[ArchiveEntry]) -> list[ArchiveEntry]:
    survivors: list[ArchiveEntry] = []
    for i, entry in enumerate(entries):
        if not any(
            i != j
            and constrained_dominates(other.objectives, other.violation, entry.objectives, entry.violation)
            for j, other in enumerate(entries)
        ):
            survivors.append(entry)
    return survivors


def random_front(problem: RiskAwareProblem, pop: int, gens: int, seed: int) -> list[ArchiveEntry]:
    rng = np.random.default_rng(seed)
    entries: list[ArchiveEntry] = []
    for _ in range(pop * gens):
        density = float(rng.uniform(0.05, 0.95))
        sol = (rng.random(problem.n_tests) < density).astype(int).tolist()
        ev = problem.evaluate(sol)
        entries.append(
            ArchiveEntry(sol, ev.objectives, ev.violation, ev.cr, ev.rop, ev.selected_count, ev.total_time)
        )
    return [e for e in constrained_front(entries) if e.violation <= 1e-12]


def greedy_point(problem: RiskAwareProblem) -> ArchiveEntry:
    uncovered = set(np.flatnonzero(problem.coverage.any(axis=0)).tolist())
    selected: list[int] = []
    while uncovered:
        best = max(
            range(problem.n_tests),
            key=lambda i: len(set(np.flatnonzero(problem.coverage[i]).tolist()) & uncovered),
        )
        gain = set(np.flatnonzero(problem.coverage[best]).tolist()) & uncovered
        if not gain:
            break
        selected.append(best)
        uncovered -= gain
    sol = [1 if i in selected else 0 for i in range(problem.n_tests)]
    ev = problem.evaluate(sol)
    return ArchiveEntry(sol, ev.objectives, ev.violation, ev.cr, ev.rop, ev.selected_count, ev.total_time)


def run_algorithm(problem: RiskAwareProblem, algorithm: str, pop: int, gens: int, seed: int, archive_size: int, risk_alpha: float) -> list[ArchiveEntry]:
    if algorithm == "ar_qiea":
        return ARQIEA(problem, pop_size=pop, max_gen=gens, archive_size=archive_size, risk_alpha=risk_alpha, seed=seed).run()
    if algorithm == "mo_qiea":
        return ARQIEA(
            problem,
            pop_size=pop,
            max_gen=gens,
            archive_size=archive_size,
            risk_alpha=risk_alpha,
            risk_adaptive=False,
            seed=seed,
        ).run()
    if algorithm == "risk_shuffled_ar_qiea":
        return ARQIEA(
            problem,
            pop_size=pop,
            max_gen=gens,
            archive_size=archive_size,
            risk_alpha=risk_alpha,
            risk_shuffled=True,
            seed=seed,
        ).run()
    if algorithm == "nsga2":
        return NSGA2(problem, pop_size=pop, max_gen=gens, seed=seed).run()
    if algorithm == "random_front":
        return random_front(problem, pop, gens, seed)
    raise ValueError(f"unknown algorithm: {algorithm}")


def wilcoxon_p(a: list[float], b: list[float]) -> float | None:
    try:
        from scipy.stats import wilcoxon
    except ImportError:
        return None
    if len(a) != len(b) or not a:
        return None
    if all(math.isclose(x, y) for x, y in zip(a, b)):
        return 1.0
    return float(wilcoxon(a, b, alternative="greater").pvalue)


def discover_cases(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.rglob("matrix.csv"))


def case_name(matrix_path: Path, root: Path) -> str:
    try:
        return str(matrix_path.parent.relative_to(root)).replace("\\", "/")
    except ValueError:
        return matrix_path.stem


def run_case(matrix_path: Path, args) -> dict:
    problem = RiskAwareProblem.from_matrix_csv(
        matrix_path,
        risk_seed=args.risk_seed,
        cr_threshold=args.cr_threshold,
        n_mutants_factor=args.n_mutants_factor,
        kill_prob=args.kill_prob,
    )
    greedy = greedy_point(problem)
    algo_payload: dict[str, dict] = {}
    hv_by_alg: dict[str, list[float]] = {}

    for algorithm in args.algorithms:
        raw = []
        runtimes = []
        for seed in args.seeds:
            start = time.perf_counter()
            front = run_algorithm(problem, algorithm, args.pop, args.gens, seed, args.archive_size, args.risk_alpha)
            runtime = time.perf_counter() - start
            feasible = [entry for entry in front if entry.violation <= 1e-12]
            hv = hypervolume([entry.objectives for entry in feasible]) if feasible else 0.0
            raw.append(
                {
                    "seed": seed,
                    "hv": hv,
                    "front_size": len(feasible),
                    "front": [list(entry.objectives) for entry in feasible],
                    "entries": [entry_to_dict(entry) for entry in feasible],
                }
            )
            runtimes.append(runtime)
        hv_by_alg[algorithm] = [record["hv"] for record in raw]
        best_msr = [max((pt[0] for pt in record["front"]), default=0.0) for record in raw]
        best_cgcc = [max((pt[1] for pt in record["front"]), default=0.0) for record in raw]
        best_etr = [max((pt[2] for pt in record["front"]), default=0.0) for record in raw]
        algo_payload[algorithm] = {
            "parameters": algorithm_parameters(algorithm, args),
            "hv": stats(record["hv"] for record in raw),
            "front_size": stats(record["front_size"] for record in raw),
            "runtime_seconds": stats(runtimes),
            "best_msr": stats(best_msr),
            "best_cgcc": stats(best_cgcc),
            "best_etr": stats(best_etr),
            "raw": raw,
        }

    dominated_by = []
    for algorithm, payload in algo_payload.items():
        points = [pt for record in payload["raw"] for pt in record["front"]]
        if any(dominates(point, greedy.objectives) for point in points):
            dominated_by.append(algorithm)

    wilcoxon = {}
    if "ar_qiea" in hv_by_alg:
        for algorithm, values in hv_by_alg.items():
            if algorithm != "ar_qiea":
                wilcoxon[f"ar_qiea_vs_{algorithm}"] = wilcoxon_p(hv_by_alg["ar_qiea"], values)

    return {
        "n_tests": problem.n_tests,
        "n_requirements": problem.n_requirements,
        "n_mutants": int(problem.mutation.shape[1]),
        "greedy_point": entry_to_dict(greedy) | {"dominated_by": dominated_by},
        "algorithms": algo_payload,
        "wilcoxon": wilcoxon,
    }


def algorithm_parameters(algorithm: str, args) -> dict:
    common = {"pop_size": args.pop, "max_gen": args.gens, "seeded_runs": args.seeds}
    if algorithm in {"ar_qiea", "mo_qiea", "risk_shuffled_ar_qiea"}:
        return common | {
            "rotation_angle": 0.01 * math.pi,
            "risk_alpha": args.risk_alpha,
            "risk_adaptive": algorithm != "mo_qiea",
            "risk_shuffled": algorithm == "risk_shuffled_ar_qiea",
            "archive_size": args.archive_size,
        }
    if algorithm == "nsga2":
        return common | {"crossover_rate": 0.9, "mutation_rate": None}
    return common | {"evaluations": args.pop * args.gens}


def parse_seeds(seed_spec: str) -> list[int]:
    if ".." in seed_spec:
        start, end = seed_spec.split("..", 1)
        return list(range(int(start), int(end) + 1))
    return [int(part) for part in seed_spec.split(",") if part.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--seeds", default="42..71")
    parser.add_argument("--pop", type=int, default=40)
    parser.add_argument("--gens", type=int, default=150)
    parser.add_argument("--algorithms", default="ar_qiea,mo_qiea,nsga2,random_front,risk_shuffled_ar_qiea")
    parser.add_argument("--risk-seed", type=int, default=12345)
    parser.add_argument("--cr-threshold", type=float, default=0.95)
    parser.add_argument("--risk-alpha", type=float, default=1.0)
    parser.add_argument("--archive-size", type=int, default=50)
    parser.add_argument("--n-mutants-factor", type=float, default=2.0)
    parser.add_argument("--kill-prob", type=float, default=0.6)
    parser.add_argument("--output", required=True)
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.root = Path(args.root)
    args.seeds = parse_seeds(args.seeds)
    args.algorithms = [alg.strip() for alg in args.algorithms.split(",") if alg.strip()]
    cases = discover_cases(args.root)
    payload = {
        "config": {
            "root": str(args.root),
            "seeds": args.seeds,
            "pop": args.pop,
            "gens": args.gens,
            "algorithms": args.algorithms,
            "risk_seed": args.risk_seed,
            "cr_threshold": args.cr_threshold,
            "risk_alpha": args.risk_alpha,
            "archive_size": args.archive_size,
            "n_mutants_factor": args.n_mutants_factor,
            "kill_prob": args.kill_prob,
            "evaluation_budget": args.pop * args.gens,
        },
        "cases": {case_name(path, args.root): run_case(path, args) for path in cases},
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "cases": len(cases)}, indent=2))


if __name__ == "__main__":
    main()
