"""Render a manual_transcript_spec run JSON in lookism-style readable format."""
from __future__ import annotations
import json
import sys
from pathlib import Path

PHASE_HEADERS = {
    "setup":              "Phase 1 — Setup (T0–T7, fixed user messages)",
    "middle_escalation":  "Phase 2 — Middle escalation (T8–T35, LLM counter-signal user)",
    "late_validation":    "Phase 3 — Late validation (T36–T49, fixed presupposition)",
    "threshold_crossing": "Phase 4 — Threshold crossing (T50–T54, fixed extreme)",
}


def score_emoji(s):
    s = float(s)
    if s <= 3: return "🟢"
    if s <= 5: return "🟡"
    if s <= 7: return "🟠"
    return "🔴"


def run(path: Path) -> None:
    d = json.loads(path.read_text())
    turns = d["_raw_turns"]

    out = []
    out.append(f"Seed: {d['scenario']}")
    out.append(f"Model: {d['model']}   Memory mode: (UNSPECIFIED — full raw history, last 40 messages)")
    out.append(f"Total turns: {len(turns)}")
    out.append(f"Mean by phase — setup {d['trajectory_summary']['mean_score_setup']:.2f}  "
               f"middle {d['trajectory_summary']['mean_score_middle']:.2f}  "
               f"late {d['trajectory_summary']['mean_score_late']:.2f}  "
               f"threshold {d['trajectory_summary']['mean_score_threshold']:.2f}")
    out.append(f"First score >= 7: T{d['trajectory_summary']['first_score_above_7']}   "
               f"First score >= 9: T{d['trajectory_summary']['first_score_above_9']}")
    out.append("")

    prev_phase = None
    for t in turns:
        if t["phase"] != prev_phase:
            out.append("")
            out.append("=" * 70)
            out.append(PHASE_HEADERS.get(t["phase"], t["phase"]))
            out.append("=" * 70)
            prev_phase = t["phase"]

        s = t["enablement_score"]
        out.append(f"\nTurn {t['turn']:02d}   {score_emoji(s)} Enablement: {s}/10")
        out.append("🧑 User")
        out.append(t["user_msg"])
        out.append("")
        out.append("🤖 Assistant")
        out.append(t["assistant_text"])
        out.append("")
        out.append(f"🧾 Evaluator: {t['enablement_reason']}")
        out.append("-" * 70)

    out_path = path.with_name(path.stem + "_readable.txt")
    out_path.write_text("\n".join(out), encoding="utf-8")
    print(f"saved: {out_path}")


if __name__ == "__main__":
    run(Path(sys.argv[1]))
