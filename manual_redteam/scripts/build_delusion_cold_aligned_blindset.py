#!/usr/bin/env python3
"""Build a condition-blind item set for the 2026-06-16 aligned delusion cold runs.

Reads the per-trajectory cold files in
  data/simulator_discover/2026-06-16_delusion_verbatim_cold_aligned/
(one file per climb trajectory, reps[] = the cold replies), and emits:
  blind_items.json  [{blind_id, user_context, assistant_text}]  (NO labels)
  SEALED_key.json   {blind_id: {model, src_traj, rep, condition}}
items shuffled with a fixed seed; the sealed key lives in a separate file the
judge process never reads. Same blind format as build_blind_set_delusion_0606.py.
"""
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/simulator_discover/2026-06-16_delusion_verbatim_cold_aligned"
OUT = ROOT / "data/blindpass/2026-06-16_delusion_cold_aligned"
SEED = 20260616

rows = []
for f in sorted(SRC.glob("*_D12_cold.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    for rep in d["reps"]:
        rows.append({
            "model": d["model"], "src_traj": d["src_traj"], "rep": rep["rep"],
            "condition": "verbatim_cold_aligned",
            "user_context": d["endpoint_verbatim"], "assistant_text": rep["reply"],
        })

random.Random(SEED).shuffle(rows)
OUT.mkdir(parents=True, exist_ok=True)
blind, key = [], {}
for r in rows:
    bid = "C" + hashlib.sha1(f"{SEED}-{r['model']}-{r['src_traj']}-{r['rep']}".encode()).hexdigest()[:8]
    blind.append({"blind_id": bid, "user_context": r["user_context"], "assistant_text": r["assistant_text"]})
    key[bid] = {k: r[k] for k in ("model", "src_traj", "rep", "condition")}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(blind)} blind items -> {OUT}")
print("[per model]", dict(Counter(v["model"] for v in key.values())))
print("[per model x traj]", dict(Counter((v["model"], v["src_traj"]) for v in key.values())))
