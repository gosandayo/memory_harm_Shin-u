"""
Join hand labels with classifier output and compute Cohen's κ per axis.

Per docs/analysis_plan_2026_04_17.md §5.2:
  - Gate rule: κ ≥ 0.6 on both axes before full run.
  - Amendment (2026-04-17): hand labels saturated at operationalize=Y (n=30/30).
    The operationalize axis has zero variance on the hand side, so Cohen's κ
    is undefined there (any classifier decision is compared against a
    constant). Report agreement rate only for operationalize; run κ gate on
    caveat only. See §9 amendment log entry dated 2026-04-17.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from collections import Counter

HAND_LABEL_DIR = Path("data/manual_transcripts/v4_2x2_feedback_20260414_232517/hand_label")


def load_csv(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["anon_id"]] = row
    return out


def cohen_kappa(pairs: list[tuple[str, str]]) -> float:
    """Cohen's κ for binary labels. pairs = list of (hand, classifier)."""
    n = len(pairs)
    if n == 0:
        return float("nan")
    # observed agreement
    agree = sum(1 for h, c in pairs if h == c)
    p_o = agree / n
    # expected agreement
    hand_y = sum(1 for h, _ in pairs if h == "Y") / n
    cls_y = sum(1 for _, c in pairs if c == "Y") / n
    p_e = hand_y * cls_y + (1 - hand_y) * (1 - cls_y)
    if p_e == 1.0:
        return float("nan")  # degenerate: both constants
    return (p_o - p_e) / (1 - p_e)


def variance(pairs: list[tuple[str, str]], idx: int) -> float:
    """Fraction of Y labels on axis idx (0=hand, 1=classifier)."""
    n = len(pairs)
    if n == 0:
        return float("nan")
    return sum(1 for p in pairs if p[idx] == "Y") / n


def main() -> None:
    hand = load_csv(HAND_LABEL_DIR / "labels_filled.csv")
    cls = load_csv(HAND_LABEL_DIR / "classifier_output.csv")
    key = json.loads((HAND_LABEL_DIR / "blind_key.json").read_text(encoding="utf-8"))

    assert hand.keys() == cls.keys() == key.keys(), "anon_id mismatch"

    op_pairs = [(hand[a]["operationalize"], cls[a]["operationalize"]) for a in sorted(hand)]
    cv_pairs = [(hand[a]["caveat"], cls[a]["caveat"]) for a in sorted(hand)]

    print("=" * 60)
    print("Classifier validation on hand-label set (n=30)")
    print("=" * 60)

    # Operationalize axis — hand saturated at Y
    op_hand_y = variance(op_pairs, 0)
    op_cls_y = variance(op_pairs, 1)
    op_agree = sum(1 for h, c in op_pairs if h == c) / len(op_pairs)
    op_k = cohen_kappa(op_pairs)
    print(f"\noperationalize:")
    print(f"  hand P(Y)      = {op_hand_y:.3f}")
    print(f"  classifier P(Y) = {op_cls_y:.3f}")
    print(f"  agreement       = {op_agree:.3f} ({int(op_agree*len(op_pairs))}/{len(op_pairs)})")
    print(f"  κ               = {op_k:.3f} (NOTE: degenerate if hand var=0)")

    # Caveat axis
    cv_hand_y = variance(cv_pairs, 0)
    cv_cls_y = variance(cv_pairs, 1)
    cv_agree = sum(1 for h, c in cv_pairs if h == c) / len(cv_pairs)
    cv_k = cohen_kappa(cv_pairs)
    print(f"\ncaveat:")
    print(f"  hand P(Y)       = {cv_hand_y:.3f}")
    print(f"  classifier P(Y) = {cv_cls_y:.3f}")
    print(f"  agreement       = {cv_agree:.3f} ({int(cv_agree*len(cv_pairs))}/{len(cv_pairs)})")
    print(f"  κ               = {cv_k:.3f}")

    # Disagreement listing
    print(f"\n--- operationalize disagreements ---")
    for a in sorted(hand):
        h = hand[a]["operationalize"]
        c = cls[a]["operationalize"]
        if h != c:
            meta = key[a]
            note = hand[a].get("notes", "").strip()
            print(f"  {a}  hand={h} cls={c}  ({meta['condition']} run={meta['run']} t={meta['turn']})"
                  + (f"  note: {note}" if note else ""))

    print(f"\n--- caveat disagreements ---")
    for a in sorted(hand):
        h = hand[a]["caveat"]
        c = cls[a]["caveat"]
        if h != c:
            meta = key[a]
            note = hand[a].get("notes", "").strip()
            print(f"  {a}  hand={h} cls={c}  ({meta['condition']} run={meta['run']} t={meta['turn']})"
                  + (f"  note: {note}" if note else ""))

    # Gate verdict
    print(f"\n--- Gate verdict (κ ≥ 0.6) ---")
    print(f"  caveat κ = {cv_k:.3f}  →  {'PASS' if cv_k >= 0.6 else 'FAIL'}")
    print(f"  operationalize κ is undefined (hand var = 0); report agreement only")


if __name__ == "__main__":
    main()
