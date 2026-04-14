"""
Memory (full-context) vs no-memory comparison for the manual transcript spec.

For each of N runs:
  1. Generate a full transcript with MEMORY_MODE = "full_context"
     (assistant sees the entire conversation history — as in Exp A full-context arm)
  2. Replay the same user messages with MEMORY_MODE = "no_memory"
     (assistant sees ONLY the current user message — as in Exp A no-memory baseline)
  3. Evaluate every assistant turn with the harmful_advice rubric

Then aggregate across N runs:
  - Per-turn mean + 95% CI for each condition
  - Phase-level means + paired diff
  - Generate a trajectory plot (styled after visualize_comparison.py)
  - Emit one lookism-style readable transcript (with 🧑/🤖/🧊 markers)

The memory mode is explicitly written into every output JSON / TXT / plot title
so it is never ambiguous what was run.

Based on Experiment A / B / C findings:
  - Exp A: Phase 3 full-ctx vs no-mem gap ~ +0.25 (lookism)
  - Exp B: a single P-signal triggers a one-shot regime shift → we expect the
    biggest gap in the LATE VALIDATION / THRESHOLD phases because that is where
    the assistant must rely on accumulated F+P
  - Exp C: counter-signal user narrows the gap early, widens it late
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import call_llm, configure_llm_backend, parse_json_response, validate_score

configure_llm_backend(api_key=os.environ["OPENAI_API_KEY"], base_url=None)

from src.lookism_agent_drift import (
    _enablement_evaluator_system_prompt,
    _enablement_evaluator_input_prompt,
)
from scripts.experiments.run_manual_transcript_spec import (  # type: ignore
    ASSISTANT_SYSTEM,
    ASSISTANT_MODEL,
    EVALUATOR_MODEL,
    TOTAL_TURNS,
    PHASE1_END,
    PHASE2_END,
    PHASE3_END,
    get_user_message,
    render_history,
    phase_label,
)

N_RUNS = 5
OUT_ROOT = Path("data/manual_transcripts") / f"mem_vs_nomem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Two explicit memory modes
# --------------------------------------------------------------------------

MEMORY_MODE_FULL = "full_context"   # raw history → assistant
MEMORY_MODE_NONE = "no_memory"      # only current user msg → assistant


def assistant_reply(mode: str, history: list[tuple[str, str]], user_msg: str) -> str:
    if mode == MEMORY_MODE_NONE:
        prompt = f"User: {user_msg}\n\nReply:"
    elif mode == MEMORY_MODE_FULL:
        history_text = render_history(history)
        prompt = (
            f"Conversation so far:\n{history_text}\n\nUser: {user_msg}\n\nReply:"
            if history else f"User: {user_msg}\n\nReply:"
        )
    else:
        raise ValueError(f"unknown memory mode: {mode}")
    return call_llm(
        system_prompt=ASSISTANT_SYSTEM,
        user_prompt=prompt,
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


# --------------------------------------------------------------------------
# Single-run procedure
# --------------------------------------------------------------------------


def run_one(run_idx: int) -> dict:
    """
    Runs a full 55-turn dialog with MEMORY_MODE_FULL (generating user messages via
    the Phase-2 LLM where applicable), then REPLAYS the same user messages under
    MEMORY_MODE_NONE.  Returns both trajectories.
    """
    print(f"\n========== Run {run_idx+1}/{N_RUNS}: full_context ==========")

    # --- Pass 1: full_context (natural dialog; Phase 2 user LLM in the loop) ---
    full_history: list[tuple[str, str]] = []
    full_turns: list[dict] = []
    last_assistant = ""

    for t in range(TOTAL_TURNS):
        user_msg = get_user_message(t, full_history, last_assistant)
        asst = assistant_reply(MEMORY_MODE_FULL, full_history, user_msg)
        score, reason = evaluate(user_msg, asst)
        full_history.append(("user", user_msg))
        full_history.append(("assistant", asst))
        last_assistant = asst
        full_turns.append({
            "turn": t, "phase": phase_label(t),
            "user_msg": user_msg, "assistant_text": asst,
            "enablement_score": score, "enablement_reason": reason,
            "memory_mode": MEMORY_MODE_FULL,
        })
        print(f"  [full] T{t:02d} {phase_label(t):<20} score={score}")

    # --- Pass 2: no_memory replay of the SAME user messages ---
    print(f"========== Run {run_idx+1}/{N_RUNS}: no_memory replay ==========")
    nomem_turns: list[dict] = []
    for ft in full_turns:
        user_msg = ft["user_msg"]
        asst = assistant_reply(MEMORY_MODE_NONE, [], user_msg)
        score, reason = evaluate(user_msg, asst)
        nomem_turns.append({
            "turn": ft["turn"], "phase": ft["phase"],
            "user_msg": user_msg, "assistant_text": asst,
            "enablement_score": score, "enablement_reason": reason,
            "memory_mode": MEMORY_MODE_NONE,
        })
        print(f"  [nomem] T{ft['turn']:02d} score={score}")

    run_data = {
        "run_idx": run_idx,
        "timestamp": datetime.now().isoformat(),
        "full_context": full_turns,
        "no_memory": nomem_turns,
    }
    out_path = OUT_ROOT / f"run_{run_idx:02d}.json"
    out_path.write_text(json.dumps(run_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved: {out_path}")
    return run_data


# --------------------------------------------------------------------------
# Aggregation + plotting
# --------------------------------------------------------------------------


def aggregate(all_runs: list[dict]) -> dict:
    full_mat  = np.array([[t["enablement_score"] for t in r["full_context"]] for r in all_runs])
    nomem_mat = np.array([[t["enablement_score"] for t in r["no_memory"]]    for r in all_runs])
    n = len(all_runs)

    def ci95(mat, axis=0):
        mean = mat.mean(axis=axis)
        sem = mat.std(axis=axis, ddof=1) / np.sqrt(n) if n > 1 else np.zeros_like(mean)
        return mean, 1.96 * sem

    full_mean,  full_ci  = ci95(full_mat)
    nomem_mean, nomem_ci = ci95(nomem_mat)

    # Phase-wise means
    phases = [("setup", 0, PHASE1_END),
              ("middle_escalation", PHASE1_END, PHASE2_END),
              ("late_validation", PHASE2_END, PHASE3_END),
              ("threshold_crossing", PHASE3_END, TOTAL_TURNS)]
    phase_stats = {}
    for name, lo, hi in phases:
        f_slice = full_mat[:, lo:hi].mean(axis=1)
        n_slice = nomem_mat[:, lo:hi].mean(axis=1)
        phase_stats[name] = {
            "full_mean":  float(f_slice.mean()),
            "nomem_mean": float(n_slice.mean()),
            "diff":       float(f_slice.mean() - n_slice.mean()),
            "full_std":   float(f_slice.std(ddof=1)) if n > 1 else 0.0,
            "nomem_std":  float(n_slice.std(ddof=1)) if n > 1 else 0.0,
        }

    return {
        "n_runs": n,
        "full_mean": full_mean.tolist(),  "full_ci": full_ci.tolist(),
        "nomem_mean": nomem_mean.tolist(), "nomem_ci": nomem_ci.tolist(),
        "full_raw":  full_mat.tolist(),
        "nomem_raw": nomem_mat.tolist(),
        "phase_stats": phase_stats,
    }


def plot_aggregate(agg: dict, out_path: Path) -> None:
    """
    Plot styled after data/phase_based_manual_20260409 reference figure:
      - Colored phase bands (Phase 1/2/3/4)
      - Raw per-turn mean (thin, markers) + smoothed mean (thick)
      - "Avg X.X" annotation per curve at the end-phase
    N=5 means we plot the cross-run mean as the "raw" line.
    """
    full_mean  = np.array(agg["full_mean"])
    nomem_mean = np.array(agg["nomem_mean"])
    turns = np.arange(len(full_mean))

    def smooth(scores, w=3):
        out = []
        for i in range(len(scores)):
            lo = max(0, i - w // 2)
            hi = min(len(scores), i + w // 2 + 1)
            out.append(np.mean(scores[lo:hi]))
        return np.array(out)

    full_smooth  = smooth(full_mean)
    nomem_smooth = smooth(nomem_mean)

    # Phase color scheme — matches reference (blue, yellow, pink) + add Phase 4
    phase_colors = ["#e8f4f8", "#fff3cd", "#fde8e8", "#f4d9d9"]
    phase_bounds = [
        ("Phase 1",              0,          PHASE1_END),
        ("Phase 2",  PHASE1_END, PHASE2_END),
        ("Phase 3",    PHASE2_END, PHASE3_END),
        ("Phase 4", PHASE3_END, TOTAL_TURNS),
    ]

    fig, ax = plt.subplots(figsize=(15, 5.5))
    legend_patches = []
    import matplotlib.patches as mpatches
    for (name, lo, hi), color in zip(phase_bounds, phase_colors):
        ax.axvspan(lo - 0.5, hi - 0.5, color=color, alpha=0.6)
        ax.text((lo + hi) / 2 - 0.5, 9.65, name,
                ha="center", va="top", fontsize=10, color="gray", fontweight="bold")
        legend_patches.append(mpatches.Patch(color=color, label=name))

    # Raw (cross-run mean) — thin with markers
    ax.plot(turns, full_mean,  "o-", color="#2c7bb6", lw=1.2, ms=4,
            alpha=0.4, label="Full context (raw)")
    ax.plot(turns, nomem_mean, "s-", color="#d7191c", lw=1.2, ms=4,
            alpha=0.4, label="No memory (raw)")
    # Smoothed — thick
    ax.plot(turns, full_smooth,  "-", color="#2c7bb6", lw=2.8,
            label="Full context (smoothed)")
    ax.plot(turns, nomem_smooth, "-", color="#d7191c", lw=2.8,
            label="No memory (smoothed)")

    # Per-phase "Avg X.X" annotations on each curve (near phase end)
    for name, lo, hi in phase_bounds:
        ps = agg["phase_stats"][{
            "Phase 1": "setup", "Phase 2": "middle_escalation",
            "Phase 3": "late_validation", "Phase 4": "threshold_crossing",
        }[name]]
        x_anno = hi - 1
        ax.annotate(f"Avg {ps['full_mean']:.1f}",
                    xy=(x_anno, full_smooth[x_anno]),
                    xytext=(x_anno - 2, full_smooth[x_anno] + 0.9),
                    color="#2c7bb6", fontsize=8, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#2c7bb6", lw=1))
        ax.annotate(f"Avg {ps['nomem_mean']:.1f}",
                    xy=(x_anno, nomem_smooth[x_anno]),
                    xytext=(x_anno - 2, nomem_smooth[x_anno] - 1.3),
                    color="#d7191c", fontsize=8, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#d7191c", lw=1))

    ax.set_xlabel("Turn", fontsize=11)
    ax.set_ylabel("Enablement score (harmful_advice rubric)", fontsize=11)
    ax.set_title(f"Memory vs No-Memory: Harmful Enablement Score Trajectory  "
                 f"(N={agg['n_runs']}, gpt-4o-mini, manual_transcript_spec)",
                 fontsize=12)
    ax.set_xlim(-0.5, TOTAL_TURNS - 0.5)
    ax.set_ylim(0, 10.2)
    ax.set_yticks(range(0, 11))
    ax.grid(axis="y", alpha=0.3)

    # Combined legend: phase patches + line handles
    line_handles, line_labels = ax.get_legend_handles_labels()
    ax.legend(legend_patches + line_handles,
              [p.get_label() for p in legend_patches] + line_labels,
              loc="upper left", fontsize=8, ncol=2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"plot saved: {out_path}")


# --------------------------------------------------------------------------
# Lookism-style readable transcript for one run
# --------------------------------------------------------------------------


def write_lookism_style_txt(run_data: dict, out_path: Path) -> None:
    lines: list[str] = []
    lines.append(f"Seed: wedding_dress_deadline (manual_transcript_spec)")
    lines.append(f"Title: Memory vs No-Memory — single-run transcript")
    lines.append(f"Run index: {run_data['run_idx']}   Model: {ASSISTANT_MODEL}")
    lines.append(f"Memory modes compared: full_context  vs  no_memory")
    lines.append("")

    full = {t["turn"]: t for t in run_data["full_context"]}
    nomem = {t["turn"]: t for t in run_data["no_memory"]}

    for turn in sorted(full.keys()):
        f = full[turn]
        n = nomem[turn]
        lines.append(f"Turn {turn}   [{f['phase']}]")
        lines.append("🧑 User")
        lines.append(f["user_msg"])
        lines.append("")
        lines.append("🤖 Assistant (full_context)")
        lines.append(f["assistant_text"])
        lines.append(f"🧊 Enablement: {f['enablement_score']}/10")
        lines.append(f"🧾 Reason: {f['enablement_reason']}")
        lines.append("")
        lines.append("🤖 Assistant (no_memory)")
        lines.append(n["assistant_text"])
        lines.append(f"🧊 Enablement: {n['enablement_score']}/10")
        lines.append(f"🧾 Reason: {n['enablement_reason']}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"transcript saved: {out_path}")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def main() -> None:
    print(f"Output dir: {OUT_ROOT}")
    print(f"N runs: {N_RUNS}   TOTAL_TURNS: {TOTAL_TURNS}")

    all_runs = [run_one(i) for i in range(N_RUNS)]

    agg = aggregate(all_runs)

    (OUT_ROOT / "aggregate.json").write_text(
        json.dumps({
            "n_runs": N_RUNS,
            "memory_modes": [MEMORY_MODE_FULL, MEMORY_MODE_NONE],
            "phase_stats": agg["phase_stats"],
            "full_mean": agg["full_mean"], "full_ci": agg["full_ci"],
            "nomem_mean": agg["nomem_mean"], "nomem_ci": agg["nomem_ci"],
        }, indent=2),
        encoding="utf-8",
    )

    plot_aggregate(agg, OUT_ROOT / "memory_vs_nomemory_trajectory.png")

    # Pick the run whose full_context mean is closest to the aggregate full mean
    full_means = [np.mean([t["enablement_score"] for t in r["full_context"]]) for r in all_runs]
    mid_idx = int(np.argmin([abs(m - np.mean(full_means)) for m in full_means]))
    write_lookism_style_txt(all_runs[mid_idx],
                            OUT_ROOT / f"representative_run_{mid_idx:02d}.txt")

    # Console summary
    print("\n========== SUMMARY ==========")
    for ph, s in agg["phase_stats"].items():
        print(f"  {ph:<22}  full={s['full_mean']:.2f}  nomem={s['nomem_mean']:.2f}  "
              f"diff={s['diff']:+.2f}")


if __name__ == "__main__":
    main()
