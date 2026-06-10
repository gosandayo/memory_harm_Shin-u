#!/usr/bin/env python3
"""Run exploratory current-S13 probes after saved current-S12-open context.

This runner is intentionally narrow and run-specific. It copies saved
transcripts through the assistant reply to current S12-open (old S14), then
appends one existing current-S13/old-S16 prompt variant and calls the target
model. Prompt text is loaded verbatim from existing jsonl sources; this script
does not author new terminal prompt text.
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

PREFIXES = {
    "longbuild_s12open": {
        "source": "manual_redteam/data/runs/2026-05-19_s16_longbuild_free_gpt4omini/branches/run01/messages.jsonl",
        "through_rung": "S14",
    },
    "longsetup_s12open": {
        "source": "manual_redteam/data/runs/2026-05-20_longsetup_s1s7_s14_adaptive_gpt4omini/branches/adaptive_run01/messages.jsonl",
        "through_rung": "S14",
    },
}

PROMPTS = {
    "open_plain": {
        "source": "manual_redteam/data/runs/2026-05-18_s16_unrestricted_gpt4omini/branches/cold_plain_s16/messages.jsonl",
        "source_rung": "S16_cold_plain",
    },
    "short_choice": {
        "source": "manual_redteam/data/runs/2026-05-18_s16_unrestricted_gpt4omini/branches/cold_shortbinary_only/messages.jsonl",
        "source_rung": "S16_cold_shortbinary",
    },
    "present_open_verdictfirst": {
        "source": "manual_redteam/data/runs/2026-05-18_s16_unrestricted_gpt4omini/branches/cold_prefuture_open/messages.jsonl",
        "source_rung": "S16_cold_prefuture_open",
    },
    "forced_twopossible_verdictfirst": {
        "source": "manual_redteam/data/runs/2026-05-18_s16_unrestricted_gpt4omini/branches/cold_twopossible_only/messages.jsonl",
        "source_rung": "S16_cold_twopossible",
    },
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "manual_redteam/data/runs/2026-05-20_s13_after_s12_context_exploratory_gpt4omini",
    )
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--max-tokens", type=int, default=1200)
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--retry", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    p.add_argument("--i-have-owner-signoff", action="store_true")
    return p.parse_args()


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO_ROOT / ".env")


def resolve(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else REPO_ROOT / p


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def prefix_through_assistant(source: Path, through_rung: str) -> list[dict]:
    rows = load_jsonl(source)
    last_idx = None
    for idx, row in enumerate(rows):
        if row.get("role") == "assistant" and row.get("rung") == through_rung:
            last_idx = idx
            break
    if last_idx is None:
        raise SystemExit(f"Could not find assistant reply for rung {through_rung!r} in {source}")
    return rows[: last_idx + 1]


def load_prompt(source: Path, source_rung: str) -> str:
    matches = [
        row["content"]
        for row in load_jsonl(source)
        if row.get("role") == "user" and row.get("rung") == source_rung
    ]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one user prompt for {source_rung!r} in {source}, got {len(matches)}")
    return " ".join(matches[0].split()).strip()


def make_client(api_key: str):
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def call_model(client, args: argparse.Namespace, history: list[dict]) -> tuple[str, dict]:
    api_history = [{"role": row["role"], "content": row["content"]} for row in history]
    last_exc = None
    for attempt in range(args.retry):
        try:
            resp = client.chat.completions.create(
                model=args.model,
                messages=api_history,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
            )
            return (resp.choices[0].message.content or "").strip(), {
                "model": args.model,
                "finish_reason": resp.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
                    "completion_tokens": getattr(resp.usage, "completion_tokens", None),
                    "total_tokens": getattr(resp.usage, "total_tokens", None),
                },
            }
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < args.retry - 1:
                print(f"[retry {attempt + 1}] {type(exc).__name__}: {exc}", file=sys.stderr)
                time.sleep(args.retry_delay * (attempt + 1))
    raise RuntimeError(f"API failed after {args.retry} attempts: {last_exc}")


def write_manifest(args: argparse.Namespace) -> None:
    manifest = {
        "run_id": args.output_dir.name,
        "status": "exploratory_not_writeup_claim",
        "model": args.model,
        "temperature": args.temperature,
        "n_per_cell": args.n,
        "api_key_env": args.api_key_env,
        "runner": "manual_redteam/scripts/s13_after_s12_context_panel.py",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "purpose": "Append existing current-S13 prompt variants after saved current-S12-open context.",
        "prefixes": PREFIXES,
        "prompts": PROMPTS,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.output_dir = resolve(args.output_dir)
    write_manifest(args)

    prefix_rows = {
        name: prefix_through_assistant(resolve(spec["source"]), spec["through_rung"])
        for name, spec in PREFIXES.items()
    }
    prompts = {
        name: load_prompt(resolve(spec["source"]), spec["source_rung"])
        for name, spec in PROMPTS.items()
    }

    if not args.i_have_owner_signoff:
        print("=== DRY RUN (no API calls). Pass --i-have-owner-signoff to launch. ===")
        for prefix_name in prefix_rows:
            for prompt_name in prompts:
                print(f"[dry-run] {prefix_name} + {prompt_name}: {args.n} samples")
        return 0

    load_dotenv_if_available()
    api_key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(f"{args.api_key_env} / OPENAI_API_KEY not set")
    client = make_client(api_key)

    for prefix_name, rows in prefix_rows.items():
        for prompt_name, prompt in prompts.items():
            for idx in range(args.n):
                branch = args.output_dir / "branches" / f"{prefix_name}__{prompt_name}_run{idx:02d}"
                msg_path = branch / "messages.jsonl"
                if msg_path.exists() and msg_path.stat().st_size > 0:
                    print(f"[skip existing] {msg_path.relative_to(REPO_ROOT)}")
                    continue
                branch.mkdir(parents=True, exist_ok=True)
                history = [dict(row) for row in rows]
                history.append({"role": "user", "content": prompt, "rung": f"S13_{prompt_name}", "source": "s13_after_s12_context_panel"})
                assistant_text, extra = call_model(client, args, history)
                history.append({"role": "assistant", "content": assistant_text, "rung": f"S13_{prompt_name}", "source": "model_sample", **extra})
                msg_path.write_text(
                    "\n".join(json.dumps(row, ensure_ascii=False) for row in history) + "\n",
                    encoding="utf-8",
                )
                (branch / "session_meta.yaml").write_text(
                    yaml.safe_dump(
                        {
                            "run_id": branch.name,
                            "prefix": prefix_name,
                            "prompt": prompt_name,
                            "model": args.model,
                            "temperature": args.temperature,
                            "max_tokens": args.max_tokens,
                            "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                        },
                        sort_keys=False,
                    ),
                    encoding="utf-8",
                )
                print(f"[{prefix_name} {prompt_name} {idx:02d}] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
