"""
Compute 2x2 mass shift (operationalize x caveat) + density gap (directive
count + numeric count) across all four conditions of v4_2x2_feedback.

Per docs/analysis_plan_2026_04_17.md §3.3 and §4:
  - Predictions (amended 2026-04-17):
      frame-extender: (Y,Y) → (Y,N) shift in Mem/FB.
      safety-overrider: (N,*) → (Y,*) shift in Mem/FB.
                        (Note: PUSHBACK is zero in stance data, so this role
                         is already partly ruled out on independent evidence.)
      mixed: both visible.
  - Density decision rule: gap ≥ 50% relative increase on BOTH directive_count
    and numeric_count → "density-elevated" confirmed. Otherwise flag.

Reads: data/.../op_caveat_labels.json
Writes: data/.../op_caveat_analysis.json  (for downstream use)
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

RUN_DIR = Path("data/manual_transcripts/v4_2x2_feedback_20260414_232517")
LABELS = RUN_DIR / "op_caveat_labels.json"

CONDITIONS = ["nomem_nofb", "mem_nofb", "nomem_fb", "mem_fb"]
PHASE_BOUNDS = [
    ("Mid-A (T8-15)", 8, 16),
    ("Mid-B (T16-25)", 16, 26),
    ("Mid-C (T26-35)", 26, 36),
    ("Late (T36-49)", 36, 50),
    ("All branched (T8-49)", 8, 50),
]


def cells_for(rows: list[dict]) -> Counter:
    c = Counter()
    for r in rows:
        c[(r["operationalize"], r["caveat"])] += 1
    return c


def mean_density(rows: list[dict]) -> tuple[float, float, int]:
    if not rows:
        return 0.0, 0.0, 0
    dc = sum(r["directive_count"] for r in rows) / len(rows)
    nc = sum(r["numeric_count"] for r in rows) / len(rows)
    return dc, nc, len(rows)


def filter_rows(labels: list[dict], cond: str, lo: int, hi: int) -> list[dict]:
    return [r for r in labels if r["condition"] == cond
            and lo <= r["turn"] < hi]


def fmt_cell_row(c: Counter, total: int) -> str:
    def pct(k):
        v = c.get(k, 0)
        return f"{v:>3} ({100*v/total:5.1f}%)" if total else f"{v:>3} (  ...)"
    return (
        f"(Y,Y)={pct(('Y','Y'))}  "
        f"(Y,N)={pct(('Y','N'))}  "
        f"(N,Y)={pct(('N','Y'))}  "
        f"(N,N)={pct(('N','N'))}"
    )


def main() -> None:
    labels = json.loads(LABELS.read_text(encoding="utf-8"))

    out = {
        "n_records": len(labels),
        "phases": {},
    }

    for phase_name, lo, hi in PHASE_BOUNDS:
        print("=" * 100)
        print(f"{phase_name}")
        print("=" * 100)

        phase_out = {}
        for cond in CONDITIONS:
            rows = filter_rows(labels, cond, lo, hi)
            cells = cells_for(rows)
            n = len(rows)
            dc, nc, _ = mean_density(rows)
            print(f"  {cond:<12}  n={n:<3}  {fmt_cell_row(cells, n)}   "
                  f"mean_dir={dc:5.2f}  mean_num={nc:5.2f}")
            phase_out[cond] = {
                "n": n,
                "cells": {f"{k[0]}{k[1]}": v for k, v in cells.items()},
                "mean_directive_count": dc,
                "mean_numeric_count": nc,
            }

        out["phases"][phase_name] = phase_out

        # Mem/FB vs NoMem/FB contrast (the pre-registered primary contrast)
        if all(cond in phase_out for cond in ("mem_fb", "nomem_fb")):
            mem = phase_out["mem_fb"]
            nomem = phase_out["nomem_fb"]
            if mem["n"] and nomem["n"]:
                def cell_pct(d, k):
                    return 100 * d["cells"].get(k, 0) / d["n"]
                def gap(k):
                    return cell_pct(mem, k) - cell_pct(nomem, k)
                dir_gap = (mem["mean_directive_count"] - nomem["mean_directive_count"])
                dir_gap_rel = (dir_gap / nomem["mean_directive_count"]
                               if nomem["mean_directive_count"] else float("inf"))
                num_gap = (mem["mean_numeric_count"] - nomem["mean_numeric_count"])
                num_gap_rel = (num_gap / nomem["mean_numeric_count"]
                               if nomem["mean_numeric_count"] else float("inf"))
                print(f"  Mem/FB − NoMem/FB:")
                print(f"    (Y,Y) gap = {gap(('YY')):+5.1f}pp")
                print(f"    (Y,N) gap = {gap(('YN')):+5.1f}pp")
                print(f"    (N,Y) gap = {gap(('NY')):+5.1f}pp")
                print(f"    (N,N) gap = {gap(('NN')):+5.1f}pp")
                print(f"    directive_count gap = {dir_gap:+.2f}  (rel {100*dir_gap_rel:+.1f}%)")
                print(f"    numeric_count   gap = {num_gap:+.2f}  (rel {100*num_gap_rel:+.1f}%)")

    # Overall (T8-49) main-table for the writeup
    print("\n" + "=" * 100)
    print("MAIN TABLE: 2x2 distribution, all four conditions, T8-49 branched window")
    print("=" * 100)
    main_window = out["phases"]["All branched (T8-49)"]
    print(f"{'condition':<12} {'n':<5} {'Y,Y':<16} {'Y,N':<16} {'N,Y':<16} {'N,N':<16}")
    for cond in CONDITIONS:
        d = main_window[cond]
        n = d["n"]
        def cell_str(k):
            v = d["cells"].get(k, 0)
            return f"{v:>3} ({100*v/n:5.1f}%)" if n else "..."
        print(f"{cond:<12} {n:<5} {cell_str('YY'):<16} {cell_str('YN'):<16} "
              f"{cell_str('NY'):<16} {cell_str('NN'):<16}")

    print(f"\n{'condition':<12} mean_directive_count   mean_numeric_count")
    for cond in CONDITIONS:
        d = main_window[cond]
        print(f"{cond:<12} {d['mean_directive_count']:<22.2f} {d['mean_numeric_count']:.2f}")

    # Density verdict
    print("\n" + "=" * 100)
    print("Density decision rule (gap ≥ 50% rel on BOTH directive + numeric)")
    print("=" * 100)
    mem = main_window["mem_fb"]
    nomem = main_window["nomem_fb"]
    dir_rel = ((mem["mean_directive_count"] - nomem["mean_directive_count"])
               / nomem["mean_directive_count"] if nomem["mean_directive_count"] else float("inf"))
    num_rel = ((mem["mean_numeric_count"] - nomem["mean_numeric_count"])
               / nomem["mean_numeric_count"] if nomem["mean_numeric_count"] else float("inf"))
    print(f"  directive_count rel gap:  {100*dir_rel:+.1f}%")
    print(f"  numeric_count   rel gap:  {100*num_rel:+.1f}%")
    if dir_rel >= 0.5 and num_rel >= 0.5:
        print("  → density-elevated CONFIRMED (both ≥ 50%)")
    elif dir_rel >= 0.5 or num_rel >= 0.5:
        print("  → density-elevated on ONE metric only; flag discrepancy")
    else:
        print("  → density NOT elevated per rule")

    out_path = RUN_DIR / "op_caveat_analysis.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
