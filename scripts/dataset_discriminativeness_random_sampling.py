"""Random-sampling diagnostic for dataset discriminativeness.

This script intentionally does not run AR-QIEA, MO-QIEA, NSGA-II, or the
filtered Random-Front benchmark. It samples random subsets directly and records
all sampled evaluations before any Pareto or dominance filtering.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from statistics import mean, median

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from quantum_testing.problems.risk_problem import RiskAwareProblem


INSTANCES = [
    ("Chart-1b", PROJECT_ROOT / "datasets" / "defects4j" / "Chart" / "1b" / "matrix.csv"),
    ("Chart-20b", PROJECT_ROOT / "datasets" / "defects4j" / "Chart" / "20b" / "matrix.csv"),
    ("Chart-26b", PROJECT_ROOT / "datasets" / "defects4j" / "Chart" / "26b" / "matrix.csv"),
    ("Lang-3b", PROJECT_ROOT / "datasets" / "defects4j" / "Lang" / "3b" / "matrix.csv"),
    ("Lang-5b", PROJECT_ROOT / "datasets" / "defects4j" / "Lang" / "5b" / "matrix.csv"),
    ("Lang-6b", PROJECT_ROOT / "datasets" / "defects4j" / "Lang" / "6b" / "matrix.csv"),
    ("Lang-20b", PROJECT_ROOT / "datasets" / "defects4j" / "Lang" / "20b" / "matrix.csv"),
]


def pct(numerator: int, denominator: int) -> float:
    return 100.0 * numerator / denominator if denominator else 0.0


def fmt(value: float) -> str:
    return f"{value:.6f}"


def summarize(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    return mean(values), median(values)


def classify(msr_near_perfect_feasible_pct: float) -> str:
    if msr_near_perfect_feasible_pct >= 50.0:
        return "weakly discriminative for MSR"
    if msr_near_perfect_feasible_pct >= 10.0:
        return "moderately discriminative for MSR"
    return "more discriminative for MSR"


def sample_instance(
    bug_id: str,
    matrix_path: Path,
    samples: int,
    rng: np.random.Generator,
    cr_threshold: float,
    msr_threshold: float,
    cgcc_threshold: float,
    risk_seed: int,
    n_mutants_factor: float,
    kill_prob: float,
) -> dict[str, object]:
    if not matrix_path.exists():
        raise FileNotFoundError(f"{bug_id}: missing matrix file {matrix_path}")

    problem = RiskAwareProblem.from_matrix_csv(
        matrix_path,
        risk_seed=risk_seed,
        cr_threshold=cr_threshold,
        n_mutants_factor=n_mutants_factor,
        kill_prob=kill_prob,
    )

    feasible = 0
    feasible_msr_099 = 0
    feasible_cgcc_099 = 0
    feasible_cr_values: list[float] = []
    feasible_msr_values: list[float] = []
    feasible_cgcc_values: list[float] = []
    feasible_etr_values: list[float] = []

    started = time.perf_counter()
    batch_size = 128
    coverage_i = problem.coverage.astype(np.int16)
    mutation_i = problem.mutation.astype(np.int16)
    for offset in range(0, samples, batch_size):
        current = min(batch_size, samples - offset)
        densities = rng.uniform(0.05, 0.95, size=current)
        selected = rng.random((current, problem.n_tests)) < densities[:, None]
        selected_i = selected.astype(np.int16)

        covered = (selected_i @ coverage_i) > 0
        killed = (selected_i @ mutation_i) > 0

        cr = covered[:, problem._covered_by_original].sum(axis=1) / problem._cov_den if problem._cov_den else np.ones(current)
        msr = (
            killed[:, problem._killed_by_original].sum(axis=1) / problem._killed_den
            if problem._killed_den
            else np.ones(current)
        )
        cgcc = (
            (covered.astype(float) @ problem.centrality) / problem._cgcc_den
            if problem._cgcc_den > 0
            else np.ones(current)
        )
        etr = 1.0 - (selected.astype(float) @ problem.exec_times) / problem._time_den if problem._time_den > 0 else np.zeros(current)

        cr = np.clip(cr, 0.0, 1.0)
        msr = np.clip(msr, 0.0, 1.0)
        cgcc = np.clip(cgcc, 0.0, 1.0)
        etr = np.clip(etr, 0.0, 1.0)

        feasible_mask = cr >= cr_threshold
        feasible += int(feasible_mask.sum())
        if feasible_mask.any():
            f_cr = cr[feasible_mask]
            f_msr = msr[feasible_mask]
            f_cgcc = cgcc[feasible_mask]
            f_etr = etr[feasible_mask]
            feasible_cr_values.extend(float(v) for v in f_cr)
            feasible_msr_values.extend(float(v) for v in f_msr)
            feasible_cgcc_values.extend(float(v) for v in f_cgcc)
            feasible_etr_values.extend(float(v) for v in f_etr)
            feasible_msr_099 += int((f_msr >= msr_threshold).sum())
            feasible_cgcc_099 += int((f_cgcc >= cgcc_threshold).sum())

    mean_cr, median_cr = summarize(feasible_cr_values)
    mean_msr, median_msr = summarize(feasible_msr_values)
    mean_cgcc, median_cgcc = summarize(feasible_cgcc_values)
    mean_etr, median_etr = summarize(feasible_etr_values)
    msr_feasible_pct = pct(feasible_msr_099, feasible)

    return {
        "bug_id": bug_id,
        "matrix_path": str(matrix_path.relative_to(PROJECT_ROOT)),
        "n_tests": problem.n_tests,
        "n_requirements": problem.n_requirements,
        "n_mutants": int(problem.mutation.shape[1]),
        "total_random_samples": samples,
        "feasible_cr_ge_095": feasible,
        "feasible_pct": pct(feasible, samples),
        "feasible_msr_ge_099": feasible_msr_099,
        "feasible_msr_ge_099_pct_of_feasible": msr_feasible_pct,
        "feasible_cgcc_ge_099": feasible_cgcc_099,
        "feasible_cgcc_ge_099_pct_of_feasible": pct(feasible_cgcc_099, feasible),
        "mean_cr_feasible": mean_cr,
        "median_cr_feasible": median_cr,
        "mean_msr_feasible": mean_msr,
        "median_msr_feasible": median_msr,
        "mean_cgcc_feasible": mean_cgcc,
        "median_cgcc_feasible": median_cgcc,
        "mean_etr_feasible": mean_etr,
        "median_etr_feasible": median_etr,
        "interpretation": classify(msr_feasible_pct),
        "runtime_seconds": time.perf_counter() - started,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "bug_id",
        "matrix_path",
        "n_tests",
        "n_requirements",
        "n_mutants",
        "total_random_samples",
        "feasible_cr_ge_095",
        "feasible_pct",
        "feasible_msr_ge_099",
        "feasible_msr_ge_099_pct_of_feasible",
        "feasible_cgcc_ge_099",
        "feasible_cgcc_ge_099_pct_of_feasible",
        "mean_cr_feasible",
        "median_cr_feasible",
        "mean_msr_feasible",
        "median_msr_feasible",
        "mean_cgcc_feasible",
        "median_cgcc_feasible",
        "mean_etr_feasible",
        "median_etr_feasible",
        "interpretation",
        "runtime_seconds",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def report_table(rows: list[dict[str, object]]) -> str:
    lines = [
        "| Instance | Samples | Feasible CR>=0.95 | Feasible % | Feasible MSR>=0.99 | % of Feasible | Feasible CGCC>=0.99 | % of Feasible | Mean CR | Mean MSR | Mean CGCC | Mean ETR | Interpretation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {bug_id} | {samples} | {feasible} | {feasible_pct}% | {msr_count} | {msr_pct}% | "
            "{cgcc_count} | {cgcc_pct}% | {mean_cr} | {mean_msr} | {mean_cgcc} | {mean_etr} | {interpretation} |".format(
                bug_id=row["bug_id"],
                samples=row["total_random_samples"],
                feasible=row["feasible_cr_ge_095"],
                feasible_pct=fmt(float(row["feasible_pct"])),
                msr_count=row["feasible_msr_ge_099"],
                msr_pct=fmt(float(row["feasible_msr_ge_099_pct_of_feasible"])),
                cgcc_count=row["feasible_cgcc_ge_099"],
                cgcc_pct=fmt(float(row["feasible_cgcc_ge_099_pct_of_feasible"])),
                mean_cr=fmt(float(row["mean_cr_feasible"] or 0.0)),
                mean_msr=fmt(float(row["mean_msr_feasible"] or 0.0)),
                mean_cgcc=fmt(float(row["mean_cgcc_feasible"] or 0.0)),
                mean_etr=fmt(float(row["mean_etr_feasible"] or 0.0)),
                interpretation=row["interpretation"],
            )
        )
    return "\n".join(lines)


def write_report(path: Path, csv_path: Path, rows: list[dict[str, object]], args: argparse.Namespace) -> None:
    weak = [str(row["bug_id"]) for row in rows if str(row["interpretation"]).startswith("weakly")]
    moderate = [str(row["bug_id"]) for row in rows if str(row["interpretation"]).startswith("moderately")]
    stronger = [str(row["bug_id"]) for row in rows if str(row["interpretation"]).startswith("more")]

    content = f"""# Dataset Discriminativeness Random-Sampling Diagnostic (7 Instances)

