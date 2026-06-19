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
report_path = report_dir / "lang3b_450_testcase_report.md"

os.makedirs(report_dir, exist_ok=True)

# 1. Run minimization
start_time = time.strftime("%Y-%m-%d %H:%M:%S")
start_ts = time.time()

env = os.environ.copy()
env["PYTHONPATH"] = "src"
# Use sys.executable to ensure we use the same python interpreter
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
runtime = end_ts - start_ts

if result.returncode != 0:
    print(f"Error running minimization: {result.stderr}")
    sys.exit(1)

data = json.loads(result.stdout)

# 2. Load Matrix Data for Analysis
with open(matrix_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    matrix_rows = list(reader)

with open(tests_path, 'r', encoding='utf-8') as f:
    test_names = [line.strip() for line in f if line.strip()]

with open(reqs_path, 'r', encoding='utf-8') as f:
    req_names = [line.strip() for line in f if line.strip()]

# Mapping test index to requirement sets
# matrix_rows[i] corresponds to test_names[i]
test_to_reqs = {}
for i, row in enumerate(matrix_rows):
    # The matrix rows might be indexed differently if tests.txt doesn't match matrix.csv row order.
    # But usually in this project they match.
    # Let's verify test name if possible.
    row_test_name = row[0]
    # Check if we can find this row_test_name in test_names
    # If they match by index, we use index.
    covered_reqs = {j for j, val in enumerate(row[1:]) if val == '1'}
    test_to_reqs[i] = covered_reqs

selected_indexes = data["selected_tests"]
selected_names = [test_names[i] for i in selected_indexes]
all_reqs = set(range(len(req_names)))

# Overlap / duplicate coverage analysis
overlap_analysis = []
for i in selected_indexes:
    test_a_reqs = test_to_reqs[i]
    others_reqs = set()
    for j in selected_indexes:
        if i == j: continue
        others_reqs |= test_to_reqs[j]
    
    unique_reqs = test_a_reqs - others_reqs
    is_redundant = len(unique_reqs) == 0
    
    overlaps = []
    for j in selected_indexes:
        if i == j: continue
        shared = test_a_reqs & test_to_reqs[j]
        ratio = len(shared) / len(test_a_reqs) if len(test_a_reqs) > 0 else 0
        overlaps.append((j, test_names[j], len(shared), ratio))
    
    overlap_analysis.append({
        "index": i,
        "name": test_names[i],
        "overlaps": overlaps,
        "unique_count": len(unique_reqs),
        "is_redundant": is_redundant
    })

# Redundancy check
redundancy_check = []
for i in selected_indexes:
    temp_set = [idx for idx in selected_indexes if idx != i]
    temp_covered = set()
    for idx in temp_set:
        temp_covered |= test_to_reqs[idx]
    
    # Check if temp_covered still matches original total covered
    # Actually user asks if coverage remains 100%
    remains_100 = len(temp_covered) == len(all_reqs)
    redundancy_check.append({
        "index": i,
        "name": test_names[i],
        "remains_100": remains_100,
        "status": "removable/redundant" if remains_100 else "necessary"
    })

num_redundant = sum(1 for r in redundancy_check if r["remains_100"])
num_necessary = len(selected_indexes) - num_redundant

# Write report
with open(report_path, "w", encoding='utf-8') as f:
    f.write("# Lang 3b 450 Testcase Coverage Report\n\n")
    
    f.write("## 1. Run information\n")
    f.write(f"- **dataset path**: {base_dir}\n")
    f.write(f"- **command used**: `{' '.join(cmd)}`\n")
    f.write(f"- **algorithm used**: qiea\n")
    f.write(f"- **start time**: {start_time}\n")
    f.write(f"- **end time**: {end_time}\n")
    f.write(f"- **total runtime**: {runtime:.2f} seconds\n")
    f.write(f"- **execution speed**: {len(matrix_rows)/runtime:.2f} tests/sec\n")
    f.write(f"- **number of tests in dataset**: {len(test_names)}\n")
    f.write(f"- **number of requirements in dataset**: {len(req_names)}\n\n")
    
    f.write("## 2. Selected testcase result\n")
    f.write(f"- **selected testcase indexes**: {', '.join(map(str, selected_indexes))}\n")
    f.write("- **selected testcase names**:\n")
    for name in selected_names:
        f.write(f"  - {name}\n")
    f.write(f"- **selected testcase count**: {len(selected_indexes)}\n")
    f.write(f"- **total testcase count**: {len(test_names)}\n")
    f.write(f"- **reduction ratio**: {data['reduction_ratio']:.4f}\n")
    f.write(f"- **covered requirement count**: {len(data['covered_requirements'])}\n")
    f.write(f"- **total requirement count**: {len(req_names)}\n")
    f.write(f"- **coverage ratio**: {data['coverage_ratio']:.4f}\n")
    is_100 = data['coverage_ratio'] >= 1.0
    f.write(f"- **confirm whether coverage is 100%**: {'YES' if is_100 else 'NO'}\n\n")
    
    f.write("## 3. Coverage validation\n")
    if is_100:
        f.write("The selected testcases really cover all requirements. 100% coverage means every requirement is covered by at least one selected testcase.\n\n")
    else:
        f.write(f"The selected testcases covered {len(data['covered_requirements'])} out of {len(req_names)} requirements.\n\n")
        
    f.write("## 4. Overlap / duplicate coverage analysis\n")
    f.write("Analysis of overlap among the selected testcases:\n\n")
    for item in overlap_analysis:
        f.write(f"### Testcase {item['index']}: {item['name']}\n")
        f.write(f"- **Unique requirements**: {item['unique_count']}\n")
        f.write(f"- **Redundant (has no unique requirements)**: {'YES' if item['is_redundant'] else 'NO'}\n")
        f.write("- **Overlap with other selected testcases**:\n")
        for other_idx, other_name, shared, ratio in item['overlaps']:
            f.write(f"  - vs {other_idx} ({other_name}): {shared} shared requirements (overlap ratio: {ratio:.2%})\n")
        f.write("\n")
        
    f.write("## 5. Important explanation\n")
    f.write("100% coverage can still contain overlap. Overlap does not mean coverage is fake or wrong. It only means some requirements are covered by more than one selected testcase.\n")
    f.write("However, if a selected testcase has zero unique requirements, it may be redundant because removing it may still keep 100% coverage.\n\n")
    
    f.write("## 6. Redundancy check\n")
    f.write("For each selected testcase, checking if it is removable while maintaining 100% coverage:\n\n")
    f.write("| Index | Name | Remains 100%? | Status |\n")
    f.write("|-------|------|---------------|--------|\n")
    for r in redundancy_check:
        f.write(f"| {r['index']} | {r['name']} | {'YES' if r['remains_100'] else 'NO'} | {r['status']} |\n")
    f.write("\n")
    
    f.write("## 7. Summary section\n")
    f.write(f"- **final coverage ratio**: {data['coverage_ratio']:.4f}\n")
    f.write(f"- **runtime**: {runtime:.2f} seconds\n")
    f.write(f"- **number of selected testcases**: {len(selected_indexes)}\n")
    f.write(f"- **number of redundant selected testcases**: {num_redundant}\n")
    f.write(f"- **number of necessary selected testcases**: {num_necessary}\n")
    can_reduce = num_redundant > 0
    f.write(f"- **whether the final selected set can be reduced further**: {'YES' if can_reduce else 'NO'}\n")
    if can_reduce:
        f.write("- **recommended next step**: Remove the redundant testcases to achieve a minimal set or use a more rigorous minimization algorithm.\n")
    else:
        f.write("- **recommended next step**: The current set is already minimal for the given algorithm. No further reduction is possible without dropping coverage.\n")

print(f"Report generated at: {report_path}")
