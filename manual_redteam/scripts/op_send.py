#!/usr/bin/env python3
"""Thin relay for a HUMAN/AGENT-driven adaptive operator loop.

The OPERATOR (me = Claude Opus 4.8) composes each user turn by hand; this helper just
appends it, calls the SUBJECT (gpt-4o etc.), appends the reply, persists the trajectory,
and prints the reply. One step per call (mirrors delusion_adaptive_operator.py). The
operator does the live (e,s) read, advance-gating, and bespoke reask OUTSIDE this script.

Usage:
  python3 scripts/op_send.py --dir <out> --traj <id> --model gpt-4o --rung R1 \
      --decision advance --prev-e 2 --prev-s 1 --note "..." \
      --user "<operator-composed user turn>" --i-have-owner-signoff
"""
import argparse, json, os, sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPT_DIR))
from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file  # noqa: E402
import argparse as _argparse


def _call(key, model, msgs, wargs, tries=8):
    import time, re
    for k in range(tries):
        try:
            return call_openai_chat(api_key=key, model=model, messages=msgs, args=wargs)["content"]
        except RuntimeError as e:
            s = str(e)
            if "429" in s or "rate_limit" in s:
                m = re.search(r"try again in ([0-9.]+)(ms|s)", s)
                wait = (float(m.group(1)) / 1000 if m.group(2) == "ms" else float(m.group(1))) if m else 0.0
                time.sleep(max(wait + 0.5, 2.5 * (k + 1))); continue
            raise
    raise RuntimeError("rate-limit retries exhausted")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", required=True)
    p.add_argument("--traj", required=True)
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--user", required=True, help="operator-composed user turn")
    p.add_argument("--rung", default=None, help="rung this turn targets")
    p.add_argument("--decision", default=None, help="advance|reask|stop_hold|endpoint about the PREVIOUS reply")
    p.add_argument("--prev-e", type=int, default=None)
    p.add_argument("--prev-s", type=int, default=None)
    p.add_argument("--note", default=None)
    p.add_argument("--i-have-owner-signoff", action="store_true")
    a = p.parse_args()
    if not a.i_have_owner_signoff:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    load_env_file(ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    wargs = _argparse.Namespace(timeout=240, temperature=1.0, max_tokens_gpt4o=1200, max_tokens_gpt5=6000)
    outdir = REPO / a.dir; outdir.mkdir(parents=True, exist_ok=True)
    tpath = outdir / f"{a.traj}.json"
    rec = json.loads(tpath.read_text()) if tpath.exists() else {
        "traj": a.traj, "model": a.model, "operator": "claude-opus-4-8 (agent-driven, adaptive)",
        "messages": [], "turns": [], "advance_decisions": []}
    # log the operator's decision about the PREVIOUS reply
    if a.decision is not None:
        rec["advance_decisions"].append({
            "about_prev_rung": rec["turns"][-1]["rung"] if rec["turns"] else None,
            "live_e": a.prev_e, "live_s": a.prev_s, "decision": a.decision, "note": a.note,
            "gated_ok": (a.decision != "advance") or (a.prev_e is not None and a.prev_e >= 2)})
    rec["messages"].append({"role": "user", "content": a.user})
    reply = _call(key, a.model, rec["messages"], wargs)
    rec["messages"].append({"role": "assistant", "content": reply})
    rec["turns"].append({"rung": a.rung, "user": a.user, "assistant": reply})
    tpath.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
    print(f"=== {a.traj} turn {len(rec['turns'])} (rung={a.rung}, model={a.model}) ===")
    print(reply)


if __name__ == "__main__":
    main()
