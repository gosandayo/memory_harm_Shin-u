#!/usr/bin/env python3
# HISTORICAL/SUPERSEDED PROTOCOL: retains the retired Tier-4 behavior only to
# reproduce recorded runs. Do not use for new experiments; see docs/TIER4_LEGACY_INDEX.md.
"""Single subject-API turn helper for an ADAPTIVE, Claude-in-loop user simulator.

The operator (Claude) composes each user turn in response to the subject's reply
and decides advancement; this helper just maintains a transcript file and executes
ONE subject turn (append user msg -> call subject API -> append assistant reply),
printing the reply + token usage. Only the SUBJECT is an API call.

Tier-4 ceiling is the OPERATOR's responsibility (never solicit method/action); this
helper does not gate content — it records. Live scoring is semantic (done by the
operator/judge), NOT regex.

Usage:
  python3 scripts/subject_turn.py --transcript T.json --model gpt-4o --user "..." \
      --i-have-owner-signoff
  (omit --user with --init to just create an empty transcript)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from adaptive_strictness_profile_v3 import (  # noqa: E402
    call_openai_chat,
    is_gpt5_family,
    load_env_file,
)
import argparse as _argparse


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"created_at_utc": now(), "model": None, "turns": []}


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--transcript", type=Path, required=True)
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--user", default=None, help="operator-composed user message for this turn")
    p.add_argument("--rung", default=None, help="optional rung tag for this user turn")
    p.add_argument("--init", action="store_true", help="just create/empty the transcript")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--max-tokens", type=int, default=1000)
    p.add_argument("--max-completion-tokens", type=int, default=4000)
    p.add_argument("--timeout", type=float, default=180.0)
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--i-have-owner-signoff", action="store_true")
    args = p.parse_args()

    data = load(args.transcript)
    if args.init or data.get("model") is None:
        data["model"] = args.model
    if args.init and args.user is None:
        save(args.transcript, data)
        print(f"[init] transcript at {args.transcript} model={data['model']}")
        return 0

    if args.user is None:
        raise SystemExit("Provide --user (operator message) or --init.")
    if not args.i_have_owner_signoff:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")

    load_env_file(REPO_ROOT / ".env")
    api_key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY(_2).")

    model = data["model"]
    data["turns"].append({"role": "user", "rung": args.rung, "content": args.user})
    messages = [{"role": t["role"], "content": t["content"]} for t in data["turns"]]
    wargs = _argparse.Namespace(
        timeout=args.timeout, temperature=args.temperature,
        max_tokens_gpt4o=args.max_tokens, max_tokens_gpt5=args.max_completion_tokens,
    )
    completion = call_openai_chat(api_key=api_key, model=model, messages=messages, args=wargs)
    reply = completion["content"]
    usage = completion.get("usage") or {}
    data["turns"].append({
        "role": "assistant", "rung": args.rung, "content": reply,
        "api_usage": usage, "api_finish_reason": completion.get("finish_reason"),
    })
    save(args.transcript, data)

    n_user = sum(1 for t in data["turns"] if t["role"] == "user")
    n_asst = sum(1 for t in data["turns"] if t["role"] == "assistant")
    print(f"=== turn {n_asst} (rung={args.rung}) model={model} ===")
    print(f"[usage] prompt={usage.get('prompt_tokens')} total={usage.get('total_tokens')} "
          f"| user_turns={n_user} asst_turns={n_asst}")
    print("--- ASSISTANT REPLY ---")
    print(reply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
