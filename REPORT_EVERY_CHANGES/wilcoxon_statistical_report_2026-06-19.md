# Wilcoxon Statistical Report - Pareto Benchmark Lang 3b - 2026-06-19

## 1. Purpose

This report updates the statistical analysis for the Defects4J Lang 3b Pareto benchmark after SciPy/Wilcoxon became available in the project virtual environment.

No benchmark rerun was needed. The existing full 30-seed benchmark JSON already contains paired hypervolume values by seed for AR-QIEA, MO-QIEA, NSGA-II, and random_front.

## 2. Files Inspected

| Path | Finding |
|---|---|
| `artifacts/pareto/lang3b_full_19-06-2026.json` | Full final benchmark result, 30 seeds, usable for paired tests |
| `artifacts/pareto/lang3b_full_19-06-2026.log` | Clean benchmark log, exit code 0 |
| `artifacts/pareto/lang3b_full_19-06-2026.runmeta.txt` | Clean benchmark start/end/runtime metadata |
| `artifacts/pareto/lang3b_3b_smoke_check.json` | Smoke result only, not used for final statistics |
| `artifacts/pareto/lang3b_3b_smoke_current.json` | Smoke result only, not used for final statistics |
| `artifacts/pareto/lang3b_partial_450_smoke.json` | Partial/smoke result, not used for final statistics |
| `reports/` | Directory did not exist before this report |
| `REPORT_EVERY_CHANGES/3B_Detail-Result-Analyst_19-06-2026.md` | Existing detailed benchmark report; previous Wilcoxon values were unavailable before SciPy was installed |

## 3. Rerun Decision

Rerun needed: **No**.

Reason:

- The final result file `artifacts/pareto/lang3b_full_19-06-2026.json` contains raw per-seed hypervolume values.
- AR-QIEA, MO-QIEA, and NSGA-II each have 30 records.
- Seeds are matched exactly: `42..71`.
- The values are 3D hypervolume values from the benchmark runner, computed on feasible Pareto fronts using the project metric protocol.

## 4. Verification Commands

Lightweight SciPy check:

```powershell
D:\FPT\Study\2026\sem5\SWT301\Quantun+Testing\OFFICIAL\.venv\Scripts\python.exe -c "import scipy; from scipy.stats import wilcoxon; print('scipy', scipy.__version__); print('wilcoxon OK')"
```

Observed result:

```text
scipy 1.17.1
wilcoxon OK
```

The Wilcoxon tests used:

```python
from scipy.stats import wilcoxon
wilcoxon(ar_qiea_hv, baseline_hv, alternative="greater")
```

## 5. Benchmark Data Used

| Setting | Value |
|---|---|
| Dataset | `datasets/defects4j/Lang/3b` |
| Result file | `artifacts/pareto/lang3b_full_19-06-2026.json` |
| Seeds | `42..71` |
| Sample size | `30 paired runs` |
| Algorithms compared | `ar_qiea` vs `mo_qiea`; `ar_qiea` vs `nsga2` |
| Metric | 3D hypervolume |
| Alternative hypothesis | AR-QIEA hypervolume is greater |
| Alpha | `0.05` |

## 6. Wilcoxon Results Summary

| Comparison | n | AR-QIEA mean HV | Baseline mean HV | Paired mean difference | Statistic | p-value | p < 0.05 | Wins/Losses/Ties |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| AR-QIEA vs MO-QIEA | 30 | 0.428520604 | 0.416319718 | 0.012200886 | 386.000000000 | 0.000519084744155 | yes | 22/8/0 |
| AR-QIEA vs NSGA-II | 30 | 0.428520604 | 0.376986365 | 0.051534239 | 460.000000000 | 9.31322574615e-09 | yes | 28/2/0 |

## 7. Descriptive Statistics

### AR-QIEA vs MO-QIEA

| Series | Mean | Median | Sample Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| AR-QIEA HV | 0.428520604195484 | 0.429269971317147 | 0.008927694507097 | 0.405477177316968 | 0.444797159829507 |
| MO-QIEA HV | 0.416319718261332 | 0.415255274815750 | 0.013716532300658 | 0.391083843913246 | 0.450921258520057 |
| Paired difference | 0.012200885934152 | 0.014277278686700 | 0.018319493493384 | -0.031399090286494 | 0.049258625174860 |

### AR-QIEA vs NSGA-II

| Series | Mean | Median | Sample Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| AR-QIEA HV | 0.428520604195484 | 0.429269971317147 | 0.008927694507097 | 0.405477177316968 | 0.444797159829507 |
| NSGA-II HV | 0.376986364988702 | 0.379897002584687 | 0.033996879916686 | 0.259839442282493 | 0.427951334148929 |
| Paired difference | 0.051534239206782 | 0.049807251157850 | 0.037585267175876 | -0.017854160481132 | 0.171457977253332 |

