#!/usr/bin/env python3
"""Blind set for the affective->cognitive pilot (2026-06-21).

OPERATIVE items (harm-flaggable): endpoint rung (climb) + cold_endpoint, both models.
NON-OPERATIVE climb-depth items (gpt-4o only): rungs R7 (understandable), R9 (competent),
R10 (defensible), R12 (not-a-mistake) -- used to read whether there was a genuine climb
before the endpoint held (climb-then-hold vs entry-refusal), NOT for harm.
Each blind item shows only {user_turn, assistant_reply}; model/arm/traj/rung sealed.
"""
import json, hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUN = REPO / "data/simulator_discover/2026-06-21_affective_to_cognitive_pilot"
OUT = REPO / "data/blindpass/2026-06-21_affective_pilot"
OUT.mkdir(parents=True, exist_ok=True)

DEPTH_RUNGS = {"R7", "R9", "R10", "R12"}
items = []  # (model, arm, traj, rung, is_operative, user, reply)

for p in sorted(RUN.glob("climb_*.json")):
    r = json.loads(p.read_text()); model = r["model"]
    for t in r["turns"]:
        if t["rung"] == "endpoint":
            items.append((model, "climb", r["traj"], "endpoint", True, t["user"], t["assistant"]))
        elif model == "gpt-4o" and t["rung"] in DEPTH_RUNGS:
            items.append((model, "climb", r["traj"], t["rung"], False, t["user"], t["assistant"]))
for p in sorted(RUN.glob("cold_*.json")):
    r = json.loads(p.read_text()); model = r["model"]; t = r["turns"][0]
    items.append((model, "cold", r["traj"], "cold_endpoint", True, t["user"], t["assistant"]))

items.sort(key=lambda x: hashlib.sha256(x[6].encode("utf-8")).hexdigest())
blind, key = [], {}
for i, (model, arm, traj, rung, oper, user, reply) in enumerate(items, 1):
    bid = f"AP{i:02d}"
    blind.append({"blind_id": bid, "user_turn": user, "assistant_reply": reply})
    key[bid] = {"model": model, "arm": arm, "traj": traj, "rung": rung, "is_operative": oper}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(blind)} items -> {OUT}/blind_items.json")
n_oper = sum(v["is_operative"] for v in key.values())
print(f"operative (harm-flaggable): {n_oper} | non-operative climb-depth: {len(key)-n_oper}")
assert all(set(it) == {"blind_id", "user_turn", "assistant_reply"} for it in blind)
print("blinding sanity OK")
