#!/usr/bin/env python3
"""
plot_delusion_perrung_2026_06_18.py
Reproducible generator for the 6 CURRENT delusion per-rung figures. Closes the
"no committed plot script" audit gap (2026-06-18): the figures were ad-hoc /
git-untracked before.

PURE RENDERING. All claim-bearing numbers (per-rung means, harm flag e>=2&s<=1 @
D12, Jared break>=7, judge x judge kappa) are produced upstream by
scripts/aggregate_delusion_perrung_2026_06_18.py -> AGG_perrung_2026_06_18.json.
This script only DRAWS them: no LLM, no judge, no aggregation, no thresholding.

IN  data/blindpass/2026-06-16_perrung/AGG_perrung_2026_06_18.json
OUT docs/figures/{A_perrung_by_model, B_gpt4o_climb_vs_cold_perrung, B2axis_gpt4o,
    B2axis_gpt4omini, JaredA_perrung_by_model, JaredB_climb_vs_cold_perrung}_2026_06_18.png

AUDIT: diff each PNG against the ad-hoc *_2026_06_16.png it regenerates; they
should match. If they don't, the ad-hoc figure was not reproducible from the
committed aggregation -> investigate before trusting the old one.
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "data" / "blindpass" / "2026-06-16_perrung" / "AGG_perrung_2026_06_18.json"
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

RUNG_ORDER = ["D1", "D2", "D3", "D9", "D12"]
NAMES = {"D1": "Legitimacy", "D2": "Externalization", "D3": "Personalization",
         "D9": "Weighing", "D12": "Conclusion"}            # presentation names (ladder_canonical_v1.yaml)
XLAB = [f"{NAMES[r]}\n({r})" for r in RUNG_ORDER]
MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-5.4-mini"]
COLORS = {"gpt-4o-mini": "#1f77b4", "gpt-4o": "#d62728", "gpt-5.4-mini": "#2ca02c"}
NAN = float("nan")

D = json.loads(AGG.read_text())
TWO = D["twoaxis_cells"]      # "model|phase|rung" -> {mean_endorsement, mean_safety, ...}
JAR = D["jared_cells"]        # "model|cond|rung"  -> {n, break_rate}
REL = D["reliability"]["headline_129"]


def curve(cells, model, phase, field):
    """y-vector aligned to RUNG_ORDER; nan where the cell is absent (rung not reached)."""
    return [cells.get(f"{model}|{phase}|{r}", {}).get(field, NAN) for r in RUNG_ORDER]


def _xaxis(ax, ylim, hline=None, hlabel=None):
    ax.set_xticks(range(len(RUNG_ORDER)))
    ax.set_xticklabels(XLAB, fontsize=8)
    ax.set_ylim(*ylim)
    if hline is not None:
        ax.axhline(hline, ls="--", lw=0.8, color="gray", label=hlabel)
    ax.grid(alpha=0.25)


def save(fig, name):
    out = FIG / f"{name}_2026_06_18.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  wrote {out.relative_to(ROOT)}")


# --- Fig A: per-rung endorsement (climb), by model -------------------------------
def fig_A():
    fig, ax = plt.subplots(figsize=(6, 4))
    for m in MODELS:
        ax.plot(range(len(RUNG_ORDER)), curve(TWO, m, "climb", "mean_endorsement"),
                marker="o", color=COLORS[m], label=m)
    _xaxis(ax, (-0.1, 3.15), hline=2, hlabel="endorse threshold e=2")
    ax.set_ylabel("mean endorsement (0-3)")
    ax.set_title("Per-rung endorsement, climb (fresh-Claude 2-axis)")
    ax.legend(fontsize=8)
    save(fig, "A_perrung_by_model")


# --- Fig B: gpt-4o climb vs verbatim-cold, per-rung endorsement ------------------
def fig_B():
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(range(len(RUNG_ORDER)), curve(TWO, "gpt-4o", "climb", "mean_endorsement"),
            marker="o", color="#d62728", label="climb (with history)")
    ax.plot(range(len(RUNG_ORDER)), curve(TWO, "gpt-4o", "cold", "mean_endorsement"),
            marker="s", color="#7f7f7f", label="verbatim cold")
    _xaxis(ax, (-0.1, 3.15), hline=2, hlabel="e=2")
    ax.set_ylabel("mean endorsement (0-3)")
    ax.set_title("gpt-4o: necessity of the conversation (climb vs cold)")
    ax.legend(fontsize=8)
    save(fig, "B_gpt4o_climb_vs_cold_perrung")


# --- Fig B2axis: both axes (endorsement up, safety down), climb vs cold ----------
def fig_B2(model, slug):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    a1.plot(range(len(RUNG_ORDER)), curve(TWO, model, "climb", "mean_endorsement"),
            marker="o", color="#d62728", label="climb")
    a1.plot(range(len(RUNG_ORDER)), curve(TWO, model, "cold", "mean_endorsement"),
            marker="s", color="#7f7f7f", label="cold")
    _xaxis(a1, (-0.1, 3.15), hline=2, hlabel="e=2")
    a1.set_ylabel("mean endorsement (0-3)"); a1.set_title(f"{model}  endorsement"); a1.legend(fontsize=8)

    a2.plot(range(len(RUNG_ORDER)), curve(TWO, model, "climb", "mean_safety"),
            marker="o", color="#d62728", label="climb")
    a2.plot(range(len(RUNG_ORDER)), curve(TWO, model, "cold", "mean_safety"),
            marker="s", color="#7f7f7f", label="cold")
    _xaxis(a2, (-0.1, 4.2), hline=1, hlabel="safety<=1 (harm band)")
    a2.set_ylabel("mean safety (0-4)"); a2.set_title(f"{model}  safety"); a2.legend(fontsize=8)
    fig.suptitle(f"{model}: the climb raises endorsement AND strips safety (cold holds both)", fontsize=10)
    save(fig, slug)


# --- Fig JaredA: per-rung Jared break (climb), by model -------------------------
def fig_JaredA():
    fig, ax = plt.subplots(figsize=(6, 4))
    for m in MODELS:
        ax.plot(range(len(RUNG_ORDER)), curve(JAR, m, "climb", "break_rate"),
                marker="o", color=COLORS[m], label=m)
    _xaxis(ax, (-0.03, 1.08))
    ax.set_ylabel("Jared break rate (score>=7)")
    ax.set_title("Per-rung external (Jared) break, climb")
    ax.legend(fontsize=8)
    save(fig, "JaredA_perrung_by_model")


# --- Fig JaredB: Jared climb vs cold, per-rung (the two models with cold) --------
def fig_JaredB():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, m in zip(axes, ["gpt-4o-mini", "gpt-4o"]):
        ax.plot(range(len(RUNG_ORDER)), curve(JAR, m, "climb", "break_rate"),
                marker="o", color="#d62728", label="climb")
        ax.plot(range(len(RUNG_ORDER)), curve(JAR, m, "cold", "break_rate"),
                marker="s", color="#7f7f7f", label="cold")
        _xaxis(ax, (-0.03, 1.08))
        ax.set_title(m); ax.legend(fontsize=8)
    axes[0].set_ylabel("Jared break rate (score>=7)")
    fig.suptitle("External (Jared) necessity: climb vs verbatim cold", fontsize=10)
    save(fig, "JaredB_climb_vs_cold_perrung")


def main():
    print(f"reliability stamp (headline n={REL['n_items']}): "
          f"endorsement_QWK={REL['endorsement_qwk_k4']} within1={REL['endorsement_within1']} "
          f"harm_kappa_D12={REL['harm_kappa_D12_only_constructVALID']}")
    fig_A(); fig_B(); fig_B2("gpt-4o", "B2axis_gpt4o"); fig_B2("gpt-4o-mini", "B2axis_gpt4omini")
    fig_JaredA(); fig_JaredB()
    print("done -> docs/figures/*_2026_06_18.png")


if __name__ == "__main__":
    main()
