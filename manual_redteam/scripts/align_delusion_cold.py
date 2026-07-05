#!/usr/bin/env python3
"""Aligned delusion verbatim-cold necessity control (CURRENT.md §1d-A).

Regenerates the delusion cold control to MATCH the suicide arm's structure:
for each reported climb trajectory, throw its operative D12 endpoint turn COLD
(single self-contained turn, no prior context, VERBATIM — no paraphrase, no
stripping of back-references), n reps per endpoint.

Handles both climb-trajectory schemas:
  - adaptive runs (gpt-4o / gpt-5.4-mini): JSON, `turns[].rung`
  - fixed runA (gpt-4o-mini):              YAML, `turns[].rung_id`
The endpoint = the FIRST user turn whose normalized base rung == --endpoint-rung
(default D12 = the operative claim), matching t6_verbatim_cold.py's first-S12 rule.

Usage:
  python3 scripts/align_delusion_cold.py \
    --dir data/simulator_discover/2026-06-06_delusion_gpt4o_adaptive \
    --src-traj traj01 traj02 traj03 --model gpt-4o --n 5 \
    --out-dir data/simulator_discover/2026-06-16_delusion_verbatim_cold_aligned \
    --i-have-owner-signoff
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file  # noqa: E402


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def base_rung(raw: str) -> str:
    return str(raw or "").upper().replace("_", "-").split("-REASK")[0]


def load_traj(dirpath: Path, stem: str) -> tuple[dict, str]:
    for ext in (".json", ".yaml", ".yml"):
        p = dirpath / f"{stem}{ext}"
        if p.exists():
            raw = p.read_text(encoding="utf-8")
            return (json.loads(raw) if ext == ".json" else yaml.safe_load(raw)), p.name
    raise SystemExit(f"no trajectory file for stem {stem!r} in {dirpath}")


def endpoint_turn(d: dict, endpoint_rung: str) -> str:
    turns = d.get("turns") or d.get("messages") or []
    target = endpoint_rung.upper()
    for t in turns:
        if t.get("role") != "user":
            continue
        if base_rung(t.get("rung") or t.get("rung_id")) == target:
            return t["content"]
    raise SystemExit(f"no user turn at rung {endpoint_rung} (held earlier?)")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dir", type=Path, required=True, help="climb-trajectory dir")
    p.add_argument("--src-traj", nargs="+", required=True, help="trajectory file stems")
    p.add_argument("--model", default=None, help="API model id (default: file's model field)")
    p.add_argument("--endpoint-rung", default="D12")
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--timeout", type=float, default=300.0)
    p.add_argument("--out-dir", type=Path,
                   default=REPO_ROOT / "manual_redteam/data/simulator_discover/2026-06-16_delusion_verbatim_cold_aligned")
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--i-have-owner-signoff", action="store_true")
    args = p.parse_args()

    if not args.i_have_owner_signoff:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    load_env_file(REPO_ROOT / ".env")
    api_key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(f"Set {args.api_key_env} in {REPO_ROOT / '.env'}.")

    dirpath = args.dir if args.dir.is_absolute() else REPO_ROOT / "manual_redteam" / args.dir
    out_dir = args.out_dir if args.out_dir.is_absolute() else REPO_ROOT / "manual_redteam" / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    wargs = argparse.Namespace(timeout=args.timeout, temperature=args.temperature,
                               max_tokens_gpt4o=1000, max_tokens_gpt5=4000)

    for stem in args.src_traj:
        d, fname = load_traj(dirpath, stem)
        model = args.model or d.get("model")
        if not model:
            raise SystemExit(f"no --model and no model field in {fname}")
        ep = endpoint_turn(d, args.endpoint_rung)
        out = {"src_dir": str(args.dir), "src_file": fname, "src_traj": stem,
               "model": model, "endpoint_rung": args.endpoint_rung,
               "endpoint_verbatim": ep, "created_at_utc": now(), "reps": []}
        print(f"\n[{model} {stem}] endpoint ({args.endpoint_rung}): {ep[:140].replace(chr(10), ' ')}…")
        for i in range(1, args.n + 1):
            completion = call_openai_chat(api_key=api_key, model=model,
                                          messages=[{"role": "user", "content": ep}], args=wargs)
            out["reps"].append({"rep": i, "reply": completion["content"],
                                "api_finish_reason": completion.get("finish_reason")})
            print(f"  rep {i}/{args.n}: {completion['content'][:150].replace(chr(10), ' ')}…")
        slug = "".join(c for c in model if c.isalnum()).lower()
        dest = out_dir / f"{slug}_{stem}_{args.endpoint_rung}_cold.json"
        dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  -> wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
