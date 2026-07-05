#!/usr/bin/env python3
"""Run the vendored DelusionEval (Jared Moore) 16-code judge over our replies.

EXTERNAL ANCHOR ONLY. Judge = gpt-5.1, default temperature, preceding_context=3,
per-code raw score 0-10 binarized at the per-code cutoff (cutoffs.csv). Never mixed
with our fresh-Claude judge in one series. Vendored from the PUBLIC repos (provenance
external/PROVENANCE.md).
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "external/llm-delusions-annotations/src"))
sys.path.insert(0, str(REPO / "scripts"))
from llm_delusions_annotations.annotation_prompts import (  # noqa: E402
    ANNOTATIONS, ANNOTATION_SYSTEM_PROMPT, build_prompt,
)
from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file  # noqa: E402

ANN_BY_ID = {a["id"]: a for a in ANNOTATIONS}
_CUT_PATH = REPO / "external/llm-delusions-annotations/src/llm_delusions_annotations/data/cutoffs.csv"
CUTOFFS = {r["annotation_id"]: int(r["cutoff"]) for r in csv.DictReader(_CUT_PATH.open())}


def list_bot_codes() -> list[str]:
    return sorted(cid for cid in ANN_BY_ID if cid.startswith("bot-") and cid in CUTOFFS)


def judge(api_key: str, reply: str, context: list[dict], code_id: str,
          model: str = "gpt-5.1") -> tuple[int | None, str]:
    """Score one assistant reply against one code. Returns (score 0-10, raw)."""
    prompt = build_prompt(ANN_BY_ID[code_id], reply, role="assistant", context_messages=context)
    wargs = argparse.Namespace(timeout=180, temperature=1.0, max_tokens_gpt4o=1500, max_tokens_gpt5=4000)
    r = call_openai_chat(api_key=api_key, model=model,
                         messages=[{"role": "system", "content": ANNOTATION_SYSTEM_PROMPT},
                                   {"role": "user", "content": prompt}], args=wargs)
    raw = r["content"]
    try:
        return int(json.loads(raw)["score"]), raw
    except Exception:
        m = re.search(r'"score"\s*:\s*(\d+)', raw)
        return (int(m.group(1)) if m else None), raw


def preceding(turns: list[dict], idx: int, n: int = 3) -> list[dict]:
    return [{"role": t["role"], "content": t["content"]} for t in turns[max(0, idx - n):idx]]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--list-codes", action="store_true")
    p.add_argument("--traj", nargs="+", help="trajectory json files")
    p.add_argument("--rungs", nargs="+", default=["D12", "D12.5"], help="assistant rungs to score")
    p.add_argument("--codes", nargs="+", default=["bot-endorses-delusion", "bot-validates-ideas",
                   "bot-positive-affirmation", "bot-dismisses-counterevidence"])
    p.add_argument("--model", default="gpt-5.1")
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--i-have-owner-signoff", action="store_true")
    args = p.parse_args()

    if args.list_codes:
        for cid in list_bot_codes():
            print(f"  {cid:34} cutoff={CUTOFFS[cid]}  {ANN_BY_ID[cid]['name']}")
        return 0

    missing = [c for c in args.codes if c not in ANN_BY_ID or c not in CUTOFFS]
    if missing:
        raise SystemExit(f"unknown/uncutoff codes: {missing}")
    if not args.i_have_owner_signoff:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    load_env_file(ROOT / ".env")
    key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit(f"set {args.api_key_env}")

    rows = []
    for tf in args.traj:
        d = json.loads(Path(tf).read_text())
        turns = d["turns"]
        model = d.get("model", "?")
        for i, t in enumerate(turns):
            if t["role"] != "assistant":
                continue
            base = str(t.get("rung", "")).upper().replace("_", "-").split("-REASK")[0]
            if base not in [r.upper() for r in args.rungs]:
                continue
            ctx = preceding(turns, i, 3)
            for code in args.codes:
                s, _ = judge(key, t["content"], ctx, code, args.model)
                hit = (s is not None and s >= CUTOFFS[code])
                rows.append({"file": Path(tf).name, "model": model, "rung": t.get("rung"),
                             "code": code, "score": s, "cutoff": CUTOFFS[code], "present": hit})
                print(f"  {Path(tf).name:16} {str(t.get('rung')):10} {code:30} score={s} "
                      f"cutoff={CUTOFFS[code]} -> {'PRESENT' if hit else '.'}")

    print("\n=== prevalence per code (present / scored) ===")
    for code in args.codes:
        r = [x for x in rows if x["code"] == code]
        print(f"  {code:30} {sum(x['present'] for x in r)}/{len(r)}")
    print("=== any-code present per reply ===")
    by_reply = {}
    for x in rows:
        k = (x["file"], x["rung"])
        by_reply.setdefault(k, []).append(x["present"])
    n_hit = sum(1 for v in by_reply.values() if any(v))
    print(f"  {n_hit}/{len(by_reply)} replies present on >=1 code")
    if args.out:
        args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
