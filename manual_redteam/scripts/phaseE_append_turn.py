"""Append one adaptive Phase E cascade turn to a copied source transcript.

The script initializes a Phase E run from an existing messages.jsonl transcript
on first use, then appends exactly one operator-chosen user turn and one target
assistant API response. It is deliberately small so the human/Codex operator can
read each target response and compose the next user turn outside the script.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

from _session_io import append_jsonl, dump_yaml, git_commit, load_jsonl, load_yaml, next_message_id, now_iso


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNS_ROOT = REPO_ROOT / "manual_redteam" / "data" / "runs" / "manual"
SPEC_PATH = REPO_ROOT / "manual_redteam" / "docs" / "phaseE_cascade_endpoint_specs_2026_05_07.md"
PREFIX_ROOT = REPO_ROOT / "manual_redteam" / "context_prefixes"
API_WRAPPER_VERSION = "phaseE_append_turn_0.1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--source-run-dir", type=Path, required=True)
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=1000)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    parser.add_argument("--operator", default="codex-live")
    parser.add_argument("--condition", default="phaseE_post_p16_cascade")
    parser.add_argument("--comparison-group-id", default="cmp_phaseE_post_p16_cascade_gpt4omini_2026_05_07")
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--planned-target", required=True)
    parser.add_argument("--move-type", required=True)
    parser.add_argument("--boundary-probed", default="")
    parser.add_argument("--bridge-source-vocabulary", default="")
    parser.add_argument("--bridge-source-turn", default="")
    parser.add_argument("--user-message", required=True)
    parser.add_argument("--interim-classification", default="uncoded")
    parser.add_argument("--next-plan", default="")
    return parser.parse_args()


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO_ROOT / ".env")


def run_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "meta": run_dir / "session_meta.yaml",
        "messages": run_dir / "messages.jsonl",
        "stage_events": run_dir / "stage_events.jsonl",
        "adaptive_trace": run_dir / "adaptive_trace.jsonl",
        "annotations": run_dir / "annotations.yaml",
    }


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def init_run(args: argparse.Namespace) -> tuple[Path, dict[str, Path]]:
    run_dir = resolve(args.run_dir)
    source_run_dir = resolve(args.source_run_dir)
    source_messages_path = source_run_dir / "messages.jsonl"
    if not source_messages_path.exists():
        raise FileNotFoundError(source_messages_path)

    run_dir.mkdir(parents=True, exist_ok=True)
    paths = run_paths(run_dir)
    if paths["meta"].exists():
        return run_dir, paths

    source_messages = load_jsonl(source_messages_path)
    if not source_messages or source_messages[-1].get("role") != "assistant":
        raise RuntimeError(f"source transcript must end with assistant response: {source_messages_path}")

    meta = {
        "run_id": run_dir.name,
        "operator": args.operator,
        "operator_agent_model": "GPT-5.5 via Codex; user prompts chosen without API",
        "date_utc": now_iso(),
        "model": args.model,
        "interface": "api",
        "interface_memory_state": "n/a",
        "temperature": args.temperature,
        "condition": args.condition,
        "comparison_group_id": args.comparison_group_id,
        "source_run_id": source_run_dir.name,
        "source_messages": str(source_messages_path.relative_to(REPO_ROOT)),
        "source_message_count": len(source_messages),
        "ladder_path": str(SPEC_PATH.relative_to(REPO_ROOT)),
        "ladder_version": "phaseE-cascade-endpoint-specs-2026-05-07",
        "git_commit": git_commit(),
        "api_wrapper_version": API_WRAPPER_VERSION,
        "intent": (
            "Phase E post-P16 cascade continuation. The source transcript is a "
            "P16/R4-reached run; the operator appends endpoint-specific cascade "
            "turns after reading each target response. API is used only for the "
            "target assistant."
        ),
        "postmortem": None,
        "hard_prohibited_move_audit": None,
        "outcome": "in_progress",
    }
    dump_yaml(paths["meta"], meta)
    for row in source_messages:
        append_jsonl(paths["messages"], row)
    paths["adaptive_trace"].touch()
    paths["annotations"].write_text(
        "# Post-hoc annotations. Schema deferred until analysis.\nannotations: []\n",
        encoding="utf-8",
    )
    append_jsonl(paths["stage_events"], {
        "event_id": 1,
        "event_type": "stage_start",
        "stage_id": "phaseE_post_p16_cascade",
        "stage_name": "phaseE_post_p16_cascade",
        "attempt": 1,
        "source_run_id": source_run_dir.name,
        "created_at": now_iso(),
        "note": "Initialized Phase E post-P16 cascade continuation from source transcript.",
    })
    return run_dir, paths


def make_caller(api_key: str):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    def _call(model: str, messages: list[dict[str, str]], temperature: float, max_tokens: int) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    return _call


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def export_userside(run_dir: Path, paths: dict[str, Path]) -> Path:
    messages = load_jsonl(paths["messages"])
    turns = [
        {"id": (int(m["message_id"]) + 1) // 2, "user": m["content"]}
        for m in messages
        if m.get("role") == "user"
    ]
    PREFIX_ROOT.mkdir(parents=True, exist_ok=True)
    out = PREFIX_ROOT / f"{run_dir.name}_userside.yaml"
    data = {
        "id": f"{run_dir.name}_userside",
        "source_run_id": run_dir.name,
        "description": "User-side messages from Phase E post-P16 cascade continuation for replay.",
        "turns": turns,
    }
    with out.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True, width=88)
    return out


def main() -> int:
    args = parse_args()
    load_dotenv_if_available()
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        sys.exit(f"Set {args.api_key_env} in environment or .env.")

    run_dir, paths = init_run(args)
    messages = load_jsonl(paths["messages"])
    api_messages = [
        {"role": row["role"], "content": row["content"]}
        for row in messages
        if row.get("role") in {"user", "assistant"}
    ] + [{"role": "user", "content": args.user_message}]

    caller = make_caller(api_key)
    assistant_text = caller(args.model, api_messages, args.temperature, args.max_tokens)

    user_id = next_message_id(messages)
    append_jsonl(paths["messages"], {
        "message_id": user_id,
        "role": "user",
        "content": args.user_message,
        "stage_id": "phaseE_post_p16_cascade",
        "attempt": 1,
        "turn_id": args.endpoint,
        "timestamp": now_iso(),
    })
    messages = load_jsonl(paths["messages"])
    assistant_id = next_message_id(messages)
    append_jsonl(paths["messages"], {
        "message_id": assistant_id,
        "role": "assistant",
        "content": assistant_text,
        "stage_id": "phaseE_post_p16_cascade",
        "attempt": 1,
        "turn_id": args.endpoint,
        "timestamp": now_iso(),
    })

    trace_rows = load_jsonl(paths["adaptive_trace"])
    append_jsonl(paths["adaptive_trace"], {
        "turn_index": len(trace_rows) + 1,
        "endpoint": args.endpoint,
        "agent_planned_target": args.planned_target,
        "agent_move_type": args.move_type,
        "user_message_id": user_id,
        "assistant_message_id": assistant_id,
        "boundary_probed": split_csv(args.boundary_probed),
        "bridge_source_vocabulary": split_csv(args.bridge_source_vocabulary),
        "bridge_source_turn": args.bridge_source_turn,
        "interim_classification": args.interim_classification,
        "agent_next_plan": args.next_plan,
        "assistant_excerpt": assistant_text[:700],
        "created_at": now_iso(),
    })

    meta = load_yaml(paths["meta"])
    meta["turns_taken"] = len(trace_rows) + 1
    meta["last_endpoint"] = args.endpoint
    meta["updated_at"] = now_iso()
    dump_yaml(paths["meta"], meta)
    userside = export_userside(run_dir, paths)

    print(f"[run] {run_dir}")
    print(f"[assistant_message_id] {assistant_id}")
    print("[assistant]")
    print(assistant_text)
    print(f"[userside] {userside}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
