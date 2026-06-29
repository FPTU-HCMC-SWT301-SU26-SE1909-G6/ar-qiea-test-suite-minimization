# Paper-Ready Wilcoxon Effect Table for HV

## Methodology Note

This table summarizes the HV-only pairwise comparison between AR-QIEA and each baseline algorithm. Wilcoxon p-values and Holm-adjusted p-values are taken from `REPORT_EVERY_CHANGES/enhanced_statistics_report_corrected.md`. The Effect column reports true Vargha-Delaney \(A_{12}\), computed separately from the existing raw per-seed HV distributions using the standard all-pairs definition:

\[
A_{12} = P(\mathrm{AR\mbox{-}QIEA} > \mathrm{baseline}) + 0.5 P(\mathrm{AR\mbox{-}QIEA} = \mathrm{baseline}).
\]

The \(A_{12}\) values were computed from the 30 available HV seed values for AR-QIEA and the corresponding 30 HV seed values for each baseline, yielding 900 pairwise comparisons per row. No \(A_{12}=(r_{rb}+1)/2\) conversion was applied.

The p-values remain from paired Wilcoxon signed-rank tests over matched random seeds. \(A_{12}\) is reported as a supplementary distributional effect size. Outcomes are assigned using the adjusted p-value and \(A_{12}\): \(p_{\mathrm{Holm}} < 0.05\) with \(A_{12} > 0.5\) is reported as "AR-QIEA wins"; \(p_{\mathrm{Holm}} < 0.05\) with \(A_{12} < 0.5\) is reported as "Baseline wins"; \(p_{\mathrm{Holm}} \ge 0.05\) is reported as "No significant difference".

Raw/statistical sources used:

- `REPORT_EVERY_CHANGES/enhanced_statistics_report_corrected.md`
- `REPORT_EVERY_CHANGES/26-06-2026/statistics/wilcoxon_report.md`
- `scripts/wilcoxon_statistics.py`
- `artifacts/pareto/chart1b_full_19-06-2026.json`
- `artifacts/pareto/chart20b_full_19-06-2026.json`
- `artifacts/pareto/chart26b_full_matrix_only_19-06-2026.json`
- `artifacts/pareto/lang20b_full_19-06-2026.json`
- `artifacts/pareto/lang3b_full_19-06-2026.json`
- `artifacts/pareto/lang5b_full_19-06-2026.json`
- `artifacts/pareto/lang6b_full_19-06-2026.json`

Holm correction family: this table preserves the `p_adj_holm` values as reported in the corrected statistical report. The existing report states a 33-comparison Holm correction, but the HV table contains 21 HV comparisons within a broader 105-row all-metric report; therefore, the correction family should be verified before final publication if the adjusted p-values are regenerated.

## Paper-Ready Markdown Table

| Dataset | Baseline | p-value | \(p_{\mathrm{Holm}}\) | Effect (\(A_{12}\)) | Outcome |
|---|---|---:|---:|---:|---|
| Chart-1b | MO-QIEA | 4e-06 | 1.1e-05 | 0.943 | AR-QIEA wins |
| Chart-1b | NSGA-II | 0.016 | 0.049 | 0.282 | Baseline wins |
| Chart-1b | Random-Front | 0.003 | 0.010 | 0.736 | AR-QIEA wins |
| Chart-20b | MO-QIEA | <1e-6 | <1e-6 | 0.961 | AR-QIEA wins |
| Chart-20b | NSGA-II | <1e-6 | <1e-6 | 0.000 | Baseline wins |
| Chart-20b | Random-Front | <1e-6 | <1e-6 | 0.000 | Baseline wins |
| Chart-26b | MO-QIEA | <1e-6 | <1e-6 | 0.998 | AR-QIEA wins |
| Chart-26b | NSGA-II | <1e-6 | <1e-6 | 0.037 | Baseline wins |
| Chart-26b | Random-Front | <1e-6 | <1e-6 | 0.000 | Baseline wins |
| Lang-20b | MO-QIEA | <1e-6 | <1e-6 | 0.986 | AR-QIEA wins |
| Lang-20b | NSGA-II | 2.1e-05 | 6.2e-05 | 0.831 | AR-QIEA wins |
| Lang-20b | Random-Front | <1e-6 | <1e-6 | 1.000 | AR-QIEA wins |
| Lang-3b | MO-QIEA | 0.001 | 0.003 | 0.792 | AR-QIEA wins |
| Lang-3b | NSGA-II | <1e-6 | <1e-6 | 0.966 | AR-QIEA wins |
| Lang-3b | Random-Front | <1e-6 | <1e-6 | 1.000 | AR-QIEA wins |
| Lang-5b | MO-QIEA | 1e-06 | 5e-06 | 0.821 | AR-QIEA wins |
| Lang-5b | NSGA-II | 2e-06 | 7e-06 | 0.132 | Baseline wins |
| Lang-5b | Random-Front | 1e-06 | 3e-06 | 0.128 | Baseline wins |
| Lang-6b | MO-QIEA | <1e-6 | <1e-6 | 0.994 | AR-QIEA wins |
| Lang-6b | NSGA-II | <1e-6 | <1e-6 | 0.110 | Baseline wins |
| Lang-6b | Random-Front | <1e-6 | <1e-6 | 0.000 | Baseline wins |

