"""
V4 Speaker Ablation: which part of the conversation history drives drift?

Four conditions on the same fixed user messages:
  full_context    — assistant sees full history (user + assistant turns)
  no_memory       — assistant sees only the current user message
  user_only       — assistant sees only past user messages (no assistant replies)
  assistant_only  — assistant sees only past assistant replies (no user messages)

If drift is driven by the assistant's own prior accommodating responses:
  → assistant_only ≈ full_context > user_only ≈ no_memory

If drift is driven by accumulated user escalation:
  → user_only ≈ full_context > assistant_only ≈ no_memory

Uses the same fixed trajectory and evaluator as run_v4_fixed_trajectory.py.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.utils import call_llm, configure_llm_backend, parse_json_response, validate_score

configure_llm_backend(api_key=os.environ["OPENAI_API_KEY"], base_url=None)
from src.lookism_agent_drift import (
    _enablement_evaluator_system_prompt,
    _enablement_evaluator_input_prompt,
)

# Import fixed messages and config from V4
from scripts.experiments.run_v4_fixed_trajectory import (
    ALL_USER_MESSAGES,
    TOTAL_TURNS,
    PHASE1_END, PHASE2A_END, PHASE2B_END, PHASE2C_END,
    ASSISTANT_MODEL, EVALUATOR_MODEL, ASSISTANT_SYSTEM,
    phase_label, evaluate,
)

OUT_ROOT = Path("data/manual_transcripts")

CONDITIONS = ["full_context", "no_memory", "user_only", "assistant_only"]

# ---------------------------------------------------------------------------
# History rendering per condition
# ---------------------------------------------------------------------------


def render_history_filtered(
    history: list[tuple[str, str]],
    mode: str,
    limit: int = 40,
) -> str:
    """Render conversation history filtered by mode."""
    recent = history[-limit:]
    lines = []
    for speaker, text in recent:
        if mode == "full_context":
            label = "User" if speaker == "user" else "Assistant"
            lines.append(f"{label}: {text}")
        elif mode == "user_only" and speaker == "user":
            lines.append(f"User: {text}")
        elif mode == "assistant_only" and speaker == "assistant":
            lines.append(f"Assistant: {text}")
        # no_memory: nothing
    return "\n".join(lines)


def get_assistant_reply(
    history: list[tuple[str, str]],
    user_msg: str,
    mode: str,
) -> str:
    if mode == "no_memory" or not history:
        prompt = f"User: {user_msg}\n\nReply:"
    else:
        history_text = render_history_filtered(history, mode)
        if history_text:
            prompt = (
                f"Conversation so far:\n{history_text}\n\nUser: {user_msg}\n\nReply:"
            )
        else:
            prompt = f"User: {user_msg}\n\nReply:"

    return call_llm(
        system_prompt=ASSISTANT_SYSTEM,
        user_prompt=prompt,
        model=ASSISTANT_MODEL,
        temperature=0.7,
    )


# ---------------------------------------------------------------------------
# Run one condition
# ---------------------------------------------------------------------------


def run_condition(mode: str) -> list[dict]:
    history: list[tuple[str, str]] = []
    turns_log: list[dict] = []

    for turn_idx in range(TOTAL_TURNS):
        user_msg = ALL_USER_MESSAGES[turn_idx]
        assistant_text = get_assistant_reply(history, user_msg, mode)
        score, reason = evaluate(user_msg, assistant_text)

        history.append(("user", user_msg))
        history.append(("assistant", assistant_text))

        turns_log.append({
            "turn": turn_idx,
            "phase": phase_label(turn_idx),
            "user_msg": user_msg,
            "assistant_text": assistant_text,
            "enablement_score": score,
            "enablement_reason": reason,
        })

        print(f"  [{mode:<16s}] T{turn_idx:02d} [{phase_label(turn_idx)}] score={score:.0f}")

    return turns_log


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


def analyze(all_results: list[dict]) -> str:
    from scipy import stats

    N = len(all_results)
    phases = [
        ("Setup (T0-7)", 0, PHASE1_END),
        ("Middle-A (T8-15)", PHASE1_END, PHASE2A_END),
        ("Middle-B (T16-25)", PHASE2A_END, PHASE2B_END),
        ("Middle-C (T26-35)", PHASE2B_END, PHASE2C_END),
        ("Late/Thr (T36-49)", PHASE2C_END, TOTAL_TURNS),
    ]

    # Build score matrices per condition
    mats = {}
    for cond in CONDITIONS:
        mats[cond] = np.array([
            [t["enablement_score"] for t in r[cond]]
            for r in all_results
        ])

    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"V4 Speaker Ablation — N={N} runs")
    lines.append(f"{'='*80}")

    # Overall means
    lines.append("\nOverall means:")
    for cond in CONDITIONS:
        lines.append(f"  {cond:<20s} {mats[cond].mean():.2f}")

    # Phase breakdown
    lines.append(f"\n{'Phase':<22} {'full':>6} {'nomem':>6} {'user':>6} {'asst':>6}")
    lines.append("-" * 55)
    for name, lo, hi in phases:
        vals = {c: mats[c][:, lo:hi].mean() for c in CONDITIONS}
        lines.append(
            f"{name:<22} {vals['full_context']:>6.2f} {vals['no_memory']:>6.2f} "
            f"{vals['user_only']:>6.2f} {vals['assistant_only']:>6.2f}"
        )

    # Pairwise comparisons vs no_memory (if N > 1)
    if N > 1:
        lines.append(f"\nPairwise vs no_memory (paired t-test, Late/Threshold phase):")
        lines.append(f"{'Condition':<20s} {'Δ':>7} {'p':>8} {'sig':>4}")
        lines.append("-" * 45)
        nomem_late = mats["no_memory"][:, PHASE2C_END:TOTAL_TURNS].mean(1)
        for cond in ["full_context", "user_only", "assistant_only"]:
            cond_late = mats[cond][:, PHASE2C_END:TOTAL_TURNS].mean(1)
            d = cond_late.mean() - nomem_late.mean()
            t_stat, p = stats.ttest_rel(cond_late, nomem_late)
            sig = "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.1 else ""
            lines.append(f"{cond:<20s} {d:>+7.2f} {p:>8.3f} {sig:>4}")

    # Key turns
    key_turns = [25, 30, 35, 40, 45, 47, 48, 49]
    lines.append(f"\nKey turns:")
    lines.append(f"{'Turn':<6} {'full':>6} {'nomem':>6} {'user':>6} {'asst':>6}")
    for t in key_turns:
        vals = {c: mats[c][:, t].mean() for c in CONDITIONS}
        lines.append(
            f"T{t:<4d} {vals['full_context']:>6.1f} {vals['no_memory']:>6.1f} "
            f"{vals['user_only']:>6.1f} {vals['assistant_only']:>6.1f}"
        )

    text = "\n".join(lines)
    print(text)
    return text


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUT_ROOT / f"v4_speaker_ablation_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    N_RUNS = int(os.environ.get("V4_ABLATION_RUNS", "1"))

    print(f"V4 Speaker Ablation Experiment")
    print(f"  Turns: {TOTAL_TURNS}  |  Model: {ASSISTANT_MODEL}")
    print(f"  Runs: {N_RUNS}  |  Conditions: {CONDITIONS}")
    print(f"  Output: {out_dir}")
    print()

    all_results = []

    for run_idx in range(N_RUNS):
        print(f"\n====== Run {run_idx} ======")
        result = {"run_idx": run_idx}

        for cond in CONDITIONS:
            print(f"  --- {cond} ---")
            result[cond] = run_condition(cond)

        all_results.append(result)

        run_path = out_dir / f"run_{run_idx:02d}.json"
        run_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Saved: {run_path}")

    (out_dir / "all_runs.json").write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    analysis_text = analyze(all_results)
    (out_dir / "analysis.txt").write_text(analysis_text, encoding="utf-8")


if __name__ == "__main__":
    main()
