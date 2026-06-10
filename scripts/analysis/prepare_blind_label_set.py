"""
Prepare condition-blinded hand-label set (n=30) for 2x2 classifier validation.

Per docs/analysis_plan_2026_04_17.md §5.3:
  - Stratified sample n=30 across four conditions (mem_fb, nomem_fb,
    mem_nofb, nomem_nofb), drawn from turns T8–T49 (post-setup, branched).
  - Run ID, condition, and turn index are stripped from the labeling file;
    each item is given an anonymous ID (item_001 ... item_030).
  - Gold mapping (anon_id -> run/condition/turn) is saved to a separate key
    file that the labeler must not open during labeling.
  - A labels_template.csv is emitted for the labeler to fill in.

Outputs (under hand_label/):
  - blind_items.txt           (plain text, one item per block, no metadata)
  - blind_key.json            (anon_id -> {run, condition, turn})
  - labels_template.csv       (anon_id, operationalize, caveat, notes)

Usage:
  python scripts/analysis/prepare_blind_label_set.py

Deterministic via fixed random seed.
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

RUN_DIR = Path("data/manual_transcripts/v4_2x2_feedback_20260414_232517")
OUT_DIR = RUN_DIR / "hand_label"
CONDITIONS = ["mem_fb", "nomem_fb", "mem_nofb", "nomem_nofb"]
PER_CONDITION = [8, 7, 8, 7]  # sums to 30
TURN_LO = 8   # post-setup
TURN_HI = 50  # exclusive
SEED = 20260417


def load_runs(run_dir: Path) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(run_dir.glob("run_*.json"))]


def sample_items(runs: list[dict], rng: random.Random) -> list[dict]:
    items: list[dict] = []
    for cond, n in zip(CONDITIONS, PER_CONDITION):
        pool = []
        for r in runs:
            for t in r[cond]:
                if TURN_LO <= t["turn"] < TURN_HI:
                    pool.append({
                        "run": r["run_idx"],
                        "condition": cond,
                        "turn": t["turn"],
                        "user_msg": t["user_msg"],
                        "assistant_text": t["assistant_text"],
                    })
        chosen = rng.sample(pool, n)
        items.extend(chosen)
    rng.shuffle(items)
    return items


def write_outputs(items: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. blind_items.txt — plaintext, no metadata
    lines = []
    for i, it in enumerate(items, start=1):
        anon = f"item_{i:03d}"
        lines.append(f"==================== {anon} ====================")
        lines.append("USER:")
        lines.append(it["user_msg"].strip())
        lines.append("")
        lines.append("ASSISTANT:")
        lines.append(it["assistant_text"].strip())
        lines.append("")
        lines.append("")
    (out_dir / "blind_items.txt").write_text("\n".join(lines), encoding="utf-8")

    # 2. blind_key.json — metadata mapping (do NOT open while labeling)
    key = {
        f"item_{i:03d}": {
            "run": it["run"],
            "condition": it["condition"],
            "turn": it["turn"],
        }
        for i, it in enumerate(items, start=1)
    }
    (out_dir / "blind_key.json").write_text(
        json.dumps(key, indent=2), encoding="utf-8"
    )

    # 3. labels_template.csv — to be filled in by labeler
    with (out_dir / "labels_template.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["anon_id", "operationalize", "caveat", "notes"])
        for i in range(1, len(items) + 1):
            w.writerow([f"item_{i:03d}", "", "", ""])


def main() -> None:
    rng = random.Random(SEED)
    runs = load_runs(RUN_DIR)
    items = sample_items(runs, rng)
    write_outputs(items, OUT_DIR)

    # Report stratification (without leaking to the labeler file)
    print(f"Wrote {len(items)} items to {OUT_DIR}/")
    print(f"  blind_items.txt         (plaintext, no metadata)")
    print(f"  blind_key.json          (DO NOT OPEN while labeling)")
    print(f"  labels_template.csv     (fill in operationalize, caveat)")
    print()
    print("Stratification (for sanity, not for labeler):")
    from collections import Counter
    counts = Counter(it["condition"] for it in items)
    for c in CONDITIONS:
        print(f"  {c:<12} n={counts[c]}")


if __name__ == "__main__":
    main()
