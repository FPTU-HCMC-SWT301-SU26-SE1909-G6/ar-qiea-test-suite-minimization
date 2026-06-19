import sys
import os
import json
import time
import subprocess
import csv
from pathlib import Path

# Setup paths
base_dir = Path("datasets/defects4j-relevant/Lang/3b_partial_450")
matrix_path = base_dir / "matrix.csv"
tests_path = base_dir / "tests.txt"
reqs_path = base_dir / "requirements.txt"
report_dir = base_dir / "report"
report_path = report_dir / "lang3b_450_testcase_report_pruned.md"

os.makedirs(report_dir, exist_ok=True)

# 1. Run minimization (Raw QIEA)
start_time = time.strftime("%Y-%m-%d %H:%M:%S")
start_ts = time.time()

env = os.environ.copy()
env["PYTHONPATH"] = "src"
cmd = [
    sys.executable, "-m", "quantum_testing.cli", "minimize",
    "--matrix", str(matrix_path),
    "--algorithm", "qiea",
    "--seed", "42"
]

print(f"Executing: {' '.join(cmd)}")
result = subprocess.run(cmd, env=env, capture_output=True, text=True)
end_ts = time.time()
end_time = time.strftime("%Y-%m-%d %H:%M:%S")
runtime_qiea = end_ts - start_ts

if result.returncode != 0:
    print(f"Error running minimization: {result.stderr}")
    sys.exit(1)

data = json.loads(result.stdout)
raw_selected = data["selected_tests"]

# 2. Load Matrix Data for Analysis
with open(matrix_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    matrix_rows = list(reader)

with open(tests_path, 'r', encoding='utf-8') as f:
    test_names = [line.strip() for line in f if line.strip()]

with open(reqs_path, 'r', encoding='utf-8') as f:
    req_names = [line.strip() for line in f if line.strip()]

test_to_reqs = {}
for i, row in enumerate(matrix_rows):
    test_to_reqs[i] = {j for j, val in enumerate(row[1:]) if val == '1'}

all_reqs = set(range(len(req_names)))

def get_coverage(test_indices):
    covered = set()
    for idx in test_indices:
        covered |= test_to_reqs[idx]
    return covered

coverage_before = len(get_coverage(raw_selected)) / len(all_reqs)

# 3. Iterative Post-Pruning
pruned_selected = list(raw_selected)
removed_tests = []

# Iteratively remove tests if coverage remains 100%
changed = True
while changed:
    changed = False
    for test_idx in list(pruned_selected):
        temp_set = [t for t in pruned_selected if t != test_idx]
        if len(get_coverage(temp_set)) == len(all_reqs):
            pruned_selected.remove(test_idx)
            removed_tests.append(test_idx)
            changed = True
            # Move to next iteration to stay safe, though greedy removal works here
            break

coverage_after = len(get_coverage(pruned_selected)) / len(all_reqs)
runtime_total = time.time() - start_ts

# 4. Analysis of pruned set
overlap_analysis = []
for i in pruned_selected:
    test_a_reqs = test_to_reqs[i]
    others_reqs = set()
    for j in pruned_selected:
        if i == j: continue
        others_reqs |= test_to_reqs[j]
    
    unique_reqs = test_a_reqs - others_reqs
    
    overlaps = []
    for j in pruned_selected:
        if i == j: continue
        shared = test_a_reqs & test_to_reqs[j]
        ratio = len(shared) / len(test_a_reqs) if len(test_a_reqs) > 0 else 0
        overlaps.append((j, test_names[j], len(shared), ratio))
    
    overlap_analysis.append({
        "index": i,
        "name": test_names[i],
        "overlaps": overlaps,
        "unique_count": len(unique_reqs)
    })

# Write report
with open(report_path, "w", encoding='utf-8') as f:
    f.write("# Lang 3b 450 Pruned Coverage Report\n\n")
    
    f.write("## 1. Run information\n")
    f.write(f"- **dataset path**: {base_dir}\n")
    f.write(f"- **command used**: `{' '.join(cmd)}`\n")
    f.write(f"- **algorithm used**: QIEA + Iterative Post-Pruning\n")
    f.write(f"- **start time**: {start_time}\n")
    f.write(f"- **end time**: {end_time}\n")
    f.write(f"- **total runtime (incl. pruning)**: {runtime_total:.2f} seconds\n")
    f.write(f"- **number of tests in dataset**: {len(test_names)}\n")
    f.write(f"- **number of requirements in dataset**: {len(req_names)}\n\n")
    
    f.write("## 2. Comparison: Raw vs Pruned\n")
    f.write("| Metric | Raw QIEA | Final Pruned |\n")
    f.write("|--------|----------|--------------|\n")
    f.write(f"| Selected Count | {len(raw_selected)} | {len(pruned_selected)} |\n")
    f.write(f"| Coverage Ratio | {coverage_before:.4f} | {coverage_after:.4f} |\n")
    f.write(f"| Reduction Ratio | {1 - len(raw_selected)/len(test_names):.4f} | {1 - len(pruned_selected)/len(test_names):.4f} |\n\n")

    f.write("## 3. Raw QIEA selected set\n")
    f.write(f"Count: {len(raw_selected)}\n\n")
    f.write("Indexes: " + ", ".join(map(str, raw_selected)) + "\n\n")

    f.write("## 4. Final pruned selected set (Necessary Tests)\n")
    f.write(f"Count: {len(pruned_selected)}\n\n")
    for idx in pruned_selected:
        f.write(f"- **{idx}**: {test_names[idx]}\n")
    f.write("\n")

    f.write("## 5. Removed redundant testcases\n")
    f.write(f"Count: {len(removed_tests)}\n\n")
    if removed_tests:
        f.write("| Index | Name |\n")
        f.write("|-------|------|\n")
        for idx in removed_tests:
            f.write(f"| {idx} | {test_names[idx]} |\n")
    else:
        f.write("No testcases were removed during pruning.\n")
    f.write("\n")

    f.write("## 6. Overlap Analysis (Pruned Set)\n")
    for item in overlap_analysis:
        f.write(f"### Testcase {item['index']}: {item['name']}\n")
        f.write(f"- **Unique requirements**: {item['unique_count']}\n")
        f.write("- **Overlap with other necessary testcases**:\n")
        if not item['overlaps']:
            f.write("  - (No other tests in pruned set)\n")
        for other_idx, other_name, shared, ratio in item['overlaps']:
            f.write(f"  - vs {other_idx} ({other_name}): {shared} shared requirements (overlap ratio: {ratio:.2%})\n")
        f.write("\n")

    f.write("## 7. Important explanation\n")
    f.write("100% coverage can still contain overlap. Overlap does not mean coverage is fake or wrong. It only means some requirements are covered by more than one selected testcase.\n")
    f.write("After iterative pruning, any remaining testcase with zero unique requirements would be redundant, but our pruning step ensures every remaining testcase is necessary to maintain 100% coverage.\n\n")

    f.write("## 8. Summary section\n")
    f.write(f"- **final coverage ratio**: {coverage_after:.4f}\n")
    f.write(f"- **number of raw selected testcases**: {len(raw_selected)}\n")
    f.write(f"- **number of pruned selected testcases**: {len(pruned_selected)}\n")
    f.write(f"- **number of removed redundant testcases**: {len(removed_tests)}\n")
    f.write(f"- **whether the final selected set can be reduced further**: NO (Verified by iterative pruning)\n")
    f.write("- **recommended next step**: Use this minimal set for regression testing to save resources while maintaining full coverage of the identified requirements.\n")

print(f"Report generated at: {report_path}")
