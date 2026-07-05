#!/usr/bin/env bash
# pb_bridge_batch.sh <model> — run all (case x {fixed_pb, cold_final}) for ONE model.
# Launch one per model in parallel (background shells). Skips cells already on disk.
set -u
cd "$(dirname "$0")/.."
MODEL="${1:?usage: pb_bridge_batch.sh <model>}"
OUT="data/pb_bridge/2026-06-19"
mkdir -p "$OUT"
for CASE in ai_sweetheart_explicit turing_test_explicit medical_awakening_explicit; do
  for COND in fixed_pb cold_final; do
    out="$OUT/${CASE}__${MODEL}__${COND}.json"
    if [ -f "$out" ]; then echo "skip $out"; continue; fi
    echo ">>> $CASE $MODEL $COND"
    python3 scripts/pb_bridge_run.py --case "$CASE" --model "$MODEL" \
      --condition "$COND" --out "$out" --i-have-owner-signoff \
      || echo "FAIL $CASE $MODEL $COND"
  done
done
echo "DONE model=$MODEL"
