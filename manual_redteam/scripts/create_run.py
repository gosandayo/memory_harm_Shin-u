"""Scaffold a new manual interaction run directory.

Creates session_meta.yaml, empty messages.jsonl, empty stage_events.jsonl,
and empty annotations.yaml under <runs-root>/<name>/.

For cold_probe / replay_probe runs, prefer derive_cold_run.py — it fills
the comparison metadata from a source run automatically.

See manual_redteam/docs/manual_session_spec.md.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

from _session_io import (
    dump_yaml,
    git_commit,
    now_iso,
    run_paths,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNS_ROOT = REPO_ROOT / "manual_redteam" / "data" / "runs" / "manual"
DEFAULT_RUBRIC = (
    REPO_ROOT / "manual_redteam" / "docs" / "annotation_template.md"
)
API_WRAPPER_VERSION = "0.1.0"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", required=True,
                   help="Run directory name, e.g. 2026-05-04_stage144_gpt4omini_run01")
    p.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS_ROOT)
    p.add_argument("--operator", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--interface", choices=["api", "web"], default="api")
    p.add_argument("--interface-memory-state",
                   choices=["on", "off", "n/a"], default="n/a",
                   help="Web UI memory toggle state. Use n/a for api.")
    p.add_argument("--temperature", type=float, default=None,
                   help="Required for interface=api; null otherwise.")
    p.add_argument("--ladder", type=Path, required=True,
                   help="Path to ladder YAML.")
    p.add_argument("--ladder-version", required=True,
                   help="Manual semantic version of the ladder (e.g. v3.2).")
    p.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    p.add_argument("--rubric-version", default="v0")
    p.add_argument("--condition",
                   choices=["accumulated_context", "cold_probe", "replay_probe"],
                   default="accumulated_context")
    p.add_argument("--comparison-group-id", default=None,
                   help="Auto-generated if omitted.")
    p.add_argument("--intent", required=True,
                   help="One-sentence statement of what this session targets.")
    p.add_argument("--force", action="store_true",
                   help="Allow writing into a non-empty run directory.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.interface == "api" and args.temperature is None:
        sys.exit("--temperature is required when --interface=api")
    if args.interface == "web" and args.interface_memory_state == "n/a":
        sys.exit("--interface-memory-state must be on/off when --interface=web")
    if not args.ladder.exists():
        sys.exit(f"ladder not found: {args.ladder}")

    run_dir = args.runs_root / args.name
    if run_dir.exists() and any(run_dir.iterdir()) and not args.force:
        sys.exit(f"run dir already exists and is non-empty: {run_dir}\n"
                 f"  use --force to write into it.")
    run_dir.mkdir(parents=True, exist_ok=True)

    paths = run_paths(run_dir)

    cmp_group = args.comparison_group_id or f"cmp_{args.name}_{uuid.uuid4().hex[:6]}"
    temperature = args.temperature if args.interface == "api" else None

    meta = {
        "run_id": args.name,
        "operator": args.operator,
        "date_utc": now_iso(),

        "model": args.model,
        "interface": args.interface,
        "interface_memory_state": args.interface_memory_state,
        "temperature": temperature,

        "condition": args.condition,
        "comparison_group_id": cmp_group,
        "paired_with": [],
        "source_run_id": None,
        "source_message_id": None,
        "source_stage_id": None,

        "ladder_path": str(args.ladder),
        "ladder_version": args.ladder_version,
        "rubric_path": str(args.rubric),
        "rubric_version": args.rubric_version,
        "git_commit": git_commit(),
        "api_wrapper_version": API_WRAPPER_VERSION,

        "intent": args.intent,
        "postmortem": None,
    }
    dump_yaml(paths["meta"], meta)

    paths["messages"].touch()
    paths["stage_events"].touch()
    if not paths["annotations"].exists():
        paths["annotations"].write_text(
            "# Post-hoc annotations. Schema deferred until N=5-10 sessions.\n"
            "# Reference messages by message_id and stages by stage_id.\n"
            "annotations: []\n",
            encoding="utf-8",
        )

    print(f"created run dir: {run_dir}")
    print(f"  meta:          {paths['meta']}")
    print(f"  messages:      {paths['messages']}")
    print(f"  stage_events:  {paths['stage_events']}")
    print(f"  annotations:   {paths['annotations']}")
    print()
    print("next: log_stage_event.py start --run-dir <dir> --stage-id <id>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
