#!/usr/bin/env python3
"""Parse Psychosis-Bench's pre-generated gpt-4o transcripts and score them with the
vendored Jared (DelusionEval) judge — matched comparison vs our trajectories.
Same judge (gpt-5.1), same codes, same preceding_context=3, same per-code cutoff."""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from jared_judge import judge, CUTOFFS  # noqa: E402
sys.path.insert(0, str(REPO / "scripts"))
from adaptive_strictness_profile_v3 import load_env_file  # noqa: E402

MD = REPO / "external/psychosis-bench/outputs/20250905_000927_async_batch_8models_16cases.md"


def parse_experiments(md_text: str) -> list[dict]:
    blocks = re.split(r"(?m)^## Experiment \d+:", md_text)
    exps = []
    for b in blocks[1:]:
        model = (re.search(r"\*\*Model:\*\*\s*(.+)", b) or [None, None])[1]
        theme = (re.search(r"\*\*Theme:\*\*\s*(.+)", b) or [None, None])[1]
        cond = (re.search(r"\*\*Condition:\*\*\s*(.+)", b) or [None, None])[1]
        case = b.splitlines()[0].strip()
        conv = b.split("## Conversation", 1)
        turns: list[tuple[str, str]] = []
        if len(conv) == 2:
            # split by turn markers
            for tchunk in re.split(r"(?m)^### Turn \d+", conv[1])[1:]:
                um = re.search(r"\*\*.{0,3}User:\*\*\s*(.*?)(?=\*\*.{0,3}Assistant:\*\*|$)", tchunk, re.S)
                am = re.search(r"\*\*.{0,3}Assistant:\*\*\s*(.*)", tchunk, re.S)
                u = um.group(1).strip() if um else ""
                a = am.group(1).strip() if am else ""
                if a:
                    turns.append((u, a))
        exps.append({"case": case, "model": (model or "").strip(),
                     "theme": (theme or "").strip(), "condition": (cond or "").strip(),
                     "turns": turns})
    return exps


def flat_messages(turns: list[tuple[str, str]]) -> list[dict]:
    msgs = []
    for u, a in turns:
        if u:
            msgs.append({"role": "user", "content": u})
        msgs.append({"role": "assistant", "content": a})
    return msgs


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model-filter", default="openai/gpt-4o")
    p.add_argument("--codes", nargs="+", default=["bot-endorses-delusion", "bot-positive-affirmation"])
    p.add_argument("--last-n", type=int, default=2, help="score the last N assistant turns per case")
    p.add_argument("--stride", type=int, default=0, help="if >0, score every Nth assistant turn (full depth) instead of last-n")
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--out", type=Path, default=REPO / "data/blindpass/2026-06-16_jared_judge_psychosis_gpt4o.json")
    p.add_argument("--i-have-owner-signoff", action="store_true")
    args = p.parse_args()
    if not args.i_have_owner_signoff:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    load_env_file(ROOT / ".env")
    key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")

    exps = [e for e in parse_experiments(MD.read_text()) if e["model"] == args.model_filter]
    print(f"parsed {len(exps)} {args.model_filter} experiments")
    rows = []
    for e in exps:
        msgs = flat_messages(e["turns"])
        asst_idx = [i for i, m in enumerate(msgs) if m["role"] == "assistant"]
        sel = asst_idx[::args.stride] if args.stride else asst_idx[-args.last_n:]
        for i in sel:
            depth = asst_idx.index(i)  # 0-based assistant-turn depth
            ctx = [{"role": m["role"], "content": m["content"]} for m in msgs[max(0, i - 3):i]]
            for code in args.codes:
                s, _ = judge(key, msgs[i]["content"], ctx, code)
                hit = (s is not None and s >= CUTOFFS[code])
                rows.append({"case": e["case"], "theme": e["theme"], "cond": e["condition"],
                             "code": code, "score": s, "present": hit, "depth": depth})
        anyhit = any(r["present"] for r in rows if r["case"] == e["case"])
        print(f"  {e['case'][:42]:42} {e['theme'][:22]:22} -> {'PRESENT' if anyhit else '.'}")

    print("\n=== Psychosis-Bench gpt-4o prevalence (Jared judge) ===")
    for code in args.codes:
        r = [x for x in rows if x["code"] == code]
        print(f"  {code:30} item {sum(x['present'] for x in r)}/{len(r)}")
    by_case = defaultdict(list)
    for x in rows:
        by_case[x["case"]].append(x["present"])
    print(f"  any-code per case: {sum(1 for v in by_case.values() if any(v))}/{len(by_case)}")
    print("  per theme (cases present / total):")
    th = defaultdict(lambda: [0, 0])
    seen = {}
    for x in rows:
        seen.setdefault(x["case"], x["theme"])
    for case, theme in seen.items():
        th[theme][1] += 1
        if any(by_case[case]):
            th[theme][0] += 1
    for theme, (h, n) in th.items():
        print(f"    {theme:26} {h}/{n}")
    print("  per depth (present / scored, first code):")
    dd = defaultdict(lambda: [0, 0])
    c0 = args.codes[0]
    for x in rows:
        if x["code"] == c0:
            dd[x["depth"]][1] += 1
            dd[x["depth"]][0] += int(x["present"])
    for depth in sorted(dd):
        h, n = dd[depth]
        print(f"    depth {depth}: {h}/{n}")
    args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
