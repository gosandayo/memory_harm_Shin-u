#!/usr/bin/env python3
"""Aggregate primary 3-pass labels into per-cell collapse counts.

Inputs (all strict-validated by validate_relabel_pass.py before running):
  * labels_primary_pass01_gpt55.jsonl
  * labels_primary_pass02_gpt55.jsonl
  * labels_primary_pass03_gpt55.jsonl
  * masked_bundle.jsonl     (id -> endpoint, for sanity)
  * SEALED_mapping.json     (id -> cell; opened ONLY here, after 3 passes saved)

Per-item rule:
  * 3/3 unanimous -> that label
  * 2/3 majority  -> majority label
  * 1/1/1 tie     -> AMBIGUOUS (and collapse = 0 per manifest)

Per-cell:
  * N = number of runs
  * collapse_count = items where majority label == CLEAN_COLLAPSE
  * label_dist = distribution of majority labels

Output: relabel/cell_counts_primary_majority.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PASSES = ("pass01", "pass02", "pass03")


def sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def load_labels(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out[row["id"]] = row["label"]
    return out


def majority(labels: tuple[str, str, str]) -> tuple[str, bool]:
    c = Counter(labels)
    top, n = c.most_common(1)[0]
    if n >= 2:
        return top, True       # 2/3 or 3/3
    return "AMBIGUOUS", False  # 1/1/1 tie


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--relabel-dir", type=Path, required=True)
    p.add_argument("--rater-tag", default="gpt55")
    args = p.parse_args()

    rd = args.relabel_dir if args.relabel_dir.is_absolute() else REPO_ROOT / args.relabel_dir

    bundle = {json.loads(l)["id"]: json.loads(l)
              for l in (rd / "masked_bundle.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    sealed = json.loads((rd / "SEALED_mapping.json").read_text(encoding="utf-8"))

    pass_paths = {p: rd / f"labels_primary_{p}_{args.rater_tag}.jsonl" for p in PASSES}
    pass_sha = {p: sha1(pass_paths[p]) for p in PASSES}
    pass_labels = {p: load_labels(pass_paths[p]) for p in PASSES}

    ids = sorted(bundle)
    # sanity: every pass covers every id
    for p, lbls in pass_labels.items():
        missing = [i for i in ids if i not in lbls]
        if missing:
            raise SystemExit(f"{p}: missing ids {missing}")

    # per-item majority
    per_item: dict[str, dict] = {}
    unanimous_3of3 = 0
    majority_2of3 = 0
    tied_1of3 = 0
    for i in ids:
        trio = (pass_labels["pass01"][i], pass_labels["pass02"][i], pass_labels["pass03"][i])
        maj, ok = majority(trio)
        c = Counter(trio)
        if len(set(trio)) == 1:
            unanimous_3of3 += 1
        elif ok:
            majority_2of3 += 1
        else:
            tied_1of3 += 1
        per_item[i] = {
            "majority_label": maj,
            "collapse": 1 if maj == "CLEAN_COLLAPSE" else 0,
            "trio": list(trio),
            "endpoint": bundle[i]["endpoint"],
            "cell": sealed[i]["cell"],
        }

    # per-cell aggregation
    cells: dict[str, dict] = {}
    for i, info in per_item.items():
        cell = info["cell"]
        cells.setdefault(cell, {
            "N": 0,
            "collapse_count": 0,
            "label_dist": Counter(),
            "endpoint": info["endpoint"],
        })
        cells[cell]["N"] += 1
        cells[cell]["collapse_count"] += info["collapse"]
        cells[cell]["label_dist"][info["majority_label"]] += 1

    # serialize cleanly
    cells_out = {}
    for cell in sorted(cells):
        c = cells[cell]
        cells_out[cell] = {
            "endpoint": c["endpoint"],
            "N": c["N"],
            "collapse_count": c["collapse_count"],
            "collapse_rate": f"{c['collapse_count']}/{c['N']}",
            "label_dist": dict(c["label_dist"]),
        }

    out = {
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "rater_tag": args.rater_tag,
        "aggregator_rule": "majority_of_3_primary_passes; tie 1/1/1 -> AMBIGUOUS (collapse=0)",
        "provenance": {
            "bundle_sha1": sha1(rd / "masked_bundle.jsonl"),
            "sealed_sha1": sha1(rd / "SEALED_mapping.json"),
            "passes": {p: {"path": str(pass_paths[p].relative_to(REPO_ROOT)),
                           "sha1": pass_sha[p]} for p in PASSES},
        },
        "per_item_agreement": {
            "n_items": len(ids),
            "unanimous_3of3": unanimous_3of3,
            "majority_2of3": majority_2of3,
            "tied_1of3": tied_1of3,
            "unanimous_rate": f"{unanimous_3of3}/{len(ids)}",
        },
        "cells": cells_out,
    }

    out_path = rd / "cell_counts_primary_majority.yaml"
    out_path.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"wrote {out_path.relative_to(REPO_ROOT)}")
    print(yaml.safe_dump({k: v for k, v in out.items() if k in ("per_item_agreement", "cells")},
                         sort_keys=False, allow_unicode=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
