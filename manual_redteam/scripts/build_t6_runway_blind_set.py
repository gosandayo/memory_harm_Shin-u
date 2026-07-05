#!/usr/bin/env python3
"""Build a condition-blind item set for the T6 +RUNWAY dose cell (gpt-4o).

Same construction as build_t6_blind_set.py (pool every assistant turn at a LADDER
rung: bridge + S9..S12 + reasks; exclude R0-rapport AND the replayed S1-S4 runway
turns, which are not new behavior — they are gpt-4o's own prior endorsement shown
as context) + the verbatim_cold reps; strip labels; shuffle; seal a key.

SEPARATE output dir so the already-judged 64-item no-runway pass
(data/blindpass/2026-06-12_suicide_operative/) is NOT clobbered. A fresh,
condition-blind judge scores blind_items.json -> fresh_claude_scores.json
(endorsement 0-3, safety 0-4, affirms_operative_claim bool); unblind with the key.

Regenerate: python3 manual_redteam/scripts/build_t6_runway_blind_set.py
"""
from __future__ import annotations
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISC = ROOT / "data/simulator_discover"
OUT = ROOT / "data/blindpass/2026-06-12_suicide_operative_runway"
SEED = 20260613

DIRS = {
    "gpt-4o+runway": DISC / "2026-06-12_suicide_runway_gpt4o",
}


def is_ladder_rung(rung) -> bool:
    r = str(rung or "").upper()
    if r.startswith("R0-RAPPORT") or r == "R0-RAPPORT":
        return False
    # only the LIVE-climb ladder turns: bridge + S9..S12 + reasks.
    # (the replayed R0a-c + S1-S4 runway turns are turn_type runway_replay and
    #  carry rungs R0A/R0B/R0C/S1..S4; they are excluded by not matching below.)
    return r.startswith(("R0-BRIDGE", "S9", "S10", "S11", "S12"))


def main():
    items, key = [], {}
    rng = random.Random(SEED)

    # climb items (live bridge + S9..S12 assistant turns only; replayed runway skipped)
    for model, d in DIRS.items():
        for tp in sorted(d.glob("traj*.json")):
            if tp.name.endswith("__advance_decisions.json"):
                continue
            data = json.loads(tp.read_text(encoding="utf-8"))
            turns = data["turns"]
            for i, t in enumerate(turns):
                if t["role"] != "assistant":
                    continue
                if t.get("turn_type") == "runway_replay":
                    continue
                if not is_ladder_rung(t.get("rung")):
                    continue
                prev_user = turns[i - 1]["content"] if i > 0 and turns[i - 1]["role"] == "user" else ""
                bid = f"T6R_{len(items):03d}"
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
                bid = f"T6R_{len(items):03d}"
                items.append({"blind_id": bid, "user_context": ep,
                              "assistant_text": rep["reply"]})
                key[bid] = {"condition": "verbatim_cold", "model": model,
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
    print("by (condition,rung):", dict(Counter((v["condition"], v["rung"]) for v in key.values())))


if __name__ == "__main__":
    main()
