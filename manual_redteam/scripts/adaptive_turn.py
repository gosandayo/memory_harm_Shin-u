#!/usr/bin/env python3
"""One adaptive turn: append a composed user message to a session, call the
model, append+print the reply. Operator (caller) composes each user turn
adaptively from the prior reply. Defaults mirror the original gpt-4o-mini
replay parity: temp 1.0, max_tokens 1200, key OPENAI_API_KEY_2.

Usage: python3 adaptive_turn.py --session <messages.jsonl> --user "<text>" [--rung S12]
"""
import argparse, json, os, sys, pathlib

try:
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).resolve().parents[2] / ".env")
except Exception:
    pass
from openai import OpenAI

ap = argparse.ArgumentParser()
ap.add_argument("--session", required=True)
ap.add_argument("--user", required=True)
ap.add_argument("--rung", default="")
ap.add_argument("--model", default="gpt-4o-mini")
ap.add_argument("--temperature", type=float, default=1.0)
ap.add_argument("--max-tokens", type=int, default=1200)
ap.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
a = ap.parse_args()

p = pathlib.Path(a.session)
p.parent.mkdir(parents=True, exist_ok=True)
msgs = []
if p.exists():
    msgs = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

user_text = " ".join(a.user.split()).strip()
msgs.append({"role": "user", "content": user_text, "rung": a.rung})

key = os.environ.get(a.api_key_env)
if not key:
    sys.exit(f"{a.api_key_env} not set (.env)")
client = OpenAI(api_key=key)
api = [{"role": m["role"], "content": m["content"]} for m in msgs]
r = client.chat.completions.create(model=a.model, messages=api,
                                   temperature=a.temperature, max_tokens=a.max_tokens)
reply = (r.choices[0].message.content or "").strip()
msgs.append({"role": "assistant", "content": reply, "rung": a.rung, "model": a.model})
p.write_text("\n".join(json.dumps(m, ensure_ascii=False) for m in msgs) + "\n")

n_user = sum(1 for m in msgs if m["role"] == "user")
print(f"=== turn {n_user} (rung={a.rung}, model={a.model}) ASSISTANT REPLY ===")
print(reply)
