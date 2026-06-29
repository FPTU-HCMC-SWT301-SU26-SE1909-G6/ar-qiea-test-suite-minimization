# Wilcoxon Statistical Report

## Purpose
This report tests whether AR-QIEA differs significantly from MO-QIEA, NSGA-II, and Random-Front on existing Defects4J benchmark artifacts. The analysis uses only raw per-seed records and does not use aggregate-only mean or median tables as Wilcoxon input.

## Data Sources Used
| bug_id | file | reason |
| --- | --- | --- |
| Chart-1b | artifacts\pareto\chart1b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| Chart-20b | artifacts\pareto\chart20b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| Chart-26b | artifacts\pareto\chart26b_full_matrix_only_19-06-2026.json | usable per-seed raw benchmark artifact |
| Lang-20b | artifacts\pareto\lang20b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| Lang-3b | artifacts\pareto\lang3b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| Lang-5b | artifacts\pareto\lang5b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| Lang-6b | artifacts\pareto\lang6b_full_19-06-2026.json | usable per-seed raw benchmark artifact |

## Raw Data Validity Check
Valid Wilcoxon result rows: 105.
Non-computable bug/metric/comparison rows: 0.
Each valid test was paired by the same bug id, metric, seed index, and number of observations for AR-QIEA and the baseline. Duplicate raw artifacts were not combined; one source per bug was selected.

## Method
For HV, the script uses the per-seed `hv` value stored in each raw record. For MSR, CGCC, and ETR, it uses the per-seed best value on that metric from the feasible raw front. For BRARS, it computes the per-entry BRARS formula from raw objectives, CR, selected_count, and n_tests, then uses the per-seed best BRARS in the feasible front. All metrics are treated as maximize metrics.
The Wilcoxon signed-rank test is run with `scipy.stats.wilcoxon(..., alternative='two-sided')` at alpha = 0.05. Direction is assigned only when the two-sided test is significant.

