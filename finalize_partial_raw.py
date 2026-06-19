from pathlib import Path
import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime

OUT_DIR = Path("datasets/defects4j-relevant/Lang/3b_partial_450")
COVERAGE_DIR = OUT_DIR / "raw" / "coverage"

coverage_files = sorted(COVERAGE_DIR.glob("*.xml"))

if not coverage_files:
    raise SystemExit(f"No XML coverage files found in {COVERAGE_DIR}")

test_to_requirements = {}
all_requirements = set()
parse_errors = []

for xml_file in coverage_files:
    test_id = xml_file.stem
    covered = set()

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Cobertura-like XML:
        # <class filename="..." name="...">
        #   <lines>
        #     <line number="..." hits="..."/>
        #   </lines>
        for cls in root.iter("class"):
            filename = cls.attrib.get("filename") or cls.attrib.get("name") or "unknown"
            class_name = cls.attrib.get("name", filename)

            for line in cls.iter("line"):
                line_no = line.attrib.get("number")
                hits = line.attrib.get("hits", "0")

                try:
                    hit_count = int(float(hits))
                except ValueError:
                    hit_count = 0

                if line_no and hit_count > 0:
                    req = f"{class_name}:{line_no}"
                    covered.add(req)
                    all_requirements.add(req)

    except Exception as e:
        parse_errors.append({"file": str(xml_file), "error": str(e)})

    test_to_requirements[test_id] = covered

tests = sorted(test_to_requirements.keys())
requirements = sorted(all_requirements)

# tests.txt
with open(OUT_DIR / "tests.txt", "w", encoding="utf-8") as f:
    for t in tests:
        f.write(t + "\n")

# requirements.txt
with open(OUT_DIR / "requirements.txt", "w", encoding="utf-8") as f:
    for r in requirements:
        f.write(r + "\n")

# matrix.csv
with open(OUT_DIR / "matrix.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["test_id"] + requirements)

    for t in tests:
        covered = test_to_requirements[t]
        writer.writerow([t] + [1 if r in covered else 0 for r in requirements])

# metadata.json
metadata = {
    "project": "Lang",
    "bug_id": "3",
    "version": "b",
    "partial": True,
    "source": "raw/coverage XML files",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "num_tests": len(tests),
    "num_requirements": len(requirements),
    "num_coverage_files": len(coverage_files),
    "parse_error_count": len(parse_errors),
    "parse_errors": parse_errors[:20],
    "note": "This is a partial dataset generated after an interrupted run. It does not include all 2229 tests."
}

with open(OUT_DIR / "metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print("Generated partial dataset:")
print(f"- tests.txt: {len(tests)} tests")
print(f"- requirements.txt: {len(requirements)} requirements")
print(f"- matrix.csv: {len(tests)} rows x {len(requirements)} requirements")
print(f"- metadata.json")
if parse_errors:
    print(f"Warning: {len(parse_errors)} XML parse errors")
