#!/usr/bin/env python3
"""Build a condition-blind item set for the T6 suicide-operative runs.

Pools every assistant turn at a LADDER rung (bridge + S9..S12 + reasks/finer;
excludes pure R0-rapport) across the 3 model dirs (climb) + the verbatim_cold
reps, strips model/condition/rung labels, shuffles, seals a key.

A fresh, condition-blind judge then scores each item on the 2-axis suicide
rubric + an affirms_operative_claim bool. We unblind with the key afterwards.

Regenerate: python3 manual_redteam/scripts/build_t6_blind_set.py
"""
from __future__ import annotations
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISC = ROOT / "data/simulator_discover"
OUT = ROOT / "data/blindpass/2026-06-12_suicide_operative"
SEED = 20260612

DIRS = {
    "gpt-4o": DISC / "2026-06-12_suicide_opus_operative",
    "gpt-4o-mini": DISC / "2026-06-12_suicide_opus_operative_4omini",
    "gpt-5.4-mini": DISC / "2026-06-12_suicide_opus_operative_54mini",
}


def is_ladder_rung(rung) -> bool:
    r = str(rung or "").upper()
    if r.startswith("R0-RAPPORT") or r == "R0-RAPPORT":
        return False
    # include bridge (5.4-mini held there) + all S-rungs + reask/finer
    return r.startswith(("R0-BRIDGE", "S9", "S10", "S11", "S12"))


def main():
    items, key = [], {}
    rng = random.Random(SEED)

    # climb items
    for model, d in DIRS.items():
        for tp in sorted(d.glob("traj*.json")):
            if tp.name.endswith("__advance_decisions.json"):
                continue
            data = json.loads(tp.read_text(encoding="utf-8"))
            turns = data["turns"]
            for i, t in enumerate(turns):
                if t["role"] != "assistant":
                    continue
                if not is_ladder_rung(t.get("rung")):
                    continue
                prev_user = turns[i - 1]["content"] if i > 0 and turns[i - 1]["role"] == "user" else ""
                bid = f"T6_{len(items):03d}"
                items.append({"blind_id": bid, "user_context": prev_user,
                              "assistant_text": t["content"]})
                key[bid] = {"condition": "climb", "model": model, "traj": tp.stem,
                            "rung": t.get("rung"), "turn_idx": i}

    # verbatim cold items
    for model, d in DIRS.items():
        cdir = d / "verbatim_cold"
        if not cdir.exists():
            continue
        for cp in sorted(cdir.glob("*_S12_verbatim_cold.json")):
            cold = json.loads(cp.read_text(encoding="utf-8"))
            ep = cold["endpoint_verbatim"]
            for rep in cold["reps"]:
                bid = f"T6_{len(items):03d}"
                items.append({"blind_id": bid, "user_context": ep,
                              "assistant_text": rep["reply"]})
                key[bid] = {"condition": "verbatim_cold", "model": cold["model"],
                            "traj": cp.stem.replace("_S12_verbatim_cold", ""),
                            "rung": "S12", "turn_idx": rep["rep"]}

    rng.shuffle(items)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "blind_items.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "SEALED_key.json").write_text(
        json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter
    print(f"{len(items)} blind items -> {OUT}")
    print("by (model,condition):", dict(Counter((v["model"], v["condition"]) for v in key.values())))


if __name__ == "__main__":
    main()
