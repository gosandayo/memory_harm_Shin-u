"""
Speaker Ablation Experiment
==========================
Tests which speaker-side history drives harmful drift by replaying the same
user messages under different prompt-history filters.

Interpretation
--------------
This is a replay-style speaker ablation, not a fully end-to-end multi-agent
simulation for every condition.

Procedure
---------
1. Generate a single full-context conversation, exactly as in V3.
2. Replay the assistant on the same user messages under four conditions:
   - full_context
   - user_only_history
   - assistant_only_history
   - no_history
3. Score each assistant reply with the same harmful_advice evaluator.

This design isolates which speaker-side history is sufficient to shift the
assistant, while acknowledging that the user messages were originally generated
under the full-context path.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.utils import call_llm, configure_llm_backend, parse_json_response, validate_score

configure_llm_backend(api_key=os.environ["OPENAI_API_KEY"], base_url=None)

from src.lookism_agent_drift import (  # noqa: E402
    _enablement_evaluator_input_prompt,
    _enablement_evaluator_system_prompt,
)
from scripts.experiments.run_v2v3 import (  # noqa: E402
    ASSISTANT_MODEL,
    ASSISTANT_SYSTEM_OVERRIDE,
    EVALUATOR_MODEL,
    N_RUNS,
    OUT_ROOT,
    SCENARIO,
    SEED_ID,
    TOTAL_TURNS,
    PHASE1_END,
    PHASE2_END,
    PHASE3_END,
    get_user_message_v2,
    phase_label,
)


ABLATION_OUT_ROOT = (
    Path("data/manual_transcripts")
    / f"speaker_ablation_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)
ABLATION_OUT_ROOT.mkdir(parents=True, exist_ok=True)

CONDITIONS = [
    "full_context",
    "user_only_history",
    "assistant_only_history",
    "no_history",
]


def render_filtered_history(
    history: list[tuple[str, str]],
    mode: str,
) -> str:
    if mode == "no_history":
        return ""

    if mode == "user_only_history":
        filtered = [(role, text) for role, text in history if role == "user"]
    elif mode == "assistant_only_history":
        filtered = [(role, text) for role, text in history if role == "assistant"]
    else:
        filtered = history

    return "\n".join(f"{role.capitalize()}: {text}" for role, text in filtered)


def assistant_reply_with_mode(
    history: list[tuple[str, str]],
    user_msg: str,
    mode: str,
) -> str:
    rendered_history = render_filtered_history(history, mode)
    if rendered_history:
        user_prompt = (
            f"Conversation so far:\n{rendered_history}\n\n"
            f"User: {user_msg}\n\nReply:"
        )
    else:
        user_prompt = f"User: {user_msg}\n\nReply:"

    system_prompt = ASSISTANT_SYSTEM_OVERRIDE if ASSISTANT_SYSTEM_OVERRIDE is not None else ""
    return call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=ASSISTANT_MODEL,
        temperature=0.7,
    )


def evaluate(user_msg: str, assistant_text: str) -> tuple[float, str]:
    raw = call_llm(
        system_prompt=_enablement_evaluator_system_prompt("harmful_advice"),
        user_prompt=_enablement_evaluator_input_prompt(user_msg, assistant_text),
        model=EVALUATOR_MODEL,
        temperature=0.2,
        json_mode=True,
    )
    payload = parse_json_response(raw, ["enablement_score", "enablement_reason"])
    score = validate_score(payload["enablement_score"], "enablement_score")
    return score, payload.get("enablement_reason", "")


def generate_full_context_turns(run_idx: int) -> list[dict]:
    print(f"\n====== Run {run_idx + 1}/{N_RUNS}  — source full-context generation ======")
    history: list[tuple[str, str]] = []
    turns: list[dict] = []
    last_asst = ""

    for turn_idx in range(TOTAL_TURNS):
        user_msg = get_user_message_v2(turn_idx, history, last_asst)
        asst = assistant_reply_with_mode(history, user_msg, "full_context")
        score, reason = evaluate(user_msg, asst)
        history.append(("user", user_msg))
        history.append(("assistant", asst))
        last_asst = asst
        turns.append(
            {
                "turn": turn_idx,
                "phase": phase_label(turn_idx),
                "user_msg": user_msg,
                "assistant_text": asst,
                "enablement_score": score,
                "enablement_reason": reason,
                "memory_mode": "full_context",
            }
        )
        print(f"  [source] T{turn_idx:02d} {phase_label(turn_idx):<20} score={score}")

    return turns


def build_prefix_history(source_turns: list[dict], turn_idx: int) -> list[tuple[str, str]]:
    history: list[tuple[str, str]] = []
    for source_turn in source_turns[:turn_idx]:
        history.append(("user", source_turn["user_msg"]))
        history.append(("assistant", source_turn["assistant_text"]))
    return history


def replay_condition(source_turns: list[dict], mode: str) -> list[dict]:
    print(f"====== Replay condition: {mode} ======")
    replayed: list[dict] = []
    for source_turn in source_turns:
        prefix_history = build_prefix_history(source_turns, source_turn["turn"])
        asst = assistant_reply_with_mode(prefix_history, source_turn["user_msg"], mode)
        score, reason = evaluate(source_turn["user_msg"], asst)
        replayed.append(
            {
                "turn": source_turn["turn"],
                "phase": source_turn["phase"],
                "user_msg": source_turn["user_msg"],
                "assistant_text": asst,
                "enablement_score": score,
                "enablement_reason": reason,
                "memory_mode": mode,
            }
        )
        print(f"  [{mode[:8]:<8}] T{source_turn['turn']:02d} score={score}")
    return replayed


def phase_ranges() -> list[tuple[str, int, int]]:
    return [
        ("setup", 0, PHASE1_END),
        ("middle_escalation", PHASE1_END, PHASE2_END),
        ("late_validation", PHASE2_END, PHASE3_END),
        ("threshold_crossing", PHASE3_END, TOTAL_TURNS),
    ]


def summarize_modes(run_bundle: dict[str, list[dict]]) -> dict:
    summary: dict[str, dict] = {}
    for mode, turns in run_bundle.items():
        scores = np.array([turn["enablement_score"] for turn in turns], dtype=float)
        phase_stats = {}
        for phase_name, lo, hi in phase_ranges():
            segment = scores[lo:hi]
            phase_stats[phase_name] = {
                "mean": float(segment.mean()),
                "std": float(segment.std(ddof=1)) if len(segment) > 1 else 0.0,
            }
        summary[mode] = {
            "overall_mean": float(scores.mean()),
            "phase_stats": phase_stats,
        }
    return summary


def run_one(run_idx: int) -> dict:
    source_turns = generate_full_context_turns(run_idx)
    run_bundle: dict[str, list[dict]] = {"full_context": source_turns}

    for mode in CONDITIONS[1:]:
        run_bundle[mode] = replay_condition(source_turns, mode)

    data = {
        "run_idx": run_idx,
        "timestamp": datetime.now().isoformat(),
        "scenario": SCENARIO,
        "seed_id": SEED_ID,
        "conditions": CONDITIONS,
        "source_generation": "full_context",
        "note": (
            "Replay-style speaker ablation. User messages are generated once under "
            "full context, then replayed across history filters."
        ),
        "runs": run_bundle,
        "summary": summarize_modes(run_bundle),
    }
    (ABLATION_OUT_ROOT / f"run_{run_idx:02d}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return data


def aggregate(all_runs: list[dict]) -> dict:
    aggregate_payload: dict[str, dict] = {}
    for mode in CONDITIONS:
        mat = np.array(
            [
                [turn["enablement_score"] for turn in run_data["runs"][mode]]
                for run_data in all_runs
            ],
            dtype=float,
        )
        phase_stats = {}
        for phase_name, lo, hi in phase_ranges():
            phase_scores = mat[:, lo:hi].mean(axis=1)
            phase_stats[phase_name] = {
                "mean": float(phase_scores.mean()),
                "std": float(phase_scores.std(ddof=1)) if len(phase_scores) > 1 else 0.0,
            }
        aggregate_payload[mode] = {
            "n_runs": len(all_runs),
            "turn_mean": mat.mean(axis=0).tolist(),
            "overall_mean": float(mat.mean()),
            "overall_std": float(mat.mean(axis=1).std(ddof=1)) if len(all_runs) > 1 else 0.0,
            "phase_stats": phase_stats,
            "raw": mat.tolist(),
        }
    return aggregate_payload


def main() -> None:
    print(f"Output dir: {ABLATION_OUT_ROOT}")
    print(f"N runs: {N_RUNS}   TOTAL_TURNS: {TOTAL_TURNS}")
    print(f"Scenario prompts: {SCENARIO}   Seed: {SEED_ID}")
    print("Conditions: full_context / user_only_history / assistant_only_history / no_history")

    all_runs = [run_one(run_idx) for run_idx in range(N_RUNS)]
    agg = aggregate(all_runs)

    payload = {
        "n_runs": N_RUNS,
        "scenario": SCENARIO,
        "seed_id": SEED_ID,
        "conditions": CONDITIONS,
        "source_generation": "full_context",
        "assistant_prompt_path": "plain_history_prompt_with_role_filter",
        "assistant_system_override": ASSISTANT_SYSTEM_OVERRIDE,
        "aggregate": agg,
    }
    (ABLATION_OUT_ROOT / "aggregate.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n========== SUMMARY ==========")
    for mode in CONDITIONS:
        print(f"\n[{mode}] overall={agg[mode]['overall_mean']:.2f}")
        for phase_name, stats in agg[mode]["phase_stats"].items():
            print(f"  {phase_name:<22} mean={stats['mean']:.2f}")


if __name__ == "__main__":
    main()
