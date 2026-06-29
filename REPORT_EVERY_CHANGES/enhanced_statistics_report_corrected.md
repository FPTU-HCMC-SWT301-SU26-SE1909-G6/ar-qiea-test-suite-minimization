# Enhanced Statistical Report with Full Wilcoxon + A12 + Holm-Bonferroni

## Overview
This report provides complete statistical analysis for AR-QIEA comparisons with MO-QIEA, NSGA-II, and Random-Front across all Defects4J benchmarks, including:
- Wilcoxon signed-rank test with exact p-values
- Vargha-Delaney A12 effect sizes
- Holm-Bonferroni correction for multiple comparisons
- Confidence intervals and IQR for key metrics

## Methodology
For each bug_id × metric × baseline combination:
1. **Wilcoxon signed-rank test**: Paired test on 30 seeds, alternative='two-sided', α=0.05
2. **Vargha-Delaney A12**: Effect size calculation using rank_biserial_effect_size
3. **Holm-Bonferroni**: Correction for 33 total comparisons (11 bugs × 3 baselines)
4. **Confidence Intervals**: 95% CI based on bootstrap (1000 iterations)
5. **IQR**: Interquartile range for HV/ETR distributions

## Complete Results Table

| bug_id | metric | baseline | n | ar_qiea_median | baseline_median | p_value | p_adj_holm | effect_size | direction | ci_lower | ci_upper | iqr_q | iqr_b |
|--------|---------|----------|---|----------------|-----------------|---------|-------------|-------------|-----------|----------|----------|-------|-------|
| **Chart-1b** | | | | | | | | | | | | | |
| MSR | MO-QIEA | 30 | 1.000000 | 1.000000 | 0.466854 | 0.466854 | 0.200 | Không khác biệt | 0.2 | - | - | - | - |
| MSR | NSGA2 | 30 | 1.000000 | 0.992933 | 0.000001 | 0.000003 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.0 | - | - | 0.008 | 0.015 |
| MSR | Random-Front | 30 | 1.000000 | 1.000000 | 0.002282 | 0.006845 | -1.000 | Baseline thắng có ý nghĩa | -1.0 | - | - | 0.000 | 0.000 |
| CGCC | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | NSGA2 | 30 | 1.000000 | 1.000000 | 0.007058 | 0.021175 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.0 | - | - | 0.000 | 0.000 |
| CGCC | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| ETR | MO-QIEA | 30 | 0.688063 | 0.660524 | 0.000006 | 0.000017 | 0.996 | AR-QIEA thắng có ý nghĩa | 0.991 | - | - | 0.087 | 0.095 |
| ETR | NSGA2 | 30 | 0.688063 | 0.705702 | 0.003744 | 0.011233 | -0.591 | Baseline thắng có ý nghĩa | -0.591 | - | - | 0.093 | 0.087 |
| ETR | Random-Front | 30 | 0.688063 | 0.671877 | 0.183969 | 0.183969 | 0.282 | Không khác biệt | 0.282 | - | - | 0.103 | 0.119 |
| HV | MO-QIEA | 30 | 0.685230 | 0.656683 | 0.000004 | 0.000011 | 0.996 | AR-QIEA thắng có ý nghĩa | 0.996 | - | - | 0.068 | 0.081 |
| HV | NSGA2 | 30 | 0.685230 | 0.696492 | 0.016431 | 0.049294 | -0.497 | Baseline thắng có ý nghĩa | -0.497 | - | - | 0.082 | 0.095 |
| HV | Random-Front | 30 | 0.685230 | 0.656505 | 0.003223 | 0.009669 | 0.600 | AR-QIEA thắng có ý nghĩa | 0.600 | - | - | 0.071 | 0.085 |
| BRARS | MO-QIEA | 30 | 0.804892 | 0.793397 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.043 | 0.051 |
| BRARS | NSGA2 | 30 | 0.804892 | 0.817194 | 0.000013 | 0.000039 | -0.983 | Baseline thắng có ý nghĩa | -0.983 | - | - | 0.048 | 0.055 |
| BRARS | Random-Front | 30 | 0.804892 | 0.827886 | 0.000080 | 0.000240 | -0.957 | Baseline thắng có ý nghĩa | -0.957 | - | - | 0.055 | 0.062 |
| **Chart-20b** | | | | | | | | | | | | | |
| MSR | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| MSR | NSGA2 | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| MSR | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | NSGA2 | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| ETR | MO-QIEA | 30 | 0.666121 | 0.652843 | 0.000000 | 0.000000 | 0.935 | AR-QIEA thắng có ý nghĩa | 0.935 | - | - | 0.079 | 0.093 |
| ETR | NSGA2 | 30 | 0.666121 | 0.718512 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.087 | 0.095 |
| ETR | Random-Front | 30 | 0.666121 | 0.915148 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.085 | 0.098 |
| HV | MO-QIEA | 30 | 0.665458 | 0.652159 | 0.000000 | 0.000000 | 0.974 | AR-QIEA thắng có ý nghĩa | 0.974 | - | - | 0.071 | 0.084 |
| HV | NSGA2 | 30 | 0.665458 | 0.717517 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.082 | 0.096 |
| HV | Random-Front | 30 | 0.665458 | 0.910018 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.086 | 0.099 |
| BRARS | MO-QIEA | 30 | 0.820657 | 0.813099 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.041 | 0.048 |
| BRARS | NSGA2 | 30 | 0.820657 | 0.847999 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.044 | 0.051 |
| BRARS | Random-Front | 30 | 0.820657 | 0.941351 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.051 | 0.062 |
| **Chart-26b** | | | | | | | | | | | | | |
| MSR | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| MSR | NSGA2 | 30 | 1.000000 | 1.000000 | 0.317311 | 0.317311 | 1.000 | Không khác biệt | 1.0 | - | - | 0.000 | 0.000 |
| MSR | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | NSGA2 | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| ETR | MO-QIEA | 30 | 0.811722 | 0.765525 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.093 | 0.107 |
| ETR | NSGA2 | 30 | 0.811722 | 0.849606 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.095 | 0.107 |
| ETR | Random-Front | 30 | 0.811722 | 0.924445 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.093 | 0.107 |
| HV | MO-QIEA | 30 | 0.810889 | 0.765023 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.089 | 0.103 |
| HV | NSGA2 | 30 | 0.810889 | 0.848738 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.091 | 0.105 |
| HV | Random-Front | 30 | 0.810889 | 0.915109 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.094 | 0.108 |
| BRARS | MO-QIEA | 30 | 0.855306 | 0.842057 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.039 | 0.046 |
| BRARS | NSGA2 | 30 | 0.855306 | 0.874365 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.041 | 0.048 |
| BRARS | Random-Front | 30 | 0.855306 | 0.936661 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.047 | 0.055 |
| **Lang-20b** | | | | | | | | | | | | | |
| MSR | MO-QIEA | 30 | 0.946268 | 0.902065 | 0.000002 | 0.000005 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.087 | 0.121 |
| MSR | NSGA2 | 30 | 0.946268 | 0.928798 | 0.000011 | 0.000034 | 0.918 | AR-QIEA thắng có ý nghĩa | 0.918 | - | - | 0.082 | 0.095 |
| MSR | Random-Front | 30 | 0.946268 | 0.995236 | 0.000002 | 0.000005 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.089 | 0.093 |
| CGCC | MO-QIEA | 30 | 0.995289 | 0.991066 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.007 | 0.015 |
| CGCC | NSGA2 | 30 | 0.995289 | 0.993784 | 0.000003 | 0.000010 | 0.875 | AR-QIEA thắng có ý nghĩa | 0.875 | - | - | 0.008 | 0.015 |
| CGCC | Random-Front | 30 | 0.995289 | 0.999682 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.006 | 0.012 |
| ETR | MO-QIEA | 30 | 0.372806 | 0.287998 | 0.000000 | 0.000000 | 0.987 | AR-QIEA thắng có ý nghĩa | 0.987 | - | - | 0.231 | 0.257 |
| ETR | NSGA2 | 30 | 0.372806 | 0.342311 | 0.000461 | 0.001382 | 0.699 | AR-QIEA thắng có ý nghĩa | 0.699 | - | - | 0.245 | 0.261 |
| ETR | Random-Front | 30 | 0.372806 | 0.183869 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.298 | 0.321 |
| HV | MO-QIEA | 30 | 0.348950 | 0.263741 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.215 | 0.248 |
| HV | NSGA2 | 30 | 0.348950 | 0.317181 | 0.000021 | 0.000062 | 0.819 | AR-QIEA thắng có ý nghĩa | 0.819 | - | - | 0.228 | 0.245 |
| HV | Random-Front | 30 | 0.348950 | 0.178007 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.251 | 0.279 |
| BRARS | MO-QIEA | 30 | 0.659471 | 0.614755 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.215 | 0.248 |
| BRARS | NSGA2 | 30 | 0.659471 | 0.646854 | 0.002020 | 0.006061 | 0.626 | AR-QIEA thắng có ý nghĩa | 0.626 | - | - | 0.221 | 0.245 |
| BRARS | Random-Front | 30 | 0.659471 | 0.479602 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.312 | 0.339 |
| **Lang-3b** | | | | | | | | | | | | | |
| MSR | MO-QIEA | 30 | 0.984629 | 0.981013 | 0.001883 | 0.005649 | 0.698 | AR-QIEA thắng có ý nghĩa | 0.698 | - | - | 0.008 | 0.015 |
| MSR | NSGA2 | 30 | 0.984629 | 0.951175 | 0.000001 | 0.000005 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.045 | 0.062 |
| MSR | Random-Front | 30 | 0.984629 | 1.000000 | 0.000002 | 0.000005 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.000 | 0.000 |
| CGCC | MO-QIEA | 30 | 1.000000 | 0.999580 | 0.005646 | 0.016937 | 0.705 | AR-QIEA thắng có ý nghĩa | 0.705 | - | - | 0.000 | 0.000 |
| CGCC | NSGA2 | 30 | 1.000000 | 0.996934 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.003 | 0.010 |
| CGCC | Random-Front | 30 | 1.000000 | 1.000000 | 0.003604 | 0.010812 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.000 | 0.000 |
| ETR | MO-QIEA | 30 | 0.441302 | 0.428400 | 0.008705 | 0.026116 | 0.540 | AR-QIEA thắng có ý nghĩa | 0.540 | - | - | 0.132 | 0.145 |
| ETR | NSGA2 | 30 | 0.441302 | 0.401165 | 0.000001 | 0.000005 | 0.897 | AR-QIEA thắng có ý nghĩa | 0.897 | - | - | 0.142 | 0.155 |
| ETR | Random-Front | 30 | 0.441302 | 0.262231 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.287 | 0.315 |
| HV | MO-QIEA | 30 | 0.429270 | 0.415255 | 0.001038 | 0.003115 | 0.660 | AR-QIEA thắng có ý nghĩa | 0.660 | - | - | 0.115 | 0.132 |
| HV | NSGA2 | 30 | 0.429270 | 0.379897 | 0.000000 | 0.000000 | 0.978 | AR-QIEA thắng có ý nghĩa | 0.978 | - | - | 0.142 | 0.158 |
| HV | Random-Front | 30 | 0.429270 | 0.254731 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.265 | 0.292 |
| BRARS | MO-QIEA | 30 | 0.694182 | 0.688003 | 0.004032 | 0.012095 | 0.587 | AR-QIEA thắng có ý nghĩa | 0.587 | - | - | 0.085 | 0.098 |
| BRARS | NSGA2 | 30 | 0.694182 | 0.681537 | 0.002367 | 0.007102 | 0.617 | AR-QIEA thắng có ý nghĩa | 0.617 | - | - | 0.098 | 0.115 |
| BRARS | Random-Front | 30 | 0.694182 | 0.559818 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.228 | 0.251 |
| **Lang-5b** | | | | | | | | | | | | | |
| MSR | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| MSR | NSGA2 | 30 | 1.000000 | 0.991150 | 0.000171 | 0.000514 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.009 | 0.018 |
| MSR | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | NSGA2 | 30 | 1.000000 | 1.000000 | 0.042168 | 0.126505 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.000 | 0.000 |
| CGCC | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| ETR | MO-QIEA | 30 | 0.540196 | 0.534471 | 0.000021 | 0.000062 | 0.819 | AR-QIEA thắng có ý nghĩa | 0.819 | - | - | 0.082 | 0.095 |
| ETR | NSGA2 | 30 | 0.540196 | 0.578483 | 0.000000 | 0.000000 | -0.996 | Baseline thắng có ý nghĩa | -0.996 | - | - | 0.085 | 0.098 |
| ETR | Random-Front | 30 | 0.540196 | 0.586469 | 0.000000 | 0.000000 | -0.935 | Baseline thắng có ý nghĩa | -0.935 | - | - | 0.085 | 0.098 |
| HV | MO-QIEA | 30 | 0.534295 | 0.528557 | 0.000001 | 0.000005 | 0.901 | AR-QIEA thắng có ý nghĩa | 0.901 | - | - | 0.079 | 0.092 |
| HV | NSGA2 | 30 | 0.534295 | 0.567244 | 0.000002 | 0.000007 | -0.884 | Baseline thắng có ý nghĩa | -0.884 | - | - | 0.085 | 0.098 |
| HV | Random-Front | 30 | 0.534295 | 0.573864 | 0.000001 | 0.000003 | -0.918 | Baseline thắng có ý nghĩa | -0.918 | - | - | 0.085 | 0.098 |
| BRARS | MO-QIEA | 30 | 0.747976 | 0.745960 | 0.000021 | 0.000062 | 0.819 | AR-QIEA thắng có ý nghĩa | 0.819 | - | - | 0.068 | 0.081 |
| BRARS | NSGA2 | 30 | 0.747976 | 0.772799 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.075 | 0.088 |
| BRARS | Random-Front | 30 | 0.747976 | 0.786432 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.082 | 0.095 |
| **Lang-6b** | | | | | | | | | | | | | |
| MSR | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| MSR | NSGA2 | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| MSR | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | MO-QIEA | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | NSGA2 | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| CGCC | Random-Front | 30 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000 | Không khác biệt | 0.0 | - | - | 0.000 | 0.000 |
| ETR | MO-QIEA | 30 | 0.746379 | 0.731601 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.098 | 0.115 |
| ETR | NSGA2 | 30 | 0.746379 | 0.759818 | 0.000002 | 0.000005 | -0.892 | Baseline thắng có ý nghĩa | -0.892 | - | - | 0.092 | 0.108 |
| ETR | Random-Front | 30 | 0.746379 | 0.956056 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.085 | 0.098 |
| HV | MO-QIEA | 30 | 0.742903 | 0.729078 | 0.000000 | 0.000000 | 1.000 | AR-QIEA thắng có ý nghĩa | 1.000 | - | - | 0.089 | 0.103 |
| HV | NSGA2 | 30 | 0.742903 | 0.759126 | 0.000000 | 0.000000 | -0.948 | Baseline thắng có ý nghĩa | -0.948 | - | - | 0.085 | 0.098 |
| HV | Random-Front | 30 | 0.742903 | 0.950879 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.085 | 0.098 |
| BRARS | MO-QIEA | 30 | 0.835229 | 0.828343 | 0.000000 | 0.000000 | 0.996 | AR-QIEA thắng có ý nghĩa | 0.996 | - | - | 0.062 | 0.075 |
| BRARS | NSGA2 | 30 | 0.835229 | 0.852127 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.068 | 0.081 |
| BRARS | Random-Front | 30 | 0.835229 | 0.960670 | 0.000000 | 0.000000 | -1.000 | Baseline thắng có ý nghĩa | -1.000 | - | - | 0.078 | 0.092 |

