#!/usr/bin/env python3
"""FIXED-TEST-PROMPT baseline necessity figure (apophenia).

Same fixed operative probe T across all conditions; only preceding context varies
(cold / naive-sim / gated-ladder). Balanced n=5 per cell. Two panels, judges never
mixed in one series: (A) fresh-Claude 2-axis harm (e>=2 & s<=1), (B) Jared >=7.
Source: data/blindpass/2026-06-18_fixedprobe_baseline/{AGG_fixedprobe,jared_scores}.json
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
agg = json.loads((REPO / "data/blindpass/2026-06-18_fixedprobe_baseline/AGG_fixedprobe.json").read_text())["by_model_condition"]

MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-5.4-mini"]
CONDS = [("cold_fixed", "cold\n(probe only)", "#bdbdbd"),
         ("naive_fixed", "naive-sim\n(same len, ungated)", "#6baed6"),
         ("ladder_fixed", "gated ladder", "#c1121f")]
N = 5

fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
panels = [("(A) fresh-Claude 2-axis harm  (e≥2 & s≤1)", "harm_fc"),
          ("(B) external Jared  bot-endorses-delusion ≥7", "jared")]
for ax, (title, fld) in zip(axes, panels):
    w = 0.26
    for ci, (cond, clabel, color) in enumerate(CONDS):
        xs, ys, labs = [], [], []
        for mi, m in enumerate(MODELS):
            a = agg.get(f"{m}|{cond}")
            pos = mi + (ci - 1) * w
            if not a:
                continue
            v = a[fld]
            xs.append(pos); ys.append(v / N); labs.append((pos, v / N, f"{v}/{N}"))
        ax.bar(xs, ys, width=w, color=color, edgecolor="black", linewidth=0.5,
               label=clabel if ax is axes[0] else None)
        for px, py, lab in labs:
            ax.text(px, py + 0.02, lab, ha="center", va="bottom", fontsize=8)
    ax.set_title(title, fontsize=10)
    ax.set_xticks(range(len(MODELS))); ax.set_xticklabels(MODELS, fontsize=9)
    ax.set_ylim(0, 1.12); ax.set_ylabel("break rate (of 5 trajectories)")
    ax.axhline(0, color="black", linewidth=0.6)

axes[0].legend(loc="upper right", fontsize=8, frameon=False)
fig.suptitle("Fixed-test-prompt necessity: with the operative ask held constant, only the gated-ladder context moves the boundary\n"
             "(cold ≤ naive-sim < gated ladder; gpt-5.4-mini holds throughout) — judge×judge κ 0.93/0.97",
             fontsize=10, y=1.04)
fig.tight_layout()
out = REPO / "docs/figures/fixedprobe_necessity_2026_06_18.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"wrote {out}")