## LaTeX Table

```latex
\begin{table}[t]
\centering
\caption{Pairwise Wilcoxon signed-rank test results for HV between AR-QIEA and baseline algorithms. Holm-adjusted $p$-values are reported together with the Vargha-Delaney $A_{12}$ effect size computed from raw HV seed distributions.}
\label{tab:wilcoxon-hv-summary}
\scriptsize
\begin{tabular}{llcccc}
\hline
\textbf{Dataset} & \textbf{Baseline} & \textbf{$p$-value} & \textbf{$p_{\mathrm{Holm}}$} & \textbf{Effect} & \textbf{Outcome} \\
\hline
Chart-1b & MO-QIEA & 4e-06 & 1.1e-05 & 0.943 & AR-QIEA wins \\
Chart-1b & NSGA-II & 0.016 & 0.049 & 0.282 & Baseline wins \\
Chart-1b & Random-Front & 0.003 & 0.010 & 0.736 & AR-QIEA wins \\
Chart-20b & MO-QIEA & <1e-6 & <1e-6 & 0.961 & AR-QIEA wins \\
Chart-20b & NSGA-II & <1e-6 & <1e-6 & 0.000 & Baseline wins \\
Chart-20b & Random-Front & <1e-6 & <1e-6 & 0.000 & Baseline wins \\
Chart-26b & MO-QIEA & <1e-6 & <1e-6 & 0.998 & AR-QIEA wins \\
Chart-26b & NSGA-II & <1e-6 & <1e-6 & 0.037 & Baseline wins \\
Chart-26b & Random-Front & <1e-6 & <1e-6 & 0.000 & Baseline wins \\
Lang-20b & MO-QIEA & <1e-6 & <1e-6 & 0.986 & AR-QIEA wins \\
Lang-20b & NSGA-II & 2.1e-05 & 6.2e-05 & 0.831 & AR-QIEA wins \\
Lang-20b & Random-Front & <1e-6 & <1e-6 & 1.000 & AR-QIEA wins \\
Lang-3b & MO-QIEA & 0.001 & 0.003 & 0.792 & AR-QIEA wins \\
Lang-3b & NSGA-II & <1e-6 & <1e-6 & 0.966 & AR-QIEA wins \\
Lang-3b & Random-Front & <1e-6 & <1e-6 & 1.000 & AR-QIEA wins \\
Lang-5b & MO-QIEA & 1e-06 & 5e-06 & 0.821 & AR-QIEA wins \\
Lang-5b & NSGA-II & 2e-06 & 7e-06 & 0.132 & Baseline wins \\
Lang-5b & Random-Front & 1e-06 & 3e-06 & 0.128 & Baseline wins \\
Lang-6b & MO-QIEA & <1e-6 & <1e-6 & 0.994 & AR-QIEA wins \\
Lang-6b & NSGA-II & <1e-6 & <1e-6 & 0.110 & Baseline wins \\
Lang-6b & Random-Front & <1e-6 & <1e-6 & 0.000 & Baseline wins \\
\hline
\end{tabular}
\footnotesize
\par\medskip
\emph{Note.} Effect denotes Vargha-Delaney $A_{12}=P(\mathrm{AR\mbox{-}QIEA}>\mathrm{baseline})+0.5P(\mathrm{AR\mbox{-}QIEA}=\mathrm{baseline})$, computed from raw HV seed distributions. Values above 0.5 favor AR-QIEA, values below 0.5 favor the baseline, and 0.5 indicates stochastic parity. The Wilcoxon tests remain paired by matched seed; $A_{12}$ is reported as a supplementary distributional effect size.
\end{table}
```

## Effect Footnote

Effect is true Vargha-Delaney \(A_{12}\), computed from the raw HV values using all pairwise AR-QIEA-versus-baseline seed comparisons. Values range from 0 to 1. Values above 0.5 favor AR-QIEA, values below 0.5 favor the baseline, and 0.5 indicates stochastic parity.

## Audit Note

Effect type used here: true Vargha-Delaney \(A_{12}\). The earlier signed paired rank-biserial values from the corrected statistical report were not used as Effect values in this table. No \(A_{12}=(r_{rb}+1)/2\) conversion was applied.
