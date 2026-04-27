"""Validate filled annotations_template.yaml, write annotations.jsonl,
and print a per-stage verdict distribution.

Run after prepare_annotations.py + human fill-in.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import yaml

VALID_VERDICTS = {"safe", "ambiguous", "concerning"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--input", type=str, default="annotations_template.yaml")
    p.add_argument("--output", type=str, default="annotations.jsonl")
    p.add_argument(
        "--allow-missing",
        action="store_true",
        help="Allow entries with verdict=null (skip them, don't fail).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    in_path = args.run_dir / args.input
    out_path = args.run_dir / args.output

    with in_path.open("r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    run_meta = doc.get("run", {})
    entries = doc.get("entries", [])
    if not entries:
        raise SystemExit(f"No entries in {in_path}")

    rows: list[dict] = []
    missing: list[tuple[int, int]] = []
    invalid: list[tuple[int, int, str]] = []

    for e in entries:
        sid = int(e["stage_id"])
        sample = int(e["sample_idx"])
        verdict = e.get("verdict")
        if verdict is None or verdict == "":
            missing.append((sid, sample))
            continue
        if verdict not in VALID_VERDICTS:
            invalid.append((sid, sample, str(verdict)))
            continue
        rows.append(
            {
                "stage_id": sid,
                "stage_name": e["stage_name"],
                "sample_idx": sample,
                "condition": run_meta.get("condition", "current_turn_only"),
                "verdict": verdict,
                "tags": e.get("tags") or [],
                "notes": (e.get("notes") or "").strip(),
            }
        )

    if invalid:
        print("ERROR: invalid verdict values (must be one of "
              f"{sorted(VALID_VERDICTS)}):")
        for sid, sample, v in invalid:
            print(f"  stage {sid} sample {sample}: {v!r}")
        raise SystemExit(1)

    if missing and not args.allow_missing:
        print(f"ERROR: {len(missing)} entries have no verdict.")
        for sid, sample in missing[:10]:
            print(f"  stage {sid} sample {sample}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
        print("Pass --allow-missing to skip them.")
        raise SystemExit(1)

    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path} ({len(rows)} annotated, {len(missing)} skipped)")
    print()

    # Per-stage distribution
    by_stage: dict[tuple[int, str], list[str]] = defaultdict(list)
    for r in rows:
        by_stage[(r["stage_id"], r["stage_name"])].append(r["verdict"])

    SYMBOL = {"safe": "✓", "ambiguous": "?", "concerning": "~"}

    print(
        f"Per-stage verdict distribution "
        f"(model={run_meta.get('model')}, T={run_meta.get('temperature')}):"
    )
    print()
    print(f"  {'id':>2}  {'name':<28}  safe  ambig  concern   pattern")
    print(f"  {'--':>2}  {'-' * 28}  ----  -----  -------   -------")
    for (sid, name), verdicts in sorted(by_stage.items()):
        c = Counter(verdicts)
        pattern = "".join(SYMBOL.get(v, "?") for v in verdicts)
        print(
            f"  {sid:>2}  {name:<28}  "
            f"{c.get('safe', 0):>4}  {c.get('ambiguous', 0):>5}  "
            f"{c.get('concerning', 0):>7}   {pattern}"
        )

    print()
    overall = Counter(r["verdict"] for r in rows)
    print(
        f"Overall: safe={overall.get('safe', 0)}  "
        f"ambiguous={overall.get('ambiguous', 0)}  "
        f"concerning={overall.get('concerning', 0)}  "
        f"(of {len(rows)})"
    )


if __name__ == "__main__":
    main()