## Purpose
This diagnostic estimates how often direct random test-subset sampling satisfies the coverage-retention constraint and then reaches near-perfect MSR or CGCC. It is intended to explain when a random baseline can be competitive because the dataset itself has many high-quality feasible subsets.

## Scope and Limitation
This report covers only 7 of the 11 paper instances: Chart-1b, Chart-20b, Chart-26b, Lang-3b, Lang-5b, Lang-6b, and Lang-20b.

It does not cover Lang-1b, Lang-4b, Lang-14b, or Lang-22b because complete raw benchmark artifacts for those four instances were not available in the current repository audit. The diagnostic is supporting evidence, not a replacement for the full 11-instance experimental table.

## Method
For each included instance, the script samples {args.samples:,} random subsets using the same random-subset generation pattern as `random_front` in `scripts/pareto_benchmark.py`: draw a subset density uniformly from [0.05, 0.95], then include each test independently with that probability. Unlike `random_front`, this diagnostic records all sampled evaluations before Pareto or constraint-dominance filtering.

Each instance is loaded with `RiskAwareProblem.from_matrix_csv`, and sampled subsets are scored with the same CR, MSR, CGCC, and ETR formulas used by `RiskAwareProblem.evaluate`. The main experiment defaults are used: risk seed {args.risk_seed}, CR threshold {args.cr_threshold}, mutant factor {args.n_mutants_factor}, and kill probability {args.kill_prob}. A subset is feasible when CR(S) >= 0.95. Near-perfect thresholds are MSR(S) >= 0.99 and CGCC(S) >= 0.99.