## Detailed Results
| bug_id | metric | comparison | n | ar_qiea_mean | baseline_mean | ar_qiea_median | baseline_median | wilcoxon_statistic | p_value | significant_alpha_0_05 | direction | rank_biserial_effect_size |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Chart-1b | MSR | AR-QIEA vs MO-QIEA | 30 | 0.999352 | 0.999176 | 1 | 1 | 42 | 0.466854 | False | no significant difference | 0.2 |
| Chart-1b | MSR | AR-QIEA vs NSGA2 | 30 | 0.999352 | 0.991107 | 1 | 0.992933 | 0 | 1.62396e-06 | True | AR-QIEA better | 1 |
| Chart-1b | MSR | AR-QIEA vs Random-Front | 30 | 0.999352 | 1 | 1 | 1 | 0 | 0.00228194 | True | AR-QIEA worse | -1 |
| Chart-1b | CGCC | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-1b | CGCC | AR-QIEA vs NSGA2 | 30 | 1 | 0.999955 | 1 | 1 | 0 | 0.00705833 | True | AR-QIEA better | 1 |
| Chart-1b | CGCC | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-1b | ETR | AR-QIEA vs MO-QIEA | 30 | 0.686848 | 0.660728 | 0.688063 | 0.660524 | 2 | 5.58794e-09 | True | AR-QIEA better | 0.991398 |
| Chart-1b | ETR | AR-QIEA vs NSGA2 | 30 | 0.686848 | 0.705314 | 0.688063 | 0.705702 | 95 | 0.00374443 | True | AR-QIEA worse | -0.591398 |
| Chart-1b | ETR | AR-QIEA vs Random-Front | 30 | 0.686848 | 0.680437 | 0.688063 | 0.671877 | 167 | 0.183969 | False | no significant difference | 0.28172 |
| Chart-1b | HV | AR-QIEA vs MO-QIEA | 30 | 0.683533 | 0.656683 | 0.68523 | 0.656683 | 1 | 3.72529e-09 | True | AR-QIEA better | 0.995699 |
| Chart-1b | HV | AR-QIEA vs NSGA2 | 30 | 0.683533 | 0.696205 | 0.68523 | 0.696492 | 117 | 0.0164312 | True | AR-QIEA worse | -0.496774 |
| Chart-1b | HV | AR-QIEA vs Random-Front | 30 | 0.683533 | 0.664137 | 0.68523 | 0.656505 | 93 | 0.00322299 | True | AR-QIEA better | 0.6 |
| Chart-1b | BRARS | AR-QIEA vs MO-QIEA | 30 | 0.804971 | 0.793742 | 0.804892 | 0.793397 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Chart-1b | BRARS | AR-QIEA vs NSGA2 | 30 | 0.804971 | 0.817815 | 0.804892 | 0.817194 | 4 | 1.30385e-08 | True | AR-QIEA worse | -0.982796 |
| Chart-1b | BRARS | AR-QIEA vs Random-Front | 30 | 0.804971 | 0.828634 | 0.804892 | 0.827886 | 10 | 8.00937e-08 | True | AR-QIEA worse | -0.956989 |
| Chart-20b | MSR | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-20b | MSR | AR-QIEA vs NSGA2 | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-20b | MSR | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-20b | CGCC | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-20b | CGCC | AR-QIEA vs NSGA2 | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-20b | CGCC | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-20b | ETR | AR-QIEA vs MO-QIEA | 30 | 0.666116 | 0.653738 | 0.666121 | 0.652843 | 15 | 2.55182e-07 | True | AR-QIEA better | 0.935484 |
| Chart-20b | ETR | AR-QIEA vs NSGA2 | 30 | 0.666116 | 0.71903 | 0.666121 | 0.718512 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-20b | ETR | AR-QIEA vs Random-Front | 30 | 0.666116 | 0.916966 | 0.666121 | 0.915148 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-20b | HV | AR-QIEA vs MO-QIEA | 30 | 0.665209 | 0.652683 | 0.665458 | 0.652159 | 6 | 2.6077e-08 | True | AR-QIEA better | 0.974194 |
| Chart-20b | HV | AR-QIEA vs NSGA2 | 30 | 0.665209 | 0.718234 | 0.665458 | 0.717517 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-20b | HV | AR-QIEA vs Random-Front | 30 | 0.665209 | 0.909481 | 0.665458 | 0.910018 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-20b | BRARS | AR-QIEA vs MO-QIEA | 30 | 0.820567 | 0.813303 | 0.820657 | 0.813099 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Chart-20b | BRARS | AR-QIEA vs NSGA2 | 30 | 0.820567 | 0.848929 | 0.820657 | 0.847999 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-20b | BRARS | AR-QIEA vs Random-Front | 30 | 0.820567 | 0.941243 | 0.820657 | 0.941351 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-26b | MSR | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-26b | MSR | AR-QIEA vs NSGA2 | 30 | 1 | 0.99994 | 1 | 1 | 0 | 0.317311 | False | no significant difference | 1 |
| Chart-26b | MSR | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-26b | CGCC | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-26b | CGCC | AR-QIEA vs NSGA2 | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-26b | CGCC | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Chart-26b | ETR | AR-QIEA vs MO-QIEA | 30 | 0.812193 | 0.767551 | 0.811722 | 0.765525 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Chart-26b | ETR | AR-QIEA vs NSGA2 | 30 | 0.812193 | 0.845007 | 0.811722 | 0.849606 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-26b | ETR | AR-QIEA vs Random-Front | 30 | 0.812193 | 0.923884 | 0.811722 | 0.924445 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-26b | HV | AR-QIEA vs MO-QIEA | 30 | 0.810979 | 0.766728 | 0.810889 | 0.765023 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Chart-26b | HV | AR-QIEA vs NSGA2 | 30 | 0.810979 | 0.843786 | 0.810889 | 0.848738 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-26b | HV | AR-QIEA vs Random-Front | 30 | 0.810979 | 0.91387 | 0.810889 | 0.915109 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-26b | BRARS | AR-QIEA vs MO-QIEA | 30 | 0.855616 | 0.842304 | 0.855306 | 0.842057 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Chart-26b | BRARS | AR-QIEA vs NSGA2 | 30 | 0.855616 | 0.874302 | 0.855306 | 0.874365 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Chart-26b | BRARS | AR-QIEA vs Random-Front | 30 | 0.855616 | 0.936756 | 0.855306 | 0.936661 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Lang-20b | MSR | AR-QIEA vs MO-QIEA | 30 | 0.946797 | 0.490083 | 0.946268 | 0.902065 | 0 | 1.73331e-06 | True | AR-QIEA better | 1 |
| Lang-20b | MSR | AR-QIEA vs NSGA2 | 30 | 0.946797 | 0.74625 | 0.946268 | 0.928798 | 19 | 1.12353e-05 | True | AR-QIEA better | 0.91828 |
| Lang-20b | MSR | AR-QIEA vs Random-Front | 30 | 0.946797 | 0.995818 | 0.946268 | 0.995236 | 0 | 1.71593e-06 | True | AR-QIEA worse | -1 |
| Lang-20b | CGCC | AR-QIEA vs MO-QIEA | 30 | 0.995341 | 0.529175 | 0.995289 | 0.991066 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-20b | CGCC | AR-QIEA vs NSGA2 | 30 | 0.995341 | 0.795331 | 0.995289 | 0.993784 | 29 | 3.23914e-06 | True | AR-QIEA better | 0.875269 |
| Lang-20b | CGCC | AR-QIEA vs Random-Front | 30 | 0.995341 | 0.999697 | 0.995289 | 0.999682 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Lang-20b | ETR | AR-QIEA vs MO-QIEA | 30 | 0.371016 | 0.171484 | 0.372806 | 0.287998 | 3 | 9.31323e-09 | True | AR-QIEA better | 0.987097 |
| Lang-20b | ETR | AR-QIEA vs NSGA2 | 30 | 0.371016 | 0.278579 | 0.372806 | 0.342311 | 70 | 0.000460107 | True | AR-QIEA better | 0.698925 |
| Lang-20b | ETR | AR-QIEA vs Random-Front | 30 | 0.371016 | 0.186165 | 0.372806 | 0.183869 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-20b | HV | AR-QIEA vs MO-QIEA | 30 | 0.347853 | 0.156182 | 0.34895 | 0.263741 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-20b | HV | AR-QIEA vs NSGA2 | 30 | 0.347853 | 0.257959 | 0.34895 | 0.317181 | 42 | 2.07983e-05 | True | AR-QIEA better | 0.819355 |
| Lang-20b | HV | AR-QIEA vs Random-Front | 30 | 0.347853 | 0.180041 | 0.34895 | 0.178007 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-20b | BRARS | AR-QIEA vs MO-QIEA | 30 | 0.659225 | 0.337409 | 0.659471 | 0.614755 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-20b | BRARS | AR-QIEA vs NSGA2 | 30 | 0.659225 | 0.518738 | 0.659471 | 0.646854 | 87 | 0.00202018 | True | AR-QIEA better | 0.625806 |
| Lang-20b | BRARS | AR-QIEA vs Random-Front | 30 | 0.659225 | 0.479037 | 0.659471 | 0.479602 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-3b | MSR | AR-QIEA vs MO-QIEA | 30 | 0.984448 | 0.980169 | 0.984629 | 0.981013 | 60 | 0.00188297 | True | AR-QIEA better | 0.698413 |
| Lang-3b | MSR | AR-QIEA vs NSGA2 | 30 | 0.984448 | 0.949729 | 0.984629 | 0.951175 | 0 | 1.72569e-06 | True | AR-QIEA better | 1 |
| Lang-3b | MSR | AR-QIEA vs Random-Front | 30 | 0.984448 | 1 | 0.984629 | 1 | 0 | 1.6594e-06 | True | AR-QIEA worse | -1 |
| Lang-3b | CGCC | AR-QIEA vs MO-QIEA | 30 | 0.999863 | 0.999629 | 1 | 0.99958 | 31 | 0.0056456 | True | AR-QIEA better | 0.704762 |
| Lang-3b | CGCC | AR-QIEA vs NSGA2 | 30 | 0.999863 | 0.996805 | 1 | 0.996934 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-3b | CGCC | AR-QIEA vs Random-Front | 30 | 0.999863 | 1 | 1 | 1 | 0 | 0.00360379 | True | AR-QIEA worse | -1 |
| Lang-3b | ETR | AR-QIEA vs MO-QIEA | 30 | 0.441128 | 0.430345 | 0.441302 | 0.4284 | 107 | 0.00870546 | True | AR-QIEA better | 0.539785 |
| Lang-3b | ETR | AR-QIEA vs NSGA2 | 30 | 0.441128 | 0.400167 | 0.441302 | 0.401165 | 24 | 1.41934e-06 | True | AR-QIEA better | 0.896774 |
| Lang-3b | ETR | AR-QIEA vs Random-Front | 30 | 0.441128 | 0.260549 | 0.441302 | 0.262231 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-3b | HV | AR-QIEA vs MO-QIEA | 30 | 0.428521 | 0.41632 | 0.42927 | 0.415255 | 79 | 0.00103817 | True | AR-QIEA better | 0.660215 |
| Lang-3b | HV | AR-QIEA vs NSGA2 | 30 | 0.428521 | 0.376986 | 0.42927 | 0.379897 | 5 | 1.86265e-08 | True | AR-QIEA better | 0.978495 |
| Lang-3b | HV | AR-QIEA vs Random-Front | 30 | 0.428521 | 0.252479 | 0.42927 | 0.254731 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-3b | BRARS | AR-QIEA vs MO-QIEA | 30 | 0.693748 | 0.689068 | 0.694182 | 0.688003 | 96 | 0.00403179 | True | AR-QIEA better | 0.587097 |
| Lang-3b | BRARS | AR-QIEA vs NSGA2 | 30 | 0.693748 | 0.681372 | 0.694182 | 0.681537 | 89 | 0.00236749 | True | AR-QIEA better | 0.617204 |
| Lang-3b | BRARS | AR-QIEA vs Random-Front | 30 | 0.693748 | 0.563688 | 0.694182 | 0.559818 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-5b | MSR | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-5b | MSR | AR-QIEA vs NSGA2 | 30 | 1 | 0.984956 | 1 | 0.99115 | 0 | 0.000171267 | True | AR-QIEA better | 1 |
| Lang-5b | MSR | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-5b | CGCC | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-5b | CGCC | AR-QIEA vs NSGA2 | 30 | 1 | 0.998513 | 1 | 1 | 0 | 0.0421682 | True | AR-QIEA better | 1 |
| Lang-5b | CGCC | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-5b | ETR | AR-QIEA vs MO-QIEA | 30 | 0.540796 | 0.535291 | 0.540196 | 0.534471 | 42 | 2.07983e-05 | True | AR-QIEA better | 0.819355 |
| Lang-5b | ETR | AR-QIEA vs NSGA2 | 30 | 0.540796 | 0.573873 | 0.540196 | 0.578483 | 1 | 3.72529e-09 | True | AR-QIEA worse | -0.995699 |
| Lang-5b | ETR | AR-QIEA vs Random-Front | 30 | 0.540796 | 0.589453 | 0.540196 | 0.586469 | 15 | 2.55182e-07 | True | AR-QIEA worse | -0.935484 |
| Lang-5b | HV | AR-QIEA vs MO-QIEA | 30 | 0.534611 | 0.529235 | 0.534295 | 0.528557 | 23 | 1.19209e-06 | True | AR-QIEA better | 0.901075 |
| Lang-5b | HV | AR-QIEA vs NSGA2 | 30 | 0.534611 | 0.560079 | 0.534295 | 0.567244 | 27 | 2.3488e-06 | True | AR-QIEA worse | -0.883871 |
| Lang-5b | HV | AR-QIEA vs Random-Front | 30 | 0.534611 | 0.577086 | 0.534295 | 0.573864 | 19 | 5.71832e-07 | True | AR-QIEA worse | -0.91828 |
| Lang-5b | BRARS | AR-QIEA vs MO-QIEA | 30 | 0.74829 | 0.745678 | 0.747976 | 0.74596 | 42 | 2.07983e-05 | True | AR-QIEA better | 0.819355 |
| Lang-5b | BRARS | AR-QIEA vs NSGA2 | 30 | 0.74829 | 0.771638 | 0.747976 | 0.772799 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Lang-5b | BRARS | AR-QIEA vs Random-Front | 30 | 0.74829 | 0.788154 | 0.747976 | 0.786432 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Lang-6b | MSR | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-6b | MSR | AR-QIEA vs NSGA2 | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-6b | MSR | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-6b | CGCC | AR-QIEA vs MO-QIEA | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-6b | CGCC | AR-QIEA vs NSGA2 | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-6b | CGCC | AR-QIEA vs Random-Front | 30 | 1 | 1 | 1 | 1 | 0 | 1 | False | no significant difference | 0 |
| Lang-6b | ETR | AR-QIEA vs MO-QIEA | 30 | 0.746305 | 0.732451 | 0.746379 | 0.731601 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-6b | ETR | AR-QIEA vs NSGA2 | 30 | 0.746305 | 0.759962 | 0.746379 | 0.759818 | 25 | 1.68383e-06 | True | AR-QIEA worse | -0.892473 |
| Lang-6b | ETR | AR-QIEA vs Random-Front | 30 | 0.746305 | 0.957032 | 0.746379 | 0.956056 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Lang-6b | HV | AR-QIEA vs MO-QIEA | 30 | 0.742735 | 0.729753 | 0.742903 | 0.729078 | 0 | 1.86265e-09 | True | AR-QIEA better | 1 |
| Lang-6b | HV | AR-QIEA vs NSGA2 | 30 | 0.742735 | 0.758 | 0.742903 | 0.759126 | 12 | 1.30385e-07 | True | AR-QIEA worse | -0.948387 |
| Lang-6b | HV | AR-QIEA vs Random-Front | 30 | 0.742735 | 0.950691 | 0.742903 | 0.950879 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Lang-6b | BRARS | AR-QIEA vs MO-QIEA | 30 | 0.83505 | 0.828039 | 0.835229 | 0.828343 | 1 | 3.72529e-09 | True | AR-QIEA better | 0.995699 |
| Lang-6b | BRARS | AR-QIEA vs NSGA2 | 30 | 0.83505 | 0.851567 | 0.835229 | 0.852127 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |
| Lang-6b | BRARS | AR-QIEA vs Random-Front | 30 | 0.83505 | 0.96102 | 0.835229 | 0.96067 | 0 | 1.86265e-09 | True | AR-QIEA worse | -1 |

