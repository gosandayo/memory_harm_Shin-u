#!/usr/bin/env bash
# pb_bridge_score_batch.sh <model> — score all pb_bridge transcripts for ONE model with the
# pinned PsychosisBench scorer (o4-mini, medium, full curve). Skips cells already scored.
#   fixed_pb / adaptive_pb -> turns 4-12 (DCS T4-12, HES/SIS T7-12)
#   cold_final -> turn 12 ; cold_action -> turns 10-12
set -u
cd "$(dirname "$0")/.."
MODEL="${1:?usage: pb_bridge_score_batch.sh <model>}"
DIR="data/pb_bridge/2026-06-19"
score() {  # <file> <turns>
  f="$1"; turns="$2"
  [ -f "$f" ] || return 0
  out="${f%.json}.pbscores.json"
  if [ -f "$out" ]; then echo "skip $out"; return 0; fi
  echo ">>> score $(basename "$f") [$turns]"
  python3 scripts/pb_bridge_score.py --transcript "$f" --judge openai/o4-mini \
    --score-turns "$turns" --i-have-owner-signoff || echo "FAIL $f"
}
for f in "$DIR"/*__"${MODEL}"__fixed_pb.json;    do score "$f" 4-12;  done
for f in "$DIR"/*__"${MODEL}"__adaptive_pb.json; do score "$f" 4-12;  done
for f in "$DIR"/*__"${MODEL}"__cold_final.json;  do score "$f" 12;    done
for f in "$DIR"/*__"${MODEL}"__cold_action.json; do score "$f" 10-12; done
echo "SCORED model=$MODEL"
