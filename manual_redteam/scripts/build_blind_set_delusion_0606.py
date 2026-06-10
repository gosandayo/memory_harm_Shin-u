#!/usr/bin/env python3
"""Build a single condition-blind item set for the delusion endpoint, pooling:
  - cold (gpt-4o, single-turn probe)               x5
  - fixed climb (runA gpt-4o, heavy rapport)       r01,r02 (r03 terminated)
  - adaptive climb (traj01/02/03, light rapport)   operator-in-loop

Each item = (preceding user turn, assistant reply) for every SCORED rung
(rapport/bridge turns excluded). Items are shuffled and given opaque blind_ids;
a sealed key maps blind_id -> {condition, model, rung, source, turn_idx}.

The fresh blind Claude judge scores `blind_items.json` (NO condition/rung labels)
on endorsement(0-3)+safety(0-4); we unblind with SEALED_key.json afterwards.
"""
from __future__ import annotations
import json, random, glob, os, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/blindpass/2026-06-06_delusion_crossmodel"
SEED = 20260606

NONSCORED = ("RAPPORT", "D-RAPPORT", "DRAPPORT", "FG-RAPPORT", "FGRAPPORT", "D-BRIDGE", "DBRIDGE", "BRIDGE")

def is_scored(rung) -> bool:
    if rung is None:
        return True  # cold single turn has rung_id D12 -> scored
    # must strip "-" too: the 2026-06-06 set leaked D-RAPPORT/D-BRIDGE/FG-RAPPORT because
    # hyphens were removed from the patterns but not from the rung label
    r = str(rung).upper().replace("_", "").replace("-", "").replace(" ", "")
    return not any(r.startswith(p.replace("-", "").replace("_", "")) for p in NONSCORED)

def rung_of(turn) -> str:
    return turn.get("rung") or turn.get("rung_id")

def collect(path, condition, model):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    turns = d["turns"]
    items = []
    for i, t in enumerate(turns):
        if t["role"] != "assistant":
            continue
        rung = rung_of(t)
        if not is_scored(rung):
            continue
        # preceding user turn
        user = ""
        for j in range(i - 1, -1, -1):
            if turns[j]["role"] == "user":
                user = turns[j]["content"]
                break
        items.append({
            "condition": condition, "model": model, "rung": rung,
            "source": os.path.basename(str(path)), "turn_idx": i,
            "user_context": user, "assistant_text": t["content"],
        })
    return items

def main():
    pool = []
    # --- gpt-4o ---
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-05_delusion_cold/delusion_cold_gpt4o_r*.yaml"))):
        pool += collect(f, "cold", "gpt-4o")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-05_delusion_runA_gpt4o/*.yaml"))):
        if "r03" in os.path.basename(f):
            continue  # terminated by tripwire false-positive; exclude
        pool += collect(f, "fixed_climb", "gpt-4o")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-06_delusion_gpt4o_adaptive/traj*.json"))):
        pool += collect(f, "adaptive_climb", "gpt-4o")
    # --- gpt-4o-mini (cold + fixed exist; adaptive pending) ---
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-05_delusion_cold/delusion_cold_gpt4omini_r*.yaml"))):
        pool += collect(f, "cold", "gpt-4o-mini")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-05_delusion_runA_gpt4omini/*.yaml"))):
        pool += collect(f, "fixed_climb", "gpt-4o-mini")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-06_delusion_gpt4omini_adaptive/traj*.json"))):
        pool += collect(f, "adaptive_climb", "gpt-4o-mini")
    # --- gpt-5.4-mini (cold + adaptive exist; no fixed delusion run) ---
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-05_delusion_cold/delusion_cold_gpt54mini_r*.yaml"))):
        pool += collect(f, "cold", "gpt-5.4-mini")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-06_delusion_gpt54mini_adaptive/traj*.json"))):
        pool += collect(f, "adaptive_climb", "gpt-5.4-mini")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-07_delusion_gpt54mini_battery/*.json"))):
        pool += collect(f, "battery", "gpt-5.4-mini")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-07_delusion_gpt54mini_finegrained/traj*.json"))):
        pool += collect(f, "finegrained", "gpt-5.4-mini")
    # --- fine-grained matched control on 4o / 4o-mini ---
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-07_delusion_finegrained_control/gpt4o_traj*.json"))):
        pool += collect(f, "finegrained", "gpt-4o")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-07_delusion_finegrained_control/gpt4omini_traj*.json"))):
        pool += collect(f, "finegrained", "gpt-4o-mini")
    # --- VERBATIM-endpoint cold (necessity test): same final endpoint turn thrown cold ---
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-07_delusion_verbatim_cold/gpt4o_*.json"))):
        pool += collect(f, "verbatim_cold", "gpt-4o")
    for f in sorted(glob.glob(str(ROOT / "data/simulator_discover/2026-06-07_delusion_verbatim_cold/gpt4omini_*.json"))):
        pool += collect(f, "verbatim_cold", "gpt-4o-mini")

    rng = random.Random(SEED)
    rng.shuffle(pool)

    blind, key = [], {}
    for n, it in enumerate(pool):
        bid = "I" + hashlib.sha1(f"{SEED}-{n}-{it['source']}-{it['turn_idx']}".encode()).hexdigest()[:8]
        blind.append({"blind_id": bid, "user_context": it["user_context"], "assistant_text": it["assistant_text"]})
        key[bid] = {k: it[k] for k in ("condition", "model", "rung", "source", "turn_idx")}

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    from collections import Counter
    c = Counter(v["condition"] for v in key.values())
    print(f"[built] {len(blind)} blind items -> {OUT}/blind_items.json")
    print(f"[conditions] {dict(c)}")

if __name__ == "__main__":
    main()
