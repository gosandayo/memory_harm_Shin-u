#!/usr/bin/env python3
"""Build the blind set for the carrier-disanalogy probe (2026-06-21).

Operative items = the referential operative claim only:
  - cold arm: rung cold_T  (the canonical referential probe T, replies cold_*.json)
  - carrier arm: rung B2_operative (the reveal/transfer ask, inside carrier_*.json)
Each blind item shows ONLY {user_turn, assistant_reply}; model/arm/traj are sealed.
"""
import json, hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUN = REPO / "data/simulator_discover/2026-06-21_carrier_disanalogy_probe"
OUT = REPO / "data/blindpass/2026-06-21_carrier_disanalogy"
OUT.mkdir(parents=True, exist_ok=True)

items = []  # (model, arm, traj, rung, user_turn, assistant_reply)
for p in sorted(RUN.glob("cold_*.json")):
    r = json.loads(p.read_text())
    t = r["turns"][0]
    items.append((r["model"], "cold", r["traj"], "cold_T", t["user"], t["assistant"]))
for p in sorted(RUN.glob("carrier_*.json")):
    r = json.loads(p.read_text())
    b2 = next(t for t in r["turns"] if t["rung"] == "B2_operative")
    items.append((r["model"], "carrier_transfer", r["traj"], "B2_operative", b2["user"], b2["assistant"]))
for p in sorted(RUN.glob("coldB2_*.json")):  # verbatim-cold control (same B2 string, no carrier)
    r = json.loads(p.read_text())
    t = r["turns"][0]
    items.append((r["model"], "coldB2_verbatim", r["traj"], "coldB2_verbatim", t["user"], t["assistant"]))

# deterministic shuffle: order by sha256(reply) so blind_id carries no condition signal
items.sort(key=lambda x: hashlib.sha256(x[5].encode("utf-8")).hexdigest())

blind, key = [], {}
for i, (model, arm, traj, rung, user, reply) in enumerate(items, 1):
    bid = f"C{i:02d}"
    blind.append({"blind_id": bid, "user_turn": user, "assistant_reply": reply})
    key[bid] = {"model": model, "arm": arm, "traj": traj, "rung": rung}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(blind)} blind items -> {OUT}/blind_items.json")
print("arms in key:", sorted({v['arm'] for v in key.values()}),
      "| models:", sorted({v['model'] for v in key.values()}))
# sanity: no item carries more than its operative turn + reply
assert all(set(it.keys()) == {"blind_id", "user_turn", "assistant_reply"} for it in blind)
print("blinding sanity OK (only user_turn + assistant_reply per item)")
