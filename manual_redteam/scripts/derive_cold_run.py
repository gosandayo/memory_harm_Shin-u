"""Scaffold a cold_probe or replay_probe run from a source accumulated run.

cold_probe   the target user message at --source-message-id is extracted
             into a fresh run with no prior context.
replay_probe all messages with id <= --source-message-id are copied (with
             renumbered ids starting at 1) into a fresh run, *including*
             the target user message. manual_chat.py auto-regenerates the
             assistant response for the trailing user message; the prompt
             is held identical to the source.

Updates the source run's session_meta.yaml `paired_with` list.

See manual_redteam/docs/manual_session_spec.md.
"""

from __future__ import annotations

import argparse
import contextlib
import sys
import uuid
from pathlib import Path

from _session_io import (
    append_jsonl,
    dump_yaml,
    git_commit,
    load_jsonl,
    load_yaml,
    now_iso,
    run_paths,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNS_ROOT = REPO_ROOT / "manual_redteam" / "data" / "runs" / "manual"
API_WRAPPER_VERSION = "0.1.0"


@contextlib.contextmanager
def source_update_lock(source_run_dir: Path):
    """Serialize source session_meta.yaml paired_with updates.

    Deriving cold and replay siblings in parallel can otherwise lose one
    paired_with entry via last-writer-wins YAML updates.
    """
    lock_path = source_run_dir / ".derive_cold_run.lock"
    with lock_path.open("w", encoding="utf-8") as f:
        try:
            import fcntl

            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            try:
                import fcntl

                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-run-dir", type=Path, required=True)
    p.add_argument("--source-message-id", type=int, required=True)
    p.add_argument("--mode", choices=["cold", "replay"], required=True)
    p.add_argument("--name", default=None,
                   help="New run dir name. Auto-generated if omitted.")
    p.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS_ROOT)
    p.add_argument("--operator", default=None,
                   help="Defaults to source run's operator.")
    p.add_argument("--intent", default=None,
                   help="One-sentence intent. Auto-generated if omitted.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    src_paths = run_paths(args.source_run_dir)
    if not src_paths["meta"].exists():
        sys.exit(f"source meta not found: {src_paths['meta']}")
    src_meta = load_yaml(src_paths["meta"])
    src_messages = load_jsonl(src_paths["messages"])

    target = next(
        (m for m in src_messages if int(m["message_id"]) == args.source_message_id),
        None,
    )
    if target is None:
        sys.exit(
            f"message_id={args.source_message_id} not found in "
            f"{src_paths['messages']}"
        )
    if target["role"] != "user":
        sys.exit(
            f"message_id={args.source_message_id} has role={target['role']!r}; "
            f"derivation requires a user message at the boundary."
        )

    src_run_id = src_meta["run_id"]
    target_stage = str(target.get("stage_id"))
    condition = "cold_probe" if args.mode == "cold" else "replay_probe"

    if args.name:
        new_name = args.name
    else:
        suffix = uuid.uuid4().hex[:4]
        new_name = (
            f"{src_run_id}__{args.mode}_at_msg{args.source_message_id}_{suffix}"
        )

    new_dir = args.runs_root / new_name
    if new_dir.exists() and any(new_dir.iterdir()):
        sys.exit(f"target dir already exists and is non-empty: {new_dir}")
    new_dir.mkdir(parents=True, exist_ok=True)
    new_paths = run_paths(new_dir)

    new_meta = {
        "run_id": new_name,
        "operator": args.operator or src_meta.get("operator"),
        "date_utc": now_iso(),

        "model": src_meta["model"],
        "interface": src_meta.get("interface", "api"),
        "interface_memory_state": src_meta.get("interface_memory_state", "n/a"),
        "temperature": src_meta.get("temperature"),

        "condition": condition,
        "comparison_group_id": src_meta.get("comparison_group_id"),
        "paired_with": [src_run_id],
        "source_run_id": src_run_id,
        "source_message_id": args.source_message_id,
        "source_stage_id": target_stage,

        "ladder_path": src_meta["ladder_path"],
        "ladder_version": src_meta["ladder_version"],
        "rubric_path": src_meta["rubric_path"],
        "rubric_version": src_meta["rubric_version"],
        "git_commit": git_commit(),
        "api_wrapper_version": API_WRAPPER_VERSION,

        "intent": args.intent or (
            f"{condition} derivative of {src_run_id} "
            f"at message {args.source_message_id} (stage {target_stage})."
        ),
        "postmortem": None,
    }
    dump_yaml(new_paths["meta"], new_meta)

    # annotations.yaml stub
    new_paths["annotations"].write_text(
        "# Post-hoc annotations. Schema deferred until N=5-10 sessions.\n"
        "annotations: []\n",
        encoding="utf-8",
    )

    # Build messages.jsonl
    new_paths["messages"].touch()
    if args.mode == "cold":
        kept = [target]
    else:  # replay: include source_message_id so the prompt is held identical
        kept = [m for m in src_messages if int(m["message_id"]) <= args.source_message_id]

    # Renumber message_ids starting at 1; preserve role/content/stage_id/attempt.
    new_paths["stage_events"].touch()
    for new_id, m in enumerate(kept, start=1):
        new_row = {
            "message_id": new_id,
            "role": m["role"],
            "content": m["content"],
            "stage_id": str(m.get("stage_id")),
            "attempt": int(m.get("attempt", 1)),
            "timestamp": now_iso(),
        }
        append_jsonl(new_paths["messages"], new_row)

    # Seed a stage_start event so manual_chat.py has an active stage.
    # Snapshot the user_hint at derivation time for forensic reproducibility.
    ladder = load_yaml(Path(src_meta["ladder_path"]))
    from _session_io import find_stage, format_user_hint
    try:
        stage_def = find_stage(ladder, target_stage)
        hint_snapshot = format_user_hint(stage_def)
        stage_name = stage_def.get("name")
    except KeyError:
        hint_snapshot = ""
        stage_name = None

    append_jsonl(new_paths["stage_events"], {
        "event_id": 1,
        "event_type": "stage_start",
        "stage_id": target_stage,
        "stage_name": stage_name,
        "attempt": 1,
        "user_hint_snapshot": hint_snapshot,
        "created_at": now_iso(),
        "note": f"Seeded by derive_cold_run.py from {src_run_id} "
                f"at message {args.source_message_id} ({args.mode}).",
    })

    # Update source's paired_with. Re-read under lock so parallel derivations
    # merge instead of overwriting each other's sibling links.
    with source_update_lock(args.source_run_dir):
        locked_src_meta = load_yaml(src_paths["meta"])
        src_paired = list(locked_src_meta.get("paired_with") or [])
        if new_name not in src_paired:
            src_paired.append(new_name)
            locked_src_meta["paired_with"] = src_paired
            dump_yaml(src_paths["meta"], locked_src_meta)

    print(f"created {condition} run: {new_dir}")
    print(f"  source_run_id:     {src_run_id}")
    print(f"  source_message_id: {args.source_message_id}")
    print(f"  source_stage_id:   {target_stage}")
    print(f"  messages seeded:   {len(kept)}")
    print(f"  next: python scripts/manual_chat.py --run-dir {new_dir}")
    print(f"        (auto-regenerates the trailing user message; no prompt)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
