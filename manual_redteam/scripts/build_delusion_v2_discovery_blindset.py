#!/usr/bin/env python3
"""Build a condition-BLIND 2-axis item set for the 2026-06-22 delusion v2 DISCOVERY
endpoints (5 tactic-varied gpt-4o trajectories), to be scored by fresh condition-blind
Claude judges. EXPLORATORY discovery run (NOT a frozen claim) — blind check of whether
the operators' live 5/5 BREAK survives the judge of record.

Blinding rule (freshop analog): each item shows ONLY the immediate D12 user turn +
the assistant reply. No rapport/bridge/intermediate turns leak in. blind_id is a
neutral hash so the tactic/condition cannot be read off the id or the order.

Emits blind_items.json (no labels) + SEALED_key.json (sealed condition map).
"""
import glob
import hashlib
import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUN = REPO / "data/simulator_discover/2026-06-22_delusion_v2_discovery"
OUT = REPO / "data/blindpass/2026-06-22_delusion_v2_discovery"
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
                         "condition": "discovery_climb_D12",
                         "user_context": user, "assistant_text": t["content"]})
            break  # the FIRST (operative) D12 reply only; ignores any D12-final log turn

assert len(rows) == 5, f"expected 5 D12 endpoints, got {len(rows)}: {[r['src_traj'] for r in rows]}"

random.Random(SEED).shuffle(rows)
OUT.mkdir(parents=True, exist_ok=True)
blind, key = [], {}
for r in rows:
    bid = "X" + hashlib.sha1(f"{SEED}-{r['src_traj']}".encode()).hexdigest()[:8]
    blind.append({"blind_id": bid, "user_turn": r["user_context"], "assistant_reply": r["assistant_text"]})
    key[bid] = {k: r[k] for k in ("model", "src_traj", "condition")}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(blind)} blind items -> {OUT}")
for b in blind:
    print(f"  {b['blind_id']}  user_turn[{len(b['user_turn'])}c]  reply[{len(b['assistant_reply'])}c]")
