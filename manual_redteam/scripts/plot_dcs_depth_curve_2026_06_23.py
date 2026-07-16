#!/usr/bin/env python3
"""Depth-curve figure (CANONICAL, all-graded-means). Minimal plot — NO in-figure prose;
all explanation goes in the LaTeX caption. Re-runnable, NO API.

Three metrics, all normalized graded means: DCS÷2 (0-2), our endorsement÷3 (0-3),
External operative criterion÷10 (0-10; internal = Jared/DelusionEval, anonymized).
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path(__file__).resolve().parents[1] / "data/blindpass/2026-06-22_oracle_depth"
FIG = Path(__file__).resolve().parents[1] / "docs/figures"
ORDER = ["cold", "afterD1", "afterD2", "afterD3", "afterD9"]  # DATA KEYS (depth field, canonical sparse codes) -- DO NOT CHANGE
XLAB = ["cold", "D1", "D2", "D3", "D4"]  # DISPLAY: contiguous D1-D5 for the paper (afterD9 = Weighing = D4)
EXT_MAX = 10
C_E, C_X, C_D = "#1f5fbf", "#2a9d4a", "#d4691e"


def load(name):
    return {s["blind_id"]: s for s in json.loads((D / name).read_text())}


def aggregate():
    key = json.loads((D / "SEALED_key.json").read_text())
    H, F1, F2 = load("haiku_scores.json"), load("fresh_claude_scores_judge1.json"), load("fresh_claude_scores_judge2.json")
    J, DCS = load("jared_scores.json"), load("DCS_depth_scores.json")
    expected = set(key)
    for name, scores in (("haiku", H), ("fresh1", F1), ("fresh2", F2),
                         ("external", J), ("dcs", DCS)):
        missing = expected - set(scores)
        extra = set(scores) - expected
        if missing or extra:
            raise ValueError(
                f"{name} score/key mismatch: missing={len(missing)} extra={len(extra)}")
    by = {d: {"e": [], "x": [], "dcs": []} for d in ORDER}
    for b, m in key.items():
        d = m["depth"]
        if d not in by:
            raise ValueError(f"unknown depth {d!r} for blind_id={b}")
        for Jd in (H, F1, F2):
            by[d]["e"].append(Jd[b]["endorsement"])
        if J[b].get("score") is None or DCS[b]["DCS"] is None:
            raise ValueError(f"null score for blind_id={b}")
        by[d]["x"].append(J[b]["score"])
        by[d]["dcs"].append(DCS[b]["DCS"])
    e   = [sum(by[d]["e"])  / len(by[d]["e"])  / 3       for d in ORDER]
    ext = [sum(by[d]["x"])  / len(by[d]["x"])  / EXT_MAX for d in ORDER]
    dcs = [sum(by[d]["dcs"]) / len(by[d]["dcs"]) / 2     for d in ORDER]
    ceil = [Counter(by[d]["dcs"])[2] / len(by[d]["dcs"]) for d in ORDER]
    return e, ext, dcs, ceil


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    e, ext, dcs, ceil = aggregate()
    x = list(range(len(ORDER)))

    fig, ax = plt.subplots(figsize=(6.2, 4.1))
    ax.plot(x, dcs, "^--", color=C_D, lw=2.2, ms=8, label="PsychosisBench DCS")
    ax.plot(x, e,   "o-",  color=C_E, lw=2.2, ms=7, label="Our endorsement (2-axis)")
    ax.plot(x, ext, "s-",  color=C_X, lw=2.2, ms=7, label="External operative criterion")
    ax.axhline(1.0, color="#999999", ls=":", lw=0.8)  # ceiling reference, unlabeled
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlim(-0.25, len(ORDER) - 0.75)
    ax.set_xticks(x); ax.set_xticklabels(XLAB)
    ax.set_xlabel("Genuine climb depth in context, then the fixed D5 operative probe")
    ax.set_ylabel("normalized mean score (0–1)")
    ax.legend(loc="upper left", framealpha=0.95)
    ax.grid(True, axis="y", alpha=0.2)
    fig.tight_layout()
    for ext_ in ("png", "svg"):
        out = FIG / f"dcs_depth_curve_2026_06_23.{ext_}"
        fig.savefig(out, dpi=150, bbox_inches="tight")
        if ext_ == "svg":
            # Matplotlib emits trailing spaces in SVG path data; normalize the
            # tracked artifact so `git diff --check` remains useful.
            out.write_text("\n".join(line.rstrip() for line in out.read_text().splitlines()) + "\n")
    plt.close(fig)
    print("wrote docs/figures/dcs_depth_curve_2026_06_23.{png,svg} (minimal)")
    print("\ncaption numbers (for LaTeX):")
    for i, d in enumerate(ORDER):
        print(f"  {XLAB[i]:7} DCS÷2={dcs[i]:.2f}  ours÷3={e[i]:.2f}  External÷10={ext[i]:.2f}  (DCS %@ceiling={ceil[i]:.0%})")


if __name__ == "__main__":
    main()
