"""Run cold (current_turn_only) probes for a red-team ladder.

For each stage in the ladder YAML, sends the stage's `probe` as the only
user message to the target model — no system prompt, no prior context.
Repeats `--n-samples` times per stage and appends each response to
`direct_probe.jsonl` in the run directory.

Only `probe` is sent to the model. `unsafe_if` and
`expected_safe_behavior` are evaluator notes and never enter the prompt.

Resumable: re-running with the same output dir skips
(stage_id, sample_idx) pairs already present in direct_probe.jsonl.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

import yaml


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--ladder",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "ladders"
        / "referential_motif_blue_door_v0.yaml",
        help="Path to ladder YAML.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Run directory. Defaults to manual_redteam/data/runs/<date>_<ladder_id>/.",
    )
    p.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        default="openai",
        help="API provider to call.",
    )
    p.add_argument("--model", type=str, default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--n-samples", type=int, default=3)
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument(
        "--stages",
        type=str,
        default=None,
        help="Comma-separated stage ids to run (e.g. '1,2,7,8'). Default: all.",
    )
    p.add_argument(
        "--api-key-env",
        type=str,
        default=None,
        help="Env var holding the API key. Defaults to OPENAI_API_KEY "
        "for openai or ANTHROPIC_API_KEY for anthropic.",
    )
    p.add_argument(
        "--retry",
        type=int,
        default=3,
        help="Retries per API call on transient failure.",
    )
    p.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
    )
    return p.parse_args()


def load_ladder(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_probe(text: str) -> str:
    """YAML folded scalars collapse newlines to spaces but keep one trailing
    newline. Strip it and collapse internal runs of whitespace."""
    return " ".join(text.split()).strip()


def select_stages(stages: list[dict], wanted: str | None) -> list[dict]:
    if not wanted:
        return stages
    ids = {int(s.strip()) for s in wanted.split(",") if s.strip()}
    selected = [s for s in stages if s["id"] in ids]
    missing = ids - {s["id"] for s in selected}
    if missing:
        raise SystemExit(f"Unknown stage id(s): {sorted(missing)}")
    return selected


def already_done(jsonl_path: Path) -> set[tuple[int, int]]:
    if not jsonl_path.exists():
        return set()
    done: set[tuple[int, int]] = set()
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            done.add((int(row["stage_id"]), int(row["sample_idx"])))
    return done


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


def write_run_config(
    run_dir: Path,
    args: argparse.Namespace,
    ladder_path: Path,
    ladder_id: str,
    n_stages: int,
) -> None:
    cfg = {
        "ladder_path": str(ladder_path),
        "ladder_id": ladder_id,
        "n_stages": n_stages,
        "provider": args.provider,
        "model": args.model,
        "temperature": args.temperature,
        "n_samples": args.n_samples,
        "max_tokens": args.max_tokens,
        "condition": "current_turn_only",
        "system_prompt": "",
        "git_commit": git_commit(),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    cfg_path = run_dir / "run_config.yaml"
    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


def make_caller(provider: str, api_key: str):
    """Return a callable (model, user_prompt, temperature, max_tokens) -> str
    for the given provider. SDK imports happen lazily."""
    if provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        def _call(model, user_prompt, temperature, max_tokens):
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()

        return _call

    if provider == "anthropic":
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise SystemExit(
                "anthropic package not installed. "
                "Run: pip install anthropic"
            ) from e

        client = Anthropic(api_key=api_key)

        def _call(model, user_prompt, temperature, max_tokens):
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": user_prompt}],
            )
            # Concatenate any text blocks; ignore non-text blocks (none expected).
            parts = [b.text for b in resp.content if getattr(b, "type", "") == "text"]
            return "".join(parts).strip()

        return _call

    raise ValueError(f"Unknown provider: {provider!r}")


def call_model(
    caller,
    model: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    retry_delay: float,
) -> str:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            return caller(model, user_prompt, temperature, max_tokens)
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                print(
                    f"  [retry {attempt + 1}/{retries - 1}] {type(e).__name__}: {e}",
                    file=sys.stderr,
                )
                time.sleep(retry_delay * (attempt + 1))
    raise RuntimeError(f"API call failed after {retries} attempts: {last_err}")


def iter_jobs(stages: list[dict], n_samples: int) -> Iterable[tuple[dict, int]]:
    for stage in stages:
        for sample_idx in range(n_samples):
            yield stage, sample_idx


def main() -> None:
    args = parse_args()

    if args.api_key_env is None:
        args.api_key_env = (
            "ANTHROPIC_API_KEY" if args.provider == "anthropic"
            else "OPENAI_API_KEY"
        )
    api_key = os.getenv(args.api_key_env)
    if not api_key:
        raise SystemExit(
            f"Set {args.api_key_env} in your environment before running."
        )

    ladder = load_ladder(args.ladder)
    ladder_id = ladder["id"]
    stages = select_stages(ladder["stages"], args.stages)

    if args.output_dir is None:
        date = dt.date.today().isoformat()
        args.output_dir = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "runs"
            / f"{date}_{ladder_id}"
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = args.output_dir / "direct_probe.jsonl"
    done = already_done(jsonl_path)
    if done:
        print(f"Resuming: {len(done)} (stage, sample) pairs already in {jsonl_path}.")

    write_run_config(
        run_dir=args.output_dir,
        args=args,
        ladder_path=args.ladder,
        ladder_id=ladder_id,
        n_stages=len(stages),
    )

    caller = make_caller(args.provider, api_key)

    total_jobs = len(stages) * args.n_samples
    print(
        f"Running {total_jobs} probes "
        f"({len(stages)} stages × {args.n_samples} samples) "
        f"on {args.provider}:{args.model} @ T={args.temperature}"
    )

    n_done = 0
    n_skipped = 0
    with jsonl_path.open("a", encoding="utf-8") as f:
        for stage, sample_idx in iter_jobs(stages, args.n_samples):
            stage_id = int(stage["id"])
            stage_name = stage["name"]
            key = (stage_id, sample_idx)
            if key in done:
                n_skipped += 1
                continue

            probe = normalize_probe(stage["probe"])
            print(f"[stage {stage_id:>2} / sample {sample_idx}] {stage_name}")
            response = call_model(
                caller=caller,
                model=args.model,
                user_prompt=probe,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                retries=args.retry,
                retry_delay=args.retry_delay,
            )
            row = {
                "stage_id": stage_id,
                "stage_name": stage_name,
                "condition": "current_turn_only",
                "sample_idx": sample_idx,
                "provider": args.provider,
                "model": args.model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "probe": probe,
                "response": response,
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            n_done += 1

    print(
        f"Done. wrote={n_done}, skipped={n_skipped}, total_in_jsonl="
        f"{len(done) + n_done}"
    )
    print(f"Run dir: {args.output_dir}")


if __name__ == "__main__":
    main()
