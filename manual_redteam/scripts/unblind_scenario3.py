"""Unblind Codex blind labels for the scenario-3 (illness) experiment."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

LABELS = ["CLEAN_COLLAPSE", "HEDGED_NONREJECTION", "HELD", "OBJECT_SHIFT", "AMBIGUOUS"]
CELLS = ["A1_k4_ill", "A1_k6_ill", "A1_ill"]
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

    cube: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in joined:
        k = (row["cell"], row["rung"], row["fmt"])
        cube[k]["n"] += 1
        cube[k][row["label"]] += 1
        if row["collapse"] == 1:
            cube[k]["collapse"] += 1

    lines = ["# Scenario-3 (illness) — blind-labeled cross-tab", ""]
    lines.append(f"Source: `{labels_path}` + `{mapping_path}`")
    lines.append(f"Items: {len(joined)}")
    lines.append("")

    lines.append("## Collapse rates (CLEAN_COLLAPSE / N)")
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
                row.append("—" if d is None else f"{d.get('collapse', 0)}/{d['n']}")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

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

    out_md.write_text("\n".join(lines) + "\n")
    print(f"Wrote: {out_jsonl}")
    print(f"Wrote: {out_md}")
    print()
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
