"""Render direct_probe.jsonl as a readable transcript.

Two output formats:
  - txt (default): plain-text dialogue with speaker icons (👤 / 🤖),
    one sample per dialogue block, designed for cold reading.
  - md: markdown variant with the same content.

Usage:
    python manual_redteam/scripts/export_markdown.py \
        --run-dir manual_redteam/data/runs/2026-04-26_referential_motif_blue_door_v0 \
        --ladder manual_redteam/ladders/referential_motif_blue_door_v0.yaml
"""

from __future__ import annotations

import argparse
import json
import textwrap
from collections import defaultdict
from pathlib import Path

USER_ICON = "\U0001f464"   # 👤
ASSIST_ICON = "\U0001f916"  # 🤖

WRAP_WIDTH = 78
BODY_INDENT = "   "  # 3 spaces — visually under the icon


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Run directory containing the input jsonl.",
    )
    p.add_argument(
        "--input",
        type=str,
        default="direct_probe.jsonl",
        help="JSONL filename inside run-dir.",
    )
    p.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output filename inside run-dir. "
        "Default: <input stem>.<format-extension>",
    )
    p.add_argument(
        "--format",
        choices=["txt", "md"],
        default="txt",
        help="Output format. txt is the dialogue-style default.",
    )
    p.add_argument(
        "--ladder",
        type=Path,
        default=None,
        help="Optional ladder YAML; if given, also include unsafe_if and "
        "expected_safe_behavior as evaluator notes.",
    )
    return p.parse_args()


def load_ladder_notes(path: Path | None) -> dict[int, dict]:
    if path is None:
        return {}
    import yaml

    with path.open("r", encoding="utf-8") as f:
        ladder = yaml.safe_load(f)
    notes = {}
    for stage in ladder.get("stages", []):
        notes[int(stage["id"])] = {
            "move_type": stage.get("move_type", ""),
            "risk_dimension": stage.get("risk_dimension", []),
            "unsafe_if": " ".join(stage.get("unsafe_if", "").split()),
            "expected_safe_behavior": " ".join(
                stage.get("expected_safe_behavior", "").split()
            ),
        }
    return notes


def wrap_block(text: str, indent: str = BODY_INDENT, width: int = WRAP_WIDTH) -> str:
    """Wrap a multi-paragraph string with a hanging indent."""
    out_lines: list[str] = []
    paragraphs = text.split("\n")
    inner_width = max(20, width - len(indent))
    for i, para in enumerate(paragraphs):
        if not para.strip():
            out_lines.append("")
            continue
        wrapped = textwrap.wrap(
            para.strip(),
            width=inner_width,
            break_long_words=False,
            break_on_hyphens=False,
        )
        if not wrapped:
            out_lines.append("")
        else:
            for line in wrapped:
                out_lines.append(indent + line)
    return "\n".join(out_lines)


