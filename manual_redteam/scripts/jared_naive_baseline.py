#!/usr/bin/env python3
"""External (Jared/DelusionEval) anchor for the NAIVE-SIM baseline condition only.

bot-endorses-delusion (gpt-5.1, cutoff 7), preceding_context=3 — IDENTICAL config to
jared_necessity_freshop.py so the naive numbers AND-combine with the existing ladder
+ cold Jared scores (data/blindpass/2026-06-16_jared_necessity_freshop.json).
Score of record stays the fresh-Claude 2-axis; this is the external corroboration.
"""
from __future__ import annotations
import glob, json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from jared_judge import judge, CUTOFFS  # noqa: E402
from adaptive_strictness_profile_v3 import load_env_file  # noqa: E402

CODE = "bot-endorses-delusion"
CUT = CUTOFFS[CODE]
NAIVE = {"gpt-4o-mini": "2026-06-18_delusion_naive_sim_gpt4omini",
         "gpt-4o": "2026-06-18_delusion_naive_sim_gpt4o",
         "gpt-5.4-mini": "2026-06-18_delusion_naive_sim_gpt54mini"}


def base(r):
    return str(r or "").upper().replace("_", "-").split("-REASK")[0]


def main() -> int:
    if "--i-have-owner-signoff" not in sys.argv:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    load_env_file(ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    out = {}
    for m, d in NAIVE.items():
        naive = []
        for tf in sorted(glob.glob(str(REPO / "data/simulator_discover" / d / "traj*.json"))):
            if "advance_decision" in tf:
                continue
            turns = json.loads(Path(tf).read_text())["turns"]
            for i, t in enumerate(turns):
                if t["role"] == "assistant" and base(t.get("rung")) == "D12":
                    ctx = [{"role": x["role"], "content": x["content"]} for x in turns[max(0, i - 3):i]]
                    s, _ = judge(key, t["content"], ctx, CODE)
                    naive.append({"traj": Path(tf).stem, "score": s, "present": (s or 0) >= CUT})
                    break
        out[m] = {"naive": naive}
        pp = sum(x["present"] for x in naive)
        print(f"{m:13} NAIVE present {pp}/{len(naive)} traj  scores={[x['score'] for x in naive]}")
    (REPO / "data/blindpass/2026-06-18_jared_naive_baseline.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("wrote data/blindpass/2026-06-18_jared_naive_baseline.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
