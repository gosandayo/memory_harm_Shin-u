#!/usr/bin/env python3
"""Per-stage verbatim-cold for the t6 4o-mini SUICIDE trajectories.
For each trajectory and each scored stage (S9/S10/S11/S12), take the LAST user
turn at that base stage and throw it COLD (single turn, no history), n reps."""
from __future__ import annotations
import datetime as dt, glob, json, os, sys
from pathlib import Path
SCRIPT_DIR=Path(__file__).resolve().parent; REPO_ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(SCRIPT_DIR))
from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file
def base(r): return str(r or "").upper().replace("_","-").split("-REASK")[0]
EP=Path("data/simulator_discover/2026-06-12_suicide_opus_operative_4omini")
OUT=Path("data/simulator_discover/2026-06-18_suicide_perstage_cold_4omini")
STAGES=["S9","S10","S11","S12"]; MODEL="gpt-4o-mini"; N=5
def main():
    if "--i-have-owner-signoff" not in sys.argv: raise SystemExit("signoff")
    load_env_file(REPO_ROOT/".env"); key=os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    OUT.mkdir(parents=True,exist_ok=True)
    import argparse; wargs=argparse.Namespace(timeout=300,temperature=1.0,max_tokens_gpt4o=1000,max_tokens_gpt5=4000)
    for tf in sorted(glob.glob(str(EP/"traj*.json"))):
        if "advance" in tf: continue
        turns=json.loads(Path(tf).read_text())["turns"]; stem=Path(tf).stem
        for stg in STAGES:
            user=None
            for t in turns:
                if t["role"]=="user" and base(t.get("rung"))==stg: user=t["content"]
            if user is None: continue
            o={"model":MODEL,"src_traj":stem,"stage":stg,"endpoint_verbatim":user,
               "created_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),"reps":[]}
            for i in range(1,N+1):
                c=call_openai_chat(api_key=key,model=MODEL,messages=[{"role":"user","content":user}],args=wargs)
                o["reps"].append({"rep":i,"reply":c["content"]})
            (OUT/f"gpt4omini_{stem}_{stg}_cold.json").write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n")
            print(f"  {stem} {stg} done")
    print("done ->",OUT)
if __name__=="__main__": main()
