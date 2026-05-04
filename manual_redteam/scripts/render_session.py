"""Render messages.jsonl + stage_events.jsonl as readable plain text.

On-demand only. The output is not committed; transcript.md does not exist.

Usage:
  python scripts/render_session.py --run-dir <dir>           # to stdout
  python scripts/render_session.py --run-dir <dir> --out f.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session_io import (
    load_jsonl,
    load_yaml,
    run_paths,
)


SEP = "=" * 65
SUB = "-" * 65


def render_header(meta: dict) -> list[str]:
    out = [SEP, f"run_id:           {meta.get('run_id')}",
           f"condition:        {meta.get('condition')}",
           f"model:            {meta.get('model')}  T={meta.get('temperature')}",
           f"interface:        {meta.get('interface')}  "
           f"memory={meta.get('interface_memory_state')}",
           f"operator:         {meta.get('operator')}",
           f"date_utc:         {meta.get('date_utc')}",
           f"ladder:           {meta.get('ladder_path')} "
           f"({meta.get('ladder_version')})",
           f"rubric:           {meta.get('rubric_path')} "
           f"({meta.get('rubric_version')})",
           f"git_commit:       {meta.get('git_commit')}",
           f"comparison_group: {meta.get('comparison_group_id')}",
           f"paired_with:      {meta.get('paired_with')}"]
    if meta.get("source_run_id"):
        out += [f"source_run_id:    {meta.get('source_run_id')}",
                f"source_message:   {meta.get('source_message_id')} "
                f"(stage {meta.get('source_stage_id')})"]
    out += [f"intent:           {meta.get('intent')}", SEP, ""]
    return out


def render_body(messages: list[dict], events: list[dict]) -> list[str]:
    """Interleave stage_start / stage_decision events with messages by id."""
    out: list[str] = []

    # Index stage_start by the smallest message_id with the same stage+attempt
    # that follows it; we'll just emit stage_start before the first message it
    # tags, and stage_decision after end_message_id.
    starts_by_first_msg: dict[int, list[dict]] = {}
    decisions_by_end_msg: dict[int, list[dict]] = {}

    # stage_start: find first message_id matching its (stage_id, attempt).
    msg_index_for_stage_attempt: dict[tuple[str, int], int] = {}
    for m in messages:
        key = (str(m.get("stage_id")), int(m.get("attempt", 0)))
        if key not in msg_index_for_stage_attempt:
            msg_index_for_stage_attempt[key] = int(m["message_id"])

    for ev in events:
        if ev["event_type"] == "stage_start":
            key = (str(ev["stage_id"]), int(ev["attempt"]))
            anchor = msg_index_for_stage_attempt.get(key)
            if anchor is None:
                # No messages yet for this start; place at start of stream.
                anchor = -1
            starts_by_first_msg.setdefault(anchor, []).append(ev)
        elif ev["event_type"] == "stage_decision":
            decisions_by_end_msg.setdefault(int(ev["end_message_id"]), []).append(ev)

    # Pre-message stage_starts (anchor == -1) emitted first.
    for ev in starts_by_first_msg.get(-1, []):
        out += render_stage_start(ev)

    for m in messages:
        mid = int(m["message_id"])
        for ev in starts_by_first_msg.get(mid, []):
            out += render_stage_start(ev)
        out += render_message(m)
        for ev in decisions_by_end_msg.get(mid, []):
            out += render_stage_decision(ev)

    return out


def render_stage_start(ev: dict) -> list[str]:
    lines = [SUB, f"[stage_start] stage {ev['stage_id']}  attempt {ev['attempt']}"
             f"  ({ev.get('stage_name','?')})"]
    if ev.get("note"):
        lines.append(f"  note: {ev['note']}")
    snap = ev.get("user_hint_snapshot") or ""
    if snap:
        lines.append("  hint:")
        for ln in snap.splitlines():
            lines.append(f"    {ln}" if ln else "")
    lines.append(SUB)
    lines.append("")
    return lines


def render_stage_decision(ev: dict) -> list[str]:
    lines = [SUB,
             f"[stage_decision] stage {ev['stage_id']}  attempt {ev['attempt']}"
             f"  decision={ev['ladder_decision']}",
             f"  messages: [{ev['start_message_id']}..{ev['end_message_id']}]"]
    if ev.get("note"):
        lines.append(f"  note: {ev['note']}")
    lines.append(SUB)
    lines.append("")
    return lines


def render_message(m: dict) -> list[str]:
    turn = (int(m["message_id"]) + 1) // 2
    role = m["role"]
    header = (f"[turn {turn}] [msg {m['message_id']}] {role}"
              f"  (stage {m.get('stage_id')} att {m.get('attempt')})")
    out = [header]
    for ln in (m["content"] or "").splitlines() or [""]:
        out.append(f"  {ln}")
    out.append("")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    paths = run_paths(args.run_dir)
    if not paths["meta"].exists():
        sys.exit(f"session_meta.yaml not found in {args.run_dir}")
    meta = load_yaml(paths["meta"])
    messages = load_jsonl(paths["messages"])
    events = load_jsonl(paths["stage_events"])

    lines = render_header(meta) + render_body(messages, events)
    text = "\n".join(lines) + "\n"

    if args.out is None:
        sys.stdout.write(text)
    else:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
