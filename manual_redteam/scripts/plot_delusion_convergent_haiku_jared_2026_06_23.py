#!/usr/bin/env python3
"""
plot_delusion_convergent_haiku_jared_2026_06_23.py

Combined CONVERGENT-VALIDITY figure (gpt-4o, delusion per-rung): OUR scorer
(pinned Haiku endorsement = judge-of-record, CURRENT.md s1b) AND an anonymized
external operative criterion both SEPARATE the endorsement-gated climb from
verbatim-cold, sharing one origin.

Rapport(start) is a PRE-CLAIM STRUCTURAL BASELINE, NOT a measured point: at the
rapport stage no operative/epistemic claim has been posed, so endorsement of the
delusional claim = 0 BY CONSTRUCTION. The per-rung blind set contains NO rapport
items (rungs = D1/D2/D3/D9/D12 only); the Rapport point is therefore drawn as a
HOLLOW gray marker and labelled "0 by construction" so it is never mistaken for a
measurement. (Both arms share it -> the climb/cold separation reads from a common
origin, which is the only reason it is shown.)

Anonymization (BINDING -- docs/jared_anonymization_policy_2026_06_23.md): the
external operative-delusion rubric is from a manuscript under double-blind review.
It is labelled ONLY "External operative criterion"; no author / "DelusionEval" /
code-name / repo appears in any title, axis, legend, or the output filename.

PURE RENDERING: re-aggregates already-scored committed data into per-(condition,rung)
means and draws them. No LLM, no new API call, no thresholding beyond the e=2 / cutoff-7
guide lines.

IN  data/blindpass/2026-06-16_perrung/{SEALED_key,haiku_scores}.json   (our Haiku, judge of record)
    data/blindpass/2026-06-16_jared_perrung.json                       (external 0-10, anonymized here)
OUT docs/figures/aims/convergent_gpt4o_ours_vs_external_2026_06_23.png
"""
from __future__ import annotations
import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
BP = ROOT / "data" / "blindpass" / "2026-06-16_perrung"
EXT = ROOT / "data" / "blindpass" / "2026-06-16_jared_perrung.json"
FIG = ROOT / "docs" / "figures" / "aims"
FIG.mkdir(parents=True, exist_ok=True)

MODEL = "gpt-4o"
RUNGS = ["RAP", "D1", "D2", "D3", "D9", "D12"]          # DATA KEYS (canonical sparse codes, index the blind set's rung field) -- DO NOT CHANGE
# DISPLAY labels remap the two deep rungs to a CONTIGUOUS D1-D5 scheme for the paper
# (Method table uses D1..D5): Weighing D9->D4, Conclusion D12->D5. Data keys above stay sparse.
NAMES = {"RAP": "Rapport\n(start)", "D1": "Legitimacy\n(D1)", "D2": "Externalization\n(D2)",
         "D3": "Personalization\n(D3)", "D9": "Weighing\n(D4)", "D12": "Conclusion\n(D5)"}
NAN = float("nan")

# ---- OUR endorsement (pinned Haiku, judge of record) ----
key = json.loads((BP / "SEALED_key.json").read_text())
hs = json.loads((BP / "haiku_scores.json").read_text())
hs = {r["blind_id"]: r for r in hs} if isinstance(hs, list) else hs
ours = defaultdict(list)
for bid, k in key.items():
    if k["model"] != MODEL:
        continue
    ph = k["condition"].split("_")[0]                  # climb / cold
    ours[(ph, k["rung"])].append(int(hs[bid]["endorsement"]))

# ---- EXTERNAL operative criterion (anonymized), 0-10 mean ----
ext = json.loads(EXT.read_text())
extc = defaultdict(list)
for r in ext:
    if r["model"] != MODEL:
        continue
    extc[(r["condition"], r["rung"])].append(float(r["score"]))


def mean_or_nan(d, ph, rg):
    v = d.get((ph, rg))
    return statistics.mean(v) if v else NAN


def series(d, ph):
    return [0.0 if rg == "RAP" else mean_or_nan(d, ph, rg) for rg in RUNGS]


def draw(ax, climb, cold, hl, hllab, ylab, title, ymax):
    x = list(range(len(RUNGS)))
    ax.axvspan(2.5, len(RUNGS) - 0.5, color="0.92", zorder=0)        # Personalization -> Conclusion
    ax.plot(x, climb, color="#d62728", lw=1.8, zorder=2)
    ax.plot(x, cold, color="#1f6f8b", lw=1.8, zorder=2)
    ax.plot(x[1:], climb[1:], "o", color="#d62728", label="adaptive climb", zorder=3)
    ax.plot(x[1:], cold[1:], "s", mfc="white", mec="#1f6f8b", mew=1.5, label="verbatim cold", zorder=3)
    ax.plot(0, 0, "o", ms=8, mfc="white", mec="gray", mew=1.3, zorder=3)   # constructed anchor (explained in caption)
    ax.axhline(hl, ls="--", lw=0.8, color="gray")
    ax.text(len(RUNGS) - 1, hl, " " + hllab, fontsize=7, color="gray", va="bottom", ha="right")
    ax.set_xticks(x)
    ax.set_xticklabels([NAMES[r] for r in RUNGS], fontsize=7.5)
    ax.set_ylim(-0.1, ymax)
    ax.set_ylabel(ylab)
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8, loc="upper left")


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
draw(a1, series(ours, "climb"), series(ours, "cold"), 2, "e=2",
     "endorsement of claim (0-3)", "Our scorer (pinned Haiku)", 3.2)
draw(a2, series(extc, "climb"), series(extc, "cold"), 7, "cutoff 7",
     "External operative criterion (0-10)", "External operative criterion", 10.4)
# No in-figure title/annotations: all interpretation lives in the LaTeX \caption{}.
fig.tight_layout()
out = FIG / "convergent_gpt4o_ours_vs_external_2026_06_23.png"
fig.savefig(out, dpi=150)
plt.close(fig)
print("wrote", out.relative_to(ROOT))

# ---- sanity dump (the numbers behind every plotted point) ----
print("\ngpt-4o per-(condition,rung) means [RAP is constructed 0]:")
for ph in ("climb", "cold"):
    oe = [None if v != v else round(v, 2) for v in series(ours, ph)]
    es = [None if v != v else round(v, 2) for v in series(extc, ph)]
    print(f"  {ph:5} our_e(0-3): {oe}")
    print(f"  {ph:5} ext (0-10): {es}")
