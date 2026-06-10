"""Phase 2 pilot harness.

Subcommands:
  init <run_id>                 — create run dir, empty messages.jsonl
  send <run_id> <user_msg>      — append user message, call gpt-4o-mini with
                                   full history, save assistant response,
                                   print response
  show <run_id>                 — print conversation so far

Conversation state lives at
  manual_redteam/data/runs/<run_id>/messages.jsonl

Each line: {"role": "user"|"assistant", "content": str, "turn_index": int}
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
RUNS_DIR = ROOT / "data" / "runs"
DEFAULT_MODEL = "gpt-4o-mini"


def _load_dotenv() -> None:
    """Best-effort .env loader (no python-dotenv dependency). Reads KEY=VALUE
    pairs from <repo>/.env and injects into os.environ if not already set.

    Lets `python3 pilot_step.py send ...` work without an external
    `set -a; source .env; set +a` prefix, which matters because the bare
    invocation matches the allowlist pattern in .claude/settings.local.json
    while the compound form does not."""
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()


def _client() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY_2") or os.environ.get("OPENAI_API_KEY")
    if not key:
        print("No OPENAI_API_KEY_2 / OPENAI_API_KEY in env", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=key)


def _run_path(run_id: str) -> Path:
    return RUNS_DIR / run_id


def _messages_path(run_id: str) -> Path:
    return _run_path(run_id) / "messages.jsonl"


def _load_messages(run_id: str) -> list[dict]:
    path = _messages_path(run_id)
    if not path.exists():
        return []
    msgs = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                msgs.append(json.loads(line))
    return msgs


def _save_message(run_id: str, msg: dict) -> None:
    path = _messages_path(run_id)
    with path.open("a") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")


def _load_model(run_id: str) -> str:
    meta_path = _run_path(run_id) / "session_meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
            m = meta.get("model")
            if isinstance(m, str) and m:
                return m
        except json.JSONDecodeError:
            pass
    return DEFAULT_MODEL


def cmd_init(run_id: str, model: str = DEFAULT_MODEL) -> int:
    run_dir = _run_path(run_id)
    if run_dir.exists():
        print(f"run dir already exists: {run_dir}", file=sys.stderr)
        return 1
    run_dir.mkdir(parents=True)
    _messages_path(run_id).touch()
    meta = {
        "run_id": run_id,
        "model": model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rulebook": "manual_redteam/docs/phase2_operator_rulebook_v1.md",
        "spec": "docs/phase2_ladder_spec_2026_05_13.md",
    }
    (run_dir / "session_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"initialized: {run_dir} (model={model})")
    return 0


def cmd_send(run_id: str, user_msg: str) -> int:
    msgs = _load_messages(run_id)
    next_idx = len(msgs)
    user_record = {"role": "user", "content": user_msg, "turn_index": next_idx}
    _save_message(run_id, user_record)

    api_messages = [{"role": m["role"], "content": m["content"]} for m in msgs]
    api_messages.append({"role": "user", "content": user_msg})

    model = _load_model(run_id)
    client = _client()
    resp = client.chat.completions.create(
        model=model,
        messages=api_messages,
    )
    content = resp.choices[0].message.content
    asst_record = {
        "role": "assistant",
        "content": content,
        "turn_index": next_idx + 1,
        "finish_reason": resp.choices[0].finish_reason,
        "usage": {
            "prompt_tokens": resp.usage.prompt_tokens,
            "completion_tokens": resp.usage.completion_tokens,
        },
    }
    _save_message(run_id, asst_record)

    print(f"--- assistant turn {next_idx + 1} ---")
    print(content)
    return 0


def cmd_show(run_id: str) -> int:
    msgs = _load_messages(run_id)
    for m in msgs:
        print(f"--- {m['role']} turn {m.get('turn_index')} ---")
        print(m["content"])
        print()
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1
    cmd = argv[1]
    if cmd == "init" and len(argv) == 3:
        return cmd_init(argv[2])
    if cmd == "init" and len(argv) == 4:
        return cmd_init(argv[2], argv[3])
    if cmd == "send" and len(argv) == 4:
        return cmd_send(argv[2], argv[3])
    if cmd == "show" and len(argv) == 3:
        return cmd_show(argv[2])
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