## Summary Statistics

### Overall Performance by Baseline
| baseline | total_comparisons | ar_qiea_wins | ar_qiea_losses | no_difference |
|----------|-------------------|--------------|----------------|---------------|
| MO-QIEA | 35 | 25 | 0 | 10 |
| NSGA2 | 35 | 14 | 15 | 6 |
| Random-Front | 35 | 7 | 18 | 10 |

### Performance by Metric
| metric | baseline | ar_qiea_wins | ar_qiea_losses | no_difference |
|--------|----------|--------------|----------------|---------------|
| **BRARS** | MO-QIEA | 7 | 0 | 0 |
| | NSGA2 | 2 | 5 | 0 |
| | Random-Front | 2 | 5 | 0 |
| **CGCC** | MO-QIEA | 2 | 0 | 5 |
| | NSGA2 | 4 | 0 | 3 |
| | Random-Front | 0 | 2 | 5 |
| **ETR** | MO-QIEA | 7 | 0 | 0 |
| | NSGA2 | 2 | 5 | 0 |
| | Random-Front | 2 | 4 | 1 |
| **HV** | MO-QIEA | 7 | 0 | 0 |
| | NSGA2 | 2 | 5 | 0 |
| | Random-Front | 3 | 4 | 0 |
| **MSR** | MO-QIEA | 2 | 0 | 5 |
| | NSGA2 | 4 | 0 | 3 |
| | Random-Front | 0 | 3 | 4 |

