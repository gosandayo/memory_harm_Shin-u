"""Run a fixed sequence of user prompts from optional frozen branch bases.

This helper is for sequence panels such as v12.7, where the experimental unit
is not a single direct probe but a fixed local chain of probes. For each sample
it optionally copies a frozen source transcript prefix, appends each scripted
user prompt, calls the target model after each prompt, and writes both branch
transcripts and a compact summary JSONL.
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

from _session_io import append_jsonl, dump_yaml, load_jsonl, now_iso, run_paths


REPO_ROOT = Path(__file__).resolve().parents[2]
API_WRAPPER_VERSION = "0.1.0"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ladder", type=Path, required=True)
    p.add_argument("--stage-id", required=True)
    p.add_argument("--condition-label", required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--branch-prefix", required=True)
    p.add_argument("--source-run-dir", type=Path, default=None)
    p.add_argument("--source-message-id", type=int, default=None)
    p.add_argument("--provider", choices=["openai"], default="openai")
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--n-samples", type=int, default=10)
    p.add_argument("--max-tokens", type=int, default=1000)
    p.add_argument("--api-key-env", default="OPENAI_API_KEY")
    p.add_argument("--retry", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    return p.parse_args()


def resolve_output_dir(output_dir: Path) -> Path:
    return output_dir if output_dir.is_absolute() else REPO_ROOT / output_dir


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO_ROOT / ".env")


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def find_stage(ladder: dict, stage_id: str) -> dict:
    for stage in ladder.get("stages", []):
        if str(stage.get("id")) == str(stage_id):
            return stage
    raise SystemExit(f"stage_id not found: {stage_id}")


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


def make_caller(api_key: str):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    def _call(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    return _call


def call_with_retry(
    caller,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    retries: int,
    retry_delay: float,
) -> str:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            return caller(model, messages, temperature, max_tokens)
        except Exception as exc:
            last_err = exc
            if attempt < retries - 1:
                print(f"  [retry {attempt + 1}/{retries - 1}] {type(exc).__name__}: {exc}")
                time.sleep(retry_delay * (attempt + 1))
    raise RuntimeError(f"API call failed after {retries} attempts: {last_err}")


def load_base_messages(source_run_dir: Path | None, source_message_id: int | None) -> list[dict]:
    if source_run_dir is None:
        return []
    if source_message_id is None:
        raise SystemExit("--source-message-id is required with --source-run-dir")
    source_run_dir = source_run_dir if source_run_dir.is_absolute() else REPO_ROOT / source_run_dir
    rows = load_jsonl(source_run_dir / "messages.jsonl")
    return [row for row in rows if int(row["message_id"]) <= source_message_id]


def write_branch_meta(
    branch_dir: Path,
    args: argparse.Namespace,
    ladder: dict,
    stage: dict,
) -> None:
    meta = {
        "run_id": branch_dir.name,
        "operator": "codex",
        "date_utc": now_iso(),
        "model": args.model,
        "interface": "api",
        "interface_memory_state": "n/a",
        "temperature": args.temperature,
        "condition": args.condition_label,
        "comparison_group_id": f"cmp_{args.output_dir.name}",
        "paired_with": [],
        "source_run_id": args.source_run_dir.name if args.source_run_dir else None,
        "source_message_id": args.source_message_id,
        "source_stage_id": None,
        "ladder_path": str(args.ladder),
        "ladder_version": ladder.get("version"),
        "rubric_path": "manual_redteam/docs/annotation_template.md",
        "rubric_version": "v0",
        "git_commit": git_commit(),
        "api_wrapper_version": API_WRAPPER_VERSION,
        "intent": (
            f"v12.7 fixed sequence panel for {stage.get('probe_id')} "
            f"under {args.condition_label}."
        ),
        "postmortem": None,
    }
    dump_yaml(branch_dir / "session_meta.yaml", meta)
    (branch_dir / "stage_events.jsonl").touch()
    (branch_dir / "annotations.yaml").write_text(
        "# Post-hoc annotations. Schema deferred until analysis.\n"
        "annotations: []\n",
        encoding="utf-8",
    )


def seed_messages(branch_dir: Path, base_messages: list[dict]) -> int:
    messages_path = branch_dir / "messages.jsonl"
    messages_path.touch()
    next_id = 1
    for row in base_messages:
        new_row = {
            "message_id": int(row["message_id"]),
            "role": row["role"],
            "content": row["content"],
            "stage_id": str(row.get("stage_id")),
            "attempt": int(row.get("attempt", 1)),
            "timestamp": row.get("timestamp") or now_iso(),
        }
        append_jsonl(messages_path, new_row)
        next_id = max(next_id, int(row["message_id"]) + 1)
    return next_id


def run_branch(
    *,
    caller,
    args: argparse.Namespace,
    ladder: dict,
    stage: dict,
    base_messages: list[dict],
    sample_idx: int,
) -> dict:
    branch_dir = resolve_output_dir(args.output_dir) / "branches" / f"{args.branch_prefix}_sample{sample_idx}"
    branch_dir.mkdir(parents=True, exist_ok=True)
    write_branch_meta(branch_dir, args, ladder, stage)

    messages_path = branch_dir / "messages.jsonl"
    if messages_path.exists():
        messages_path.unlink()
    next_id = seed_messages(branch_dir, base_messages)

    api_messages = [
        {"role": row["role"], "content": row["content"]}
        for row in base_messages
    ]
    turn_summaries: list[dict[str, Any]] = []

    for turn in stage["sequence"]:
        prompt = normalize_text(turn["prompt"])
        user_row = {
            "message_id": next_id,
            "role": "user",
            "content": prompt,
            "stage_id": str(stage["id"]),
            "attempt": 1,
            "timestamp": now_iso(),
            "turn_id": turn["turn_id"],
        }
        append_jsonl(messages_path, user_row)
        api_messages.append({"role": "user", "content": prompt})
        next_id += 1

        response = call_with_retry(
            caller=caller,
            model=args.model,
            messages=api_messages,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            retries=args.retry,
            retry_delay=args.retry_delay,
        )
        assistant_row = {
            "message_id": next_id,
            "role": "assistant",
            "content": response,
            "stage_id": str(stage["id"]),
            "attempt": 1,
            "timestamp": now_iso(),
            "turn_id": turn["turn_id"],
        }
        append_jsonl(messages_path, assistant_row)
        api_messages.append({"role": "assistant", "content": response})
        next_id += 1

        turn_summaries.append(
            {
                "turn_id": turn["turn_id"],
                "move_type": turn.get("move_type"),
                "prompt": prompt,
                "response": response,
            }
        )

    return {
        "stage_id": int(stage["id"]),
        "stage_name": stage["name"],
        "probe_id": stage.get("probe_id"),
        "condition": args.condition_label,
        "sample_idx": sample_idx,
        "branch_dir": str(branch_dir.relative_to(REPO_ROOT)),
        "provider": args.provider,
        "model": args.model,
        "temperature": args.temperature,
        "source_run_dir": str(args.source_run_dir) if args.source_run_dir else None,
        "source_message_id": args.source_message_id,
        "turns": turn_summaries,
        "final_turn_id": turn_summaries[-1]["turn_id"],
        "final_response": turn_summaries[-1]["response"],
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def main() -> int:
    args = parse_args()
    load_dotenv_if_available()
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set")

    output_dir = resolve_output_dir(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ladder = load_yaml(args.ladder)
    stage = find_stage(ladder, args.stage_id)
    base_messages = load_base_messages(args.source_run_dir, args.source_message_id)
    caller = make_caller(api_key)
    summary_path = output_dir / "sequence_probe.jsonl"

    print(
        f"Running {args.n_samples} sequence branches for {stage['name']} "
        f"under {args.condition_label}; base_messages={len(base_messages)}"
    )
    with summary_path.open("a", encoding="utf-8") as handle:
        for sample_idx in range(args.n_samples):
            print(f"[sample {sample_idx}] {args.condition_label}")
            row = run_branch(
                caller=caller,
                args=args,
                ladder=ladder,
                stage=stage,
                base_messages=base_messages,
                sample_idx=sample_idx,
            )
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()

    run_config = {
        "ladder_path": str(args.ladder),
        "ladder_id": ladder["id"],
        "stage_id": args.stage_id,
        "condition_label": args.condition_label,
        "source_run_dir": str(args.source_run_dir) if args.source_run_dir else None,
        "source_message_id": args.source_message_id,
        "branch_prefix": args.branch_prefix,
        "provider": args.provider,
        "model": args.model,
        "temperature": args.temperature,
        "n_samples": args.n_samples,
        "max_tokens": args.max_tokens,
        "git_commit": git_commit(),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    dump_yaml(output_dir / f"run_config_{args.condition_label}.yaml", run_config)
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
