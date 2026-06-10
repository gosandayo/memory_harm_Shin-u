"""
Generate score trend chart and readable transcript for memory vs no-memory comparison.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_pair(full_ctx_path: Path) -> tuple[dict, dict]:
    nomem_path = full_ctx_path.parent / (full_ctx_path.stem + "_nomemory.json")
    with open(full_ctx_path) as f:
        full = json.load(f)
    with open(nomem_path) as f:
        nomem = json.load(f)
    return full, nomem


def plot_scores(full: dict, nomem: dict, out_path: Path) -> None:
    orig_scores  = [t["enablement_score"] for t in full["turns"]]
    nomem_scores = [t["enablement_score"] for t in nomem["turns"]]
    turns = list(range(len(orig_scores)))

    phase_colors = {1: "#e8f4f8", 2: "#fff3cd", 3: "#fde8e8"}
    # Infer boundaries from phase labels in data
    ph_turns = {1: [], 2: [], 3: []}
    for t in full["turns"]:
        ph_turns[t["phase"]].append(t["turn"])
    phase_bounds = []
    for ph in [1, 2, 3]:
        if ph_turns[ph]:
            phase_bounds.append((min(ph_turns[ph]), max(ph_turns[ph]) + 1, ph))

    fig, ax = plt.subplots(figsize=(14, 5))

    for start, end, ph in phase_bounds:
        ax.axvspan(start - 0.5, end - 0.5, color=phase_colors[ph], alpha=0.6,
                   label=f"Phase {ph}")

    # Smoothed lines
    def smooth(scores, w=3):
        out = []
        for i in range(len(scores)):
            lo = max(0, i - w // 2)
            hi = min(len(scores), i + w // 2 + 1)
            out.append(np.mean(scores[lo:hi]))
        return out

    ax.plot(turns, orig_scores,  "o-", color="#2c7bb6", lw=1.5, ms=4,
            alpha=0.4, label="Full context (raw)")
    ax.plot(turns, nomem_scores, "s-", color="#d7191c", lw=1.5, ms=4,
            alpha=0.4, label="No memory (raw)")
    ax.plot(turns, smooth(orig_scores),  "-", color="#2c7bb6", lw=2.5,
            label="Full context (smoothed)")
    ax.plot(turns, smooth(nomem_scores), "-", color="#d7191c", lw=2.5,
            label="No memory (smoothed)")

    # Phase labels
    for start, end, ph in phase_bounds:
        mid = (start + end) / 2
        ax.text(mid, 9.6, f"Phase {ph}", ha="center", va="top", fontsize=9,
                color="gray", fontweight="bold")

    # Phase averages annotation
    p3_start = next((s for s, e, p in phase_bounds if p == 3), len(orig_scores) - 10)
    p3_mid = (p3_start + len(orig_scores)) // 2
    p3_orig  = np.mean(orig_scores[p3_start:])
    p3_nomem = np.mean(nomem_scores[p3_start:])
    ax.annotate(f"Avg {p3_orig:.1f}", xy=(p3_mid, p3_orig), xytext=(p3_mid + 2, p3_orig + 0.8),
                color="#2c7bb6", fontsize=8, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#2c7bb6", lw=1))
    ax.annotate(f"Avg {p3_nomem:.1f}", xy=(p3_mid, p3_nomem), xytext=(p3_mid + 2, p3_nomem - 1.2),
                color="#d7191c", fontsize=8, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#d7191c", lw=1))

    ax.set_xlabel("Turn", fontsize=11)
    ax.set_ylabel("Enablement score (harmful_advice rubric)", fontsize=11)
    ax.set_title("Memory vs No-Memory: Harmful Enablement Score Trajectory", fontsize=13)
    ax.set_xlim(-0.5, len(turns) - 0.5)
    ax.set_ylim(0, 10.2)
    ax.set_yticks(range(0, 11))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Chart saved: {out_path}")
    plt.close()


def write_transcript(full: dict, nomem: dict, out_path: Path) -> None:
    orig_turns  = {t["turn"]: t for t in full["turns"]}
    nomem_turns = {t["turn"]: t for t in nomem["turns"]}
    all_turns = sorted(orig_turns.keys())

    phase_headers = {0: "Phase 1 — Context building", 5: "Phase 2 — Gray-zone escalation",
                     21: "Phase 3 — Fork & endorsement extraction"}

    lines: list[str] = []
    lines.append("# Memory vs No-Memory — Conversation Transcript\n")
    lines.append("Rubric: **harmful_advice**  |  Model: gpt-4o-mini\n")
    lines.append("---\n")

    score_bar_map = {0: "▱▱▱▱▱▱▱▱▱▱", 1: "▰▱▱▱▱▱▱▱▱▱", 2: "▰▰▱▱▱▱▱▱▱▱",
                     3: "▰▰▰▱▱▱▱▱▱▱", 4: "▰▰▰▰▱▱▱▱▱▱", 5: "▰▰▰▰▰▱▱▱▱▱",
                     6: "▰▰▰▰▰▰▱▱▱▱", 7: "▰▰▰▰▰▰▰▱▱▱", 8: "▰▰▰▰▰▰▰▰▱▱",
                     9: "▰▰▰▰▰▰▰▰▰▱", 10: "▰▰▰▰▰▰▰▰▰▰"}

    def score_bar(s):
        s_int = min(10, max(0, round(float(s))))
        return score_bar_map.get(s_int, "?")

    def score_emoji(s):
        s = float(s)
        if s <= 3:  return "🟢"
        if s <= 5:  return "🟡"
        if s <= 7:  return "🟠"
        return "🔴"

    for turn_idx in all_turns:
        if turn_idx in phase_headers:
            lines.append(f"\n## {phase_headers[turn_idx]}\n")

        orig  = orig_turns[turn_idx]
        nomem = nomem_turns.get(turn_idx, {})

        os = orig["enablement_score"]
        ns = nomem.get("enablement_score", "?")

        lines.append(f"### Turn {turn_idx:02d}  ·  Phase {orig['phase']}")
        lines.append(f"> Score: Full-ctx {score_emoji(os)} **{os}** {score_bar(os)}"
                     f"  |  No-mem {score_emoji(ns)} **{ns}** {score_bar(ns)}\n")

        lines.append(f"**👤 User**")
        lines.append(f"> {orig['user_msg']}\n")

        lines.append(f"**🤖 Assistant (full context)**")
        lines.append(f"> {orig['assistant_text']}\n")
        lines.append(f"*Eval: {orig['enablement_reason']}*\n")

        if nomem:
            lines.append(f"**🤖 Assistant (no memory)**")
            lines.append(f"> {nomem['assistant_text']}\n")
            lines.append(f"*Eval: {nomem.get('enablement_reason', '')}*\n")

        lines.append("---\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Transcript saved: {out_path}")


def run(full_ctx_path: Path) -> None:
    full, nomem = load_pair(full_ctx_path)
    stem = full_ctx_path.stem
    out_dir = full_ctx_path.parent

    plot_scores(full, nomem, out_dir / f"{stem}_comparison.png")
    write_transcript(full, nomem, out_dir / f"{stem}_comparison.md")


if __name__ == "__main__":
    runs = sorted(Path("data/lookism_agent_drift/phase_based_manual_20260409").glob("run_*.json"))
    runs = [r for r in runs if "nomemory" not in r.name]
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else runs[-1]
    print(f"Visualizing: {target}")
    run(target)
