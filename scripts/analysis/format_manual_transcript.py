#!/usr/bin/env python3
"""Render manual transcript JSON files into readable plain-text transcripts.

Supports two schemas:
1. Single-condition transcripts with `_raw_turns`
2. Multi-condition run files such as V4 2x2 (`nomem_nofb`, `mem_nofb`, `nomem_fb`, `mem_fb`)

Examples:
    python scripts/analysis/format_manual_transcript.py data/manual_transcripts/.../run_00.json
    python scripts/analysis/format_manual_transcript.py data/manual_transcripts/v4_2x2_feedback_20260414_232517
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


PHASE_HEADERS = {
    "setup": "Setup",
    "middle_escalation": "Middle Escalation",
    "late_validation": "Late Validation",
    "threshold_crossing": "Threshold Crossing",
    "middle_A": "Middle-A",
    "middle_B": "Middle-B",
    "middle_C": "Middle-C",
    "late_threshold": "Late/Threshold",
}

DEFAULT_CONDITION_ORDER = [
    "nomem_nofb",
    "mem_nofb",
    "nomem_fb",
    "mem_fb",
]


def score_band(score: float) -> str:
    score = float(score)
    if score <= 3:
        return "LOW"
    if score <= 5:
        return "MID"
    if score <= 7:
        return "HIGH"
    return "SEVERE"


def phase_label(phase: str) -> str:
    return PHASE_HEADERS.get(phase, phase)


def condition_order(conditions: list[str]) -> list[str]:
    ordered = [c for c in DEFAULT_CONDITION_ORDER if c in conditions]
    ordered.extend(sorted(c for c in conditions if c not in ordered))
    return ordered


def wrap_header(title: str) -> list[str]:
    return ["", "=" * 88, title, "=" * 88]


def phase_summary(turns: list[dict]) -> str:
    buckets: dict[str, list[float]] = defaultdict(list)
    for turn in turns:
        buckets[turn["phase"]].append(float(turn["enablement_score"]))
    parts = []
    for phase in buckets:
        mean = sum(buckets[phase]) / len(buckets[phase])
        parts.append(f"{phase_label(phase)}={mean:.2f}")
    return "  ".join(parts)


def render_single_condition(turns: list[dict], *, title: str, include_reason: bool = True) -> list[str]:
    lines = wrap_header(title)
    lines.append(f"Turns: {len(turns)}")
    lines.append(f"Phase means: {phase_summary(turns)}")

    prev_phase = None
    for turn in turns:
        phase = turn["phase"]
        if phase != prev_phase:
            lines.extend(wrap_header(f"{phase_label(phase)} ({phase})"))
            prev_phase = phase

        score = float(turn["enablement_score"])
        lines.append(
            f"Turn {turn['turn']:02d} | score={score:.1f} [{score_band(score)}]"
            + (
                f" | stance_of_prev={turn.get('stance_of_prev')}"
                if turn.get("stance_of_prev") is not None
                else ""
            )
        )
        lines.append("User:")
        lines.append(turn["user_msg"])
        lines.append("")
        lines.append("Assistant:")
        lines.append(turn["assistant_text"])
        if include_reason:
            lines.append("")
            lines.append("Evaluator reason:")
            lines.append(turn["enablement_reason"])
        lines.append("-" * 88)

    return lines


def detect_schema(data: dict) -> str:
    if "_raw_turns" in data:
        return "single"
    multi_keys = [
        key
        for key, value in data.items()
        if isinstance(value, list)
        and value
        and isinstance(value[0], dict)
        and {"turn", "phase", "user_msg", "assistant_text", "enablement_score"} <= set(value[0].keys())
    ]
    if multi_keys:
        return "multi"
    raise ValueError("Unrecognized transcript schema")


def render_single_schema(path: Path, data: dict) -> Path:
    turns = data.get("_raw_turns") or data.get("turns") or []
    title = (
        f"Seed: {data.get('scenario', path.stem)}\n"
        f"Model: {data.get('model', 'unknown')}\n"
        f"Source: {path.name}"
    )
    lines = render_single_condition(turns, title=title)
    out_path = path.with_name(path.stem + "_readable.txt")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def render_multi_schema(path: Path, data: dict) -> Path:
    conditions = condition_order(
        [
            key
            for key, value in data.items()
            if isinstance(value, list)
            and value
            and isinstance(value[0], dict)
            and {"turn", "phase", "user_msg", "assistant_text", "enablement_score"} <= set(value[0].keys())
        ]
    )
    turns_by_condition = {cond: {row["turn"]: row for row in data[cond]} for cond in conditions}
    all_turns = sorted({turn for rows in turns_by_condition.values() for turn in rows})

    lines = wrap_header(f"Readable comparison for {path.name}")
    if "run_idx" in data:
        lines.append(f"Run index: {data['run_idx']}")
    lines.append("Conditions: " + ", ".join(conditions))
    lines.append("")
    lines.append("Condition summaries:")
    for cond in conditions:
        rows = data[cond]
        mean = sum(float(row["enablement_score"]) for row in rows) / len(rows)
        high = sum(float(row["enablement_score"]) >= 7 for row in rows)
        lines.append(
            f"  {cond:10s} mean={mean:.2f}  score>=7={high}/{len(rows)}  {phase_summary(rows)}"
        )

    prev_phase = None
    for turn_idx in all_turns:
        exemplar = next(turns_by_condition[cond][turn_idx] for cond in conditions if turn_idx in turns_by_condition[cond])
        phase = exemplar["phase"]
        if phase != prev_phase:
            lines.extend(wrap_header(f"{phase_label(phase)} ({phase})"))
            prev_phase = phase

        lines.extend(wrap_header(f"Turn {turn_idx:02d}"))

        if "nomem_nofb" in turns_by_condition and "mem_nofb" in turns_by_condition:
            nofb_delta = (
                float(turns_by_condition["mem_nofb"][turn_idx]["enablement_score"])
                - float(turns_by_condition["nomem_nofb"][turn_idx]["enablement_score"])
            )
            lines.append(
                "NoFB memory delta: "
                f"{turns_by_condition['nomem_nofb'][turn_idx]['enablement_score']} -> "
                f"{turns_by_condition['mem_nofb'][turn_idx]['enablement_score']}  "
                f"(delta={nofb_delta:+.1f})"
            )
        if "nomem_fb" in turns_by_condition and "mem_fb" in turns_by_condition:
            fb_delta = (
                float(turns_by_condition["mem_fb"][turn_idx]["enablement_score"])
                - float(turns_by_condition["nomem_fb"][turn_idx]["enablement_score"])
            )
            lines.append(
                "FB memory delta:   "
                f"{turns_by_condition['nomem_fb'][turn_idx]['enablement_score']} -> "
                f"{turns_by_condition['mem_fb'][turn_idx]['enablement_score']}  "
                f"(delta={fb_delta:+.1f})"
            )
        lines.append("")

        user_msgs = {
            cond: turns_by_condition[cond][turn_idx]["user_msg"]
            for cond in conditions
            if turn_idx in turns_by_condition[cond]
        }
        unique_user_msgs = list(dict.fromkeys(user_msgs.values()))

        if len(unique_user_msgs) == 1:
            lines.append("Shared user prompt:")
            lines.append(unique_user_msgs[0])
            lines.append("")
        else:
            lines.append("User prompts differ across conditions:")
            for cond in conditions:
                if turn_idx not in turns_by_condition[cond]:
                    continue
                lines.append(f"[{cond}] User:")
                lines.append(turns_by_condition[cond][turn_idx]["user_msg"])
                lines.append("")

        for cond in conditions:
            if turn_idx not in turns_by_condition[cond]:
                continue
            row = turns_by_condition[cond][turn_idx]
            score = float(row["enablement_score"])
            stance = row.get("stance_of_prev")
            header = f"[{cond}] score={score:.1f} [{score_band(score)}]"
            if stance is not None:
                header += f" | stance_of_prev={stance}"
            lines.append(header)
            lines.append("Assistant:")
            lines.append(row["assistant_text"])
            lines.append("")
            lines.append("Evaluator reason:")
            lines.append(row["enablement_reason"])
            lines.append("-" * 88)

    out_path = path.with_name(path.stem + "_readable.txt")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def iter_json_paths(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(p for p in path.glob("run_*.json") if p.is_file())
    return [path]


def process_path(path: Path) -> list[Path]:
    outputs: list[Path] = []
    for json_path in iter_json_paths(path):
        data = json.loads(json_path.read_text())
        schema = detect_schema(data)
        if schema == "single":
            outputs.append(render_single_schema(json_path, data))
        else:
            outputs.append(render_multi_schema(json_path, data))
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Format manual transcript JSON into readable txt")
    parser.add_argument("paths", nargs="+", help="Run JSON file or directory containing run_*.json files")
    args = parser.parse_args()

    outputs: list[Path] = []
    for raw_path in args.paths:
        outputs.extend(process_path(Path(raw_path)))

    for out_path in outputs:
        print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
