"""Replay saved user-side scripts against a target assistant model.

Input files are YAML exports with:

  id: ...
  source_run_id: ...
  turns:
    - id: 1
      user: ...

For each script, this runner sends the fixed user turns sequentially to the
target model, preserving the generated assistant responses as context. It does
not adapt the user turns to the target model's wording.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_USERSIDE_GLOB = (
    "manual_redteam/context_prefixes/"
    "2026-05-07_phaseB_live_adaptive_p16_gpt4omini_run*_userside.yaml"
)
DEFAULT_RUNS_ROOT = REPO_ROOT / "manual_redteam" / "data" / "runs"
API_WRAPPER_VERSION = "replay_userside_script_0.1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--userside-glob", default=DEFAULT_USERSIDE_GLOB)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--provider", choices=["openai", "anthropic"], default="openai")
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--max-tokens", type=int, default=1000)
    p.add_argument("--api-key-env", default=None)
    p.add_argument("--retry", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    return p.parse_args()


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO_ROOT / ".env")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        return None


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)


def make_caller(provider: str, api_key: str):
    if provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        def _call(model: str, messages: list[dict[str, str]], temperature: float, max_tokens: int) -> str:
            kwargs = {"model": model, "messages": messages}
            if model.startswith("gpt-5") or model.startswith("o1") or model.startswith("o3"):
                kwargs["max_completion_tokens"] = max_tokens
            else:
                kwargs["temperature"] = temperature
                kwargs["max_tokens"] = max_tokens
            response = client.chat.completions.create(**kwargs)
            return (response.choices[0].message.content or "").strip()

        return _call

    if provider == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        def _call(model: str, messages: list[dict[str, str]], temperature: float, max_tokens: int) -> str:
            response = client.messages.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
            return "".join(parts).strip()

        return _call

    raise ValueError(provider)


def call_with_retry(caller, args: argparse.Namespace, messages: list[dict[str, str]]) -> str:
    last_err: Exception | None = None
    for attempt in range(args.retry):
        try:
            return caller(args.model, messages, args.temperature, args.max_tokens)
        except Exception as exc:
            last_err = exc
            if attempt < args.retry - 1:
                print(f"  [retry {attempt + 1}/{args.retry - 1}] {type(exc).__name__}: {exc}")
                time.sleep(args.retry_delay * (attempt + 1))
    raise RuntimeError(f"API call failed after {args.retry} attempts: {last_err}")


def safe_stem(text: str) -> str:
    keep = []
    for ch in text:
        if ch.isalnum() or ch in ("-", "_"):
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep).strip("_")[:120]


def replay_one(
    *,
    caller,
    args: argparse.Namespace,
    output_dir: Path,
    userside_path: Path,
) -> None:
    script = load_yaml(userside_path)
    source_run_id = str(script.get("source_run_id") or userside_path.stem)
    replay_id = f"{safe_stem(source_run_id)}__{safe_stem(args.model)}"
    branch_dir = output_dir / "branches" / replay_id
    branch_dir.mkdir(parents=True, exist_ok=True)
    messages_path = branch_dir / "messages.jsonl"
    meta_path = branch_dir / "session_meta.yaml"

    if messages_path.exists():
        done_turns = {
            int(json.loads(line)["turn_id"])
            for line in messages_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line).get("role") == "assistant"
        }
    else:
        done_turns = set()

    meta = {
        "run_id": replay_id,
        "source_userside_path": str(userside_path),
        "source_run_id": source_run_id,
        "date_utc": now_iso(),
        "condition": "pure_userside_replay",
        "provider": args.provider,
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "git_commit": git_commit(),
        "api_wrapper_version": API_WRAPPER_VERSION,
        "postmortem": None,
    }
    dump_yaml(meta_path, meta)

    api_messages: list[dict[str, str]] = []
    if messages_path.exists():
        rows = [
            json.loads(line)
            for line in messages_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        api_messages = [{"role": row["role"], "content": row["content"]} for row in rows]

    for turn in script.get("turns", []):
        turn_id = int(turn["id"])
        if turn_id in done_turns:
            continue
        user_text = " ".join(str(turn["user"]).split()).strip()
        user_row = {
            "message_id": len(api_messages) + 1,
            "turn_id": turn_id,
            "role": "user",
            "content": user_text,
            "timestamp": now_iso(),
        }
        append_jsonl(messages_path, user_row)
        api_messages.append({"role": "user", "content": user_text})

        frozen_assistant = turn.get("assistant")
        if frozen_assistant is not None:
            assistant_text = " ".join(str(frozen_assistant).split()).strip()
            print(
                f"[{replay_id}] turn {turn_id}: frozen assistant "
                f"(no API call, len={len(assistant_text)})"
            )
            assistant_row = {
                "message_id": len(api_messages) + 1,
                "turn_id": turn_id,
                "role": "assistant",
                "content": assistant_text,
                "timestamp": now_iso(),
                "source": "frozen_prefix",
            }
        else:
            print(f"[{replay_id}] turn {turn_id}: calling {args.model}")
            assistant_text = call_with_retry(caller, args, api_messages)
            assistant_row = {
                "message_id": len(api_messages) + 1,
                "turn_id": turn_id,
                "role": "assistant",
                "content": assistant_text,
                "timestamp": now_iso(),
            }
        append_jsonl(messages_path, assistant_row)
        api_messages.append({"role": "assistant", "content": assistant_text})

    rows = [
        json.loads(line)
        for line in messages_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    final_assistant = next((row for row in reversed(rows) if row.get("role") == "assistant"), None)
    append_jsonl(output_dir / "replay_summary.jsonl", {
        "replay_id": replay_id,
        "source_run_id": source_run_id,
        "source_userside_path": str(userside_path),
        "provider": args.provider,
        "model": args.model,
        "n_turns": len(script.get("turns", [])),
        "messages_path": str(messages_path),
        "final_assistant_excerpt": (final_assistant or {}).get("content", "")[:800],
        "completed_at": now_iso(),
    })


def main() -> int:
    args = parse_args()
    load_dotenv_if_available()
    if args.api_key_env is None:
        args.api_key_env = "ANTHROPIC_API_KEY" if args.provider == "anthropic" else "OPENAI_API_KEY"
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Set {args.api_key_env} in environment or .env.")

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "branches").mkdir(exist_ok=True)
    dump_yaml(output_dir / "run_config.yaml", {
        "userside_glob": args.userside_glob,
        "provider": args.provider,
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "api_key_env": args.api_key_env,
        "condition": "pure_userside_replay",
        "started_at": now_iso(),
        "git_commit": git_commit(),
        "api_wrapper_version": API_WRAPPER_VERSION,
    })

    paths = sorted(REPO_ROOT.glob(args.userside_glob))
    if not paths:
        raise SystemExit(f"No userside scripts matched: {args.userside_glob}")

    caller = make_caller(args.provider, api_key)
    for path in paths:
        replay_one(caller=caller, args=args, output_dir=output_dir, userside_path=path)
    print(f"[done] {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
