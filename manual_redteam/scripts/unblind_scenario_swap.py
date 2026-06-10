"""Unblind Codex blind labels for the scenario-swap S12+S13 experiment.

Reads:
  - codex_labels.jsonl  (from Codex; id -> label)
  - SEALED_mapping.json (id -> source metadata: cell, rung, fmt, run, ...)

Writes:
  - unblinded_labels.jsonl  (one row per item, joined)
  - cross_tab.md            (cell x rung x fmt x label table)

Pre-reg: manual_redteam/docs/load_bearing_s12_design_2026_05_25.md (parent)
Extension handoff: manual_redteam/docs/codex_scenario_swap_blindpass_handoff_2026_05_27.md
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

LABELS = ["CLEAN_COLLAPSE", "HEDGED_NONREJECTION", "HELD", "OBJECT_SHIFT", "AMBIGUOUS"]
CELLS = ["A0", "A1_k4", "A1_k6", "A1", "A1_k4_car", "A1_k6_car", "A1_car"]
RUNGS = ["S12", "S13"]
FMTS = ["open", "twochoice"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle-dir", type=Path, required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    labels_path = args.bundle_dir / "codex_labels.jsonl"
    mapping_path = args.bundle_dir / "SEALED_mapping.json"
    out_jsonl = args.bundle_dir / "unblinded_labels.jsonl"
    out_md = args.bundle_dir / "cross_tab.md"

    mapping = json.loads(mapping_path.read_text())
    labels = [json.loads(l) for l in labels_path.read_text().splitlines() if l.strip()]

    joined = []
    for lab in labels:
        meta = mapping.get(lab["id"])
        if meta is None:
            raise SystemExit(f"No mapping for id {lab['id']}")
        joined.append({**lab, **meta})

    with out_jsonl.open("w") as fh:
        for row in joined:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    # cell x rung x fmt -> {label: count, n, collapse}
    cube: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in joined:
        k = (row["cell"], row["rung"], row["fmt"])
        cube[k]["n"] += 1
        cube[k][row["label"]] += 1
        if row["collapse"] == 1:
            cube[k]["collapse"] += 1

    lines = ["# Scenario-swap S12+S13 — blind-labeled cross-tab", ""]
    lines.append(f"Source: `{labels_path}` + `{mapping_path}`")
    lines.append(f"Items: {len(joined)}")
    lines.append("")

    # --- Headline: collapse rates per (cell, rung, fmt) ----------------------
    lines.append("## Collapse rates (CLEAN_COLLAPSE / N) — by (rung, fmt)")
    lines.append("")
    for rung in RUNGS:
        lines.append(f"### {rung}")
        lines.append("")
        lines.append("| Cell | open | twochoice |")
        lines.append("|---|---|---|")
        for cell in CELLS:
            row = [cell]
            for fmt in FMTS:
                d = cube.get((cell, rung, fmt))
                if d is None:
                    row.append("—")
                else:
                    row.append(f"{d.get('collapse', 0)}/{d['n']}")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # --- Full label distribution --------------------------------------------
    lines.append("## Full label distribution")
    lines.append("")
    header = ["Cell", "rung", "fmt", "N"] + LABELS
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for cell in CELLS:
        for rung in RUNGS:
            for fmt in FMTS:
                d = cube.get((cell, rung, fmt))
                if d is None:
                    continue
                row = [cell, rung, fmt, str(d["n"])] + [str(d.get(lbl, 0)) for lbl in LABELS]
                lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # --- Scenario-swap headline: blue vs career, S13 endpoints --------------
    # Only cells that exist on both sides: A1_k4 vs A1_k4_car, A1_k6 vs A1_k6_car, A1 vs A1_car.
    lines.append("## Scenario-swap comparison (blue vs career, S13 only)")
    lines.append("")
    lines.append("| Lead-in length | blue / S13_open | car / S13_open | blue / S13_twochoice | car / S13_twochoice |")
    lines.append("|---|---|---|---|---|")
    for k4, k6, k8, label in [
        ("A1_k4", "A1_k4_car", None, "k=4"),
        ("A1_k6", "A1_k6_car", None, "k=6"),
        ("A1", "A1_car", None, "k=8 (full)"),
    ]:
        def cell_str(cell: str, fmt: str) -> str:
            d = cube.get((cell, "S13", fmt))
            return "—" if d is None else f"{d.get('collapse', 0)}/{d['n']}"
        lines.append(
            f"| {label} | {cell_str(k4, 'open')} | {cell_str(k6, 'open')} | "
            f"{cell_str(k4, 'twochoice')} | {cell_str(k6, 'twochoice')} |"
        )
    lines.append("")

    # --- Cross-rung S12 vs S13 comparison (career cells only) ----------------
    lines.append("## S12 vs S13 (career cells)")
    lines.append("")
    lines.append("| Cell | S12_open | S12_twochoice | S13_open | S13_twochoice |")
    lines.append("|---|---|---|---|---|")
    for cell in ["A1_k4_car", "A1_k6_car", "A1_car"]:
        row = [cell]
        for rung in ["S12", "S13"]:
            for fmt in ["open", "twochoice"]:
                d = cube.get((cell, rung, fmt))
                row.append("—" if d is None else f"{d.get('collapse', 0)}/{d['n']}")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # --- Marginals by cell --------------------------------------------------
    lines.append("## Marginal by cell (all rungs + formats combined)")
    lines.append("")
    lines.append("| Cell | N | CLEAN | HEDGED | HELD | OBJ_SHIFT | AMBIG | collapse rate |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for cell in CELLS:
        keys = [(cell, r, f) for r in RUNGS for f in FMTS if (cell, r, f) in cube]
        if not keys:
            continue
        n = sum(cube[k]["n"] for k in keys)
        counts = {lbl: sum(cube[k].get(lbl, 0) for k in keys) for lbl in LABELS}
        coll = counts["CLEAN_COLLAPSE"]
        lines.append(
            f"| {cell} | {n} | {counts['CLEAN_COLLAPSE']} | "
            f"{counts['HEDGED_NONREJECTION']} | {counts['HELD']} | "
            f"{counts['OBJECT_SHIFT']} | {counts['AMBIGUOUS']} | "
            f"{coll}/{n} = {coll/n:.2f} |"
        )
    lines.append("")

    out_md.write_text("\n".join(lines) + "\n")
    print(f"Wrote: {out_jsonl}")
    print(f"Wrote: {out_md}")
    print()
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
