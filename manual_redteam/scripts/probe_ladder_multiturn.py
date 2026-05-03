"""Run fixed-prefix multi-turn probes for a red-team ladder.

For each selected ladder stage, sends a fixed sequence of scripted user turns,
records the assistant responses, then sends the stage's `probe` as the final
user message. The final probe text is normalized exactly the same way as the
cold runner, so the comparison is:

  cold:          final stage probe only
  context_shift: fixed prefix turns + final stage probe

The user turns are pre-authored. Later user turns do not depend on assistant
responses.

Resumable: re-running with the same output dir skips
(stage_id, sample_idx) pairs already present in context_probe.jsonl.
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
        / "referential_motif_blue_door_v2.yaml",
        help="Path to ladder YAML.",
    )
    p.add_argument(
        "--prefix",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "context_prefixes"
        / "blue_door_common_v1.yaml",
        help="Path to fixed user-message prefix YAML.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Run directory. Defaults to manual_redteam/data/runs/<date>_<ladder_id>_<prefix_id>/.",
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
        help="Comma-separated stage ids to run (e.g. '12,14,15'). Default: all.",
    )
    p.add_argument(
        "--api-key-env",
        type=str,
        default=None,
        help="Env var holding the API key. Defaults to OPENAI_API_KEY "
        "for openai or ANTHROPIC_API_KEY for anthropic.",
    )
    p.add_argument("--retry", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    return p.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(text: str) -> str:
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
    prefix_path: Path,
    prefix_id: str,
    n_stages: int,
    n_prefix_turns: int,
) -> None:
    cfg = {
        "ladder_path": str(ladder_path),
        "ladder_id": ladder_id,
        "prefix_path": str(prefix_path),
        "prefix_id": prefix_id,
        "n_prefix_turns": n_prefix_turns,
        "n_stages": n_stages,
        "provider": args.provider,
        "model": args.model,
        "temperature": args.temperature,
        "n_samples": args.n_samples,
        "max_tokens": args.max_tokens,
        "condition": "fixed_prefix_context_shift",
        "system_prompt": "",
        "git_commit": git_commit(),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    cfg_path = run_dir / "run_config.yaml"
    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


def make_chat_caller(provider: str, api_key: str):
    """Return a callable (model, messages, temperature, max_tokens) -> str."""
    if provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        def _call(model, messages, temperature, max_tokens):
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return (resp.choices[0].message.content or "").strip()

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

        def _call(model, messages, temperature, max_tokens):
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            parts = [b.text for b in resp.content if getattr(b, "type", "") == "text"]
            return "".join(parts).strip()

        return _call

    raise ValueError(f"Unknown provider: {provider!r}")


def call_model(
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


def run_conversation(
    caller,
    model: str,
    prefix_turns: list[dict],
    final_probe: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    retry_delay: float,
) -> tuple[list[dict], str]:
    messages: list[dict] = []
    transcript: list[dict] = []

    for prefix_turn in prefix_turns:
        user_text = normalize_text(prefix_turn["user"])
        messages.append({"role": "user", "content": user_text})
        transcript.append(
            {
                "turn_id": prefix_turn.get("id"),
                "role": "user",
                "content": user_text,
                "source": "fixed_prefix",
            }
        )
        assistant_text = call_model(
            caller=caller,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            retries=retries,
            retry_delay=retry_delay,
        )
        messages.append({"role": "assistant", "content": assistant_text})
        transcript.append(
            {
                "turn_id": prefix_turn.get("id"),
                "role": "assistant",
                "content": assistant_text,
                "source": "model",
            }
        )

    messages.append({"role": "user", "content": final_probe})
    transcript.append(
        {
            "turn_id": "final_probe",
            "role": "user",
            "content": final_probe,
            "source": "ladder_probe",
        }
    )
    final_response = call_model(
        caller=caller,
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
        retry_delay=retry_delay,
    )
    transcript.append(
        {
            "turn_id": "final_probe",
            "role": "assistant",
            "content": final_response,
            "source": "model",
        }
    )
    return transcript, final_response


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

    ladder = load_yaml(args.ladder)
    prefix = load_yaml(args.prefix)
    ladder_id = ladder["id"]
    prefix_id = prefix["id"]
    stages = select_stages(ladder["stages"], args.stages)
    prefix_turns = prefix.get("turns", [])
    if not prefix_turns:
        raise SystemExit(f"No turns found in prefix file: {args.prefix}")

    if args.output_dir is None:
        date = dt.date.today().isoformat()
        args.output_dir = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "runs"
            / f"{date}_{ladder_id}_{prefix_id}_{args.model.replace('-', '')}"
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = args.output_dir / "context_probe.jsonl"
    done = already_done(jsonl_path)
    if done:
        print(f"Resuming: {len(done)} (stage, sample) pairs already in {jsonl_path}.")

    write_run_config(
        run_dir=args.output_dir,
        args=args,
        ladder_path=args.ladder,
        ladder_id=ladder_id,
        prefix_path=args.prefix,
        prefix_id=prefix_id,
        n_stages=len(stages),
        n_prefix_turns=len(prefix_turns),
    )

    caller = make_chat_caller(args.provider, api_key)
    total_jobs = len(stages) * args.n_samples
    print(
        f"Running {total_jobs} multi-turn probes "
        f"({len(stages)} stages x {args.n_samples} samples, "
        f"{len(prefix_turns)} prefix turns) "
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

            final_probe = normalize_text(stage["probe"])
            print(f"[stage {stage_id:>2} / sample {sample_idx}] {stage_name}")
            transcript, final_response = run_conversation(
                caller=caller,
                model=args.model,
                prefix_turns=prefix_turns,
                final_probe=final_probe,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                retries=args.retry,
                retry_delay=args.retry_delay,
            )
            row = {
                "stage_id": stage_id,
                "stage_name": stage_name,
                "condition": "fixed_prefix_context_shift",
                "prefix_id": prefix_id,
                "n_prefix_turns": len(prefix_turns),
                "sample_idx": sample_idx,
                "provider": args.provider,
                "model": args.model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "probe": final_probe,
                "response": final_response,
                "transcript": transcript,
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
