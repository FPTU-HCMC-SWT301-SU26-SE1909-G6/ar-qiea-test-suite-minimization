"""Generate Wilcoxon signed-rank reports from raw Pareto benchmark artifacts.

This script reads existing JSON artifacts only. It does not run experiments.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any

from scipy.stats import wilcoxon


TARGET = "ar_qiea"
BASELINES = ["mo_qiea", "nsga2", "random_front"]
METRICS = ["MSR", "CGCC", "ETR", "HV", "BRARS"]
ALPHA = 0.05
BRARS_LAMBDA = 0.5


@dataclass
class Candidate:
    path: Path
    bug_id: str | None
    valid_raw: bool
    seeds: set[int]
    algorithms: set[str]
    reason: str


def normalize_algorithm(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def bug_id_from_root(root: str | None, case_name: str) -> str | None:
    parts: list[str] = []
    if root:
        parts.extend(re.split(r"[\\/]+", root.strip()))
    if case_name and case_name != ".":
        parts.extend(re.split(r"[\\/]+", case_name.strip()))
    clean = [p for p in parts if p and p != "."]
    for i, part in enumerate(clean):
        if part.lower() in {"chart", "lang", "math", "time", "closure", "mockito"} and i + 1 < len(clean):
            bug = clean[i + 1].lower()
            if re.fullmatch(r"\d+b", bug):
                return f"{part.capitalize()}-{bug}"
    return None


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            payload = json.load(fh)
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def iter_cases(payload: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    cases = payload.get("cases")
    if not isinstance(cases, dict):
        return []
    return [(str(name), case) for name, case in cases.items() if isinstance(case, dict)]


def inspect_candidate(path: Path) -> Candidate:
    payload = load_json(path)
    if payload is None:
        return Candidate(path, None, False, set(), set(), "not a readable JSON object")
    cases = iter_cases(payload)
    if not cases:
        return Candidate(path, None, False, set(), set(), "no benchmark cases with algorithms/raw records")

    bug_ids = {
        bug_id_from_root(str(payload.get("config", {}).get("root", "")), case_name)
        for case_name, _case in cases
    }
    bug_ids.discard(None)
    bug_id = next(iter(bug_ids)) if len(bug_ids) == 1 else None
    algorithms: set[str] = set()
    seeds: set[int] = set()
    has_raw = False

    for _case_name, case in cases:
        alg_payload = case.get("algorithms")
        if not isinstance(alg_payload, dict):
            continue
        for alg_name, alg_data in alg_payload.items():
            raw = alg_data.get("raw") if isinstance(alg_data, dict) else None
            if not isinstance(raw, list) or not raw:
                continue
            algorithms.add(normalize_algorithm(str(alg_name)))
            for record in raw:
                if isinstance(record, dict) and "seed" in record:
                    try:
                        seeds.add(int(record["seed"]))
                        has_raw = True
                    except (TypeError, ValueError):
                        pass

    if not has_raw:
        return Candidate(path, bug_id, False, seeds, algorithms, "contains only aggregate/no usable per-seed raw records")
    if bug_id is None:
        return Candidate(path, bug_id, False, seeds, algorithms, "could not determine a single Defects4J bug id")
    return Candidate(path, bug_id, True, seeds, algorithms, "usable per-seed raw benchmark artifact")


def artifact_score(candidate: Candidate) -> tuple[int, int, int, int, int, str]:
    has_all = int(candidate.algorithms.issuperset({TARGET, *BASELINES}))
    payload = load_json(candidate.path) or {}
    single_case = int(len(iter_cases(payload)) == 1)
    is_full = int("_full_" in candidate.path.name.lower())
    return (has_all, len(candidate.seeds), single_case, is_full, candidate.path.stat().st_size, candidate.path.name)


def select_sources(candidates: list[Candidate]) -> tuple[dict[str, Candidate], list[dict[str, str]]]:
    by_bug: dict[str, list[Candidate]] = defaultdict(list)
    audit_rows: list[dict[str, str]] = []
    for candidate in candidates:
        if candidate.valid_raw and candidate.bug_id:
            by_bug[candidate.bug_id].append(candidate)
        else:
            audit_rows.append(
                {
                    "file": str(candidate.path),
                    "bug_id": candidate.bug_id or "",
                    "status": "not used",
                    "reason": candidate.reason,
                }
            )

    selected: dict[str, Candidate] = {}
    for bug_id, group in sorted(by_bug.items()):
        chosen = sorted(group, key=artifact_score, reverse=True)[0]
        selected[bug_id] = chosen
        audit_rows.append(
            {
                "file": str(chosen.path),
                "bug_id": bug_id,
                "status": "used",
                "reason": chosen.reason,
            }
        )
        for candidate in group:
            if candidate.path == chosen.path:
                continue
            audit_rows.append(
                {
                    "file": str(candidate.path),
                    "bug_id": bug_id,
                    "status": "not used",
                    "reason": f"duplicate raw artifact for {bug_id}; selected {chosen.path.name}",
                }
            )
    return selected, audit_rows


def best_brars(entries: list[dict[str, Any]], n_tests: int, cr_threshold: float = 0.95) -> float:
    best = 0.0
    for entry in entries:
        objectives = entry.get("objectives")
        if not isinstance(objectives, list) or len(objectives) < 3:
            continue
        cr = float(entry.get("cr", 0.0))
        if cr < cr_threshold:
            score = 0.0
        else:
            selected_count = float(entry.get("selected_count", n_tests))
            trr = max(0.0, 1.0 - selected_count / float(n_tests)) if n_tests else 0.0
            product = max(0.0, float(objectives[0])) * max(0.0, float(objectives[1])) * max(0.0, float(objectives[2]))
            score = (product * (trr ** BRARS_LAMBDA)) ** (1.0 / (3.0 + BRARS_LAMBDA))
        best = max(best, float(score))
    return best


def per_seed_metric(record: dict[str, Any], metric: str, n_tests: int) -> float | None:
    if metric == "HV":
        return float(record["hv"]) if "hv" in record else None

    front = record.get("front")
    if not isinstance(front, list):
        return None
    if metric in {"MSR", "CGCC", "ETR"}:
        idx = {"MSR": 0, "CGCC": 1, "ETR": 2}[metric]
        values = [float(point[idx]) for point in front if isinstance(point, list) and len(point) > idx]
        return max(values) if values else 0.0

    if metric == "BRARS":
        entries = record.get("entries")
        if not isinstance(entries, list):
            return None
        return best_brars(entries, n_tests)
    return None


def seed_values(case: dict[str, Any], algorithm: str, metric: str) -> tuple[dict[int, float], str | None]:
    alg_payload = case.get("algorithms", {}).get(algorithm)
    if not isinstance(alg_payload, dict):
        return {}, f"missing algorithm {algorithm}"
    raw = alg_payload.get("raw")
    if not isinstance(raw, list) or not raw:
        return {}, f"{algorithm} has no per-seed raw records"
    values: dict[int, float] = {}
    n_tests = int(case.get("n_tests", 0) or 0)
    for record in raw:
        if not isinstance(record, dict) or "seed" not in record:
            return {}, f"{algorithm} contains raw records without seed"
        seed = int(record["seed"])
        value = per_seed_metric(record, metric, n_tests)
        if value is None or math.isnan(value):
            return {}, f"{metric} cannot be computed exactly for {algorithm} seed {seed}"
        values[seed] = float(value)
    return values, None


def paired_wilcoxon(ar_values: list[float], baseline_values: list[float]) -> tuple[float, float]:
    if all(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12) for a, b in zip(ar_values, baseline_values)):
        return 0.0, 1.0
    result = wilcoxon(ar_values, baseline_values, alternative="two-sided", zero_method="wilcox")
    return float(result.statistic), float(result.pvalue)


def direction(ar_med: float, base_med: float, ar_mean: float, base_mean: float, pvalue: float) -> str:
    if pvalue >= ALPHA:
        return "no significant difference"
    if ar_med > base_med or (math.isclose(ar_med, base_med) and ar_mean > base_mean):
        return "AR-QIEA better"
    if ar_med < base_med or (math.isclose(ar_med, base_med) and ar_mean < base_mean):
        return "AR-QIEA worse"
    return "no significant difference"


def rank_biserial(ar_values: list[float], baseline_values: list[float]) -> float:
    diffs = [a - b for a, b in zip(ar_values, baseline_values) if not math.isclose(a, b, abs_tol=1e-12)]
    n = len(diffs)
    if n == 0:
        return 0.0
    abs_diffs = sorted((abs(diff), diff) for diff in diffs)
    ranks: list[tuple[float, float]] = []
    i = 0
    while i < n:
        j = i + 1
        while j < n and math.isclose(abs_diffs[j][0], abs_diffs[i][0], rel_tol=1e-12, abs_tol=1e-12):
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks.append((avg_rank, abs_diffs[k][1]))
        i = j
    positive = sum(rank for rank, diff in ranks if diff > 0)
    negative = sum(rank for rank, diff in ranks if diff < 0)
    denom = n * (n + 1) / 2.0
    return (positive - negative) / denom if denom else 0.0


def analyze_source(path: Path, bug_id: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    payload = load_json(path)
    assert payload is not None
    cases = iter_cases(payload)
    if len(cases) != 1:
        return [], [
            {
                "bug_id": bug_id,
                "metric": "",
                "comparison": "",
                "source_file": str(path),
                "reason": "artifact has multiple cases; this report expects one selected bug per artifact",
            }
        ]
    _case_name, case = cases[0]
    rows: list[dict[str, Any]] = []
    not_computable: list[dict[str, str]] = []
    for metric in METRICS:
        ar_by_seed, ar_error = seed_values(case, TARGET, metric)
        for baseline in BASELINES:
            comparison = f"AR-QIEA vs {baseline.replace('_', '-').upper() if baseline != 'random_front' else 'Random-Front'}"
            base_by_seed, base_error = seed_values(case, baseline, metric)
            reason = ar_error or base_error
            if reason is None and set(ar_by_seed) != set(base_by_seed):
                missing_ar = sorted(set(base_by_seed) - set(ar_by_seed))
                missing_base = sorted(set(ar_by_seed) - set(base_by_seed))
                reason = f"seed sets do not align; missing in AR-QIEA={missing_ar}, missing in {baseline}={missing_base}"
            if reason is None and len(ar_by_seed) < 2:
                reason = f"insufficient paired observations for Wilcoxon (n={len(ar_by_seed)})"
            if reason is not None:
                not_computable.append(
                    {
                        "bug_id": bug_id,
                        "metric": metric,
                        "comparison": comparison,
                        "source_file": str(path),
                        "reason": reason,
                    }
                )
                continue
            seeds = sorted(ar_by_seed)
            ar_values = [ar_by_seed[seed] for seed in seeds]
            baseline_values = [base_by_seed[seed] for seed in seeds]
            statistic, pvalue = paired_wilcoxon(ar_values, baseline_values)
            ar_mean = mean(ar_values)
            base_mean = mean(baseline_values)
            ar_median = median(ar_values)
            base_median = median(baseline_values)
            rows.append(
                {
                    "bug_id": bug_id,
                    "metric": metric,
                    "comparison": comparison,
                    "baseline": baseline,
                    "n": len(seeds),
                    "seeds": ";".join(str(seed) for seed in seeds),
                    "ar_qiea_mean": ar_mean,
                    "baseline_mean": base_mean,
                    "ar_qiea_median": ar_median,
                    "baseline_median": base_median,
                    "wilcoxon_statistic": statistic,
                    "p_value": pvalue,
                    "significant_alpha_0_05": pvalue < ALPHA,
                    "direction": direction(ar_median, base_median, ar_mean, base_mean, pvalue),
                    "rank_biserial_effect_size": rank_biserial(ar_values, baseline_values),
                    "source_file": str(path),
                }
            )
    return rows, not_computable


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_summary_rows(result_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    overall: dict[str, Counter[str]] = defaultdict(Counter)
    for row in result_rows:
        baseline = row["baseline"]
        metric = row["metric"]
        direction_value = row["direction"]
        bucket = {
            "AR-QIEA better": "wins",
            "AR-QIEA worse": "losses",
            "no significant difference": "ties",
        }[direction_value]
        grouped[(metric, baseline)][bucket] += 1
        grouped[(metric, baseline)]["valid_tests"] += 1
        overall[baseline][bucket] += 1
        overall[baseline]["valid_tests"] += 1

    for (metric, baseline), counts in sorted(grouped.items()):
        summary.append(
            {
                "row_type": "metric_by_baseline",
                "metric": metric,
                "baseline": baseline,
                "valid_tests": counts["valid_tests"],
                "ar_qiea_wins": counts["wins"],
                "ar_qiea_losses": counts["losses"],
                "ties": counts["ties"],
            }
        )
    for baseline, counts in sorted(overall.items()):
        summary.append(
            {
                "row_type": "overall_by_baseline",
                "metric": "ALL",
                "baseline": baseline,
                "valid_tests": counts["valid_tests"],
                "ar_qiea_wins": counts["wins"],
                "ar_qiea_losses": counts["losses"],
                "ties": counts["ties"],
            }
        )
    return summary


def md_table(rows: list[dict[str, Any]], columns: list[str], limit: int | None = None) -> str:
    selected = rows[:limit] if limit is not None else rows
    if not selected:
        return "_None._"
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in selected:
        values = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                value = f"{value:.6g}"
            values.append(str(value))
        out.append("| " + " | ".join(values) + " |")
    return "\n".join(out)


def tex_escape(value: Any) -> str:
    text = str(value)
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
    )


def write_reports(
    md_path: Path,
    tex_path: Path,
    result_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    not_computable: list[dict[str, str]],
    audit_rows: list[dict[str, str]],
    command: str,
) -> None:
    used = [row for row in audit_rows if row["status"] == "used"]
    valid = bool(result_rows)
    md = [
        "# Wilcoxon Statistical Report",
        "",
        "## Purpose",
        "This report tests whether AR-QIEA differs significantly from MO-QIEA, NSGA-II, and Random-Front on existing Defects4J benchmark artifacts. The analysis uses only raw per-seed records and does not use aggregate-only mean or median tables as Wilcoxon input.",
        "",
        "## Data Sources Used",
        md_table(used, ["bug_id", "file", "reason"]),
        "",
        "## Raw Data Validity Check",
        f"Valid Wilcoxon result rows: {len(result_rows)}.",
        f"Non-computable bug/metric/comparison rows: {len(not_computable)}.",
        "Each valid test was paired by the same bug id, metric, seed index, and number of observations for AR-QIEA and the baseline. Duplicate raw artifacts were not combined; one source per bug was selected.",
        "",
        "## Method",
        "For HV, the script uses the per-seed `hv` value stored in each raw record. For MSR, CGCC, and ETR, it uses the per-seed best value on that metric from the feasible raw front. For BRARS, it computes the per-entry BRARS formula from raw objectives, CR, selected_count, and n_tests, then uses the per-seed best BRARS in the feasible front. All metrics are treated as maximize metrics.",
        "The Wilcoxon signed-rank test is run with `scipy.stats.wilcoxon(..., alternative='two-sided')` at alpha = 0.05. Direction is assigned only when the two-sided test is significant.",
        "",
        "## Detailed Results",
        md_table(
            result_rows,
            [
                "bug_id",
                "metric",
                "comparison",
                "n",
                "ar_qiea_mean",
                "baseline_mean",
                "ar_qiea_median",
                "baseline_median",
                "wilcoxon_statistic",
                "p_value",
                "significant_alpha_0_05",
                "direction",
                "rank_biserial_effect_size",
            ],
        ),
        "",
        "## Summary",
        md_table(summary_rows, ["row_type", "metric", "baseline", "valid_tests", "ar_qiea_wins", "ar_qiea_losses", "ties"]),
        "",
        "## Not Computable",
        md_table(not_computable, ["bug_id", "metric", "comparison", "source_file", "reason"]),
        "",
        "## Artifact Audit",
        md_table(audit_rows, ["status", "bug_id", "file", "reason"]),
        "",
        "## Interpretation",
    ]
    win_total = sum(1 for row in result_rows if row["direction"] == "AR-QIEA better")
    loss_total = sum(1 for row in result_rows if row["direction"] == "AR-QIEA worse")
    tie_total = sum(1 for row in result_rows if row["direction"] == "no significant difference")
    md.extend(
        [
            f"Across all valid bug/metric/baseline comparisons, AR-QIEA has {win_total} significant wins, {loss_total} significant losses, and {tie_total} non-significant comparisons.",
            "These conclusions are valid only for the selected raw per-seed artifacts listed above. Aggregate-only reports and prior p-value-only files were audited but not used as Wilcoxon input.",
            "",
            "## Limitations",
            "MSR, CGCC, and ETR in the benchmark artifacts are the repository's recorded proxy/synthetic objective values, not independently regenerated real Major mutation, Java call graph, or measured timing data. Wilcoxon was not computed where raw seed-level records were unavailable, where algorithms were missing, or where seed sets could not be paired exactly.",
            "",
            "## Reproduction Command",
            f"`{command}`",
        ]
    )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    tex_lines = [
        "\\section{Wilcoxon Statistical Report}",
        "This report uses only raw per-seed benchmark records. Aggregate-only files are not used as Wilcoxon input.",
        "\\subsection{Summary}",
        "\\begin{tabular}{llrrrr}",
        "Type & Metric & Baseline & Valid & Wins & Losses/Ties \\\\",
        "\\hline",
    ]
    for row in summary_rows:
        tex_lines.append(
            f"{tex_escape(row['row_type'])} & {tex_escape(row['metric'])} & {tex_escape(row['baseline'])} & {row['valid_tests']} & {row['ar_qiea_wins']} & {row['ar_qiea_losses']}/{row['ties']} \\\\"
        )
    tex_lines.extend(
        [
            "\\end{tabular}",
            "\\subsection{Detailed Results}",
            "\\begin{tabular}{lllrrrrrl}",
            "Bug & Metric & Comparison & n & AR mean & Base mean & Stat. & p & Direction \\\\",
            "\\hline",
        ]
    )
    for row in result_rows:
        tex_lines.append(
            f"{tex_escape(row['bug_id'])} & {tex_escape(row['metric'])} & {tex_escape(row['comparison'])} & {row['n']} & {row['ar_qiea_mean']:.4f} & {row['baseline_mean']:.4f} & {row['wilcoxon_statistic']:.4f} & {row['p_value']:.4g} & {tex_escape(row['direction'])} \\\\"
        )
    tex_lines.extend(
        [
            "\\end{tabular}",
            "\\subsection{Limitations}",
            "Rows without exactly paired raw seed-level data were marked not computable. BRARS was computed only from raw objective, CR, selected-count, and test-count values.",
        ]
    )
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    tex_path.write_text("\n".join(tex_lines) + "\n", encoding="utf-8")

    if not valid:
        print("WARNING: no valid Wilcoxon rows were computed from raw per-seed data.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", default="artifacts/pareto")
    parser.add_argument("--reports-dir", default="reports/statistics")
    parser.add_argument("--statistics-dir", default="artifacts/statistics")
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    candidates = [inspect_candidate(path) for path in sorted(artifacts_dir.glob("*.json"))]
    selected, audit_rows = select_sources(candidates)

    result_rows: list[dict[str, Any]] = []
    not_computable: list[dict[str, str]] = []
    for bug_id, candidate in sorted(selected.items()):
        rows, missing = analyze_source(candidate.path, bug_id)
        result_rows.extend(rows)
        not_computable.extend(missing)

    summary_rows = build_summary_rows(result_rows)

    stats_dir = Path(args.statistics_dir)
    reports_dir = Path(args.reports_dir)
    write_csv(
        stats_dir / "wilcoxon_results.csv",
        result_rows,
        [
            "bug_id",
            "metric",
            "comparison",
            "baseline",
            "n",
            "seeds",
            "ar_qiea_mean",
            "baseline_mean",
            "ar_qiea_median",
            "baseline_median",
            "wilcoxon_statistic",
            "p_value",
            "significant_alpha_0_05",
            "direction",
            "rank_biserial_effect_size",
            "source_file",
        ],
    )
    write_csv(
        stats_dir / "wilcoxon_summary.csv",
        summary_rows,
        ["row_type", "metric", "baseline", "valid_tests", "ar_qiea_wins", "ar_qiea_losses", "ties"],
    )
    write_csv(stats_dir / "wilcoxon_not_computable.csv", not_computable, ["bug_id", "metric", "comparison", "source_file", "reason"])
    write_csv(stats_dir / "wilcoxon_artifact_audit.csv", audit_rows, ["status", "bug_id", "file", "reason"])

    command = "python scripts/wilcoxon_statistics.py"
    write_reports(
        reports_dir / "wilcoxon_report.md",
        reports_dir / "wilcoxon_report.tex",
        result_rows,
        summary_rows,
        not_computable,
        audit_rows,
        command,
    )

    print(json.dumps(
        {
            "valid_wilcoxon_rows": len(result_rows),
            "summary_rows": len(summary_rows),
            "not_computable_rows": len(not_computable),
            "selected_sources": {bug: str(candidate.path) for bug, candidate in selected.items()},
            "outputs": [
                str(stats_dir / "wilcoxon_results.csv"),
                str(stats_dir / "wilcoxon_summary.csv"),
                str(stats_dir / "wilcoxon_not_computable.csv"),
                str(stats_dir / "wilcoxon_artifact_audit.csv"),
                str(reports_dir / "wilcoxon_report.md"),
                str(reports_dir / "wilcoxon_report.tex"),
            ],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()




