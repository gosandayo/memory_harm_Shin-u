#!/usr/bin/env python3
"""Replicate PsychosisBench's 16 scripted cases on OUR subject models (matched subjects
for the bakeoff), then score assistant turns with the EXTERNAL Jared judge
(bot-endorses-delusion). Each case = 12 sequential user prompts fed with growing history.
Scores stride-2 assistant turns (depths 0,2,4,6,8,10) for the harm-vs-depth curve."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPT_DIR))
from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file
from jared_judge import judge, CUTOFFS

CODE = "bot-endorses-delusion"; CUT = CUTOFFS[CODE]
CASES = json.loads((REPO / "external/psychosis-bench/data/test_cases.json").read_text())["cases"]
STRIDE = 2

def call_retry(key, model, msgs, wargs, tries=4):
    import time
    for k in range(tries):
        try:
            return call_openai_chat(api_key=key, model=model, messages=msgs, args=wargs)["content"]
        except Exception as e:
            if k == tries - 1: raise
            time.sleep(3 * (k + 1))

def main():
    if "--i-have-owner-signoff" not in sys.argv: raise SystemExit("signoff")
    import argparse
    MODELS = ["gpt-4o-mini", "gpt-5.4-mini"]
    OUT = REPO / "data/blindpass/2026-06-17_psychosis_rerun.json"
    if "--models" in sys.argv: MODELS = sys.argv[sys.argv.index("--models") + 1].split(",")
    if "--out" in sys.argv: OUT = REPO / sys.argv[sys.argv.index("--out") + 1]
    load_env_file(ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    wargs = argparse.Namespace(timeout=300, temperature=1.0, max_tokens_gpt4o=1000, max_tokens_gpt5=4000)
    rows = []
    for model in MODELS:
        for c in CASES:
            convo = []          # full transcript [{role,content}...]
            asst_turns = []     # (depth_idx, assistant_text, context_for_judge)
            for pi, prompt in enumerate(c["prompts"]):
                convo.append({"role": "user", "content": prompt})
                reply = call_retry(key, model, convo, wargs)
                convo.append({"role": "assistant", "content": reply})
                asst_turns.append((pi, reply, [dict(x) for x in convo[max(0, len(convo) - 1 - 3):len(convo) - 1]]))
            # score stride-2 assistant turns
            for depth, reply, ctx in asst_turns[::STRIDE]:
                s, _ = judge(key, reply, ctx, CODE)
                rows.append({"model": model, "case": c["name"], "theme": c["theme"], "cond": c["condition"],
                             "depth": depth, "score": s, "present": (s or 0) >= CUT})
            print(f"  {model:12} {c['name'][:34]:34} done ({len(asst_turns)} turns)")
            OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")  # incremental save per CASE
    print(f"wrote {OUT} ({len(rows)} scored turns)")

if __name__ == "__main__":
    main()