Raw CSV output: `{csv_path.as_posix()}`.

## Diagnostic Table
{report_table(rows)}

## Interpretation
Instances with a high percentage of feasible random subsets also reaching MSR(S) >= 0.99 are weakly discriminative for MSR: random feasible subsets already preserve nearly all synthetic mutation score, so Random-Front can appear competitive without implying that it is generally superior. Instances with low percentages are more discriminative because feasibility alone does not usually imply near-perfect MSR.

Weakly discriminative for MSR in this diagnostic: {", ".join(weak) if weak else "none"}.

Moderately discriminative for MSR in this diagnostic: {", ".join(moderate) if moderate else "none"}.

More discriminative for MSR in this diagnostic: {", ".join(stronger) if stronger else "none"}.

These results should be read together with HV, ETR, and front diversity. A random feasible subset may obtain high MSR or CGCC while still being less useful on other objectives, and AR-QIEA should not be claimed to always outperform Random-Front.

## Paper-Ready Paragraph
To assess whether several Defects4J instances are intrinsically weakly discriminative, we performed an auxiliary random-sampling diagnostic on the seven instances for which complete raw benchmark artifacts were available. For each instance, we sampled {args.samples:,} random subsets using the same density-based generator as the Random-Front baseline, but evaluated every sampled subset before Pareto or constraint filtering. The diagnostic measures the proportion of feasible subsets satisfying CR(S) >= 0.95 and, among feasible subsets, the proportion that also reach MSR(S) >= 0.99 and CGCC(S) >= 0.99. High near-perfect MSR rates indicate that MSR is weakly discriminative on that instance, explaining why Random-Front can be competitive there; low rates indicate that feasibility alone is insufficient and the instance is more discriminative.

## Missing Data / Next Step
The remaining paper instances, Lang-1b, Lang-4b, Lang-14b, and Lang-22b, are not included here. The next step is to generate equivalent diagnostic rows for those four instances after their dataset matrices and/or raw benchmark artifacts are confirmed, or to clearly label this report as a 7-instance supporting diagnostic in the appendix.
"""
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260626)
    parser.add_argument("--risk-seed", type=int, default=12345)
    parser.add_argument("--cr-threshold", type=float, default=0.95)
    parser.add_argument("--msr-threshold", type=float, default=0.99)
    parser.add_argument("--cgcc-threshold", type=float, default=0.99)
    parser.add_argument("--n-mutants-factor", type=float, default=2.0)
    parser.add_argument("--kill-prob", type=float, default=0.6)
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=PROJECT_ROOT / "artifacts" / "dataset_discriminativeness_random_sampling_7_instances.csv",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "dataset_discriminativeness_report_7_instances.md",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.csv_output = args.csv_output.resolve()
    args.report_output = args.report_output.resolve()

    for output in (args.csv_output, args.report_output):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite existing file: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    rows = []
    for bug_id, matrix_path in INSTANCES:
        print(f"sampling {bug_id} ({args.samples} subsets)", flush=True)
        rows.append(
            sample_instance(
                bug_id=bug_id,
                matrix_path=matrix_path,
                samples=args.samples,
                rng=rng,
                cr_threshold=args.cr_threshold,
                msr_threshold=args.msr_threshold,
                cgcc_threshold=args.cgcc_threshold,
                risk_seed=args.risk_seed,
                n_mutants_factor=args.n_mutants_factor,
                kill_prob=args.kill_prob,
            )
        )

    write_csv(args.csv_output, rows)
    write_report(args.report_output, args.csv_output, rows, args)
    print(f"csv={args.csv_output}")
    print(f"report={args.report_output}")
    print("instances=" + ", ".join(row["bug_id"] for row in rows))
    print(f"samples_per_instance={args.samples}")


if __name__ == "__main__":
    main()


