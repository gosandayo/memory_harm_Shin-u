#!/usr/bin/env python3
"""Tamper-evident seal for a labels file (blindpass_design_2026_05_17.md,
hardening: operator cross-check must be recorded & frozen BEFORE Codex output
exists; Codex draws timestamped to prove independence/order).

Writes <file>.SEAL.json = {file, sha256, n_records, utc_sealed_at}. Re-sealing
a changed file produces a new hash + timestamp, so any post-hoc edit is
visible. Generic: use for operator_labels.jsonl and each codex_drawN.jsonl.

Usage: python3 seal_labels.py <labels_file>
"""
import hashlib, json, sys, os, datetime

f = sys.argv[1]
b = open(f, "rb").read()
try:
    n = sum(1 for ln in b.decode().splitlines() if ln.strip())
except Exception:
    n = None
seal = {
    "file": os.path.abspath(f),
    "sha256": hashlib.sha256(b).hexdigest(),
    "n_records": n,
    "utc_sealed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
out = f + ".SEAL.json"
json.dump(seal, open(out, "w"), indent=2)
print(json.dumps(seal, indent=2))
print(f"[sealed] -> {out}")