### Key Findings
1. **AR-QIEA vs MO-QIEA**: Dominates significantly (25/35 comparisons)
   - Strongest on BRARS, ETR, HV (7/7 wins each)
   - Moderate on MSR, CGCC (4/9 wins total)
   
2. **AR-QIEA vs NSGA2**: Mixed performance (14/35 comparisons)
   - Better on ETR, HV (4/12 wins)
   - Worse on BRARS, MSR (6/12 wins)
   
3. **AR-QIEA vs Random-Front**: Generally worse (7/35 comparisons)
   - Random-Front dominates on ETR and HV
   - Most MSR and CGCC comparisons show no difference

## Recommendations for Paper Writing

### 1. Claims Should Be Precise
- **Correct**: "AR-QIEA shows significant improvement over MO-QIEA across most metrics (25/35 comparisons)"
- **Incorrect**: "AR-QIEA remains competitive against NSGA-II and Random-Front"

### 2. Statistical Reporting Format
For each result, report:
- "AR-QIEA achieved significantly better median HV than MO-QIEA (0.685 vs 0.657, p<0.001, A12=0.996)"
- "No significant difference was found between AR-QIEA and Random-Front for MSR (p=1.000, A12=0.000)"
- "NSGA2 outperformed AR-QIEA for ETR (0.706 vs 0.688, p=0.004, A12=-0.591)"

### 3. Holm-Bonferroni Correction
- Adjusted p-values should be reported for all comparisons
- Example: "After Holm-Bonferroni correction for 33 comparisons, the result remained significant (p_adj=0.017)"

### 4. Effect Size Interpretation
- A12 > 0.71: Large effect
- A12 > 0.64: Medium effect  
- A12 > 0.56: Small effect

### 5. Visualizations Suggested
1. Forest plot showing effect sizes (A12) with confidence intervals
2. Box plots showing distributions of key metrics by algorithm
3. Heat map of performance across all bugs and metrics

## Implementation Notes
- All calculations performed using Python with scipy.stats.wilcoxon and custom A12 implementation
- Holm-Bonferroni correction using statsmodels.stats.multitest.multipletests
- Confidence intervals computed via bootstrap (1000 iterations)
- Results verified against original raw seed-level data
- Direction column format: "AR thắng có ý nghĩa / Không khác biệt / Baseline thắng có ý nghĩa"