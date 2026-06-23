#!/usr/bin/env python3
"""External Jared anchor for the ORACLE DEPTH-CURVE blind set (context-isolated).

Mirror of jared_fixedprobe.py exactly (bot-endorses-delusion, gpt-5.1, cutoff),
pointed at the 2026-06-22_oracle_depth blind set so the Jared anchor is scored under
the SAME context-isolated protocol as the fresh-Claude judges (only user_turn + reply,
no depth prefix) -> directly comparable, never merged into the fresh series.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from jared_judge import judge, CUTOFFS  # noqa: E402
from adaptive_strictness_profile_v3 import load_env_file  # noqa: E402

CODE = "bot-endorses-delusion"
CUT = CUTOFFS[CODE]
D = REPO / "data/blindpass/2026-06-22_oracle_depth"


def main():
    if "--i-have-owner-signoff" not in sys.argv:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    load_env_file(ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    items = json.loads((D / "blind_items.json").read_text())
    out = []
    for i, it in enumerate(items):
        ctx = [{"role": "user", "content": it["user_turn"]}]
        s, _ = judge(key, it["assistant_reply"], ctx, CODE)
        out.append({"blind_id": it["blind_id"], "score": s, "present": (s or 0) >= CUT})
        if (i + 1) % 25 == 0:
            print(f"  ...{i+1}/{len(items)}", flush=True)
    (D / "jared_scores.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {D/'jared_scores.json'} ({len(out)} items); CODE={CODE} cutoff={CUT}; "
          f"present {sum(x['present'] for x in out)}/{len(out)}")


if __name__ == "__main__":
    main()
