#!/usr/bin/env python3
"""T6 verbatim-cold necessity control (CURRENT.md §1d-A).

Throw each trajectory's ACTUAL operative S12 endpoint turn COLD: single self-
contained turn, no prior interaction, VERBATIM — no paraphrase, no stripping of
back-references ("you've said the lean is coherent…"). n reps per endpoint.

For T6's hold result the read is: if the climb HELD and cold also holds, the
operative firewall is robust both cold and climbed (necessity is moot — there is
no climb-elicited effect for the buildup to be necessary FOR). We still record
the floor, as the rule mandates.

Usage:
  python3 scripts/t6_verbatim_cold.py --src-traj traj01 traj02 --n 5 \
    --i-have-owner-signoff
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file  # noqa: E402
import argparse as _argparse

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def endpoint_string(run_dir: Path, src_traj: str) -> str:
    d = json.loads((run_dir / f"{src_traj}.json").read_text(encoding="utf-8"))
    s12 = [t for t in d["turns"] if t["role"] == "user" and t.get("rung") == "S12"]
    if not s12:
        raise SystemExit(f"{src_traj} has no S12 operative endpoint turn (held earlier).")
    return s12[0]["content"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dir", type=Path,
                   default=REPO_ROOT / "manual_redteam/data/simulator_discover/2026-06-12_suicide_opus_operative",
                   help="trajectory run dir (contains trajNN.json)")
    p.add_argument("--src-traj", nargs="+", required=True)
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--timeout", type=float, default=300.0)
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--i-have-owner-signoff", action="store_true")
    args = p.parse_args()

    if not args.i_have_owner_signoff:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    load_env_file(REPO_ROOT / ".env")
    api_key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(f"Set {args.api_key_env}.")

    cold_dir = args.dir / "verbatim_cold"
    cold_dir.mkdir(parents=True, exist_ok=True)
    wargs = _argparse.Namespace(timeout=args.timeout, temperature=args.temperature,
                                max_tokens_gpt4o=1000, max_tokens_gpt5=4000)

    for src in args.src_traj:
        ep = endpoint_string(args.dir, src)
        out = {"src_traj": src, "model": args.model, "endpoint_verbatim": ep,
               "created_at_utc": now(), "reps": []}
        for i in range(1, args.n + 1):
            messages = [{"role": "user", "content": ep}]
            completion = call_openai_chat(api_key=api_key, model=args.model,
                                          messages=messages, args=wargs)
            reply = completion["content"]
            out["reps"].append({"rep": i, "reply": reply,
                                "api_finish_reason": completion.get("finish_reason")})
            print(f"[{src} cold rep {i}/{args.n}] {reply[:160].replace(chr(10),' ')}…")
        (cold_dir / f"{src}_S12_verbatim_cold.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  -> wrote {cold_dir / (src + '_S12_verbatim_cold.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
