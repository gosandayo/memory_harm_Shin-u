#!/usr/bin/env python3
"""External Jared anchor for the GRANDIOSE FIXED-TEST-PROMPT baseline.

Sibling of scripts/jared_fixedprobe.py. bot-grand-significance (gpt-5.1, cutoff 7).
Context-isolated: reply scored against the same fixed probe as eliciting context, so
all three conditions are scored identically. Reads the sealed grandiose blind set.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from jared_judge import judge, CUTOFFS  # noqa: E402
from adaptive_strictness_profile_v3 import load_env_file  # noqa: E402

CODE = "bot-grand-significance"
CUT = CUTOFFS[CODE]
D = REPO / "data/blindpass/2026-06-20_grandiose_fixedprobe"


def main():
    if "--i-have-owner-signoff" not in sys.argv:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    load_env_file(ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    items = json.loads((D / "blind_items.json").read_text())
    out = []
    for it in items:
        ctx = [{"role": "user", "content": it["user_turn"]}]
        s, _ = judge(key, it["assistant_reply"], ctx, CODE)
        out.append({"blind_id": it["blind_id"], "score": s, "present": (s or 0) >= CUT})
    (D / "jared_scores.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {D/'jared_scores.json'} ({len(out)} items); present {sum(x['present'] for x in out)}/{len(out)} (code={CODE}, cutoff={CUT})")


if __name__ == "__main__":
    main()
