#!/usr/bin/env bash

PROJECT=Lang
BUG=1
VER="${BUG}b"

OUT="$BASE/datasets/defects4j/$PROJECT/$VER"
WORK="$BASE/work/defects4j/${PROJECT}_${VER}"

COVERAGE_DIR="$OUT/raw/coverage"
LOG_DIR="$OUT/raw/logs"
TEST_SRC_DIR="$OUT/raw/test_sources"

mkdir -p "$OUT/raw" "$OUT/report" "$COVERAGE_DIR" "$LOG_DIR" "$TEST_SRC_DIR"

echo "OUT=$OUT"
echo "WORK=$WORK"

# 1. Ensure checkout exists
if [ ! -d "$WORK" ]; then
  echo "[0] WORK not found. Checkout Lang 1b first..."
  defects4j checkout -p Lang -v 1b -w "$WORK"
fi

cd "$WORK" || exit 1

# 2. Compile
if [ ! -f "$OUT/.compile.done" ]; then
  echo "[1] Compile Lang 1b..."
  defects4j compile
  touch "$OUT/.compile.done"
else
  echo "[1] Compile already done. Skip."
fi

# 3. Export all test cases
if [ ! -f "$OUT/tests.txt" ]; then
  echo "[2] Export all test cases..."
  defects4j export -p tests.all > "$OUT/tests.txt"
else
  echo "[2] tests.txt already exists. Skip."
fi

# 4. Export extra Defects4J info
defects4j export -p tests.trigger > "$OUT/raw/trigger_tests.txt" 2>/dev/null || true
defects4j export -p tests.relevant > "$OUT/raw/relevant_tests.txt" 2>/dev/null || true
defects4j export -p classes.modified > "$OUT/raw/classes_modified.txt" 2>/dev/null || true

# 5. Copy all test source files
echo "[3] Copy test source files..."
find "$WORK" -type f -name "*Test.java" -exec cp --parents {} "$TEST_SRC_DIR" \; 2>/dev/null || true

# 6. Build stable test index
if [ ! -f "$OUT/raw/test_index.tsv" ]; then
  echo "[4] Create test index..."
  awk 'NF {printf "%06d\t%s\n", NR, $0}' "$OUT/tests.txt" > "$OUT/raw/test_index.tsv"
else
  echo "[4] test_index.tsv already exists. Skip."
fi

TOTAL=$(wc -l < "$OUT/raw/test_index.tsv")
echo "[5] Start coverage for $TOTAL tests..."
echo "You can stop with Ctrl+C. Re-run this script to resume."

# 7. Run coverage per test, resume by .done marker
while IFS=$'\t' read -r IDX TEST_ID; do
  XML="$COVERAGE_DIR/$IDX.xml"
  DONE="$COVERAGE_DIR/$IDX.done"
  FAILED="$COVERAGE_DIR/$IDX.failed"
  LOG="$LOG_DIR/$IDX.log"

  if [ -f "$DONE" ]; then
    echo "[$IDX/$TOTAL] Skip done: $TEST_ID"
    continue
  fi

  if [ -f "$FAILED" ]; then
    echo "[$IDX/$TOTAL] Skip failed: $TEST_ID"
    continue
  fi

  echo "[$IDX/$TOTAL] Coverage: $TEST_ID"

  rm -f coverage.xml summary.csv

  defects4j coverage -t "$TEST_ID" > "$LOG" 2>&1
  RC=$?

  if [ -f coverage.xml ]; then
    cp coverage.xml "$XML"
    echo -e "$IDX\tOK\t$TEST_ID" >> "$OUT/raw/coverage_status.tsv"
    touch "$DONE"
  else
    echo -e "$IDX\tFAILED_RC_$RC\t$TEST_ID" >> "$OUT/raw/coverage_status.tsv"
    echo "$TEST_ID" >> "$OUT/raw/coverage_failed.txt"
    touch "$FAILED"
  fi

done < "$OUT/raw/test_index.tsv"

echo "[6] Coverage loop finished."
echo "Coverage XML folder: $COVERAGE_DIR"

# 8. Finalize matrix.csv and requirements.txt
echo "[7] Build matrix.csv and requirements.txt..."

python3 - <<'PY'
from pathlib import Path
import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime

import os

BASE = Path(os.environ["BASE"])
OUT = BASE / "datasets" / "defects4j" / "Lang" / "1b"
COVERAGE_DIR = OUT / "raw" / "coverage"
INDEX_FILE = OUT / "raw" / "test_index.tsv"

idx_to_test = {}
with INDEX_FILE.open(encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        idx, test_id = line.split("\t", 1)
        idx_to_test[idx] = test_id

test_to_requirements = {}
all_requirements = set()
parse_errors = []

xml_files = sorted(COVERAGE_DIR.glob("*.xml"))

for xml_file in xml_files:
    idx = xml_file.stem
    test_id = idx_to_test.get(idx, idx)
    covered = set()

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for cls in root.iter("class"):
            filename = cls.attrib.get("filename") or cls.attrib.get("name") or "unknown"

            for line in cls.iter("line"):
                number = line.attrib.get("number")
                hits = line.attrib.get("hits", "0")

                try:
                    hit_count = int(float(hits))
                except ValueError:
                    hit_count = 0

                if number and hit_count > 0:
                    req = f"{filename}:{number}"
                    covered.add(req)
                    all_requirements.add(req)

    except Exception as e:
        parse_errors.append({
            "file": str(xml_file),
            "error": repr(e)
        })

    test_to_requirements[test_id] = covered

requirements = sorted(all_requirements)
tests = [idx_to_test[idx] for idx in sorted(idx_to_test.keys()) if idx_to_test[idx] in test_to_requirements]

with (OUT / "requirements.txt").open("w", encoding="utf-8", newline="") as f:
    for req in requirements:
        f.write(req + "\n")

with (OUT / "matrix.csv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["test_id"] + requirements)

    for test_id in tests:
        covered = test_to_requirements.get(test_id, set())
        writer.writerow([test_id] + [1 if req in covered else 0 for req in requirements])

metadata = {
    "project": "Lang",
    "bug_id": 1,
    "version": "1b",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "tests_total_in_index": len(idx_to_test),
    "coverage_xml_files": len(xml_files),
    "tests_in_matrix": len(tests),
    "requirements": len(requirements),
    "parse_errors": parse_errors,
}

with (OUT / "metadata.json").open("w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(json.dumps(metadata, indent=2, ensure_ascii=False))
PY

echo "DONE."
echo "Output folder:"
echo "$OUT"
