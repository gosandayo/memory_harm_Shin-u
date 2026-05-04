"""REPL for a manual interaction session.

Reads session_meta.yaml + messages.jsonl + stage_events.jsonl from --run-dir.
Loads the active stage from the latest stage_start event, displays its
user_hint to the operator, prompts for a user message, runs wrapper
assertions, sends the conversation to the API, and atomically appends both
the user message and the assistant response to messages.jsonl.

Operator types only. The wrapper does all persistence.

REPL commands:
  :hint    re-display the active stage's user_hint
  :stage   show active stage line
  :help    list commands
  :quit    exit (saves nothing extra; messages on disk are the truth)

See manual_redteam/docs/manual_session_spec.md.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from _session_io import (
    append_jsonl,
    find_stage,
    format_user_hint,
    hint_leak_in_message,
    latest_stage_start,
    load_jsonl,
    load_yaml,
    next_message_id,
    now_iso,
    run_paths,
)


SEP = "─" * 65


# ---------- Assertions ----------

def assert_api_messages(api_messages: list[dict], hint_snapshot: str) -> None:
    if not api_messages:
        raise AssertionError("API messages list is empty.")
    for i, m in enumerate(api_messages):
        if m.get("role") not in ("user", "assistant"):
            raise AssertionError(
                f"message[{i}] has role={m.get('role')!r}; only "
                f"user/assistant allowed."
            )
    if api_messages[0]["role"] != "user":
        raise AssertionError(
            f"first API message has role={api_messages[0]['role']!r}; "
            f"must be user."
        )
    if hint_snapshot:
        for i, m in enumerate(api_messages):
            if hint_leak_in_message(hint_snapshot, m["content"]):
                raise AssertionError(
                    f"message[{i}] contains a verbatim line from the active "
                    f"stage's user_hint snapshot. Hints must not appear in "
                    f"API messages."
                )


# ---------- Recovery ----------

def recover_orphan_user(messages_path: Path, messages: list[dict]) -> list[dict]:
    """If messages.jsonl ends with a user message and no assistant response,
    prompt the operator for a recovery action and return the (possibly
    truncated) messages list."""
    if not messages:
        return messages
    last = messages[-1]
    if last["role"] != "user":
        return messages

    print("[recovery] messages.jsonl ends with a user message")
    print(f"  message_id={last['message_id']} stage={last.get('stage_id')} "
          f"attempt={last.get('attempt')}")
    print("  no assistant response on disk.")
    print()
    print("  [r] regenerate assistant response from current messages")
    print("  [d] drop the orphan user message")
    print("  [a] abort and inspect manually")
    while True:
        choice = input("> ").strip().lower()
        if choice == "r":
            return messages  # caller will see last role==user and call API once
        if choice == "d":
            # Rewrite messages.jsonl without the orphan.
            kept = messages[:-1]
            tmp = messages_path.with_suffix(".jsonl.tmp")
            with tmp.open("w", encoding="utf-8") as f:
                for m in kept:
                    import json as _j
                    f.write(_j.dumps(m, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
            tmp.replace(messages_path)
            print(f"  dropped orphan message_id={last['message_id']}.")
            return kept
        if choice == "a":
            sys.exit("aborted by operator.")
        print("  unrecognized choice; type r, d, or a.")


# ---------- API caller ----------

def make_caller(model: str):
    """Return callable(api_messages, temperature, max_tokens) -> str.

    Provider is inferred from model id: 'gpt' -> openai, 'claude' -> anthropic.
    """
    if "gpt" in model.lower() or model.lower().startswith("o"):
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        def _call(msgs, temperature, max_tokens):
            resp = client.chat.completions.create(
                model=model,
                messages=msgs,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()
        return _call

    if "claude" in model.lower():
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        def _call(msgs, temperature, max_tokens):
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=msgs,
            )
            parts = [b.text for b in resp.content if getattr(b, "type", "") == "text"]
            return "".join(parts).strip()
        return _call

    raise SystemExit(f"cannot infer provider from model={model!r}")


def call_with_retry(caller, msgs, temperature, max_tokens, retries, delay):
    last_err: Exception | None = None
    for i in range(retries):
        try:
            return caller(msgs, temperature, max_tokens)
        except Exception as e:
            last_err = e
            if i < retries - 1:
                print(f"[api error: {e}] retrying in {delay}s...")
                time.sleep(delay)
    raise SystemExit(f"API failed after {retries} attempts: {last_err}")


# ---------- Display ----------

def show_stage_header(stage_event: dict) -> None:
    print()
    print(SEP)
    print(f"Stage {stage_event['stage_id']} — {stage_event.get('stage_name','?')}"
          f"  (attempt {stage_event['attempt']})")
    snapshot = stage_event.get("user_hint_snapshot") or "(no user_hint defined)"
    print("Hint:")
    for line in snapshot.splitlines():
        print(f"  {line}" if line else "")
    print(SEP)


# ---------- Main loop ----------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    return p.parse_args()


def read_user_input() -> str:
    """Read a possibly multi-line user message.

    First line begins immediately. Submit by entering a line with just '.' on
    it. Submit empty (no content) is rejected. Special commands starting with
    ':' are returned as-is on the first line.
    """
    print("user > (end with a single '.' on its own line)")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            return ":quit"
        if not lines and line.startswith(":"):
            return line.strip()
        if line.strip() == ".":
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    return text


def main() -> int:
    args = parse_args()
    paths = run_paths(args.run_dir)
    if not paths["meta"].exists():
        sys.exit(f"session_meta.yaml not found in {args.run_dir}")
    meta = load_yaml(paths["meta"])

    if meta.get("interface") != "api":
        sys.exit(f"manual_chat.py only supports interface=api "
                 f"(this run has interface={meta.get('interface')!r}).")

    ladder = load_yaml(Path(meta["ladder_path"]))
    messages = load_jsonl(paths["messages"])
    events = load_jsonl(paths["stage_events"])

    # Distinguish two reasons messages.jsonl might end with a user message:
    #   (a) derived run (cold_probe / replay_probe) seeded by derive_cold_run.py
    #       and not yet completed -> auto-regenerate, no prompt
    #   (b) accumulated_context run with an orphan from a crashed API call
    #       -> operator recovery prompt
    pending_assistant = False
    derived = meta.get("condition") in ("cold_probe", "replay_probe")
    has_assistant = any(m["role"] == "assistant" for m in messages)
    seeded_for_regen = (
        derived and not has_assistant and messages and messages[-1]["role"] == "user"
    )
    if seeded_for_regen:
        print(f"[derived run: {meta['condition']}] auto-regenerating "
              f"assistant for trailing user message (id={messages[-1]['message_id']}).")
        pending_assistant = True
    else:
        messages = recover_orphan_user(paths["messages"], messages)
        if messages and messages[-1]["role"] == "user":
            pending_assistant = True  # operator chose [r]: regenerate

    caller = make_caller(meta["model"])
    temperature = float(meta["temperature"])

    print(f"[run]  {meta['run_id']}  ({meta['condition']})")
    print(f"[model] {meta['model']}  T={temperature}")
    print(f"[messages on disk] {len(messages)}")

    while True:
        events = load_jsonl(paths["stage_events"])  # re-read (operator may have logged)
        active = latest_stage_start(events)
        if active is None:
            print("\nno active stage. run:")
            print("  python scripts/log_stage_event.py start "
                  f"--run-dir {args.run_dir} --stage-id <id>")
            return 1

        # Confirm the active stage exists in the current ladder (sanity).
        try:
            find_stage(ladder, active["stage_id"])
        except KeyError as e:
            sys.exit(str(e))

        show_stage_header(active)

        # If we have a pending assistant from recovery, skip user input this round.
        if pending_assistant:
            user_text = None
            pending_assistant = False
        else:
            raw = read_user_input()
            if raw == ":quit":
                print("bye.")
                return 0
            if raw == ":help":
                print("commands: :hint  :stage  :help  :quit")
                continue
            if raw == ":hint":
                continue  # header already shown, just loop back to reprint
            if raw == ":stage":
                print(f"active: stage {active['stage_id']} attempt {active['attempt']}")
                continue
            if not raw:
                print("(empty input ignored)")
                continue
            user_text = raw

            # Append user message first; if API fails, the user message
            # remains on disk and is recovered next startup.
            messages = load_jsonl(paths["messages"])
            user_row = {
                "message_id": next_message_id(messages),
                "role": "user",
                "content": user_text,
                "stage_id": str(active["stage_id"]),
                "attempt": int(active["attempt"]),
                "timestamp": now_iso(),
            }
            # Build provisional API payload for assertions BEFORE writing.
            api_payload = [
                {"role": m["role"], "content": m["content"]} for m in messages
            ] + [{"role": "user", "content": user_text}]
            try:
                assert_api_messages(api_payload, active.get("user_hint_snapshot", ""))
            except AssertionError as e:
                print(f"[assertion failed] {e}")
                print("user message NOT written. fix and retry.")
                continue

            append_jsonl(paths["messages"], user_row)
            messages.append(user_row)

        # Send to API.
        api_payload = [
            {"role": m["role"], "content": m["content"]} for m in messages
        ]
        # Re-assert post-write (should still hold).
        assert_api_messages(api_payload, active.get("user_hint_snapshot", ""))

        print("\n[calling api...]")
        assistant_text = call_with_retry(
            caller, api_payload, temperature, args.max_tokens,
            args.retries, args.retry_delay,
        )

        messages = load_jsonl(paths["messages"])
        assistant_row = {
            "message_id": next_message_id(messages),
            "role": "assistant",
            "content": assistant_text,
            "stage_id": str(active["stage_id"]),
            "attempt": int(active["attempt"]),
            "timestamp": now_iso(),
        }
        append_jsonl(paths["messages"], assistant_row)

        print()
        print("assistant >")
        print(assistant_text)
        print()


if __name__ == "__main__":
    raise SystemExit(main())
