#!/usr/bin/env python3
"""cold -> endpoint necessity under the EXTERNAL (Jared/DelusionEval) judge, delusion, 3 models.

For each model scores, with bot-endorses-delusion (gpt-5.1):
  (a) the operative D12 endpoint reply of each adaptive trajectory  (after the conversation)
  (b) the verbatim-cold replies (the same endpoint turn thrown cold) (no conversation)
Reports RAW scores + present(>=cutoff), endpoint at trajectory level, cold at item level.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from jared_judge import judge, CUTOFFS  # noqa: E402
from adaptive_strictness_profile_v3 import load_env_file  # noqa: E402

CODE = "bot-endorses-delusion"
CUT = CUTOFFS[CODE]


def base(r):
    return str(r or "").upper().replace("_", "-").split("-REASK")[0]


MODELS = {
    "gpt-4o-mini": {
        "ep": "data/simulator_discover/2026-06-16_delusion_gpt4omini_adaptive",
        "cold": "data/simulator_discover/2026-06-16_delusion_gpt4omini_adaptive_cold/gpt4omini_*_D12_cold.json",
    },
    "gpt-4o": {
        "ep": "data/simulator_discover/2026-06-06_delusion_gpt4o_adaptive",
        "cold": "data/simulator_discover/2026-06-16_delusion_verbatim_cold_aligned/gpt4o_*_D12_cold.json",
    },
    "gpt-5.4-mini": {
        "ep": "data/simulator_discover/2026-06-06_delusion_gpt54mini_adaptive",
        "cold": "data/simulator_discover/2026-06-16_delusion_verbatim_cold_aligned/gpt54mini_*_D12_cold.json",
    },
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--i-have-owner-signoff", action="store_true")
    a = p.parse_args()
    if not a.i_have_owner_signoff:
        raise SystemExit("signoff")
    load_env_file(ROOT / ".env")
    key = os.environ.get(a.api_key_env) or os.environ.get("OPENAI_API_KEY")
    out = {}
    for m, cfg in MODELS.items():
        ep = []
        for tf in sorted(glob.glob(str(REPO / cfg["ep"] / "traj*.json"))):
            if "advance_decision" in tf:
                continue
            turns = json.loads(Path(tf).read_text())["turns"]
            for i, t in enumerate(turns):
                if t["role"] == "assistant" and base(t.get("rung")) == "D12":
                    ctx = [{"role": x["role"], "content": x["content"]} for x in turns[max(0, i - 3):i]]
                    s, _ = judge(key, t["content"], ctx, CODE)
                    ep.append({"traj": Path(tf).stem, "score": s, "present": (s or 0) >= CUT})
                    break
        cold = []
        for cf in sorted(glob.glob(str(REPO / cfg["cold"]))):
            d = json.loads(Path(cf).read_text())
            ctx = [{"role": "user", "content": d["endpoint_verbatim"]}]
            for rep in d["reps"]:
                s, _ = judge(key, rep["reply"], ctx, CODE)
                cold.append({"src": Path(cf).stem, "rep": rep["rep"], "score": s, "present": (s or 0) >= CUT})
        out[m] = {"endpoint": ep, "cold": cold}
        epp = sum(x["present"] for x in ep)
        cpp = sum(x["present"] for x in cold)
        print(f"{m:13} ENDPOINT {epp}/{len(ep)} present  scores={[x['score'] for x in ep]}  "
              f"|  COLD {cpp}/{len(cold)} present  max={max((x['score'] for x in cold), default=None)}")
    (REPO / "data/blindpass/2026-06-16_jared_necessity_delusion.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("wrote data/blindpass/2026-06-16_jared_necessity_delusion.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
