#!/usr/bin/env bash
set -e

PROJECT=Lang
BUG=1
VER="${BUG}b"

OUT="$BASE/datasets/defects4j/$PROJECT/$VER"
WORK="$BASE/work/defects4j/${PROJECT}_${VER}"

mkdir -p "$OUT/raw" "$OUT/report" "$BASE/work/defects4j"

echo "OUT=$OUT"
echo "WORK=$WORK"

# Step 1: checkout
if [ ! -f "$OUT/.checkout.done" ]; then
  echo "[1/3] Checkout Lang 1b..."

  # Nếu lần trước bị tắt máy giữa chừng, WORK có thể bị lỗi.
  # Xóa checkout dở rồi tải lại.
  rm -rf "$WORK"

  defects4j checkout -p Lang -v 1b -w "$WORK"
  touch "$OUT/.checkout.done"
else
  echo "[1/3] Checkout already done. Skip."
fi

# Step 2: compile
if [ ! -f "$OUT/.compile.done" ]; then
  echo "[2/3] Compile Lang 1b..."
  cd "$WORK"
  defects4j compile
  touch "$OUT/.compile.done"
else
  echo "[2/3] Compile already done. Skip."
fi

# Step 3: export tests/info
if [ ! -f "$OUT/.export.done" ]; then
  echo "[3/3] Export tests/info..."
  cd "$WORK"

  defects4j export -p tests.all > "$OUT/tests.txt"
  defects4j export -p tests.trigger > "$OUT/raw/trigger_tests.txt" 2>/dev/null || true
  defects4j export -p tests.relevant > "$OUT/raw/relevant_tests.txt" 2>/dev/null || true
  defects4j export -p classes.modified > "$OUT/raw/classes_modified.txt" 2>/dev/null || true

  cat > "$OUT/metadata.json" <<EOF
{
  "project": "Lang",
  "bug_id": 1,
  "version": "1b",
  "workdir": "$WORK",
  "output": "$OUT"
}
EOF

  touch "$OUT/.export.done"
else
  echo "[3/3] Export already done. Skip."
fi

echo "DONE: Lang 1b is ready."
echo "Open folder:"
echo "$OUT"
