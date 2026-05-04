"""Append a stage_start or stage_decision event to stage_events.jsonl.

Subcommands:
  start    declare "from here, probing stage X"; snapshots user_hint from
           the ladder YAML referenced in session_meta.yaml.
  decision record an operational ladder-climbing decision after observing
           the exchange. Not a rubric verdict.

See manual_redteam/docs/manual_session_spec.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session_io import (
    append_jsonl,
    attempt_count_for_stage,
    find_stage,
    format_user_hint,
    latest_stage_start,
    load_jsonl,
    load_yaml,
    messages_for_stage_attempt,
    next_event_id,
    now_iso,
    run_paths,
)


LADDER_DECISIONS = ["held", "partial", "endorsed_after_context", "aborted"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", type=Path, required=True)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="Append a stage_start event.")
    s.add_argument("--stage-id", required=True)
    s.add_argument("--note", default="")

    d = sub.add_parser("decision", help="Append a stage_decision event.")
    d.add_argument("--stage-id", default=None,
                   help="Defaults to the latest active stage.")
    d.add_argument("--decision", required=True, choices=LADDER_DECISIONS)
    d.add_argument("--note", default="")
    return p.parse_args()


def cmd_start(run_dir: Path, stage_id: str, note: str) -> int:
    paths = run_paths(run_dir)
    meta = load_yaml(paths["meta"])
    ladder = load_yaml(Path(meta["ladder_path"]))
    stage = find_stage(ladder, stage_id)
    hint_snapshot = format_user_hint(stage)

    events = load_jsonl(paths["stage_events"])
    event_id = next_event_id(events)
    attempt = attempt_count_for_stage(events, stage_id) + 1

    row = {
        "event_id": event_id,
        "event_type": "stage_start",
        "stage_id": str(stage_id),
        "stage_name": stage.get("name"),
        "attempt": attempt,
        "user_hint_snapshot": hint_snapshot,
        "created_at": now_iso(),
        "note": note,
    }
    append_jsonl(paths["stage_events"], row)
    print(f"stage_start: stage_id={stage_id} attempt={attempt} event_id={event_id}")
    return 0


def cmd_decision(
    run_dir: Path, stage_id: str | None, decision: str, note: str
) -> int:
    paths = run_paths(run_dir)
    events = load_jsonl(paths["stage_events"])
    messages = load_jsonl(paths["messages"])

    active = latest_stage_start(events)
    if active is None:
        sys.exit("no stage_start events; nothing to decide on.")
    if stage_id is None:
        stage_id = active["stage_id"]
    elif str(stage_id) != str(active["stage_id"]):
        sys.exit(
            f"--stage-id {stage_id!r} does not match latest active stage "
            f"{active['stage_id']!r}; pass the active stage or omit --stage-id."
        )
    attempt = int(active["attempt"])

    relevant = messages_for_stage_attempt(messages, stage_id, attempt)
    if not relevant:
        sys.exit(
            f"no messages tagged stage_id={stage_id} attempt={attempt}; "
            f"cannot record a decision yet."
        )
    start_mid = min(int(m["message_id"]) for m in relevant)
    end_mid = max(int(m["message_id"]) for m in relevant)

    event_id = next_event_id(events)
    row = {
        "event_id": event_id,
        "event_type": "stage_decision",
        "stage_id": str(stage_id),
        "attempt": attempt,
        "start_message_id": start_mid,
        "end_message_id": end_mid,
        "ladder_decision": decision,
        "created_at": now_iso(),
        "note": note,
    }
    append_jsonl(paths["stage_events"], row)
    print(
        f"stage_decision: stage_id={stage_id} attempt={attempt} "
        f"messages=[{start_mid}..{end_mid}] decision={decision} "
        f"event_id={event_id}"
    )
    return 0


def main() -> int:
    args = parse_args()
    if not args.run_dir.exists():
        sys.exit(f"run dir not found: {args.run_dir}")
    if args.cmd == "start":
        return cmd_start(args.run_dir, args.stage_id, args.note)
    if args.cmd == "decision":
        return cmd_decision(args.run_dir, args.stage_id, args.decision, args.note)
    sys.exit(f"unknown subcommand: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
