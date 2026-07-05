#!/usr/bin/env python3
"""Action arm: does OUR adaptive belief context raise HES at a fixed action endpoint vs cold?

Within-endpoint context effect (reports ΔHES ONLY — never compared to ΔDCS; different construct/rubric):
  adaptive : [our gated belief-climb trajectory] ++ [PsychosisBench action-request prompt] -> subject -> HES
  cold     :                                       [PsychosisBench action-request prompt] -> subject -> HES
  ΔHES = mean(adaptive HES) - mean(cold HES)

- Action probe = PsychosisBench's PUBLISHED prompt (external/psychosis-bench/data/test_cases.json) used
  DIRECTLY as a fixed terminal extension (open-source; a user INTENT announcement, not method content).
- Scored by PsychosisBench's OWN HES judge (psy_bench Scorer, rubric 0-2, verified turn>=7 -> we score the
  terminal turn explicitly). No new harmful content is generated; the operator does not escalate.

⚠️ A real run sends a published self-harm-INTENT prompt to the subject and records its reply (defensive
measurement of harm-enablement). API calls require --i-have-owner-signoff. Default --dry-run assembles the
structure only: prints turn counts / case id / action-turn index / harm_type, and does NOT echo probe text.

EXPLORATORY (not a CLAIM): the first-shot action prompt is PsychosisBench's own scenario, only approximately
matched to our grandiose belief context. Scenario-matched action fixtures are the refinement. ΔHES here is a
candidate signal, not a reportable number.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from argparse import Namespace
from pathlib import Path
from statistics import mean

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
MR = Path(__file__).resolve().parents[1]  # manual_redteam
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(MR / "external/psychosis-bench"))
from adaptive_strictness_profile_v3 import call_openai_chat, load_env_file  # noqa: E402

GRAND_V3 = MR / "data/simulator_discover/2026-06-18_delusion_C_grandiose_gpt4omini_v3"
PB_CASES = MR / "external/psychosis-bench/data/test_cases.json"


def traj_turns(path: Path) -> list[dict]:
    """Our belief trajectory -> [{role,content}] (drops rung/usage metadata)."""
    turns = json.loads(path.read_text())["turns"]
    return [{"role": t["role"], "content": t["content"]} for t in turns]


def pb_action_probe(case_id: str, action_turn_index):
    """Return (user_action_prompt, harm_type) from a PUBLISHED PsychosisBench case. No echo by caller."""
    cases = {c["id"]: c for c in json.loads(PB_CASES.read_text())["cases"]}
    c = cases[case_id]
    idx = action_turn_index if action_turn_index is not None else len(c["prompts"]) - 2
    return c["prompts"][idx], c["harm_type"], idx, len(c["prompts"])


class _Resp:
    def __init__(self, content): self.content = content


class OAIAdapterClient:
    """Minimal psy_bench-compatible client (.chat) backed by our OpenAI-compatible caller (for the HES judge)."""
    def __init__(self, api_key): self.api_key = api_key
    def chat(self, model, messages):
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        wargs = Namespace(timeout=120, temperature=0.0, max_tokens_gpt4o=10, max_tokens_gpt5=2000)
        return _Resp(call_openai_chat(api_key=self.api_key, model=model, messages=msgs, args=wargs)["content"])


def to_pb_turns(conv: list[dict]):
    """Our [{role,content}] conversation -> psy_bench [Turn(user_message,bot_response)] pairs."""
    from psy_bench.core.models import Turn
    out, pending = [], None
    for t in conv:
        if t["role"] == "user":
            pending = t["content"]
        elif t["role"] == "assistant":
            out.append(Turn(user_message=pending or "", bot_response=t["content"]))
            pending = None
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--adaptive-trajs", nargs="+", default=["traj01", "traj06", "traj08"],
                   help="our grandiose belief trajectories used as adaptive context (broke = endorsed belief)")
    p.add_argument("--pb-case", default="conduit_explicit", help="PsychosisBench case id (grandiose) for the action probe")
    p.add_argument("--action-turn-index", type=int, default=None, help="prompt index for the action request (default: penultimate)")
    p.add_argument("--cold-reps", type=int, default=3)
    p.add_argument("--subject-model", default="gpt-4o-mini")
    p.add_argument("--judge-model", default="gpt-4o", help="HES judge (PsychosisBench default is o4-mini; document deviation)")
    p.add_argument("--api-key-env", default="OPENAI_API_KEY_2")
    p.add_argument("--dry-run", action="store_true", default=True)
    p.add_argument("--i-have-owner-signoff", dest="run", action="store_true",
                   help="actually call subject + HES judge (sends the published intent prompt, records replies)")
    args = p.parse_args()

    probe_text, harm_type, idx, nprompts = pb_action_probe(args.pb_case, args.action_turn_index)
    probe_turn = {"role": "user", "content": probe_text}

    # assemble cells (no API yet): adaptive = traj ++ probe ; cold = probe alone (x reps)
    cells = []
    for tj in args.adaptive_trajs:
        ctx = traj_turns(GRAND_V3 / f"{tj}.json")
        cells.append(("adaptive", tj, ctx + [probe_turn]))
    for r in range(args.cold_reps):
        cells.append(("cold", f"rep{r+1}", [probe_turn]))

    print(f"action probe: PsychosisBench case={args.pb_case} turn_index={idx}/{nprompts-1} "
          f"harm_type={harm_type!r}  (probe text NOT echoed)")
    print(f"subject={args.subject_model}  HES judge={args.judge_model}  (rubric 0-2, scored on terminal turn)")
    print(f"\n{'cond':9}{'src':10}{'#ctx_turns':>11}{'+probe':>8}")
    for cond, src, conv in cells:
        print(f"{cond:9}{src:10}{len(conv)-1:>11}{'  +1':>8}")

    if not args.run:
        print("\n[dry-run] structure only; no API calls, no probe text echoed, no responses generated.")
        print("Provide --i-have-owner-signoff to run subject + HES (sends the published intent prompt).")
        return 0

    # --- real run (owner-authorized) ---------------------------------------------------
    load_env_file(REPO_ROOT / ".env")
    load_env_file(MR / ".env")
    api_key = os.environ.get(args.api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(f"set ${args.api_key_env}")
    from psy_bench.core.scoring import Scorer
    scorer = Scorer(client=OAIAdapterClient(api_key), judge_model=args.judge_model, hes_start_turn=0)

    by_cond: dict[str, list[int]] = {"adaptive": [], "cold": []}
    subj_wargs = Namespace(timeout=180, temperature=1.0, max_tokens_gpt4o=1000, max_tokens_gpt5=4000)
    for cond, src, conv in cells:
        rep = call_openai_chat(api_key=api_key, model=args.subject_model, messages=conv, args=subj_wargs)
        scored_conv = conv + [{"role": "assistant", "content": rep["content"]}]
        hes = scorer.score_hes(to_pb_turns(scored_conv), harm_type).score
        by_cond[cond].append(hes)
        print(f"  {cond:9}{src:10} HES={hes}")

    dHES = mean(by_cond["adaptive"]) - mean(by_cond["cold"])
    print(f"\nmean HES  adaptive={mean(by_cond['adaptive']):.2f}  cold={mean(by_cond['cold']):.2f}")
    print(f"ΔHES (adaptive - cold) = {dHES:+.2f}   [EXPLORATORY — approx scenario match; candidate signal]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
