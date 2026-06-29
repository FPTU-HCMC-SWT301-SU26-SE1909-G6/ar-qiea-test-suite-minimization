# Quantum Testing

Research code and experimental artifacts for **Pareto-based test suite minimization** using quantum-inspired evolutionary search. The current repository focuses on risk-aware, multi-objective minimization of Defects4J coverage matrices, with particular emphasis on Apache Commons Lang cases from Defects4J.

The project is implemented as a Python package named `quantum-testing` and is currently at an alpha/research-artifact stage.

## Research Overview

Regression test suites can become expensive to execute as software evolves. Test suite minimization seeks a smaller subset of tests that preserves important testing capability while reducing execution effort. This repository studies that problem as a **true Pareto multi-objective optimization task** rather than as a single weighted objective.

Given an original test suite `T` and a coverage matrix, the implemented benchmark searches for subsets `S subset T` that satisfy a coverage-retention constraint while optimizing several competing criteria:

- preserve mutation-related fault-detection capability;
- preserve coverage of central or high-risk code elements;
- reduce estimated execution time;
- expose a Pareto front of trade-offs instead of returning only one selected suite.

The main implemented research direction is **Adaptive Risk-Aware Quantum-Inspired Evolutionary Algorithm (AR-QIEA)** compared with a non-risk-aware MO-QIEA ablation, NSGA-II, and a random Pareto-front baseline.

## Problem Statement

The core problem is **Pareto-based test suite minimization**:

```text
Given:
  T = original test suite
  S = selected subset of T
  cov(X) = requirements covered by test set X

Constraint:
  CR(S) >= 0.95

Maximize:
  MSR(S), CGCC(S), ETR(S)
```

The search result is a feasible non-dominated set of candidate test subsets. Users can then choose a subset according to the trade-off they prefer.

## Objectives and Metrics

| Metric | Meaning | Role |
|---|---|---|
| `CR` | Coverage Retention: fraction of original covered requirements retained by `S` | Hard constraint, default threshold `0.95` |
| `MSR` | Mutation Score Retention: fraction of mutants killed by `S` relative to the original suite | Objective, maximize |
| `CGCC` | Call Graph Centrality Coverage: centrality-weighted coverage retained by `S` | Objective, maximize |
| `ETR` | Execution Time Reduction: estimated time saved by selecting `S` | Objective, maximize |
| `ROP` | Redundancy/Overlap Penalty | Diagnostic value, not an optimization objective |
| Hypervolume | 2D/3D Pareto-front hypervolume with reference point `(0, 0, 0)` for 3D fronts | Main comparison metric in Pareto benchmarks |

In the current code, risk signals are generated from the coverage matrix using seeded proxy data:

- centrality is approximated from requirement coverage frequency;
- mutation matrices are generated synthetically but coupled to coverage;
- execution time is estimated from per-test coverage counts with seeded lognormal noise.

These proxies are useful for repeatable experiments, but they should not be interpreted as full real mutation analysis or full static call-graph analysis.

## Implemented Algorithms

| Algorithm | Implementation | Notes |
|---|---|---|
| AR-QIEA | `src/quantum_testing/algorithms/ar_qiea.py` | Adaptive risk-aware quantum-inspired evolutionary algorithm with archive-based Pareto search |
| MO-QIEA | `ARQIEA(..., risk_adaptive=False)` | Ablation baseline that disables risk-adaptive rotation |
| Risk-shuffled AR-QIEA | `scripts/pareto_benchmark.py` option `risk_shuffled_ar_qiea` | Diagnostic ablation that shuffles risk scores |
| NSGA-II | `src/quantum_testing/algorithms/nsga2.py` | Binary multi-objective evolutionary baseline |
| Random front | `scripts/pareto_benchmark.py` | Samples random bitstrings and returns the feasible non-dominated front |
| Greedy set cover | `src/quantum_testing/cli.py` and benchmark helper | Deterministic single-point coverage baseline |
| QIEA | `src/quantum_testing/algorithms/qiea.py` | Earlier single-objective quantum-inspired baseline |

