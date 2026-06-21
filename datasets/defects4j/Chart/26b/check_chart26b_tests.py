import re
import os
from pathlib import Path

work_dir = Path(os.environ["WORK_DIR"])
out_dir = Path(os.environ["OUT_DIR"])

test_dir_name = (out_dir / "raw" / "dir.src.tests.txt").read_text().strip()
test_root = work_dir / test_dir_name

def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)
    return text

def parse_package(text):
    m = re.search(r"^\s*package\s+([A-Za-z0-9_.]+)\s*;", text, re.MULTILINE)
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

tests = []

for java_file in sorted(test_root.rglob("*.java")):
    tests.extend(find_test_methods(java_file))

tests = sorted(set(tests))

print("Test root:", test_root)
print("Collected test methods:", len(tests))
print("")
print("First 30 tests:")

for test in tests[:30]:
    print(test)
