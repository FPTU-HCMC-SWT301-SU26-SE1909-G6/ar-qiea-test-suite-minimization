# Dataset Discriminativeness Random-Sampling Diagnostic (7 Instances)

## Purpose
This diagnostic estimates how often direct random test-subset sampling satisfies the coverage-retention constraint and then reaches near-perfect MSR or CGCC. It is intended to explain when a random baseline can be competitive because the dataset itself has many high-quality feasible subsets.

## Scope and Limitation
This report covers only 7 of the 11 paper instances: Chart-1b, Chart-20b, Chart-26b, Lang-3b, Lang-5b, Lang-6b, and Lang-20b.

It does not cover Lang-1b, Lang-4b, Lang-14b, or Lang-22b because complete raw benchmark artifacts for those four instances were not available in the current repository audit. The diagnostic is supporting evidence, not a replacement for the full 11-instance experimental table.

## Method
For each included instance, the script samples 10,000 random subsets using the same random-subset generation pattern as `random_front` in `scripts/pareto_benchmark.py`: draw a subset density uniformly from [0.05, 0.95], then include each test independently with that probability. Unlike `random_front`, this diagnostic records all sampled evaluations before Pareto or constraint-dominance filtering.

Each instance is loaded with `RiskAwareProblem.from_matrix_csv`, and sampled subsets are scored with the same CR, MSR, CGCC, and ETR formulas used by `RiskAwareProblem.evaluate`. The main experiment defaults are used: risk seed 12345, CR threshold 0.95, mutant factor 2.0, and kill probability 0.6. A subset is feasible when CR(S) >= 0.95. Near-perfect thresholds are MSR(S) >= 0.99 and CGCC(S) >= 0.99.

Raw CSV output: `D:/FPT/Study/2026/sem5/SWT301/Quantun+Testing/OFFICIAL - Copy/ar-qiea-test-suite-minimization/artifacts/dataset_discriminativeness_random_sampling_7_instances.csv`.

## Diagnostic Table
| Instance | Samples | Feasible CR>=0.95 | Feasible % | Feasible MSR>=0.99 | % of Feasible | Feasible CGCC>=0.99 | % of Feasible | Mean CR | Mean MSR | Mean CGCC | Mean ETR | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Chart-1b | 10000 | 2043 | 20.430000% | 694 | 33.969652% | 2043 | 100.000000% | 0.989010 | 0.974770 | 0.999486 | 0.202504 | moderately discriminative for MSR |
| Chart-20b | 10000 | 4166 | 41.660000% | 2277 | 54.656745% | 4166 | 100.000000% | 1.000000 | 0.974256 | 1.000000 | 0.314447 | weakly discriminative for MSR |
| Chart-26b | 10000 | 4941 | 49.410000% | 2632 | 53.268569% | 4941 | 100.000000% | 0.994735 | 0.987547 | 0.999837 | 0.355119 | weakly discriminative for MSR |
| Lang-3b | 10000 | 1042 | 10.420000% | 93 | 8.925144% | 1042 | 100.000000% | 0.972219 | 0.964720 | 0.995857 | 0.089638 | more discriminative for MSR |
| Lang-5b | 10000 | 1682 | 16.820000% | 745 | 44.292509% | 1192 | 70.868014% | 0.983513 | 0.966038 | 0.993560 | 0.167521 | moderately discriminative for MSR |
| Lang-6b | 10000 | 8516 | 85.160000% | 5646 | 66.298732% | 8516 | 100.000000% | 0.993181 | 0.989392 | 0.999304 | 0.439150 | weakly discriminative for MSR |
| Lang-20b | 10000 | 532 | 5.320000% | 6 | 1.127820% | 531 | 99.812030% | 0.967346 | 0.958805 | 0.994852 | 0.080599 | more discriminative for MSR |

## Interpretation
Instances with a high percentage of feasible random subsets also reaching MSR(S) >= 0.99 are weakly discriminative for MSR: random feasible subsets already preserve nearly all synthetic mutation score, so Random-Front can appear competitive without implying that it is generally superior. Instances with low percentages are more discriminative because feasibility alone does not usually imply near-perfect MSR.

Weakly discriminative for MSR in this diagnostic: Chart-20b, Chart-26b, Lang-6b.

Moderately discriminative for MSR in this diagnostic: Chart-1b, Lang-5b.

More discriminative for MSR in this diagnostic: Lang-3b, Lang-20b.

These results should be read together with HV, ETR, and front diversity. A random feasible subset may obtain high MSR or CGCC while still being less useful on other objectives, and AR-QIEA should not be claimed to always outperform Random-Front.

## Paper-Ready Paragraph
To assess whether several Defects4J instances are intrinsically weakly discriminative, we performed an auxiliary random-sampling diagnostic on the seven instances for which complete raw benchmark artifacts were available. For each instance, we sampled 10,000 random subsets using the same density-based generator as the Random-Front baseline, but evaluated every sampled subset before Pareto or constraint filtering. The diagnostic measures the proportion of feasible subsets satisfying CR(S) >= 0.95 and, among feasible subsets, the proportion that also reach MSR(S) >= 0.99 and CGCC(S) >= 0.99. High near-perfect MSR rates indicate that MSR is weakly discriminative on that instance, explaining why Random-Front can be competitive there; low rates indicate that feasibility alone is insufficient and the instance is more discriminative.

## Missing Data / Next Step
The remaining paper instances, Lang-1b, Lang-4b, Lang-14b, and Lang-22b, are not included here. The next step is to generate equivalent diagnostic rows for those four instances after their dataset matrices and/or raw benchmark artifacts are confirmed, or to clearly label this report as a 7-instance supporting diagnostic in the appendix.

