"""Unblind Codex blind labels for the load-bearing S12 experiment.

Reads:
  - codex_labels.jsonl  (from Codex; id -> label)
  - SEALED_mapping.json (id -> source metadata: cell, fmt, run, ...)

Writes:
  - unblinded_labels.jsonl  (one row per item, joined)
  - cross_tab.md            (cell x fmt x label table, plus collapse rates)

Pre-reg: manual_redteam/docs/load_bearing_s12_design_2026_05_25.md
Handoff: manual_redteam/docs/codex_s12_blindpass_handoff_2026_05_26.md
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

LABELS = ["CLEAN_COLLAPSE", "HEDGED_NONREJECTION", "HELD", "OBJECT_SHIFT", "AMBIGUOUS"]
CELLS = ["A0", "A1_k4", "A1_k6", "A1", "A2", "A3", "A4user", "A4model"]
FMTS = ["open", "twochoice"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle-dir", type=Path, required=True,
                   help="Dir containing codex_labels.jsonl + SEALED_mapping.json")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    labels_path = args.bundle_dir / "codex_labels.jsonl"
    mapping_path = args.bundle_dir / "SEALED_mapping.json"
    out_jsonl = args.bundle_dir / "unblinded_labels.jsonl"
    out_md = args.bundle_dir / "cross_tab.md"

    mapping = json.loads(mapping_path.read_text())
    labels = [json.loads(l) for l in labels_path.read_text().splitlines() if l.strip()]

    # join
    joined = []
    for lab in labels:
        meta = mapping.get(lab["id"])
        if meta is None:
            raise SystemExit(f"No mapping for id {lab['id']}")
        joined.append({**lab, **meta})

    with out_jsonl.open("w") as fh:
        for row in joined:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    # cross-tab: (cell, fmt) -> {label: count, n: total, collapse: count(CLEAN)}
    cell_fmt: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in joined:
        k = (row["cell"], row["fmt"])
        cell_fmt[k]["n"] += 1
        cell_fmt[k][row["label"]] += 1
        if row["collapse"] == 1:
            cell_fmt[k]["collapse"] += 1

    lines = ["# Load-bearing S12 — blind-labeled cross-tab", ""]
    lines.append(f"Source: `{labels_path}` + `{mapping_path}`")
    lines.append(f"Items: {len(joined)}")
    lines.append("")
    lines.append("## Collapse rates (CLEAN_COLLAPSE / N)")
    lines.append("")
    lines.append("| Cell | open | twochoice |")
    lines.append("|---|---|---|")
    for cell in CELLS:
        cells_row = [cell]
        for fmt in FMTS:
            d = cell_fmt.get((cell, fmt))
            if d is None:
                cells_row.append("—")
            else:
                cells_row.append(f"{d.get('collapse', 0)}/{d['n']}")
        lines.append("| " + " | ".join(cells_row) + " |")
    lines.append("")
    lines.append("## Full label distribution")
    lines.append("")
    header = ["Cell", "fmt", "N"] + LABELS
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for cell in CELLS:
        for fmt in FMTS:
            d = cell_fmt.get((cell, fmt))
            if d is None:
                continue
            row = [cell, fmt, str(d["n"])] + [str(d.get(lbl, 0)) for lbl in LABELS]
            lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # marginals by cell (open + twochoice combined)
    lines.append("## Marginal by cell (formats combined)")
    lines.append("")
    lines.append("| Cell | N | CLEAN | HEDGED | HELD | OBJ_SHIFT | AMBIG | collapse rate |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for cell in CELLS:
        n = sum(cell_fmt[(cell, fmt)]["n"] for fmt in FMTS if (cell, fmt) in cell_fmt)
        if n == 0:
            continue
        counts = {lbl: sum(cell_fmt[(cell, fmt)].get(lbl, 0)
                           for fmt in FMTS if (cell, fmt) in cell_fmt)
                  for lbl in LABELS}
        coll = counts["CLEAN_COLLAPSE"]
        lines.append(
            f"| {cell} | {n} | {counts['CLEAN_COLLAPSE']} | "
            f"{counts['HEDGED_NONREJECTION']} | {counts['HELD']} | "
            f"{counts['OBJECT_SHIFT']} | {counts['AMBIGUOUS']} | "
            f"{coll}/{n} = {coll/n:.2f} |"
        )

    out_md.write_text("\n".join(lines) + "\n")
    print(f"Wrote: {out_jsonl}")
    print(f"Wrote: {out_md}")
    print()
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
