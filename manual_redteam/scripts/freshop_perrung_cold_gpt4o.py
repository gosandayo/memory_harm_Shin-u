#!/usr/bin/env python3
"""(B) per-rung verbatim-cold for gpt-4o fresh-op trajectories.

For each broken gpt-4o trajectory and each intermediate scored rung (D1/D2/D3/D9),
take the LAST user turn at that base rung (the turn that elicited the achieved
reply) and throw it COLD (single turn, no history), n reps. D12 cold already
exists (data/.../fresh_op_cold) and is reused downstream.
"""
from __future__ import annotations
import datetime as dt, glob, json, os, sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPT_DIR))
from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file  # noqa: E402

def base(r): return str(r or "").upper().replace("_", "-").split("-REASK")[0]
EP_DIR = Path("data/simulator_discover/2026-06-16_delusion_fresh_op_gpt4o")
OUT = Path("data/simulator_discover/2026-06-16_delusion_fresh_op_perrung_cold_gpt4o")
RUNGS = ["D1", "D2", "D3", "D9"]
MODEL = "gpt-4o"
N = 5

def main() -> int:
    if "--i-have-owner-signoff" not in sys.argv:
        raise SystemExit("pass --i-have-owner-signoff")
    load_env_file(REPO_ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    OUT.mkdir(parents=True, exist_ok=True)
    import argparse
    wargs = argparse.Namespace(timeout=300.0, temperature=1.0, max_tokens_gpt4o=1000, max_tokens_gpt5=4000)
    for tf in sorted(glob.glob(str(EP_DIR / "traj*.json"))):
        if "advance_decision" in tf: continue
        turns = json.loads(Path(tf).read_text())["turns"]
        stem = Path(tf).stem
        # only broken trajectories reach D12
        if not any(t["role"] == "assistant" and base(t.get("rung")) == "D12" for t in turns):
            continue
        for rung in RUNGS:
            # LAST user turn at this base rung
            user = None
            for t in turns:
                if t["role"] == "user" and base(t.get("rung")) == rung:
                    user = t["content"]
            if user is None: continue
            out = {"model": MODEL, "src_traj": stem, "rung": rung,
                   "endpoint_verbatim": user, "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                   "reps": []}
            print(f"[{stem} {rung}] cold: {user[:90].replace(chr(10),' ')}…")
            for i in range(1, N + 1):
                c = call_openai_chat(api_key=key, model=MODEL, messages=[{"role": "user", "content": user}], args=wargs)
                out["reps"].append({"rep": i, "reply": c["content"]})
            (OUT / f"gpt4o_{stem}_{rung}_cold.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("done ->", OUT)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
