#!/usr/bin/env python3
"""Generalized manifest-driven fixed panel runner.

Sibling of s15_plain_panel.py. Differences:
  * cells are declared in a manifest YAML, not hardcoded;
  * every turn's user text is loaded VERBATIM from an existing run jsonl by
    (source_file, source_rung), OR from a reviewed prompt file for the one
    owner-approved minimal-pair construction. The script never contains or
    authors terminal prompt text.

Manifest schema (see manifest.yaml in the run dir):

    cells:
      - name: S13_cold_forced_only
        turns:
          - source_file: <repo-rel jsonl>      # load user turn from here
            source_rung: S15_cold_forced       # rung/stage key in that jsonl
      - name: S13_cold_forced_ctxclaim
        turns:
          - prompt_file: <repo-rel .txt>       # reviewed constructed minimal pair
            rung: S15_cold_context_forced

Each cell is run independently (fresh history) N times. Cold cells have one
turn; hot/durability cells list several turns replayed in order.

Launch is gated: this script does nothing until invoked, and will refuse to
run cells whose manifest entry is marked `pending_signoff: true`.
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--max-tokens", type=int, default=1200)
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--retry", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    p.add_argument(
        "--i-have-owner-signoff",
        action="store_true",
        help="Required to actually call the API. Without it, dry-run only.",
    )
    return p.parse_args()


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO_ROOT / ".env")


def _resolve(rel: str) -> Path:
    pth = Path(rel)
    return pth if pth.is_absolute() else REPO_ROOT / pth


def load_user_turn(source_file: str, source_rung: str) -> str:
    """Load the verbatim user content for a rung from an existing jsonl."""
    path = _resolve(source_file)
    matches: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if row.get("role") != "user":
            continue
        if (row.get("rung") or row.get("stage")) == source_rung:
            matches.append(row["content"])
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise SystemExit(
            f"rung {source_rung!r} matched {len(matches)} user turns in "
            f"{source_file}; fixed_panel requires an unambiguous source_rung. "
            "Use a prompt_file or add positional replay support for multi-turn sources."
        )
    raise SystemExit(f"rung {source_rung!r} not found in {source_file}")


def build_turns(cell: dict) -> list[tuple[str, str]]:
    turns: list[tuple[str, str]] = []
    for t in cell["turns"]:
        if "prompt_file" in t:
            text = _resolve(t["prompt_file"]).read_text(encoding="utf-8").strip()
            rung = t.get("rung", "constructed")
        else:
            text = load_user_turn(t["source_file"], t["source_rung"])
            rung = t.get("rung", t["source_rung"])
        turns.append((rung, text))
    return turns


def make_client(api_key: str):
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def call_with_retry(client, args, history):
    last_exc = None
    for attempt in range(args.retry):
        try:
            resp = client.chat.completions.create(
                model=args.model,
                messages=history,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
            )
            return (resp.choices[0].message.content or "").strip(), {
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


def run_cell(*, client, args, out_root: Path, cell: dict, dry_run: bool) -> None:
    name = cell["name"]
    if cell.get("pending_signoff"):
        if dry_run:
            turns = build_turns(cell)
            print(f"[GATED - pending_signoff, validated] {name}: {len(turns)} turn(s)")
        else:
            print(f"[GATED - pending_signoff, skipped] {name}")
        return
    turns = build_turns(cell)
    for idx in range(args.n):
        branch = out_root / "branches" / f"{name}_run{idx:02d}"
        msg_path = branch / "messages.jsonl"
        if msg_path.exists() and msg_path.stat().st_size > 0:
            print(f"[skip existing] {branch.relative_to(REPO_ROOT)}")
            continue
        if dry_run:
            print(f"[dry-run] would run {name} run{idx:02d}: {len(turns)} turn(s)")
            continue
        branch.mkdir(parents=True, exist_ok=True)
        (branch / "session_meta.yaml").write_text(
            yaml.safe_dump(
                {
                    "run_id": branch.name,
                    "cell": name,
                    "model": args.model,
                    "temperature": args.temperature,
                    "max_tokens": args.max_tokens,
                    "condition": "fixed_panel",
                    "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        history: list[dict[str, str]] = []
        with msg_path.open("w", encoding="utf-8") as f:
            for turn_index, (rung, user_text) in enumerate(turns, start=1):
                history.append({"role": "user", "content": user_text})
                assistant_text, extra = call_with_retry(client, args, history)
                history.append({"role": "assistant", "content": assistant_text})
                f.write(json.dumps({"role": "user", "content": user_text, "rung": rung, "turn_index": turn_index}, ensure_ascii=False) + "\n")
                f.write(json.dumps({"role": "assistant", "content": assistant_text, "rung": rung, "turn_index": turn_index, **extra}, ensure_ascii=False) + "\n")
                f.flush()
                print(f"[{name} {idx:02d}] {rung} done")


def main() -> int:
    args = parse_args()
    manifest = yaml.safe_load(_resolve(str(args.manifest)).read_text(encoding="utf-8"))
    out_root = _resolve(str(args.manifest)).parent
    cells = manifest.get("cells", [])
    if not cells:
        raise SystemExit("manifest has no `cells:` list")

    dry_run = not args.i_have_owner_signoff
    if dry_run:
        print("=== DRY RUN (no API calls). Pass --i-have-owner-signoff to launch. ===")
        client = None
    else:
        load_dotenv_if_available()
        api_key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit(f"{args.api_key_env} / OPENAI_API_KEY not set")
        client = make_client(api_key)

    for cell in cells:
        run_cell(client=client, args=args, out_root=out_root, cell=cell, dry_run=dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
