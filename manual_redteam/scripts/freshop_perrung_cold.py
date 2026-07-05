#!/usr/bin/env python3
"""Generalized per-rung verbatim-cold for fresh-op trajectories (any model).
For each trajectory that reached D12, throw each intermediate rung's LAST user
turn (D1/D2/D3/D9) cold, n reps. Usage: --model gpt-4o-mini --dir <epdir>"""
from __future__ import annotations
import argparse, datetime as dt, glob, json, os, sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPT_DIR))
from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file
def base(r): return str(r or "").upper().replace("_","-").split("-REASK")[0]
RUNGS=["D1","D2","D3","D9"]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model",required=True); p.add_argument("--dir",required=True)
    p.add_argument("--out",required=True); p.add_argument("--slug",required=True)
    p.add_argument("--n",type=int,default=5); p.add_argument("--i-have-owner-signoff",action="store_true")
    a=p.parse_args()
    if not a.i_have_owner_signoff: raise SystemExit("signoff")
    load_env_file(REPO_ROOT/".env")
    key=os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    wargs=argparse.Namespace(timeout=300.0,temperature=1.0,max_tokens_gpt4o=1000,max_tokens_gpt5=4000)
    for tf in sorted(glob.glob(str(Path(a.dir)/"traj*.json"))):
        if "advance_decision" in tf: continue
        turns=json.loads(Path(tf).read_text())["turns"]; stem=Path(tf).stem
        if not any(t["role"]=="assistant" and base(t.get("rung"))=="D12" for t in turns): continue
        for rung in RUNGS:
            user=None
            for t in turns:
                if t["role"]=="user" and base(t.get("rung"))==rung: user=t["content"]
            if user is None: continue
            o={"model":a.model,"src_traj":stem,"rung":rung,"endpoint_verbatim":user,
               "created_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),"reps":[]}
            for i in range(1,a.n+1):
                c=call_openai_chat(api_key=key,model=a.model,messages=[{"role":"user","content":user}],args=wargs)
                o["reps"].append({"rep":i,"reply":c["content"]})
            (out/f"{a.slug}_{stem}_{rung}_cold.json").write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n")
            print(f"  {stem} {rung} done")
    print("done ->",out)
if __name__=="__main__": main()
