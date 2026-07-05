#!/usr/bin/env python3
"""Seed the +runway cell transcript for gpt-4o (T6 dose probe).

Fixed-replay (CURRENT.md §1b): inject gpt-4o's OWN genuine S1-S4 endorsement
turns (Run B r01, turns 0-13 = R0a-c rapport + S1-S4 disclosure runway) as
pre-existing conversation history. These are NOT new API calls — they are the
model's already-recorded replies, replayed so the live bridge->S9..S12 climb
runs with the prior-endorsement runway in context.

⚠️ The seed is gpt-4o's OWN transcript (borrowing another model's would be a
context-claim confound). S5-S7 are dropped (orthogonal med-action guardrail).

Usage: python3 scripts/seed_t6_runway_gpt4o.py --traj traj01
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_SRC = ROOT / "data/simulator_discover/2026-06-04_s1s7_pilot/runB_gpt4o_s1s7_r01.yaml"
OUT_DIR = ROOT / "data/simulator_discover/2026-06-12_suicide_runway_gpt4o"

# turns 0-13 = R0a/R0b/R0c + S1/S2/S3/S4 (S4 endorsed qualified at turn 13).
RUNWAY_RUNGS = ["R0a", "R0a", "R0b", "R0b", "R0c", "R0c",
                "S1", "S1", "S2", "S2", "S3", "S3", "S4", "S4"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--traj", default="traj01")
    args = p.parse_args()

    src = json.loads(SEED_SRC.read_text(encoding="utf-8"))
    seed_turns = src["turns"][:14]
    assert len(seed_turns) == len(RUNWAY_RUNGS)

    turns = []
    for t, rung in zip(seed_turns, RUNWAY_RUNGS):
        turns.append({
            "role": t["role"], "rung": rung,
            "turn_type": "runway_replay",
            "content": t["content"],
            "replayed_from": "runB_gpt4o_s1s7_r01",
        })

    data = {
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "model": "gpt-4o", "traj": args.traj,
        "arm": "suicide", "endpoint_type": "operative_claim",
        "condition": "plus_runway",
        "operator": "claude-opus-adaptive",
        "scenario": "blue_door",
        "runway": "fixed_replay S1-S4 (Run B r01, gpt-4o own); S5-S7 excluded",
        "note": "dose cell vs the no-runway suicide-only cell (2026-06-12_suicide_opus_operative)",
        "turns": turns,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{args.traj}.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"seeded {out} with {len(turns)} replayed runway turns (R0a-c + S1-S4)")


if __name__ == "__main__":
    main()
