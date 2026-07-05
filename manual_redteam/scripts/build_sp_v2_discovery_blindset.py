#!/usr/bin/env python3
"""Condition-BLIND 2-axis item set for the 2026-06-22 SP (Secret Project) v2 DISCOVERY
D12 endpoints (5 tactic-varied gpt-4o trajectories). EXPLORATORY generalization test.
Same contract/blinding as build_delusion_v2_discovery_blindset.py: each item carries ONLY
the immediate D12 operative user turn + the assistant reply; neutral hashed blind_id.
"""
import glob
import hashlib
import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUN = REPO / "data/simulator_discover/2026-06-22_SP_v2_discovery"
OUT = REPO / "data/blindpass/2026-06-22_SP_v2_discovery"
SEED = 20260622


def base(r):
    return str(r or "").upper().replace("_", "-").split("-REASK")[0]


rows = []
for tf in sorted(glob.glob(str(RUN / "traj_*.json"))):
    if "advance_decision" in tf:
        continue
    data = json.loads(Path(tf).read_text())
    turns = data["turns"]
    for i, t in enumerate(turns):
        if t["role"] == "assistant" and base(t.get("rung")) == "D12":
            user = next((turns[j]["content"] for j in range(i - 1, -1, -1)
                         if turns[j]["role"] == "user"), "")
            rows.append({"model": data.get("model"), "src_traj": Path(tf).stem,
                         "condition": "SP_discovery_climb_D12",
                         "user_context": user, "assistant_text": t["content"]})
            break  # FIRST operative D12 reply only (ignore any D12-final log turn)

assert len(rows) == 5, f"expected 5 D12 endpoints, got {len(rows)}"

random.Random(SEED).shuffle(rows)
OUT.mkdir(parents=True, exist_ok=True)
blind, key = [], {}
for r in rows:
    bid = "S" + hashlib.sha1(f"{SEED}-SP-{r['src_traj']}".encode()).hexdigest()[:8]
    blind.append({"blind_id": bid, "user_turn": r["user_context"], "assistant_reply": r["assistant_text"]})
    key[bid] = {k: r[k] for k in ("model", "src_traj", "condition")}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(blind)} blind items -> {OUT}")
for b in blind:
    print(f"  {b['blind_id']}  user_turn[{len(b['user_turn'])}c]  reply[{len(b['assistant_reply'])}c]")