## Dataset Preparation and Artifact Structure

Processed Defects4J datasets are stored under `datasets/defects4j/<Project>/<BugId>b/`. The included folders are processed artifacts: they are intended to let the benchmark run from a fixed coverage matrix without requiring users to rerun Defects4J coverage collection first.

The preparation workflow used by the dataset scripts is:

1. Check out the target Defects4J buggy version.
2. Collect candidate test identifiers from Defects4J metadata such as `tests.all`, `tests.relevant`, and `tests.trigger`.
3. Run Defects4J coverage for the relevant suite and for individual tests.
4. Parse coverage XML files into source-element requirements.
5. Build the processed files `tests.txt`, `requirements.txt`, `matrix.csv`, and `metadata.json`.
6. Validate matrix consistency before using the dataset in benchmark runs.

Each processed dataset folder may contain:

| File or directory | Meaning |
|---|---|
| `tests.txt` | Final valid test suite used as the original suite `T` in experiments. |
| `requirements.txt` | Extracted requirement/source-element list `R`, usually covered source lines from modified or relevant Defects4J classes. |
| `matrix.csv` | Binary test-requirement coverage matrix. The first column is `test_id`; remaining columns correspond to `requirements.txt`. |
| `metadata.json` | Dataset summary and provenance fields such as test count, requirement count, matrix format, requirement definition, validation status, warnings, skipped tests, failed coverage collection, zero-coverage rows, or coverage statistics when available. |
| `raw/coverage/` | Raw per-test coverage XML files, when retained locally. Some archived folders may include only the processed matrix artifacts. |
| Auxiliary files | Optional Defects4J or workflow records such as `tests.all`, `tests.relevant`, `tests.trigger`, `skipped_tests.txt`, logs, coverage-failure records, or `report/summary.md`. Presence varies by instance. |

The consistency checks expected for a usable processed dataset are:

- matrix rows match the final tests in `tests.txt`;
- matrix columns match the requirements in `requirements.txt`;
- matrix values are binary coverage indicators;
- duplicated or invalid tests are excluded from the final matrix;
- skipped tests, failed coverage collection, zero-coverage rows, and uncovered requirements are recorded as warnings or metadata instead of being silently hidden.

Zero-coverage rows can occur when the requirement set is focused on modified or relevant program elements: a test may be valid in the original suite but not cover the selected requirement slice. A dataset with non-critical warnings can still be usable for the reported benchmark if the warnings are explicit in `metadata.json` or the accompanying report.

Included processed dataset folders currently include:

- `datasets/defects4j/Lang/3b`
- `datasets/defects4j/Lang/5b`
- `datasets/defects4j/Lang/6b`
- `datasets/defects4j/Lang/20b`
- `datasets/defects4j/Chart/1b`
- `datasets/defects4j/Chart/9b`
- `datasets/defects4j/Chart/17b`
- `datasets/defects4j/Chart/20b`
- `datasets/defects4j/Chart/26b`

To inspect a dataset, open its `metadata.json`, compare the first row of `matrix.csv` with `requirements.txt`, and compare the matrix test-id column with `tests.txt`. The benchmark runner stores the exact `root`, seed list, algorithms, and proxy-risk configuration in each output JSON under `config`, so users can identify which instance was used for a result.

## Repository Structure

