#!/usr/bin/env python3
"""Depth-curve figure (CANONICAL, 2026-06-23 all-graded-means form). Re-runnable, NO API.

THREE metrics, ALL as normalized GRADED MEANS (transparency: no threshold baked in):
  - PsychosisBench DCS (0-2) ÷2          -- confirmation, coarsest construct
  - our 2-axis endorsement (0-3) ÷3      -- graded affirmation of the rung-local proposition
  - External operative criterion (0-10) ÷10  -- keyed-to-me operative endorsement, strictest
    [internal = the Jared/DelusionEval `bot-endorses-delusion` score; ANON in the figure per the
     binding double-blind policy — legend says "External operative criterion"]

Why graded means (not present-rate / harm-flag): threshold-neutral (sidesteps the e>=2-vs-e==3
and the external cutoff debates), keeps the full signal. Ordinal-mean softness is covered by the
%@2 ceiling annotation (threshold-free, ordinal-safe saturation evidence: D9 = 100% at ceiling).

Claim (Shin 2026-06-23): DCS agrees on the ONSET of externalization (sharp rise at D2) but
SATURATES thereafter (%@2 = 67/90/100 over D2/D3/endpoint), while the finer measures keep
resolving later depths -- nested DCS >= ours >= External at every depth. Three DIFFERENT
constructs compared on RESOLUTION vs depth, NOT a harm-rate agreement; gap read qualitatively.
The construct-validated binaries (our e>=2&s<=1 endpoint harm; external present-rate, cutoff>=7)
live in the TEXT/centerpiece, not this figure.
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
ORDER = ["cold", "afterD1", "afterD2", "afterD3", "afterD9"]
XLAB = ["cold", "D1\nLegitimacy", "D2\nExternalization", "D3\nPersonalization", "D9 → D12\nWeighing → endpoint"]
EXT_MAX = 10  # external operative rubric nominal max (observed 0-9, present cutoff >=7)
EXT_LABEL = "External operative criterion ÷10 (keyed-to-me; strictest)"  # internal: Jared/DelusionEval
C_E, C_X, C_D = "#1f5fbf", "#2a9d4a", "#d4691e"


def load(name):
    return {s["blind_id"]: s for s in json.loads((D / name).read_text())}


def aggregate():
    key = json.loads((D / "SEALED_key.json").read_text())
    H, F1, F2 = load("haiku_scores.json"), load("fresh_claude_scores_judge1.json"), load("fresh_claude_scores_judge2.json")
    J, DCS = load("jared_scores.json"), load("DCS_depth_scores.json")
    by = {d: {"e": [], "x": [], "dcs": []} for d in ORDER}
    for b, m in key.items():
        d = m["depth"]
        for Jd in (H, F1, F2):
            if b in Jd:
                by[d]["e"].append(Jd[b]["endorsement"])
        if b in J and J[b].get("score") is not None:
            by[d]["x"].append(J[b]["score"])
        if b in DCS and DCS[b]["DCS"] is not None:
            by[d]["dcs"].append(DCS[b]["DCS"])
    e   = [sum(by[d]["e"])  / len(by[d]["e"])  / 3       for d in ORDER]   # our endorsement mean ÷3
    ext = [sum(by[d]["x"])  / len(by[d]["x"])  / EXT_MAX for d in ORDER]   # external mean ÷10
    dcs = [sum(by[d]["dcs"]) / len(by[d]["dcs"]) / 2     for d in ORDER]   # DCS mean ÷2
    ceil = [Counter(by[d]["dcs"])[2] / len(by[d]["dcs"]) for d in ORDER]   # fraction at DCS ceiling
    return e, ext, dcs, ceil


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    e, ext, dcs, ceil = aggregate()
    x = list(range(len(ORDER)))

    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    ax.fill_between(x, ext, dcs, color="#cccccc", alpha=0.22, zorder=0,
                    label="resolution band the finer measures fill")
    ld, = ax.plot(x, dcs, "^--", color=C_D, lw=2.4, ms=9, label="PsychosisBench DCS ÷2 (confirmation; coarsest)")
    le, = ax.plot(x, e,   "o-",  color=C_E, lw=2.4, ms=8, label="Our endorsement ÷3 (graded)")
    lx, = ax.plot(x, ext, "s-",  color=C_X, lw=2.4, ms=8, label=EXT_LABEL)

    ax.axhline(1.0, color=C_D, ls=":", lw=1, alpha=0.45)
    ax.text(0.04, 1.012, "DCS ceiling (÷2 = 1.0)", color=C_D, fontsize=8.3, ha="left", va="bottom")
    for xi, (d2, cf) in enumerate(zip(dcs, ceil)):
        ax.annotate(f"{cf:.0%}@2", (xi, d2), textcoords="offset points", xytext=(0, 9),
                    fontsize=7.4, color=C_D, ha="center")
    ax.annotate("DCS at/near ceiling from D2 → endpoint\n(no resolution left)",
                xy=(3, dcs[3]), xytext=(1.35, 1.05), fontsize=8.0, color=C_D,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color=C_D, lw=1.0, alpha=0.7))

    ax.set_ylim(-0.05, 1.18)
    ax.set_xlim(-0.3, len(ORDER) - 0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(XLAB, fontsize=8.7)
    ax.set_ylabel("normalized mean score  (per metric's own scale)", fontsize=10)
    ax.set_xlabel("Depth = genuine climb in context before the constant D12 operative probe T", fontsize=9.5)
    ax.set_title("Three graded measures nested by construct strictness — DCS saturates by D2,\n"
                 "finer measures keep resolving to the D12 endpoint\n"
                 "gpt-4o · D12 operative probe T held constant · n=30/depth = 3 traj × 10 reps · DCS o4-mini, pin 73966f95",
                 fontsize=9.8)
    ax.legend(loc="lower right", fontsize=8.1, framealpha=0.95)
    ax.grid(True, axis="y", alpha=0.22)
    fig.text(0.5, -0.02,
             "Different CONSTRUCTS compared on resolution vs depth (not a harm-rate agreement); gap read qualitatively. "
             "%@2 = items at DCS ceiling.  Construct-validated binaries (our e≥2∧s≤1 endpoint harm; external present-rate ≥7) reported in text.",
             ha="center", va="top", fontsize=7.3, color="#444444", wrap=True)
    fig.tight_layout()
    for ext_ in ("png", "svg"):
        fig.savefig(FIG / f"dcs_depth_curve_2026_06_23.{ext_}", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote docs/figures/dcs_depth_curve_2026_06_23.{png,svg} (all-graded-means, anon legend)")
    print("\nper-depth (caption numbers; all normalized graded means):")
    for i, d in enumerate(ORDER):
        print(f"  {d:<9} ours÷3={e[i]:.2f}  External÷10={ext[i]:.2f}  DCS÷2={dcs[i]:.2f}  ({ceil[i]:.0%}@ceiling)")


if __name__ == "__main__":
    main()
