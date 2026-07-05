#!/usr/bin/env python3
"""Build a condition-BLIND 2-axis item set for the 2026-06-16 fresh-operator
delusion necessity (endpoint vs verbatim-cold), to be scored by a fresh
condition-blind Claude judge and reported ALONGSIDE the Jared primary.

Blinding rule: each item shows ONLY the immediate D12 user turn + the assistant
reply. The D12 user turn is verbatim-identical between a climb endpoint and its
cold throw, so the judge cannot tell climb from cold from context length.
  - endpoint item: user_context = the D12 user turn; assistant_text = D12 reply
  - cold item:     user_context = endpoint_verbatim; assistant_text = cold reply

Emits blind_items.json (no labels) + SEALED_key.json (sealed condition map).
"""
import glob
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data/blindpass/2026-06-16_freshop_necessity"
SEED = 20260616

EP_DIRS = {
    "gpt-4o-mini": "data/simulator_discover/2026-06-16_delusion_fresh_op_gpt4omini",
    "gpt-4o": "data/simulator_discover/2026-06-16_delusion_fresh_op_gpt4o",
    "gpt-5.4-mini": "data/simulator_discover/2026-06-16_delusion_fresh_op_gpt54mini",
}
COLD_GLOB = "data/simulator_discover/2026-06-16_delusion_fresh_op_cold/*_D12_cold.json"


def base(r):
    return str(r or "").upper().replace("_", "-").split("-REASK")[0]


rows = []
# endpoints: D12 user turn + D12 reply
for model, d in EP_DIRS.items():
    for tf in sorted(glob.glob(str(REPO / d / "traj*.json"))):
        if "advance_decision" in tf:
            continue
        turns = json.loads(Path(tf).read_text())["turns"]
        for i, t in enumerate(turns):
            if t["role"] == "assistant" and base(t.get("rung")) == "D12":
                # nearest preceding user turn = the D12 ask
                user = next((turns[j]["content"] for j in range(i - 1, -1, -1)
                             if turns[j]["role"] == "user"), "")
                rows.append({"model": model, "src_traj": Path(tf).stem, "rep": 0,
                             "condition": "endpoint_climb",
                             "user_context": user, "assistant_text": t["content"]})
                break

# cold: endpoint_verbatim + each cold reply
for cf in sorted(glob.glob(str(REPO / COLD_GLOB))):
    c = json.loads(Path(cf).read_text())
    for rep in c["reps"]:
        rows.append({"model": c["model"], "src_traj": c["src_traj"], "rep": rep["rep"],
                     "condition": "verbatim_cold",
                     "user_context": c["endpoint_verbatim"], "assistant_text": rep["reply"]})

random.Random(SEED).shuffle(rows)
OUT.mkdir(parents=True, exist_ok=True)
blind, key = [], {}
for r in rows:
    bid = "F" + hashlib.sha1(f"{SEED}-{r['model']}-{r['src_traj']}-{r['condition']}-{r['rep']}".encode()).hexdigest()[:8]
    blind.append({"blind_id": bid, "user_turn": r["user_context"], "assistant_reply": r["assistant_text"]})
    key[bid] = {k: r[k] for k in ("model", "src_traj", "rep", "condition")}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(blind)} blind items -> {OUT}")
print("[condition]", dict(Counter(v["condition"] for v in key.values())))
print("[model]", dict(Counter(v["model"] for v in key.values())))