```text
quantum-testing/
  src/quantum_testing/
    algorithms/          AR-QIEA, NSGA-II, and QIEA implementations
    analyzers/           Proxy centrality and mutation helpers
    problems/            Coverage and risk-aware minimization problem definitions
    metrics.py           Single-objective testing metrics
    metrics_mo.py        Pareto dominance, crowding distance, hypervolume
    cli.py               Installed command-line interface
  scripts/
    pareto_benchmark.py  Main Pareto benchmark runner
    plot_pareto.py       Pareto projection and hypervolume plotting script
  datasets/
    defects4j/           Processed Defects4J matrices and metadata
  artifacts/
    pareto/              Benchmark JSON outputs, logs, and run metadata
  REPORT_EVERY_CHANGES/  Detailed analysis and statistical notes
  tests/                 Pytest unit tests for metrics, problem, and algorithms
  SPEC-AR-QIEA.md        Research and implementation specification
  pyproject.toml         Package metadata and dependencies
```

## Setup

Python `>=3.10` is required. The project metadata lists NumPy, SciPy, and Matplotlib as runtime dependencies, with Pytest dependencies available through the `dev` extra.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

If you use `uv`, the repository also contains `uv.lock`.

## Running Tests

Run the unit tests with:

```bash
python -m pytest -q
```

The detailed Lang 3b report records a targeted pre-benchmark check:

```bash
python -m pytest -q tests/test_metrics_mo.py tests/test_risk_problem.py tests/test_ar_qiea.py tests/test_nsga2.py
```

That recorded check passed with `17 passed` before the full Lang 3b benchmark run.

## CLI Usage

After installation, the console script is available as `quantum-testing`. The same commands can also be run with `python -m quantum_testing.cli`.

```bash
quantum-testing demo --seed 42
quantum-testing minimize --matrix datasets/defects4j/Lang/3b/matrix.csv --algorithm qiea --seed 42
quantum-testing minimize --matrix datasets/defects4j/Lang/3b/matrix.csv --algorithm greedy
quantum-testing pareto --matrix datasets/defects4j/Lang/3b/matrix.csv --algo ar-qiea --seed 42 --risk-seed 12345 --cr-threshold 0.95 --pop 40 --gens 150
quantum-testing pareto --matrix datasets/defects4j/Lang/3b/matrix.csv --algo mo-qiea --seed 42
quantum-testing pareto --matrix datasets/defects4j/Lang/3b/matrix.csv --algo nsga2 --seed 42
```

## Running Benchmarks

The main benchmark runner is `scripts/pareto_benchmark.py`.

Fast smoke example:

```bash
python scripts/pareto_benchmark.py \
  --root datasets/defects4j/Lang/6b \
  --seeds 42..44 \
  --pop 10 \
  --gens 20 \
  --algorithms ar_qiea,mo_qiea,nsga2,random_front \
  --risk-seed 12345 \
  --cr-threshold 0.95 \
  --output artifacts/pareto/smoke-local.json
```

Recorded full Lang 3b benchmark command:

```bash
python scripts/pareto_benchmark.py \
  --root datasets/defects4j/Lang/3b \
  --seeds 42..71 \
  --pop 40 \
  --gens 150 \
  --algorithms ar_qiea,mo_qiea,nsga2,random_front \
  --risk-seed 12345 \
  --cr-threshold 0.95 \
  --output artifacts/pareto/lang3b_full_19-06-2026.json
```

The recorded run completed successfully with exit code `0`. Its run metadata is stored in:

```text
artifacts/pareto/lang3b_full_19-06-2026.runmeta.txt
```

The run took approximately `4693.88` seconds, or `78.23` minutes, on the recorded environment.

## Plotting Results

Use `scripts/plot_pareto.py` to generate 2D Pareto projections and hypervolume bar charts from a benchmark JSON file:

```bash
python scripts/plot_pareto.py \
  --input artifacts/pareto/lang3b_full_19-06-2026.json \
  --output-dir artifacts/pareto/plots
```

To plot a specific case key, pass `--case`. For the recorded Lang 3b result, the case key is `.` because the benchmark root points directly at one dataset directory.

## Outputs and Reports

Important result and analysis files include:

