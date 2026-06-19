import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


def run_cmd(cmd, cwd=None, timeout=None):
    p = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    return p.returncode, p.stdout, p.stderr


def d4j_export(work_dir, prop):
    code, out, err = run_cmd(["defects4j", "export", "-p", prop, "-w", str(work_dir)])
    if code != 0:
        raise RuntimeError(f"defects4j export failed for {prop}\nSTDOUT:\n{out}\nSTDERR:\n{err}")
    return out.strip()


def read_package(java_text):
    m = re.search(r"^\s*package\s+([A-Za-z0-9_.]+)\s*;", java_text, flags=re.MULTILINE)
    return m.group(1) if m else ""


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)
    return text


def find_test_methods(java_file):
    text = java_file.read_text(errors="ignore")
    package = read_package(text)
    clean = strip_comments(text)

    class_name = java_file.stem
    fqcn = f"{package}.{class_name}" if package else class_name

    methods = set()

    # JUnit 4 style:
    # @Test
    # public void methodName() { ... }
    junit4_pattern = re.compile(
        r"@Test\b[\s\S]{0,500}?"
        r"(?:public|protected|private)?\s+"
        r"(?:void|[A-Za-z0-9_<>\[\].]+)\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        flags=re.MULTILINE,
    )

    for m in junit4_pattern.finditer(clean):
        methods.add(m.group(1))

    # JUnit 3 style:
    # public void testSomething() { ... }
    junit3_pattern = re.compile(
        r"(?:public|protected)?\s+void\s+(test[A-Za-z0-9_]*)\s*\(",
        flags=re.MULTILINE,
    )

    for m in junit3_pattern.finditer(clean):
        methods.add(m.group(1))

    return [f"{fqcn}::{m}" for m in sorted(methods)]


def collect_tests(work_dir):
    rel_test_dir = d4j_export(work_dir, "dir.src.tests")
    test_root = work_dir / rel_test_dir

    if not test_root.exists():
        raise RuntimeError(f"Test source dir not found: {test_root}")

    tests = []
    for java_file in sorted(test_root.rglob("*Test.java")):
        tests.extend(find_test_methods(java_file))

    # Some old projects have test classes with names like XxxTestCase.java
    for java_file in sorted(test_root.rglob("*TestCase.java")):
        tests.extend(find_test_methods(java_file))

    tests = sorted(set(tests))
    return tests


def parse_coverage_requirements(xml_path, require_hits=True):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    reqs = set()

    for cls in root.findall(".//class"):
        cls_name = cls.attrib.get("name") or cls.attrib.get("filename") or "UNKNOWN_CLASS"
        cls_name = cls_name.replace("/", ".").replace("\\", ".")

        for line in cls.findall(".//line"):
            number = line.attrib.get("number")
            hits = int(line.attrib.get("hits", "0"))

            if number is None:
                continue

            if require_hits and hits <= 0:
                continue

            reqs.add(f"{cls_name}:{number}")

    return sorted(reqs)


def parse_covered_reqs(xml_path):
    return set(parse_coverage_requirements(xml_path, require_hits=True))


