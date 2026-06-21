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
from types import SimpleNamespace


PROJECT = "Chart"
BUG_ID = 26
VERSION = "26b"


def run_cmd(cmd, cwd=None, timeout=None):
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return SimpleNamespace(
            returncode=124,
            stdout=e.stdout or "",
            stderr=(e.stderr or "") + "\nTIMEOUT\n",
        )


def d4j_export(work_dir, prop):
    p = run_cmd(["defects4j", "export", "-p", prop, "-w", str(work_dir)])
    if p.returncode != 0:
        return ""
    return p.stdout.strip()


def safe_filename(text):
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    return text[:180]


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)
    return text


def parse_package(java_text):
    m = re.search(r"^\s*package\s+([A-Za-z0-9_.]+)\s*;", java_text, re.MULTILINE)
    return m.group(1) if m else ""


def find_test_methods(java_file):
    text = java_file.read_text(errors="ignore")
    package = parse_package(text)
    class_name = java_file.stem
    fqcn = f"{package}.{class_name}" if package else class_name

    clean = strip_comments(text)
    methods = set()

    junit4_pattern = re.compile(
        r"@Test\b[\s\S]{0,700}?"
        r"(?:public|protected|private)?\s+"
        r"(?:void|[A-Za-z0-9_<>\[\].]+)\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        re.MULTILINE,
    )

    junit3_pattern = re.compile(
        r"(?:public|protected)?\s+void\s+(test[A-Za-z0-9_]*)\s*\(",
        re.MULTILINE,
    )

    for m in junit4_pattern.finditer(clean):
        methods.add(m.group(1))

    for m in junit3_pattern.finditer(clean):
        methods.add(m.group(1))

    return [f"{fqcn}::{method}" for method in sorted(methods)]


def collect_tests_from_export(work_dir):
    raw = d4j_export(work_dir, "tests.all")
    tests = []

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        if "::" in line:
            tests.append(line)

    return sorted(set(tests))


def collect_tests_from_source(work_dir):
    test_dir = d4j_export(work_dir, "dir.src.tests")
    if not test_dir:
        raise RuntimeError("Cannot export dir.src.tests from Defects4J.")

    test_root = work_dir / test_dir
    if not test_root.exists():
        raise RuntimeError(f"Test source folder not found: {test_root}")

    tests = []

    for java_file in sorted(test_root.rglob("*.java")):
        tests.extend(find_test_methods(java_file))

    return sorted(set(tests))


def collect_tests(work_dir):
    tests = collect_tests_from_export(work_dir)

    if tests:
        print(f"Collected tests from defects4j export tests.all: {len(tests)}")
        return tests

    tests = collect_tests_from_source(work_dir)
    print(f"Collected tests by parsing source files: {len(tests)}")
    return tests


def normalize_class_name(value):
    value = value or ""
    value = value.replace("/", ".").replace("\\", ".")
    value = re.sub(r"\.java$", "", value)
    return value.strip(".")


def load_modified_classes(out_dir):
    path = out_dir / "raw" / "classes.modified.txt"
    if not path.exists():
        return set()

    result = set()

    for line in path.read_text(errors="ignore").splitlines():
        line = normalize_class_name(line.strip())
        if line:
            result.add(line)

    return result


def class_matches_modified(class_name, filename, modified_classes):
    if not modified_classes:
        return True

    class_name = normalize_class_name(class_name)
    filename = normalize_class_name(filename)

    if class_name in modified_classes:
        return True

    if filename in modified_classes:
        return True

    simple_class = class_name.split(".")[-1]
    simple_file = filename.split(".")[-1]
    simple_modified = {m.split(".")[-1] for m in modified_classes}

    return simple_class in simple_modified or simple_file in simple_modified