def render_txt(
    rows: list[dict],
    by_stage: dict[tuple[int, str], list[dict]],
    notes: dict[int, dict],
    in_name: str,
) -> str:
    first = rows[0]
    L: list[str] = []
    L.append("=" * WRAP_WIDTH)
    L.append(f" {in_name}")
    L.append("=" * WRAP_WIDTH)
    L.append(
        f" model: {first.get('model', '?')}   "
        f"T={first.get('temperature', '?')}   "
        f"condition: {first.get('condition', '?')}"
    )
    L.append(f" stages: {len(by_stage)}   rows: {len(rows)}")
    L.append("")

    for (sid, name), samples in sorted(by_stage.items()):
        probe = samples[0]["probe"]

        L.append("")
        L.append("#" * WRAP_WIDTH)
        L.append(f"#  STAGE {sid} — {name}")
        L.append("#" * WRAP_WIDTH)

        if sid in notes:
            n = notes[sid]
            L.append(f"  move_type:       {n['move_type']}")
            risk = ", ".join(n["risk_dimension"]) if n["risk_dimension"] else ""
            if risk:
                L.append(f"  risk_dimension:  {risk}")
            if n["unsafe_if"]:
                L.append("  unsafe_if:")
                L.append(wrap_block(n["unsafe_if"], indent="    "))
            if n["expected_safe_behavior"]:
                L.append("  expected_safe_behavior:")
                L.append(wrap_block(n["expected_safe_behavior"], indent="    "))
        L.append("")

        for s in samples:
            L.append("-" * WRAP_WIDTH)
            L.append(f" sample {s['sample_idx']}")
            L.append("-" * WRAP_WIDTH)
            L.append("")
            L.append(f"{USER_ICON} USER")
            L.append(wrap_block(probe))
            L.append("")
            L.append(f"{ASSIST_ICON} ASSISTANT")
            L.append(wrap_block(s["response"]))
            L.append("")

    L.append("=" * WRAP_WIDTH)
    L.append(" end of transcript")
    L.append("=" * WRAP_WIDTH)
    return "\n".join(L) + "\n"


def render_md(
    rows: list[dict],
    by_stage: dict[tuple[int, str], list[dict]],
    notes: dict[int, dict],
    in_name: str,
) -> str:
    first = rows[0]
    L: list[str] = []
    L.append(f"# {in_name}")
    L.append("")
    L.append(
        f"- model: `{first.get('model', '?')}` "
        f"@ T={first.get('temperature', '?')}"
    )
    L.append(f"- condition: `{first.get('condition', '?')}`")
    L.append(f"- stages: {len(by_stage)} | rows: {len(rows)}")
    L.append("")
    L.append("---")
    L.append("")

    for (sid, name), samples in sorted(by_stage.items()):
        probe = samples[0]["probe"]
        L.append(f"## Stage {sid} — {name}")
        L.append("")
        if sid in notes:
            n = notes[sid]
            L.append(f"- **move_type**: {n['move_type']}")
            risk = ", ".join(n["risk_dimension"]) if n["risk_dimension"] else ""
            if risk:
                L.append(f"- **risk_dimension**: {risk}")
            if n["unsafe_if"]:
                L.append(f"- **unsafe_if**: {n['unsafe_if']}")
            if n["expected_safe_behavior"]:
                L.append(
                    f"- **expected_safe_behavior**: {n['expected_safe_behavior']}"
                )
            L.append("")
        for s in samples:
            L.append(f"### sample {s['sample_idx']}")
            L.append("")
            L.append(f"{USER_ICON} **USER**")
            L.append("")
            L.append("> " + probe.replace("\n", "\n> "))
            L.append("")
            L.append(f"{ASSIST_ICON} **ASSISTANT**")
            L.append("")
            for para in s["response"].split("\n"):
                L.append(para if para else "")
            L.append("")
        L.append("---")
        L.append("")
    return "\n".join(L)


def main() -> None:
    args = parse_args()
    in_path = args.run_dir / args.input
    if not in_path.exists():
        raise SystemExit(f"Not found: {in_path}")

    rows = [
        json.loads(line)
        for line in in_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise SystemExit(f"No rows in {in_path}")

    by_stage: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for r in rows:
        by_stage[(r["stage_id"], r["stage_name"])].append(r)
    for samples in by_stage.values():
        samples.sort(key=lambda r: r["sample_idx"])

    notes = load_ladder_notes(args.ladder)

    ext = "txt" if args.format == "txt" else "md"
    out_name = args.output or (Path(args.input).stem + f".{ext}")
    out_path = args.run_dir / out_name

    renderer = render_txt if args.format == "txt" else render_md
    out_text = renderer(rows, by_stage, notes, in_path.name)
    out_path.write_text(out_text, encoding="utf-8")
    print(f"Wrote {out_path} ({len(rows)} rows across {len(by_stage)} stages)")


if __name__ == "__main__":
    main()
