#!/usr/bin/env python3
"""Run a fixed S15-plain comparison panel.

Arms:
  short: R0a,R0b,Bridge,S8,S9,S9b,S11 + shared S12,S14,S15
  long:  Setup1..S7,Bridge,S8,S9,S9b,S11 + shared S12,S14,S15

The shared terminal prompts are taken from the 2026-05-19 long-build run.
No context-claim or forced-binary terminal wording is added.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "manual_redteam" / "data" / "runs" / "2026-05-19_s15_plain_panel_gpt4omini"
SHORT_TEMPLATE_PATH = (
    REPO_ROOT
    / "manual_redteam"
    / "data"
    / "runs"
    / "2026-05-18_s16_adaptive_nocontextclaim_gpt4omini"
    / "branches"
    / "run01"
    / "messages.jsonl"
)
LONG_TEMPLATE_PATH = (
    REPO_ROOT
    / "manual_redteam"
    / "data"
    / "runs"
    / "2026-05-19_s16_longbuild_free_gpt4omini"
    / "branches"
    / "run01"
    / "messages.jsonl"
)

SHORT_BUILD_RUNG_ORDER = ["R0a", "R0b", "Bridge", "S8", "S9", "S9b", "S11"]
LONG_BUILD_RUNG_ORDER = [
    "Setup1",
    "Setup2",
    "Setup3",
    "S1",
    "S2",
    "S3",
    "S4",
    "S5",
    "S6",
    "S7",
    "Bridge",
    "S8",
    "S9",
    "S9b",
    "S11",
]
TERMINAL_RUNG_ORDER = ["S12", "S14", "S15"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--max-tokens", type=int, default=1200)
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--retry", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    return p.parse_args()


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO_ROOT / ".env")


def load_user_prompts(path: Path) -> dict[str, str]:
    prompts: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("role") != "user":
            continue
        rung = row.get("rung") or row.get("stage")
        if rung and rung not in prompts:
            prompts[rung] = row["content"]
    return prompts


def make_sequence(
    build_prompts: dict[str, str],
    build_order: list[str],
    terminal_prompts: dict[str, str],
) -> list[tuple[str, str]]:
    missing = [r for r in build_order if r not in build_prompts]
    missing += [r for r in TERMINAL_RUNG_ORDER if r not in terminal_prompts]
    if missing:
        raise SystemExit(f"Missing prompt rung(s): {missing}")
    return [(r, build_prompts[r]) for r in build_order] + [
        (r, terminal_prompts[r]) for r in TERMINAL_RUNG_ORDER
    ]


def make_client(api_key: str):
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def call_with_retry(client, args: argparse.Namespace, history: list[dict[str, str]]) -> tuple[str, dict]:
    last_exc: Exception | None = None
    for attempt in range(args.retry):
        try:
            resp = client.chat.completions.create(
                model=args.model,
                messages=history,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            return (resp.choices[0].message.content or "").strip(), {
                "finish_reason": resp.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
                    "completion_tokens": getattr(resp.usage, "completion_tokens", None),
                    "total_tokens": getattr(resp.usage, "total_tokens", None),
                },
            }
        except Exception as exc:
            last_exc = exc
            if attempt < args.retry - 1:
                print(f"[retry {attempt + 1}] {type(exc).__name__}: {exc}", file=sys.stderr)
                time.sleep(args.retry_delay * (attempt + 1))
    raise RuntimeError(f"API failed after {args.retry} attempts: {last_exc}")


def run_branch(
    *,
    client,
    args: argparse.Namespace,
    branch_dir: Path,
    arm: str,
    sample_idx: int,
    sequence: list[tuple[str, str]],
) -> None:
    branch_dir.mkdir(parents=True, exist_ok=True)
    msg_path = branch_dir / "messages.jsonl"
    meta_path = branch_dir / "session_meta.yaml"
    if msg_path.exists() and msg_path.stat().st_size > 0:
        print(f"[skip existing] {branch_dir.relative_to(REPO_ROOT)}")
        return

    meta = {
        "run_id": branch_dir.name,
        "arm": arm,
        "sample_idx": sample_idx,
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "condition": "fixed_replay_plain_S15",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "short_template_path": str(SHORT_TEMPLATE_PATH.relative_to(REPO_ROOT)),
        "long_template_path": str(LONG_TEMPLATE_PATH.relative_to(REPO_ROOT)),
        "terminal_rungs": TERMINAL_RUNG_ORDER,
    }
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")

    api_history: list[dict[str, str]] = []
    with msg_path.open("w", encoding="utf-8") as f:
        for turn_index, (rung, user_text) in enumerate(sequence, start=1):
            api_history.append({"role": "user", "content": user_text})
            assistant_text, extra = call_with_retry(client, args, api_history)
            api_history.append({"role": "assistant", "content": assistant_text})
            f.write(json.dumps({
                "role": "user",
                "content": user_text,
                "rung": rung,
                "turn_index": turn_index,
            }, ensure_ascii=False) + "\n")
            f.write(json.dumps({
                "role": "assistant",
                "content": assistant_text,
                "rung": rung,
                "turn_index": turn_index,
                **extra,
            }, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{arm} {sample_idx:02d}] {rung} done")


def write_prompt_manifest(output_root: Path, short_sequence, long_sequence) -> None:
    manifest = {
        "short_sequence": [{"rung": rung, "user": text} for rung, text in short_sequence],
        "long_sequence": [{"rung": rung, "user": text} for rung, text in long_sequence],
    }
    (output_root / "prompt_manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    load_dotenv_if_available()
    api_key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(f"{args.api_key_env} / OPENAI_API_KEY not set")

    output_root = args.output_root if args.output_root.is_absolute() else REPO_ROOT / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    short_prompts = load_user_prompts(SHORT_TEMPLATE_PATH)
    long_prompts = load_user_prompts(LONG_TEMPLATE_PATH)
    terminal_prompts = {r: long_prompts[r] for r in TERMINAL_RUNG_ORDER}
    short_sequence = make_sequence(short_prompts, SHORT_BUILD_RUNG_ORDER, terminal_prompts)
    long_sequence = make_sequence(long_prompts, LONG_BUILD_RUNG_ORDER, terminal_prompts)
    write_prompt_manifest(output_root, short_sequence, long_sequence)

    client = make_client(api_key)
    for sample_idx in range(args.n):
        run_branch(
            client=client,
            args=args,
            branch_dir=output_root / "branches" / f"short_plainS15_run{sample_idx:02d}",
            arm="short",
            sample_idx=sample_idx,
            sequence=short_sequence,
        )
        run_branch(
            client=client,
            args=args,
            branch_dir=output_root / "branches" / f"long_plainS15_run{sample_idx:02d}",
            arm="long",
            sample_idx=sample_idx,
            sequence=long_sequence,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
