"""
Visualize Memory Format Experiment Results
==========================================
Generates summary figures for the memory-format factorization experiment.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_DIR = Path("data/lookism_agent_drift/memory_format_experiment")
OUT_FIG  = DATA_DIR / "memory_format_figures.png"

PHASE1_END = 8    # turns 0-7
PHASE2_END = 29   # turns 8-28
# Phase 3: turns 29-49

CONDITIONS = [
    "no_memory",
    "factual_memory",
    "factual_pref",
    "factual_eval",
    "factual_pref_eval",
    "factual_pref_safety",
]
LABELS = {
    "no_memory": "No Memory\n(baseline)",
    "factual_memory": "F-only",
    "factual_pref": "F+P",
    "factual_eval": "F+EV",
    "factual_pref_eval": "F+P+EV",
    "factual_pref_safety": "F+P+SPR",
}
COLORS = {
    "no_memory": "#4C78A8",
    "factual_memory": "#9E9E9E",
    "factual_pref": "#72B7B2",
    "factual_eval": "#F58518",
    "factual_pref_eval": "#E45756",
    "factual_pref_safety": "#54A24B",
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

agg_files = sorted(
    p for p in DATA_DIR.glob("aggregate*.json")
    if not p.name.endswith("_selected.json")
)
assert agg_files, "No aggregate file found"
agg_path = agg_files[-1]

with open(agg_path) as f:
    raw = json.load(f)

# Convert to float arrays; replace 0.0 scoring failures with NaN
data: dict[str, np.ndarray] = {}
for cond in CONDITIONS:
    arr = np.array(raw[cond], dtype=float)      # shape: (n_runs, 50)
    arr[arr == 0.0] = np.nan                     # treat scoring failures as missing
    data[cond] = arr

n_turns = 50
turns = np.arange(n_turns)

# Phase mean & SD per run
def phase_stats(arr: np.ndarray, t_start: int, t_end: int):
    """Return per-run phase means (ignoring NaN), then grand mean & SE."""
    chunk = arr[:, t_start:t_end]               # (n_runs, n_turns)
    run_means = np.nanmean(chunk, axis=1)        # (n_runs,)
    grand_mean = np.nanmean(run_means)
    grand_se   = np.nanstd(run_means, ddof=1) / math.sqrt(len(run_means))
    return run_means, grand_mean, grand_se

# ---------------------------------------------------------------------------
# Simple t-test helper
# ---------------------------------------------------------------------------

def welch_t(a: np.ndarray, b: np.ndarray):
    """Welch two-sample t-test; returns t, p."""
    na, nb = len(a), len(b)
    ma, mb = np.mean(a), np.mean(b)
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    se = math.sqrt(va/na + vb/nb)
    t  = (ma - mb) / se
    df = (va/na + vb/nb)**2 / ((va/na)**2/(na-1) + (vb/nb)**2/(nb-1))
    # Approx p from t and df using regularised incomplete beta
    x = df / (df + t*t)
    # scipy not available — use manual two-tailed approximation via erfc
    # For |t| > 3, p < 0.005 — just mark as <0.0001 if |t|>4
    p_approx = math.erfc(abs(t) / math.sqrt(2))  # normal approx, conservative
    return t, p_approx

def sig_stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    return "n.s."

# ---------------------------------------------------------------------------
# Compute per-turn grand mean ± 1 SE  (NaN-safe)
# ---------------------------------------------------------------------------

turn_means: dict[str, np.ndarray] = {}
turn_ses:   dict[str, np.ndarray] = {}
for cond in CONDITIONS:
    arr = data[cond]
    m = np.nanmean(arr, axis=0)
    s = np.nanstd(arr, axis=0, ddof=1) / math.sqrt(arr.shape[0])
    turn_means[cond] = m
    turn_ses[cond]   = s

# ---------------------------------------------------------------------------
# Compute phase stats
# ---------------------------------------------------------------------------

phase_data: dict[str, dict] = {}
for cond in CONDITIONS:
    arr = data[cond]
    p1_runs, p1_mean, p1_se = phase_stats(arr, 0, PHASE1_END)
    p2_runs, p2_mean, p2_se = phase_stats(arr, PHASE1_END, PHASE2_END)
    p3_runs, p3_mean, p3_se = phase_stats(arr, PHASE2_END, n_turns)
    phase_data[cond] = dict(
        p1_runs=p1_runs, p1_mean=p1_mean, p1_se=p1_se,
        p2_runs=p2_runs, p2_mean=p2_mean, p2_se=p2_se,
        p3_runs=p3_runs, p3_mean=p3_mean, p3_se=p3_se,
    )

# ---------------------------------------------------------------------------
# Build figure
# ---------------------------------------------------------------------------

fig = plt.figure(figsize=(16, 14))
fig.patch.set_facecolor("white")

gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.32,
                       left=0.07, right=0.97, top=0.93, bottom=0.06)

# Panel A — per-turn trajectories
ax_a = fig.add_subplot(gs[0, :])   # full width

for cond in CONDITIONS:
    m = turn_means[cond]
    s = turn_ses[cond]
    col = COLORS[cond]
    lbl = LABELS[cond].replace("\n", " ")
    ax_a.plot(turns, m, color=col, lw=2, label=lbl)
    ax_a.fill_between(turns, m-s, m+s, color=col, alpha=0.18)

# Phase boundary lines
ax_a.axvline(PHASE1_END - 0.5, color="gray", ls="--", lw=1.2, alpha=0.6)
ax_a.axvline(PHASE2_END - 0.5, color="gray", ls="--", lw=1.2, alpha=0.6)
ax_a.text(PHASE1_END/2, 9.4, "Phase 1\n(identical)", ha="center", va="top",
          fontsize=9, color="gray")
ax_a.text((PHASE1_END + PHASE2_END)/2, 9.4, "Phase 2\n(memory injected)",
          ha="center", va="top", fontsize=9, color="gray")
ax_a.text((PHASE2_END + n_turns)/2, 9.4, "Phase 3\n(context forks)",
          ha="center", va="top", fontsize=9, color="gray")
ax_a.set_xlim(-0.5, 49.5)
ax_a.set_ylim(0, 10)
ax_a.set_xlabel("Turn", fontsize=11)
ax_a.set_ylabel("Enablement score (0–10)", fontsize=11)
ax_a.set_title("A  Per-turn enablement scores by memory condition (mean ± 1 SE)",
               fontsize=12, fontweight="bold", loc="left")
ax_a.legend(fontsize=10, loc="lower left")
ax_a.grid(True, alpha=0.25)

# Panel B — Phase-level bar chart
ax_b = fig.add_subplot(gs[1, 0])

phase_labels = ["Phase 1\n(T0–7)", "Phase 2\n(T8–28)", "Phase 3\n(T29–49)"]
x = np.arange(3)
width = 0.26

for i, cond in enumerate(CONDITIONS):
    pd = phase_data[cond]
    label = LABELS[cond]
    col = COLORS[cond]
    means = [pd["p1_mean"], pd["p2_mean"], pd["p3_mean"]]
    ses   = [pd["p1_se"],   pd["p2_se"],   pd["p3_se"]]
    offset = (i - 1) * width
    bars = ax_b.bar(x + offset, means, width, yerr=ses,
                    color=col, alpha=0.85, capsize=4,
    label=label.replace("\n", " "), error_kw=dict(lw=1.5))

ax_b.set_xticks(x)
ax_b.set_xticklabels(phase_labels, fontsize=10)
ax_b.set_ylim(0, 10)
ax_b.set_ylabel("Mean enablement score", fontsize=10)
ax_b.set_title("B  Phase-level means (±1 SE)", fontsize=11, fontweight="bold", loc="left")
ax_b.legend(fontsize=8)
ax_b.grid(True, alpha=0.25, axis="y")

# Panel C — P2 violin
ax_c = fig.add_subplot(gs[1, 1])

p2_by_cond = [phase_data[cond]["p2_runs"] for cond in CONDITIONS]
p3_by_cond = [phase_data[cond]["p3_runs"] for cond in CONDITIONS]

x_pos = list(range(1, len(CONDITIONS) + 1))
vp2 = ax_c.violinplot(p2_by_cond, positions=[p - 0.15 for p in x_pos],
                       widths=0.25, showmeans=True, showmedians=False)
vp3 = ax_c.violinplot(p3_by_cond, positions=[p + 0.15 for p in x_pos],
                       widths=0.25, showmeans=True, showmedians=False)

for vp, alpha in [(vp2, 0.75), (vp3, 0.45)]:
    for body, cond in zip(vp["bodies"], CONDITIONS):
        col = COLORS[cond]
        body.set_facecolor(col)
        body.set_alpha(alpha)
    for part in ("cmeans", "cbars", "cmins", "cmaxes"):
        if part in vp:
            vp[part].set_color("black")
            vp[part].set_lw(1.2)

ax_c.set_xticks(x_pos)
ax_c.set_xticklabels([LABELS[c].replace("\n", " ") for c in CONDITIONS], fontsize=8)
ax_c.set_ylim(0, 10)
ax_c.set_ylabel("Phase mean enablement score", fontsize=10)
ax_c.set_title("C  Distribution across runs\n(dark=Phase 2, light=Phase 3)",
               fontsize=11, fontweight="bold", loc="left")

p2_patch = mpatches.Patch(color="gray", alpha=0.75, label="Phase 2")
p3_patch = mpatches.Patch(color="gray", alpha=0.40, label="Phase 3")
ax_c.legend(handles=[p2_patch, p3_patch], fontsize=9)
ax_c.grid(True, alpha=0.25, axis="y")

# ---------------------------------------------------------------------------
# Significance annotations on panel C
# ---------------------------------------------------------------------------

def bracket(ax, x1, x2, y, text, fontsize=9):
    ax.plot([x1, x1, x2, x2], [y, y+0.1, y+0.1, y], lw=1.2, color="black")
    ax.text((x1+x2)/2, y+0.15, text, ha="center", va="bottom", fontsize=fontsize)

# Compare P2 means across conditions
nm_p2 = phase_data["no_memory"]["p2_runs"]
nm_p3 = phase_data["no_memory"]["p3_runs"]

# Print stat summary
print("\n=== Memory Format Experiment: Statistical Summary ===\n")
print(f"{'Condition':<16} {'N':>4} {'P1 mean':>8} {'P2 mean':>8} {'P2 SD':>7} {'P3 mean':>8} {'P3 SD':>7}")
print("-"*62)
for cond in CONDITIONS:
    pd = phase_data[cond]
    lbl = LABELS[cond].replace("\n", " ")
    p1_sd = np.std(pd["p1_runs"], ddof=1)
    p2_sd = np.std(pd["p2_runs"], ddof=1)
    p3_sd = np.std(pd["p3_runs"], ddof=1)
    n = len(pd["p1_runs"])
    print(f"{lbl:<16} {n:>4} {pd['p1_mean']:>8.3f} {pd['p2_mean']:>8.3f} {p2_sd:>7.3f} {pd['p3_mean']:>8.3f} {p3_sd:>7.3f}")

print("\n--- Pairwise t-tests (Welch) ---")
pairs = [
    ("P2 F-only vs no_memory", phase_data["factual_memory"]["p2_runs"], nm_p2),
    ("P2 F+P vs F-only", phase_data["factual_pref"]["p2_runs"], phase_data["factual_memory"]["p2_runs"]),
    ("P2 F+EV vs F-only", phase_data["factual_eval"]["p2_runs"], phase_data["factual_memory"]["p2_runs"]),
    ("P2 F+P+EV vs F+P", phase_data["factual_pref_eval"]["p2_runs"], phase_data["factual_pref"]["p2_runs"]),
    ("P2 F+P+SPR vs F+P", phase_data["factual_pref_safety"]["p2_runs"], phase_data["factual_pref"]["p2_runs"]),
    ("P2 F+P+EV vs F+P+SPR", phase_data["factual_pref_eval"]["p2_runs"], phase_data["factual_pref_safety"]["p2_runs"]),
    ("P3 F-only vs no_memory", phase_data["factual_memory"]["p3_runs"], nm_p3),
    ("P3 F+P vs F-only", phase_data["factual_pref"]["p3_runs"], phase_data["factual_memory"]["p3_runs"]),
    ("P3 F+EV vs F-only", phase_data["factual_eval"]["p3_runs"], phase_data["factual_memory"]["p3_runs"]),
    ("P3 F+P+EV vs F+P", phase_data["factual_pref_eval"]["p3_runs"], phase_data["factual_pref"]["p3_runs"]),
    ("P3 F+P+SPR vs F+P", phase_data["factual_pref_safety"]["p3_runs"], phase_data["factual_pref"]["p3_runs"]),
    ("P3 F+P+EV vs F+P+SPR", phase_data["factual_pref_eval"]["p3_runs"], phase_data["factual_pref_safety"]["p3_runs"]),
]
for name, a, b in pairs:
    t, p = welch_t(a, b)
    diff = np.mean(a) - np.mean(b)
    stars = sig_stars(p)
    print(f"  {name:<30}: diff={diff:+.3f}, t={t:+.2f}, p≈{p:.4f} {stars}")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

fig.suptitle(
    "Memory Format Experiment: Effect of Memory Type on Enablement Drift\n"
    "(Factorized memory summaries, gpt-4o-mini, wedding scenario)",
    fontsize=13, fontweight="bold", y=0.98
)
fig.savefig(OUT_FIG, dpi=160, bbox_inches="tight")
print(f"\nFigure saved: {OUT_FIG}")