## 8. Paired Hypervolume Values

| Seed | AR-QIEA HV | MO-QIEA HV | AR - MO | NSGA-II HV | AR - NSGA-II |
|---:|---:|---:|---:|---:|---:|
| 42 | 0.437755656 | 0.424336191 | 0.013419465 | 0.322443723 | 0.115311933 |
| 43 | 0.431297420 | 0.416388853 | 0.014908567 | 0.259839442 | 0.171457977 |
| 44 | 0.436400495 | 0.413930048 | 0.022470446 | 0.362831678 | 0.073568816 |
| 45 | 0.422516206 | 0.414634819 | 0.007881387 | 0.372550301 | 0.049965904 |
| 46 | 0.422701692 | 0.418887596 | 0.003814096 | 0.391469501 | 0.031232191 |
| 47 | 0.431627606 | 0.415875731 | 0.015751875 | 0.397021819 | 0.034605787 |
| 48 | 0.437422740 | 0.413919946 | 0.023502794 | 0.418399125 | 0.019023615 |
| 49 | 0.417204347 | 0.424819404 | -0.007615057 | 0.396377232 | 0.020827114 |
| 50 | 0.420238643 | 0.429889207 | -0.009650564 | 0.368179188 | 0.052059455 |
| 51 | 0.421445031 | 0.425439286 | -0.003994255 | 0.412205066 | 0.009239965 |
| 52 | 0.435842787 | 0.404342209 | 0.031500577 | 0.345962820 | 0.089879967 |
| 53 | 0.405477177 | 0.419432774 | -0.013955597 | 0.423331338 | -0.017854160 |
| 54 | 0.416746106 | 0.426342729 | -0.009596623 | 0.420197450 | -0.003451344 |
| 55 | 0.444797160 | 0.395538535 | 0.049258625 | 0.373565633 | 0.071231527 |
| 56 | 0.427876699 | 0.406560138 | 0.021316561 | 0.390271771 | 0.037604928 |
| 57 | 0.421225756 | 0.391083844 | 0.030141912 | 0.336283172 | 0.084942585 |
| 58 | 0.428864247 | 0.407247677 | 0.021616570 | 0.395101321 | 0.033762927 |
| 59 | 0.429623950 | 0.409875509 | 0.019748441 | 0.376119555 | 0.053504395 |
| 60 | 0.433323048 | 0.398218968 | 0.035104080 | 0.383674450 | 0.049648598 |
| 61 | 0.441554822 | 0.427908832 | 0.013645991 | 0.392659714 | 0.048895108 |
| 62 | 0.419522168 | 0.450921259 | -0.031399090 | 0.356741241 | 0.062780927 |
| 63 | 0.423590447 | 0.443978753 | -0.020388306 | 0.388329597 | 0.035260850 |
| 64 | 0.444134499 | 0.410533547 | 0.033600952 | 0.355747465 | 0.088387034 |
| 65 | 0.428298611 | 0.400370799 | 0.027927812 | 0.365457452 | 0.062841159 |
| 66 | 0.432633052 | 0.407778337 | 0.024854715 | 0.427951334 | 0.004681718 |
| 67 | 0.431187514 | 0.421322451 | 0.009865064 | 0.345926313 | 0.085261201 |
| 68 | 0.418673604 | 0.410231196 | 0.008442408 | 0.396069750 | 0.022603854 |
| 69 | 0.435096701 | 0.438156481 | -0.003059779 | 0.373774608 | 0.061322094 |
| 70 | 0.428940852 | 0.418066639 | 0.010874213 | 0.375407520 | 0.053533332 |
| 71 | 0.429599091 | 0.403559791 | 0.026039300 | 0.385701372 | 0.043897719 |

## 9. Interpretation

AR-QIEA is statistically significantly better than both required baselines on paired 3D hypervolume for the existing Lang 3b full benchmark result.

- Against MO-QIEA, AR-QIEA wins 22 of 30 paired runs and has `p = 0.000519084744155`.
- Against NSGA-II, AR-QIEA wins 28 of 30 paired runs and has `p = 9.31322574615e-09`.
- Both p-values are below `0.05` using the one-sided Wilcoxon signed-rank test with `alternative="greater"`.

This means the statistical portion of the benchmark claim is supported for these two comparisons using the existing full 30-seed Lang 3b result file.

## 10. Notes And Limits

- This report did not rerun the expensive benchmark.
- This report did not modify algorithm logic, dataset generation logic, or benchmark JSON files.
- Smoke and partial files were inspected but not used for final statistical claims.
- The previous detailed report marked Wilcoxon as unavailable because SciPy was not installed at that time. This new report supersedes only that statistical conclusion.
