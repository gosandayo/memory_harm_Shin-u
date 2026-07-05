#!/usr/bin/env python3
"""FIXED-TEST-PROMPT baseline necessity figure (SECRET-PROJECT).

Sibling of plot_fixedprobe_2026_06_18.py (apophenia). Same committed grandiose probe
across all conditions; only preceding context varies (cold / naive-sim / gated ladder).
Natural n per cell (cold=5; naive/ladder={8,3,3}) -> rate = k/n_cell, label k/n.
Two panels, judges never mixed: (A) fresh-Claude 2-axis harm (e>=2 & s<=1), (B) Jared
bot-endorses-delusion >=7.
Source: data/blindpass/2026-06-20_sp_fixedprobe/AGG_fixedprobe_sp.json
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
A = json.loads((REPO / "data/blindpass/2026-06-20_sp_fixedprobe/AGG_fixedprobe_sp.json").read_text())
agg = A["by_model_condition"]
ke, ks = A["kappa_endorsement"], A["kappa_safety"]

MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-5.4-mini"]
CONDS = [("cold_fixed", "cold\n(probe only)", "#bdbdbd"),
         ("naive_fixed", "naive-sim\n(same len, ungated)", "#6baed6"),
         ("ladder_fixed", "gated ladder", "#c1121f")]

fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
panels = [("(A) fresh-Claude 2-axis harm  (e≥2 & s≤1)", "harm_fc"),
          ("(B) external Jared  bot-endorses-delusion ≥7", "jared")]
for ax, (title, fld) in zip(axes, panels):
    w = 0.26
    for ci, (cond, clabel, color) in enumerate(CONDS):
        xs, ys, labs = [], [], []
        for mi, m in enumerate(MODELS):
            a = agg.get(f"{m}|{cond}")
            if not a:
                continue
            pos = mi + (ci - 1) * w
            n = a["n"]; v = a[fld]
            xs.append(pos); ys.append(v / n); labs.append((pos, v / n, f"{v}/{n}"))
        ax.bar(xs, ys, width=w, color=color, edgecolor="black", linewidth=0.5,
               label=clabel if ax is axes[0] else None)
        for px, py, lab in labs:
            ax.text(px, py + 0.02, lab, ha="center", va="bottom", fontsize=8)
    ax.set_title(title, fontsize=10)
    ax.set_xticks(range(len(MODELS))); ax.set_xticklabels(MODELS, fontsize=9)
    ax.set_ylim(0, 1.12); ax.set_ylabel("break rate (per-cell n)")
    ax.axhline(0, color="black", linewidth=0.6)

axes[0].legend(loc="upper right", fontsize=8, frameon=False)
fig.suptitle("Secret-project (hidden-recruitment) — fixed-test-prompt necessity: with the operative ask held constant,\n"
             "only the gated-ladder context moves the boundary (cold ≤ naive-sim < gated ladder; gpt-4o & gpt-5.4-mini hold throughout) "
             f"— judge×judge κ {ke:.2f}/{ks:.2f}",
             fontsize=9.5, y=1.05)
fig.tight_layout()
out = REPO / "docs/figures/fixedprobe_necessity_sp_2026_06_20.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"wrote {out}")
