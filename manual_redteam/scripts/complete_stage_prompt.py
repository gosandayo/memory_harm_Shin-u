"""Append a stage prompt and collect one assistant response.

This is a small non-interactive helper for manual transcript branches. It uses
the latest run transcript as API context, appends one user message for a stage
or explicit prompt, calls the model, then appends the assistant response.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv
from openai import OpenAI


REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--max-tokens", type=int, default=1000)
    parser.add_argument("--prompt", default=None)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def stage_prompt(run_dir: Path, stage_id: str) -> str:
    meta_path = run_dir / "session_meta.yaml"
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    ladder_path = Path(meta["ladder_path"])
    if not ladder_path.is_absolute():
        ladder_path = REPO_ROOT / ladder_path
    ladder = yaml.safe_load(ladder_path.read_text(encoding="utf-8"))
    for stage in ladder["stages"]:
        if str(stage["id"]) == str(stage_id):
            return stage["probe"].strip()
    sys.exit(f"stage_id not found in ladder: {stage_id}")


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir
    if not run_dir.is_absolute():
        run_dir = REPO_ROOT / run_dir
    if not run_dir.exists():
        sys.exit(f"run dir not found: {run_dir}")

    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        sys.exit(f"{args.api_key_env} is not set")

    meta = yaml.safe_load((run_dir / "session_meta.yaml").read_text(encoding="utf-8"))
    model = meta["model"]
    temperature = meta["temperature"]
    prompt = args.prompt if args.prompt is not None else stage_prompt(run_dir, args.stage_id)

    messages_path = run_dir / "messages.jsonl"
    rows = load_jsonl(messages_path)
    next_id = max([int(row["message_id"]) for row in rows], default=0) + 1
    user_row = {
        "message_id": next_id,
        "role": "user",
        "content": prompt,
        "stage_id": str(args.stage_id),
        "attempt": args.attempt,
        "timestamp": now_iso(),
    }
    append_jsonl(messages_path, user_row)
    rows.append(user_row)

    api_messages = [
        {"role": row["role"], "content": row["content"]}
        for row in rows
    ]
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=api_messages,
        temperature=temperature,
        max_tokens=args.max_tokens,
    )
    content = response.choices[0].message.content or ""
    assistant_row = {
        "message_id": next_id + 1,
        "role": "assistant",
        "content": content,
        "stage_id": str(args.stage_id),
        "attempt": args.attempt,
        "timestamp": now_iso(),
    }
    append_jsonl(messages_path, assistant_row)
    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
