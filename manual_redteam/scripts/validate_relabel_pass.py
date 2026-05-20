#!/usr/bin/env python3
"""Validate a primary relabel pass against the locked masked bundle.

Checks the contract every pass must meet BEFORE it is accepted as a
canonical pass and BEFORE the SEALED mapping is opened:

  * 20 JSONL lines, no blanks, no extras, no duplicates
  * exact output keys: id, endpoint, label, collapse, rationale
  * every id appears in the bundle
  * every endpoint matches the bundle's endpoint for that id
  * label in the 5-value enum
  * collapse == 1 iff label == CLEAN_COLLAPSE
  * rationale is a non-empty string

This does NOT compare to other passes (that's the aggregator's job) and
does NOT open SEALED_mapping.json. Pure shape + bundle-consistency check.

Usage:
    python3 manual_redteam/scripts/validate_relabel_pass.py \\
        --bundle manual_redteam/data/runs/2026-05-19_cold_terminal_factor_panel_gpt4omini/relabel/masked_bundle.jsonl \\
        --pass   manual_redteam/data/runs/2026-05-19_cold_terminal_factor_panel_gpt4omini/relabel/labels_primary_pass02_gpt55.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

VALID_LABELS = {
    "CLEAN_COLLAPSE",
    "HEDGED_NONREJECTION",
    "HELD",
    "OBJECT_SHIFT",
    "AMBIGUOUS",
}
VALID_ENDPOINTS = {"S13_PERSONAL_VERDICT", "S14_ACTION_VERDICT"}
EXPECTED_KEYS = {"id", "endpoint", "label", "collapse", "rationale"}
EXPECTED_COUNT = 20


def load_jsonl(path: Path) -> list[dict]:
    out = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        if not line:
            raise SystemExit(f"{path}:{i}: blank line is not valid JSONL for this pass")
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise SystemExit(f"{path}:{i}: invalid JSON ({e})")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--pass", dest="pass_path", type=Path, required=True)
    args = p.parse_args()

    bundle = load_jsonl(args.bundle)
    labels = load_jsonl(args.pass_path)

    bundle_by_id = {b["id"]: b for b in bundle}

    errors: list[str] = []

    if len(bundle) != EXPECTED_COUNT:
        errors.append(f"bundle length: got {len(bundle)} items, expected {EXPECTED_COUNT}")

    if len(labels) != EXPECTED_COUNT:
        errors.append(f"length: got {len(labels)} labels, expected {EXPECTED_COUNT}")
    elif len(labels) != len(bundle):
        errors.append(f"length: got {len(labels)} labels, expected bundle length {len(bundle)}")

    for n, row in enumerate(labels, 1):
        if not isinstance(row, dict):
            errors.append(f"row {n}: JSON value must be an object")
            continue
        keys = set(row)
        if keys != EXPECTED_KEYS:
            missing_keys = sorted(EXPECTED_KEYS - keys)
            extra_keys = sorted(keys - EXPECTED_KEYS)
            errors.append(
                f"row {n}: keys must be exactly {sorted(EXPECTED_KEYS)} "
                f"(missing={missing_keys}, extra={extra_keys})"
            )

    seen_ids = Counter(row.get("id", "") for row in labels if isinstance(row, dict))
    dups = [i for i, c in seen_ids.items() if c > 1 and i]
    if dups:
        errors.append(f"duplicate ids: {dups}")
    missing = [i for i in bundle_by_id if i not in seen_ids]
    if missing:
        errors.append(f"ids missing from pass: {missing}")

    label_dist: Counter[str] = Counter()
    collapse_total = 0
    for row in labels:
        if not isinstance(row, dict):
            continue
        rid = row.get("id")
        if rid is None or rid not in bundle_by_id:
            errors.append(f"unknown id in pass: {rid}")
            continue
        bep = bundle_by_id[rid]["endpoint"]
        rep = row.get("endpoint")
        if rep != bep:
            errors.append(f"id {rid}: endpoint mismatch (pass={rep!r}, bundle={bep!r})")
        lab = row.get("label")
        if lab not in VALID_LABELS:
            errors.append(f"id {rid}: label not in enum: {lab!r}")
        if rep not in VALID_ENDPOINTS:
            errors.append(f"id {rid}: endpoint not in enum: {rep!r}")
        col = row.get("collapse")
        if col not in (0, 1):
            errors.append(f"id {rid}: collapse not in {{0,1}}: {col!r}")
        elif (col == 1) != (lab == "CLEAN_COLLAPSE"):
            errors.append(
                f"id {rid}: collapse/label inconsistent (label={lab!r}, collapse={col})"
            )
        rat = row.get("rationale")
        if not isinstance(rat, str) or not rat.strip():
            errors.append(f"id {rid}: rationale missing or empty")
        if lab in VALID_LABELS:
            label_dist[lab] += 1
            if col == 1:
                collapse_total += 1

    print(f"bundle items: {len(bundle)}")
    print(f"pass items:   {len(labels)}")
    print(f"label dist:   {dict(label_dist)}")
    print(f"collapse=1:   {collapse_total}/{len(labels)}")

    if errors:
        print("\nVALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("\nOK: pass conforms to the locked contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
