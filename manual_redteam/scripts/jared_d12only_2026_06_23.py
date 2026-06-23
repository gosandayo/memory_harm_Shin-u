#!/usr/bin/env python3
"""Jared/DelusionEval external anchor (bot-endorses-delusion) on the D12-only blind set.
Separate series — never merged into the Haiku/fresh κ."""
import json, os, sys
from pathlib import Path
SD = Path(__file__).resolve().parent; REPO = SD.parents[0]; ROOT = SD.parents[1]
sys.path.insert(0, str(SD))
from adaptive_strictness_profile_v3 import load_env_file
from jared_judge import judge, CUTOFFS
load_env_file(ROOT/".env")
key = os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
CODE="bot-endorses-delusion"; CUT=CUTOFFS[CODE]
D=REPO/"data/blindpass/2026-06-23_d12only"
items=json.loads((D/"blind_items.json").read_text())
out=[]
for it in items:
    ctx=[{"role":"user","content":it["user_turn"]}]
    s,_=judge(key, it["assistant_reply"], ctx, CODE)
    out.append({"blind_id":it["blind_id"],"score":s,"present":(s or 0)>=CUT})
    print(f"  {it['blind_id']} score={s} present={(s or 0)>=CUT}")
(D/"jared_scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(f"\nCODE={CODE} cutoff={CUT} | present(operative)={sum(r['present'] for r in out)}/{len(out)}")
