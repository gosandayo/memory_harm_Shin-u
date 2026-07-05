#!/usr/bin/env python3
"""External Jared anchor (gpt-5.1) for the accum-vs-push blind set, context-isolated.

Mirrors jared_fixedprobe.py (CODE=bot-endorses-delusion, cutoff per CUTOFFS) but
parametrized to this dir and routed via OpenRouter (model openai/gpt-5.1) using
OPENROUTER_API_KEY from ../.env. Reads the sealed blind set; writes jared_scores.json.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from jared_judge import judge, CUTOFFS  # noqa: E402
from adaptive_strictness_profile_v3 import load_env_file  # noqa: E402

CODE = "bot-endorses-delusion"
CUT = CUTOFFS[CODE]
D = REPO / "data/blindpass/2026-06-23_accum_vs_push"
MODEL = "openai/gpt-5.1"  # OpenRouter-prefixed


def main():
    if "--i-have-owner-signoff" not in sys.argv:
        raise SystemExit("Pass --i-have-owner-signoff to launch API calls.")
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    load_env_file(ROOT / ".env")
    # Route the OpenAI-shaped client at OpenRouter using the OpenRouter key.
    or_key = os.environ.get("OPENROUTER_API_KEY")
    if or_key:
        os.environ.setdefault("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        os.environ["OPENAI_API_KEY"] = or_key
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("no OPENROUTER_API_KEY / OPENAI_API_KEY in env")

    items = json.loads((D / "blind_items.json").read_text())
    if limit:
        items = items[:limit]
    out = []
    for it in items:
        ctx = [{"role": "user", "content": it["user_turn"]}]
        s, _ = judge(key, it["assistant_reply"], ctx, CODE, MODEL)
        out.append({"blind_id": it["blind_id"], "score": s,
                    "present": (s or 0) >= CUT})
        print(f"  {it['blind_id']}  score={s}  cutoff={CUT}  "
              f"{'PRESENT' if (s or 0) >= CUT else '.'}")
    suffix = f"_test{limit}" if limit else ""
    outp = D / f"jared_scores{suffix}.json"
    outp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {outp} ({len(out)} items); present "
          f"{sum(x['present'] for x in out)}/{len(out)}; model {MODEL}")


if __name__ == "__main__":
    main()
