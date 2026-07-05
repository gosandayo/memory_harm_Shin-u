#!/usr/bin/env python3
"""ANONYMIZED (double-blind submission) variant of plot_baseline_severity_2026_06_19.py.

IDENTICAL data + bars; ONLY the identifying label is anonymized for the submission:
  - y-axis "Jared bot-endorses-delusion >= 7"  ->  "external operative criterion"
  - output file -> docs/figures/baseline_severity_anon_2026_06_23.png  (NEW file)
The internal figure (baseline_severity_jared_2026_06_19.png) and its script are KEPT as-is.
See docs/jared_anonymization_policy_2026_06_23.md. Run from manual_redteam/.
"""
import json
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "data/blindpass/2026-06-18_fixedprobe_baseline"
MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-5.4-mini"]

key = json.loads((FP / "SEALED_key.json").read_text())
jr = {r["blind_id"]: r for r in json.loads((FP / "jared_scores.json").read_text())}
cell = defaultdict(lambda: [0, 0])
for bid, meta in key.items():
    c = meta["condition"].replace("_fixed", "")
    cell[(meta["model"], c)][0] += int(bool(jr[bid]["present"]))
    cell[(meta["model"], c)][1] += 1

pb = json.loads((REPO / "data/blindpass/AGG_psychosis_caselevel.json").read_text())["by_model"]
for m, a in pb.items():
    cell[(m, "psychosisbench")] = [a["break_cases"], a["n_cases"]]

CONDS = ["cold", "naive", "psychosisbench", "ladder"]
LABELS = {"cold": "cold\n(single-shot)", "naive": "naive\n(ungated)",
          "psychosisbench": "PsychosisBench\n(fixed script)", "ladder": "gated ladder\n(adaptive)"}
COLORS = {"cold": "#bdbdbd", "naive": "#6baed6", "psychosisbench": "#fdae6b", "ladder": "#d62728"}

fig, ax = plt.subplots(figsize=(10, 5))
W = 0.2
for ci, c in enumerate(CONDS):
    xs, ys, ann = [], [], []
    for mi, m in enumerate(MODELS):
        b, n = cell.get((m, c), [None, 0])
        xs.append(mi + (ci - 1.5) * W)
        ys.append((b / n) if n else 0)
        ann.append(f"{b}/{n}" if n else "n/a")
    ax.bar(xs, ys, W, label=LABELS[c], color=COLORS[c], edgecolor="black", linewidth=0.5)
    for x, y, a, (b, n) in zip(xs, ys, ann, [cell.get((m, c), [None, 0]) for m in MODELS]):
        ax.text(x, y + 0.02, a, ha="center", va="bottom", fontsize=8,
                color="black" if n else "#999999")

ax.set_xticks(range(len(MODELS)))
ax.set_xticklabels(MODELS)
# ANONYMIZED label (was "Jared bot-endorses-delusion >= 7")
ax.set_ylabel("hard-endorsement rate\n(external operative criterion)")
ax.set_ylim(0, 1.08)
ax.legend(ncol=4, fontsize=8, loc="upper right", frameon=False)
ax.set_title("Only adaptive gated context drives models to HARD operative endorsement\n"
             "static contexts — single-shot, ungated chat, and a published fixed-script "
             "benchmark — stay near zero on the same metric", fontsize=10)
fig.text(0.5, -0.02,
         "Severity axis: PsychosisBench's own metric is graded DCS (paper mean 0.91/5, soft "
         "confirmation); 0/16 here = fixed scripts rarely cross a HARD threshold, consistent with "
         "(not contradicting) its low DCS.  cold/naive/ladder n=5 trajectories; PsychosisBench "
         "n=16 cases (case-level); gpt-5.4-mini PsychosisBench not run.",
         ha="center", fontsize=7, wrap=True)
out = REPO / "docs/figures/baseline_severity_anon_2026_06_23.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"wrote {out}")
for m in MODELS:
    row = " ".join(f"{c}={cell.get((m,c),['-',0])[0]}/{cell.get((m,c),['-',0])[1]}" for c in CONDS)
    print(f"  {m:14} {row}")
