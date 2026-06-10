"""Interactive live-adaptive P16 robustness session runner.

This is intentionally operator-driven: the operator writes every user message
after reading the target assistant's previous response. The only API call is
the target assistant response generation.

It preserves the Phase A adaptive task file layout:
  session_meta.yaml
  messages.jsonl
  stage_events.jsonl
  adaptive_trace.jsonl
  annotations.yaml
and exports a user-side replay YAML on finish.
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import yaml

from _session_io import append_jsonl, dump_yaml, git_commit, load_jsonl, load_yaml, next_message_id, now_iso


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNS_ROOT = REPO_ROOT / "manual_redteam" / "data" / "runs" / "manual"
SPEC_PATH = REPO_ROOT / "manual_redteam" / "docs" / "cold_robustness_adaptive_task_spec_2026_05_06.md"
RUBRIC_PATH = REPO_ROOT / "manual_redteam" / "docs" / "annotation_template_v1_causal.md"
PREFIX_ROOT = REPO_ROOT / "manual_redteam" / "context_prefixes"
API_WRAPPER_VERSION = "live_adaptive_p16_session_0.1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", default=None, help="Run directory name.")
    p.add_argument("--run-dir", type=Path, default=None, help="Existing or new run directory.")
    p.add_argument("--operator", default="codex-live")
    p.add_argument("--operator-agent-model", default="GPT-5.5 via Codex; user prompts chosen without API")
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--max-tokens", type=int, default=1000)
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--condition", default="cold_live_adaptive_robustness")
    p.add_argument("--comparison-group-id", default="cmp_phaseB_live_adaptive_p16_2026_05_07")
    p.add_argument("--persona-id", default="phaseA_cold_robustness_blue_door_patient_v1")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    return p.parse_args()


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


def init_run(args: argparse.Namespace) -> Path:
    if args.run_dir:
        run_dir = args.run_dir if args.run_dir.is_absolute() else REPO_ROOT / args.run_dir
    else:
        name = args.name or f"2026-05-07_phaseB_live_adaptive_p16_gpt4omini_{uuid.uuid4().hex[:4]}"
        run_dir = DEFAULT_RUNS_ROOT / name

    run_dir.mkdir(parents=True, exist_ok=True)
    paths = run_paths(run_dir)
    if paths["meta"].exists():
        return run_dir

    meta = {
        "run_id": run_dir.name,
        "operator": args.operator,
        "operator_agent_model": args.operator_agent_model,
        "operator_agent_persona_id": args.persona_id,
        "date_utc": now_iso(),
        "model": args.model,
        "interface": "api",
        "interface_memory_state": "n/a",
        "temperature": args.temperature,
        "condition": args.condition,
        "comparison_group_id": args.comparison_group_id,
        "paired_with": [],
        "source_run_id": None,
        "source_message_id": None,
        "source_stage_id": None,
        "ladder_path": str(SPEC_PATH.relative_to(REPO_ROOT)),
        "ladder_version": "phaseA-cold-robustness-adaptive-spec-2026-05-06",
        "rubric_path": str(RUBRIC_PATH.relative_to(REPO_ROOT)),
        "rubric_version": "v1_causal_adapted",
        "git_commit": git_commit(),
        "api_wrapper_version": API_WRAPPER_VERSION,
        "intent": (
            "Live adaptive P16 robustness run: operator chooses each user prompt "
            "after reading the target assistant response; API is used only for "
            "the target assistant."
        ),
        "postmortem": None,
        "hard_prohibited_move_audit": None,
        "persona_reference": "cold_robustness_adaptive_task_spec_2026_05_06.md#Persona",
    }
    dump_yaml(paths["meta"], meta)
    paths["messages"].touch()
    paths["adaptive_trace"].touch()
    paths["annotations"].write_text(
        "# Post-hoc annotations. Schema deferred until analysis.\nannotations: []\n",
        encoding="utf-8",
    )
    append_jsonl(paths["stage_events"], {
        "event_id": 1,
        "event_type": "stage_start",
        "stage_id": "phaseB_live_adaptive_p16",
        "stage_name": "phaseB_live_adaptive_p16",
        "attempt": 1,
        "user_hint_snapshot": "Live adaptive P16 robustness task; see task spec.",
        "created_at": now_iso(),
        "note": "Started live adaptive P16 robustness run.",
    })
    return run_dir


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


def call_with_retry(caller, args: argparse.Namespace, messages: list[dict[str, str]]) -> str:
    import time

    last_err: Exception | None = None
    for attempt in range(args.retries):
        try:
            return caller(args.model, messages, args.temperature, args.max_tokens)
        except Exception as exc:
            last_err = exc
            if attempt < args.retries - 1:
                print(f"[api error: {type(exc).__name__}: {exc}] retrying...")
                time.sleep(args.retry_delay * (attempt + 1))
    raise RuntimeError(f"API call failed after {args.retries} attempts: {last_err}")


def read_block(prompt: str) -> str:
    print(prompt)
    print("(end with a single '.' on its own line)")
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
    return "\n".join(lines).strip()


def read_line(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    try:
        value = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        return ":quit"
    if not value and default is not None:
        return default
    return value


def print_last_context(messages: list[dict[str, Any]]) -> None:
    print()
    print("=" * 72)
    if not messages:
        print("[new run: no messages yet]")
    else:
        last = messages[-1]
        print(f"[last {last['role']} #{last['message_id']}]")
        print(last["content"])
    print("=" * 72)
    print()


def append_turn(
    paths: dict[str, Path],
    *,
    planned_target: str,
    move_type: str,
    boundary_probed: list[str],
    bridge_source_vocabulary: list[str],
    bridge_source_turn: str,
    user_text: str,
    assistant_text: str,
    interim_classification: str,
    next_plan: str,
    prohibited_move_check: str,
) -> None:
    messages = load_jsonl(paths["messages"])
    user_id = next_message_id(messages)
    append_jsonl(paths["messages"], {
        "message_id": user_id,
        "role": "user",
        "content": user_text,
        "stage_id": "phaseB_live_adaptive_p16",
        "attempt": 1,
        "timestamp": now_iso(),
    })
    messages = load_jsonl(paths["messages"])
    assistant_id = next_message_id(messages)
    append_jsonl(paths["messages"], {
        "message_id": assistant_id,
        "role": "assistant",
        "content": assistant_text,
        "stage_id": "phaseB_live_adaptive_p16",
        "attempt": 1,
        "timestamp": now_iso(),
    })
    trace_rows = load_jsonl(paths["adaptive_trace"])
    append_jsonl(paths["adaptive_trace"], {
        "turn_index": len(trace_rows) + 1,
        "agent_planned_target": planned_target,
        "agent_move_type": move_type,
        "user_message_id": user_id,
        "assistant_message_id": assistant_id,
        "boundary_probed": boundary_probed,
        "bridge_source_vocabulary": bridge_source_vocabulary,
        "bridge_source_turn": bridge_source_turn,
        "interim_classification": interim_classification,
        "agent_next_plan": next_plan,
        "prohibited_move_check": prohibited_move_check,
        "assistant_excerpt": assistant_text[:500],
    })


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
        "description": "User-side messages from live adaptive P16 robustness run for replay.",
        "turns": turns,
    }
    with out.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True, width=88)
    return out


def finish_run(run_dir: Path, paths: dict[str, Path]) -> int:
    outcome = read_line("outcome", "turn_budget")
    furthest = read_line("furthest_unsafe_boundaries comma-list", "")
    postmortem = read_block("postmortem")
    audit = read_line("hard_prohibited_move_audit", "ok")

    meta = load_yaml(paths["meta"])
    trace_rows = load_jsonl(paths["adaptive_trace"])
    messages = load_jsonl(paths["messages"])
    meta["outcome"] = outcome
    meta["turns_taken"] = len(trace_rows)
    meta["furthest_unsafe_boundaries"] = [x.strip() for x in furthest.split(",") if x.strip()]
    meta["hard_prohibited_move_audit"] = audit
    meta["postmortem"] = postmortem
    meta["ended_at"] = now_iso()
    dump_yaml(paths["meta"], meta)

    if messages:
        append_jsonl(paths["stage_events"], {
            "event_id": 2,
            "event_type": "stage_decision",
            "stage_id": "phaseB_live_adaptive_p16",
            "attempt": 1,
            "start_message_id": 1,
            "end_message_id": int(messages[-1]["message_id"]),
            "ladder_decision": "endorsed_after_context" if "p16" in outcome.lower() else "held",
            "created_at": now_iso(),
            "note": f"Final outcome={outcome}; turns={len(trace_rows)}.",
        })
    userside = export_userside(run_dir, paths)
    print(f"[finished] {run_dir}")
    print(f"[userside] {userside}")
    return 0


def main() -> int:
    args = parse_args()
    load_dotenv_if_available()
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        sys.exit(f"Set {args.api_key_env} in environment or .env.")
    run_dir = init_run(args)
    paths = run_paths(run_dir)
    caller = make_caller(api_key)

    print(f"[run] {run_dir}")
    print("[commands] type :finish at planned_target prompt to close run; :quit to exit without closing.")

    while True:
        messages = load_jsonl(paths["messages"])
        print_last_context(messages)
        planned_target = read_line("agent_planned_target")
        if planned_target == ":quit":
            return 0
        if planned_target == ":finish":
            return finish_run(run_dir, paths)
        move_type = read_line("agent_move_type")
        if move_type == ":quit":
            return 0
        boundaries_raw = read_line("boundary_probed comma-list")
        if boundaries_raw == ":quit":
            return 0
        boundary_probed = [x.strip() for x in boundaries_raw.split(",") if x.strip()]
        bridge_raw = read_line("bridge_source_vocabulary comma-list", "")
        if bridge_raw == ":quit":
            return 0
        bridge_source_vocabulary = [x.strip() for x in bridge_raw.split(",") if x.strip()]
        bridge_source_turn = read_line("bridge_source_turn", "")
        if bridge_source_turn == ":quit":
            return 0
        user_text = read_block("user message")
        if user_text in (":quit", ""):
            return 0

        api_messages = [
            {"role": row["role"], "content": row["content"]}
            for row in messages
        ] + [{"role": "user", "content": user_text}]
        print("[calling target assistant API...]")
        assistant_text = call_with_retry(caller, args, api_messages)
        print()
        print("assistant >")
        print(assistant_text)
        print()

        interim = read_line("interim_classification safe|mixed|unsafe|severe_unsafe")
        next_plan = read_line("agent_next_plan")
        prohibited = read_line("prohibited_move_check", "ok")
        append_turn(
            paths,
            planned_target=planned_target,
            move_type=move_type,
            boundary_probed=boundary_probed,
            bridge_source_vocabulary=bridge_source_vocabulary,
            bridge_source_turn=bridge_source_turn,
            user_text=user_text,
            assistant_text=assistant_text,
            interim_classification=interim,
            next_plan=next_plan,
            prohibited_move_check=prohibited,
        )


if __name__ == "__main__":
    raise SystemExit(main())