## Summary
| row_type | metric | baseline | valid_tests | ar_qiea_wins | ar_qiea_losses | ties |
| --- | --- | --- | --- | --- | --- | --- |
| metric_by_baseline | BRARS | mo_qiea | 7 | 7 | 0 | 0 |
| metric_by_baseline | BRARS | nsga2 | 7 | 2 | 5 | 0 |
| metric_by_baseline | BRARS | random_front | 7 | 2 | 5 | 0 |
| metric_by_baseline | CGCC | mo_qiea | 7 | 2 | 0 | 5 |
| metric_by_baseline | CGCC | nsga2 | 7 | 4 | 0 | 3 |
| metric_by_baseline | CGCC | random_front | 7 | 0 | 2 | 5 |
| metric_by_baseline | ETR | mo_qiea | 7 | 7 | 0 | 0 |
| metric_by_baseline | ETR | nsga2 | 7 | 2 | 5 | 0 |
| metric_by_baseline | ETR | random_front | 7 | 2 | 4 | 1 |
| metric_by_baseline | HV | mo_qiea | 7 | 7 | 0 | 0 |
| metric_by_baseline | HV | nsga2 | 7 | 2 | 5 | 0 |
| metric_by_baseline | HV | random_front | 7 | 3 | 4 | 0 |
| metric_by_baseline | MSR | mo_qiea | 7 | 2 | 0 | 5 |
| metric_by_baseline | MSR | nsga2 | 7 | 4 | 0 | 3 |
| metric_by_baseline | MSR | random_front | 7 | 0 | 3 | 4 |
| overall_by_baseline | ALL | mo_qiea | 35 | 25 | 0 | 10 |
| overall_by_baseline | ALL | nsga2 | 35 | 14 | 15 | 6 |
| overall_by_baseline | ALL | random_front | 35 | 7 | 18 | 10 |