| Path | Purpose |
|---|---|
| `artifacts/pareto/lang3b_full_19-06-2026.json` | Full 30-seed Lang 3b benchmark output |
| `artifacts/pareto/lang3b_full_19-06-2026.log` | Benchmark runner output log |
| `artifacts/pareto/lang3b_full_19-06-2026.runmeta.txt` | Start/end/runtime metadata and command line |
| `artifacts/pareto/*smoke*.json` | Smoke or partial benchmark outputs |
| `REPORT_EVERY_CHANGES/3B_Detail-Result-Analyst_19-06-2026.md` | Detailed Lang 3b benchmark analysis |
| `REPORT_EVERY_CHANGES/wilcoxon_statistical_report_2026-06-19.md` | Post-run Wilcoxon statistical analysis |

The full Lang 3b artifact reports these mean hypervolume values over seeds `42..71`:

| Algorithm | Mean HV | Std HV | Mean front size |
|---|---:|---:|---:|
| AR-QIEA | 0.428521 | 0.008778 | 44.90 |
| MO-QIEA | 0.416320 | 0.013486 | 36.30 |
| NSGA-II | 0.376986 | 0.033425 | 17.63 |
| Random front | 0.252479 | 0.021973 | 24.07 |

The Wilcoxon report states that, for the recorded Lang 3b benchmark, AR-QIEA has higher paired 3D hypervolume than:

- MO-QIEA: `p = 0.000519084744155`, 22 wins / 8 losses / 0 ties;
- NSGA-II: `p = 9.31322574615e-09`, 28 wins / 2 losses / 0 ties.

These results should be cited as **Lang 3b results only**, not as full Defects4J-wide evidence.

## Reproducibility Notes

- Benchmark algorithm seeds are controlled with `--seeds`; the main recorded benchmark uses `42..71`.
- Synthetic risk data is controlled separately with `--risk-seed`; the recorded Lang 3b run uses `12345`.
- The default coverage-retention threshold is `--cr-threshold 0.95`.
- The recorded full benchmark uses `pop=40`, `gens=150`, and an evaluation budget of `6000` observations per stochastic algorithm run.
- The benchmark output stores raw per-seed fronts and hypervolume values in JSON.
- SciPy is required for Wilcoxon tests. The detailed benchmark report notes SciPy was unavailable during the original run, while the later Wilcoxon report confirms SciPy was available for post-run statistical testing.
- The current MSR, CGCC, and ETR values are based on seeded proxy data derived from coverage, not real Major mutation runs or a fully resolved Java call graph.

## Current Status and Limitations

This repository is suitable as a research-code artifact for the implemented Pareto minimization workflow, but it is not a complete Defects4J study.

Current strengths:

- implemented Pareto metrics, constraint domination, and hypervolume;
- implemented AR-QIEA, MO-QIEA ablation, NSGA-II, random-front baseline, greedy point, and earlier QIEA baseline;
- validated full Lang 3b matrix and a full 30-seed Lang 3b benchmark artifact;
- detailed reports for the Lang 3b benchmark and Wilcoxon analysis.

Known limitations:

- only Lang 3b has a complete full benchmark artifact in this repository;
- Lang 6b smoke data is intentionally small, and the non-smoke Lang 6b folder is incomplete/inconsistent;
- real mutation-analysis data is not present in the current dataset folders;
- call-graph centrality is currently represented by a proxy, not by a full Java static-analysis pipeline;
- existing full results should not be described as full Defects4J results;
- the project is alpha-stage research code and may still contain experimental scripts and historical reports.

## Citation

If this repository is used in a paper or report, please cite the corresponding manuscript/artifact once available.

```bibtex
@misc{quantum_testing_artifact,
  title        = {Quantum Testing: Pareto-Based Test Suite Minimization with Quantum-Inspired Evolutionary Search},
  author       = {Rabuno},
  year         = {2026},
  note         = {Research code artifact. Citation details to be updated.}
}
```

## Author

Rabuno

## License

This project is released under the MIT License. See `LICENSE` for details.