def safe_filename(test_id):
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_id)
    return s[:180]


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 make_lang3b_dataset.py <WORK_DIR> <OUT_DIR>")
        sys.exit(1)

    work_dir = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()

    raw_dir = out_dir / "raw"
    coverage_dir = raw_dir / "coverage"
    logs_dir = raw_dir / "logs"
    report_dir = out_dir / "report"

    coverage_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    max_tests_env = os.environ.get("MAX_TESTS", "450").strip()
    max_tests = int(max_tests_env) if max_tests_env else 450

    print(f"[1] Work dir: {work_dir}")
    print(f"[2] Out dir : {out_dir}")
    print(f"[3] MAX_TESTS={max_tests} ; use MAX_TESTS=0 for all tests")

    print("[4] Collecting test methods from test source files...")
    tests = collect_tests(work_dir)

    if max_tests > 0:
        tests = tests[:max_tests]

    tests_file = out_dir / "tests.txt"
    tests_file.write_text("\n".join(tests) + "\n", encoding="utf-8")

    print(f"    tests written: {len(tests)} -> {tests_file}")

    print("[5] Running full relevant coverage to build requirements.txt...")
    old_xml = work_dir / "coverage.xml"
    if old_xml.exists():
        old_xml.unlink()

    code, out, err = run_cmd(["defects4j", "coverage", "-w", str(work_dir), "-r"], timeout=None)

    (logs_dir / "coverage_relevant.stdout.log").write_text(out, encoding="utf-8", errors="ignore")
    (logs_dir / "coverage_relevant.stderr.log").write_text(err, encoding="utf-8", errors="ignore")

    if not old_xml.exists():
        raise RuntimeError(
            "coverage.xml was not created by defects4j coverage -r.\n"
            "Check raw/logs/coverage_relevant.stderr.log"
        )

    full_xml = coverage_dir / "coverage_relevant.xml"
    shutil.copy2(old_xml, full_xml)

    requirements = parse_coverage_requirements(full_xml, require_hits=True)

    req_file = out_dir / "requirements.txt"
    req_file.write_text("\n".join(requirements) + "\n", encoding="utf-8")

    print(f"    requirements written: {len(requirements)} -> {req_file}")

    print("[6] Running coverage for each test and building matrix.csv...")
    matrix_path = out_dir / "matrix.csv"
    skipped_path = raw_dir / "skipped_tests.txt"

    skipped = []
    rows_written = 0
    start = time.time()

    with matrix_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["test_id"] + requirements)

        for idx, test_id in enumerate(tests, start=1):
            if old_xml.exists():
                old_xml.unlink()

            print(f"[{idx:05d}/{len(tests):05d}] Coverage: {test_id}", flush=True)

            code, out, err = run_cmd(
                ["defects4j", "coverage", "-w", str(work_dir), "-t", test_id],
                timeout=None,
            )

            log_base = safe_filename(test_id)
            (logs_dir / f"{idx:05d}_{log_base}.stdout.log").write_text(out, encoding="utf-8", errors="ignore")
            (logs_dir / f"{idx:05d}_{log_base}.stderr.log").write_text(err, encoding="utf-8", errors="ignore")

            if not old_xml.exists():
                skipped.append({
                    "index": idx,
                    "test_id": test_id,
                    "reason": "coverage.xml not created",
                    "returncode": code,
                })
                continue

            dst_xml = coverage_dir / f"{idx:05d}_{log_base}.xml"
            shutil.copy2(old_xml, dst_xml)

            covered = parse_covered_reqs(dst_xml)
            row = [test_id] + [1 if req in covered else 0 for req in requirements]
            writer.writerow(row)
            rows_written += 1

    skipped_path.write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in skipped) + ("\n" if skipped else ""),
        encoding="utf-8",
    )

    elapsed = time.time() - start

    metadata = {
        "project": "Lang",
        "bug_id": 3,
        "version": "3b",
        "work_dir": str(work_dir),
        "out_dir": str(out_dir),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "max_tests": max_tests,
        "tests_total_in_tests_txt": len(tests),
        "tests_total_in_matrix": rows_written,
        "requirements_total": len(requirements),
        "skipped_tests_total": len(skipped),
        "matrix_format": "CSV header = test_id + requirements; cells are 0/1 coverage",
        "requirement_definition": "Covered source lines in Defects4J modified classes, based on defects4j coverage -r",
    }

    metadata_path = out_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    report = []
    report.append("# Lang 3b Dataset Report")
    report.append("")
    report.append(f"- Project: Lang")
    report.append(f"- Bug: 3b")
    report.append(f"- Tests in tests.txt: {len(tests)}")
    report.append(f"- Tests in matrix.csv: {rows_written}")
    report.append(f"- Requirements: {len(requirements)}")
    report.append(f"- Skipped tests: {len(skipped)}")
    report.append(f"- Runtime seconds: {elapsed:.2f}")
    report.append("")
    report.append("Files:")
    report.append("- tests.txt")
    report.append("- requirements.txt")
    report.append("- matrix.csv")
    report.append("- metadata.json")
    report.append("- raw/coverage/")
    report.append("- raw/logs/")
    report.append("")

    (report_dir / "summary.md").write_text("\n".join(report), encoding="utf-8")

    print("[7] DONE")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
