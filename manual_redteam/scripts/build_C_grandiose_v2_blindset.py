#!/usr/bin/env python3
"""Build a condition-BLIND 2-axis item set for the 2026-06-18 scenario-C
(grandiose significance, concrete-idea spec) gpt-4o-mini pilot.

One item per trajectory = the FIRST D12 assistant reply + the nearest preceding
user turn (the D12 ask). The judge is blind to traj/condition; it scores the
REPLY against the grandiose-significance belief defined in the judge rubric.

Emits blind_items.json (no labels) + SEALED_key.json (sealed map). Mirrors
build_freshop_blindset.py.
"""
import glob
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EP_DIR = REPO / "data/simulator_discover/2026-06-18_delusion_C_grandiose_gpt4omini_v2"
OUT = REPO / "data/blindpass/2026-06-18_C_grandiose_v2"
SEED = 20260618


def base(r):
    return str(r or "").upper().replace("_", "-").split("-REASK")[0]


rows = []
for tf in sorted(glob.glob(str(EP_DIR / "traj*.json"))):
    if "advance_decision" in tf:
        continue
    turns = json.loads(Path(tf).read_text())["turns"]
    for i, t in enumerate(turns):
        if t["role"] == "assistant" and base(t.get("rung")) == "D12":
            user = next((turns[j]["content"] for j in range(i - 1, -1, -1)
                         if turns[j]["role"] == "user"), "")
            rows.append({"src_traj": Path(tf).stem, "rung": "D12",
                         "user_context": user, "assistant_text": t["content"]})
            break  # FIRST D12 only (handles traj02 turn-15 vs turn-17 artifact)

rows.sort(key=lambda r: hashlib.sha1(f"{SEED}-{r['src_traj']}".encode()).hexdigest())
OUT.mkdir(parents=True, exist_ok=True)
blind, key = [], {}
for r in rows:
    bid = "C" + hashlib.sha1(f"{SEED}-{r['src_traj']}-{r['rung']}".encode()).hexdigest()[:8]
    blind.append({"blind_id": bid, "user_turn": r["user_context"], "assistant_reply": r["assistant_text"]})
    key[bid] = {"src_traj": r["src_traj"], "rung": r["rung"]}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(blind)} blind items -> {OUT}")
for b in blind:
    print(f"  {b['blind_id']}  reply[:60]={b['assistant_reply'][:60]!r}")
