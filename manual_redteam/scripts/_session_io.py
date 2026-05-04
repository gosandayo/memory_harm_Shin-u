"""Shared helpers for manual interaction session scripts.

Implements file I/O and ladder lookup primitives used by:
  create_run.py, manual_chat.py, log_stage_event.py,
  derive_cold_run.py, render_session.py

See manual_redteam/docs/manual_session_spec.md for the contract.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml


# ---------- Time / git ----------

def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parent,
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        return None


# ---------- Atomic JSONL append ----------

def append_jsonl(path: Path, row: dict) -> None:
    """Append one row as a JSON line, then flush + fsync."""
    line = json.dumps(row, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


# ---------- YAML ----------

def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


# ---------- Run paths ----------

def run_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "meta": run_dir / "session_meta.yaml",
        "messages": run_dir / "messages.jsonl",
        "stage_events": run_dir / "stage_events.jsonl",
        "annotations": run_dir / "annotations.yaml",
    }


# ---------- Id allocation ----------

def next_message_id(messages: list[dict]) -> int:
    if not messages:
        return 1
    return max(int(m["message_id"]) for m in messages) + 1


def next_event_id(events: list[dict]) -> int:
    if not events:
        return 1
    return max(int(e["event_id"]) for e in events) + 1


# ---------- Ladder lookup ----------

def find_stage(ladder: dict, stage_id: Any) -> dict:
    """Look up a stage by id. Accepts int or str ids; compares as strings."""
    target = str(stage_id)
    for s in ladder.get("stages", []):
        if str(s.get("id")) == target:
            return s
    raise KeyError(f"stage_id={stage_id!r} not found in ladder {ladder.get('id')!r}")


def format_user_hint(stage: dict) -> str:
    """Render a stage's user_hint (goal + watch_for) as a single text block.

    Returns empty string if no user_hint is defined.
    """
    hint = stage.get("user_hint")
    if not hint:
        return ""
    parts: list[str] = []
    goal = (hint.get("goal") or "").strip()
    watch = (hint.get("watch_for") or "").strip()
    if goal:
        parts.append(f"Goal:\n  {goal}")
    if watch:
        parts.append(f"Watch for:\n  {watch}")
    return "\n\n".join(parts)


# ---------- Stage state from event log ----------

def latest_stage_start(events: list[dict]) -> dict | None:
    """Return the most recent stage_start event, or None."""
    for ev in reversed(events):
        if ev.get("event_type") == "stage_start":
            return ev
    return None


def attempt_count_for_stage(events: list[dict], stage_id: Any) -> int:
    """How many stage_start events exist for this stage_id."""
    target = str(stage_id)
    return sum(
        1
        for ev in events
        if ev.get("event_type") == "stage_start"
        and str(ev.get("stage_id")) == target
    )


def messages_for_stage_attempt(
    messages: list[dict], stage_id: Any, attempt: int
) -> list[dict]:
    target = str(stage_id)
    return [
        m
        for m in messages
        if str(m.get("stage_id")) == target and int(m.get("attempt", 0)) == attempt
    ]


# ---------- Hint leak check ----------

def _normalize_ws(s: str) -> str:
    return " ".join(s.split())


def hint_leak_in_message(snapshot: str, message_content: str) -> bool:
    """True if a substantive hint line appears verbatim in the message.

    We check each hint line >= 40 chars (after whitespace normalization) as
    a substring of the (whitespace-normalized) message. This catches
    accidental copy-paste of goal / watch_for text into a user message
    while tolerating short shared phrases.
    """
    norm_msg = _normalize_ws(message_content)
    for raw_line in snapshot.splitlines():
        line = _normalize_ws(raw_line)
        if len(line) < 40:
            continue
        if line in norm_msg:
            return True
    return False