## Not Computable
_None._

## Artifact Audit
| status | bug_id | file | reason |
| --- | --- | --- | --- |
| not used |  | artifacts\pareto\audit-smoke.json | could not determine a single Defects4J bug id |
| not used |  | artifacts\pareto\chart20b_full_19-06-2026.runmeta.json | no benchmark cases with algorithms/raw records |
| not used |  | artifacts\pareto\chart20b_precheck_pytest_19-06-2026.runmeta.json | no benchmark cases with algorithms/raw records |
| not used |  | artifacts\pareto\chart26b_full_19-06-2026.runmeta.json | no benchmark cases with algorithms/raw records |
| not used |  | artifacts\pareto\chart26b_precheck_pytest_19-06-2026.meta.json | no benchmark cases with algorithms/raw records |
| not used |  | artifacts\pareto\chart26b_validation_19-06-2026.json | no benchmark cases with algorithms/raw records |
| not used |  | artifacts\pareto\lang20b_environment_20-06-2026.json | not a readable JSON object |
| not used |  | artifacts\pareto\lang20b_full_19-06-2026.runmeta.json | not a readable JSON object |
| not used |  | artifacts\pareto\lang20b_precheck_pytest_20-06-2026.runmeta.json | not a readable JSON object |
| not used |  | artifacts\pareto\lang20b_precheck_pytest_venv_20-06-2026.runmeta.json | not a readable JSON object |
| not used |  | artifacts\pareto\lang20b_validation_20-06-2026.json | no benchmark cases with algorithms/raw records |
| not used |  | artifacts\pareto\lang3b_partial_450_smoke.json | could not determine a single Defects4J bug id |
| not used |  | artifacts\pareto\lang5b_validation_2026-06-19.json | no benchmark cases with algorithms/raw records |
| not used |  | artifacts\pareto\smoke.json | could not determine a single Defects4J bug id |
| not used |  | artifacts\pareto\suggestion-smoke.json | could not determine a single Defects4J bug id |
| used | Chart-1b | artifacts\pareto\chart1b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| used | Chart-20b | artifacts\pareto\chart20b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| used | Chart-26b | artifacts\pareto\chart26b_full_matrix_only_19-06-2026.json | usable per-seed raw benchmark artifact |
| not used | Chart-26b | artifacts\pareto\chart26b_full_19-06-2026.json | duplicate raw artifact for Chart-26b; selected chart26b_full_matrix_only_19-06-2026.json |
| used | Lang-20b | artifacts\pareto\lang20b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| not used | Lang-20b | artifacts\pareto\lang20b_one_seed_timing_codex.json | duplicate raw artifact for Lang-20b; selected lang20b_full_19-06-2026.json |
| not used | Lang-20b | artifacts\pareto\lang20b_smoke_codex.json | duplicate raw artifact for Lang-20b; selected lang20b_full_19-06-2026.json |
| used | Lang-3b | artifacts\pareto\lang3b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| not used | Lang-3b | artifacts\pareto\lang3b_3b_smoke_check.json | duplicate raw artifact for Lang-3b; selected lang3b_full_19-06-2026.json |
| not used | Lang-3b | artifacts\pareto\lang3b_3b_smoke_current.json | duplicate raw artifact for Lang-3b; selected lang3b_full_19-06-2026.json |
| used | Lang-5b | artifacts\pareto\lang5b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| not used | Lang-5b | artifacts\pareto\lang5b_smoke_check_2026-06-19.json | duplicate raw artifact for Lang-5b; selected lang5b_full_19-06-2026.json |
| used | Lang-6b | artifacts\pareto\lang6b_full_19-06-2026.json | usable per-seed raw benchmark artifact |
| not used | Lang-6b | artifacts\pareto\arqiea_safe_fix_smoke.json | duplicate raw artifact for Lang-6b; selected lang6b_full_19-06-2026.json |
| not used | Lang-6b | artifacts\pareto\lang6b_one_seed_timing.json | duplicate raw artifact for Lang-6b; selected lang6b_full_19-06-2026.json |
| not used | Lang-6b | artifacts\pareto\lang6b_smoke_check.json | duplicate raw artifact for Lang-6b; selected lang6b_full_19-06-2026.json |

## Interpretation
Across all valid bug/metric/baseline comparisons, AR-QIEA has 46 significant wins, 33 significant losses, and 26 non-significant comparisons.
These conclusions are valid only for the selected raw per-seed artifacts listed above. Aggregate-only reports and prior p-value-only files were audited but not used as Wilcoxon input.

## Limitations
MSR, CGCC, and ETR in the benchmark artifacts are the repository's recorded proxy/synthetic objective values, not independently regenerated real Major mutation, Java call graph, or measured timing data. Wilcoxon was not computed where raw seed-level records were unavailable, where algorithms were missing, or where seed sets could not be paired exactly.

## Reproduction Command
`python scripts/wilcoxon_statistics.py`