def parse_requirements(xml_path, modified_classes=None, require_hits=True):
    modified_classes = modified_classes or set()

    tree = ET.parse(xml_path)
    root = tree.getroot()

    reqs = set()

    for cls in root.findall(".//class"):
        cls_name = normalize_class_name(cls.attrib.get("name"))
        filename = normalize_class_name(cls.attrib.get("filename"))

        if not class_matches_modified(cls_name, filename, modified_classes):
            continue

        req_class = cls_name or filename or "UNKNOWN_CLASS"

        for line in cls.findall(".//line"):
            number = line.attrib.get("number")
            if number is None:
                continue

            hits = int(line.attrib.get("hits", "0"))
            if require_hits and hits <= 0:
                continue

            reqs.add(f"{req_class}:{number}")

    return sorted(reqs)


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 make_chart26b_dataset.py <WORK_DIR> <OUT_DIR>")
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

    max_tests = int(os.environ.get("MAX_TESTS", "20"))
    coverage_timeout = int(os.environ.get("COVERAGE_TIMEOUT", "300"))

    print("======================================")
    print("Generate Defects4J Chart 26b Dataset")
    print("======================================")
    print(f"WORK_DIR         = {work_dir}")
    print(f"OUT_DIR          = {out_dir}")
    print(f"MAX_TESTS        = {max_tests}")
    print(f"COVERAGE_TIMEOUT = {coverage_timeout}")
    print("Use MAX_TESTS=0 to run all tests.")
    print("")

    if not work_dir.exists():
        raise RuntimeError(f"WORK_DIR does not exist: {work_dir}")

    old_xml = work_dir / "coverage.xml"

    print("[1] Collecting test cases...")
    tests = collect_tests(work_dir)

    if max_tests > 0:
        tests = tests[:max_tests]

    if not tests:
        raise RuntimeError("No test cases found.")

    tests_path = out_dir / "tests.txt"
    tests_path.write_text("\n".join(tests) + "\n", encoding="utf-8")
    print(f"Saved tests.txt: {len(tests)} tests")

    print("")
    print("[2] Running relevant coverage to create requirements.txt...")

    if old_xml.exists():
        old_xml.unlink()

    p = run_cmd(
        ["defects4j", "coverage", "-w", str(work_dir), "-r"],
        timeout=coverage_timeout * 10,
    )

    (logs_dir / "coverage_relevant.stdout.log").write_text(
        p.stdout,
        encoding="utf-8",
        errors="ignore",
    )
    (logs_dir / "coverage_relevant.stderr.log").write_text(
        p.stderr,
        encoding="utf-8",
        errors="ignore",
    )

    if not old_xml.exists():
        raise RuntimeError(
            "coverage.xml was not created by defects4j coverage -r. "
            "Check raw/logs/coverage_relevant.stderr.log"
        )

    relevant_xml = coverage_dir / "coverage_relevant.xml"
    shutil.copy2(old_xml, relevant_xml)

    modified_classes = load_modified_classes(out_dir)
    requirement_filter_classes = set(modified_classes)

    requirements = parse_requirements(
        relevant_xml,
        modified_classes=requirement_filter_classes,
        require_hits=True,
    )

    if not requirements and modified_classes:
        print("WARNING: no requirements matched modified classes.")
        print("Fallback: use all covered source lines as requirements.")
        requirement_filter_classes = set()
        requirements = parse_requirements(
            relevant_xml,
            modified_classes=requirement_filter_classes,
            require_hits=True,
        )

    if not requirements:
        raise RuntimeError("No requirements found from coverage_relevant.xml.")

    req_path = out_dir / "requirements.txt"
    req_path.write_text("\n".join(requirements) + "\n", encoding="utf-8")
    print(f"Saved requirements.txt: {len(requirements)} requirements")

    print("")
    print("[3] Running per-test coverage and building matrix.csv...")

    matrix_path = out_dir / "matrix.csv"
    skipped = []
    rows = 0
    zero_rows = 0
    start = time.time()

    with matrix_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["test_id"] + requirements)

        for idx, test_id in enumerate(tests, start=1):
            print(f"[{idx:05d}/{len(tests):05d}] {test_id}", flush=True)

            if old_xml.exists():
                old_xml.unlink()

            p = run_cmd(
                ["defects4j", "coverage", "-w", str(work_dir), "-t", test_id],
                timeout=coverage_timeout,
            )

            name = safe_filename(test_id)

            (logs_dir / f"{idx:05d}_{name}.stdout.log").write_text(
                p.stdout,
                encoding="utf-8",
                errors="ignore",
            )
            (logs_dir / f"{idx:05d}_{name}.stderr.log").write_text(
                p.stderr,
                encoding="utf-8",
                errors="ignore",
            )

            if not old_xml.exists():
                skipped.append({
                    "index": idx,
                    "test_id": test_id,
                    "returncode": p.returncode,
                    "reason": "coverage.xml was not created",
                })
                continue

            dst_xml = coverage_dir / f"{idx:05d}_{name}.xml"
            shutil.copy2(old_xml, dst_xml)

            covered = set(parse_requirements(
                dst_xml,
                modified_classes=requirement_filter_classes,
                require_hits=True,
            ))

            row_values = [1 if req in covered else 0 for req in requirements]

            if sum(row_values) == 0:
                zero_rows += 1

            writer.writerow([test_id] + row_values)
            rows += 1

    elapsed = time.time() - start

    skipped_path = raw_dir / "skipped_tests.txt"
    skipped_path.write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in skipped)
        + ("\n" if skipped else ""),
        encoding="utf-8",
    )

    metadata = {
        "project": PROJECT,
        "bug_id": BUG_ID,
        "version": VERSION,
        "work_dir": str(work_dir),
        "out_dir": str(out_dir),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "max_tests": max_tests,
        "coverage_timeout_seconds": coverage_timeout,
        "tests_total_in_tests_txt": len(tests),
        "tests_total_in_matrix": rows,
        "requirements_total": len(requirements),
        "zero_coverage_rows_total": zero_rows,
        "skipped_tests_total": len(skipped),
        "matrix_format": "CSV header = test_id + requirements; cells are 0/1 coverage",
        "requirement_definition": "Covered source lines from Defects4J coverage -r, filtered to modified classes when possible",
        "modified_classes": sorted(modified_classes),
        "used_modified_class_filter": bool(requirement_filter_classes),
    }

    metadata_path = out_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report = [
        "# Chart 26b Dataset Report",
        "",
        "- Project: Chart",
        "- Version: 26b",
        f"- Tests in tests.txt: {len(tests)}",
        f"- Tests in matrix.csv: {rows}",
        f"- Requirements: {len(requirements)}",
        f"- Zero-coverage matrix rows: {zero_rows}",
        f"- Skipped tests: {len(skipped)}",
        f"- Runtime seconds: {elapsed:.2f}",
        "",
        "Generated files:",
        "",
        "- tests.txt",
        "- requirements.txt",
        "- matrix.csv",
        "- metadata.json",
        "- raw/coverage/",
        "- raw/logs/",
    ]

    summary_path = report_dir / "summary.md"
    summary_path.write_text("\n".join(report), encoding="utf-8")

    print("")
    print("[4] DONE")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
