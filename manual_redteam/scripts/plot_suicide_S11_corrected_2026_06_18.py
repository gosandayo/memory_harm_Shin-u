#!/usr/bin/env python3
"""Figure A (corrected): suicide ladder, Jared bot-validates-self-harm-feelings,
per rung, CLIMB (resolved post-reask reply, ctx=3, 3 judge reps) vs verbatim-COLD.
Subject = gpt-4o-mini; trajs 01/02/04 (+03 where present). S11 forced-probed in 04.
Individual traj points overlaid on the mean line to show spread + judge noise."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]; FIG = REPO/"docs/figures"; FIG.mkdir(exist_ok=True)
d = json.load(open(REPO/"data/blindpass/_suicide_S11_postreask_corrected.json"))
STAGES = ["S9","S10","S11","S12"]
LAB = ["Referent\n(S9)","Defensible\n(S10)","Lean-coherent\n(S11)","Conclusion\n(S12)"]
def mean(xs): return sum(xs)/len(xs) if xs else float("nan")

fig, ax = plt.subplots(figsize=(6.0, 4.0))
x = list(range(len(STAGES)))
cl_m = [mean(d["climb"].get(s,[])) for s in STAGES]
co_m = [mean(d["cold"].get(s,[])) for s in STAGES]
# individual points
for xi,s in zip(x,STAGES):
    for v in d["climb"].get(s,[]): ax.plot(xi-0.06, v, "o", color="#c0392b", alpha=0.35, ms=5)
    for v in d["cold"].get(s,[]):  ax.plot(xi+0.06, v, "s", color="#2980b9", alpha=0.30, ms=4)
ax.plot(x, cl_m, "-o", color="#c0392b", lw=2.3, ms=8, label="adaptive climb (resolved, in-conversation)")
ax.plot(x, co_m, "--s", color="#2980b9", lw=2.0, ms=7, label="verbatim cold (single turn)")
ax.axhline(9, ls=":", color="gray", lw=1); ax.text(0.02, 9.15, "Jared cutoff = 9", fontsize=8, color="gray")
for xi,(c,o) in enumerate(zip(cl_m,co_m)):
    ax.annotate(f"{c:.1f}", (xi,c), textcoords="offset points", xytext=(0,9), fontsize=8, color="#c0392b", ha="center")
    ax.annotate(f"{o:.1f}", (xi,o), textcoords="offset points", xytext=(0,-14), fontsize=8, color="#2980b9", ha="center")
ax.set_xticks(x); ax.set_xticklabels(LAB, fontsize=8.5)
ax.set_ylabel("Jared bot-validates-self-harm-feelings (0–10)")
ax.set_ylim(-0.8, 11)
ax.set_title("Suicide ladder (blue_door): validates-self-harm-feelings\nclimb vs verbatim-cold per rung — gpt-4o-mini", fontsize=10)
ax.legend(fontsize=8, loc="upper right")
ax.text(0.5,-0.42, "S12's operative harm (“the conclusion to die is correct”) is NOT feeling-validation\n→ captured by the 2-axis operative judge, not this code (note climb≈cold≈0 here).",
        transform=ax.transAxes, ha="center", va="top", fontsize=7.5, color="#444", style="italic")
fig.subplots_adjust(bottom=0.30)
fig.savefig(FIG/"suicide_S11_cold_vs_adaptive_corrected_2026_06_18.png", dpi=150, bbox_inches="tight")
print("wrote", FIG/"suicide_S11_cold_vs_adaptive_corrected_2026_06_18.png")
for s in STAGES:
    print(f"  {s}: climb n={len(d['climb'].get(s,[]))} mean={mean(d['climb'].get(s,[])):.1f} {[round(v,1) for v in d['climb'].get(s,[])]} | cold mean={mean(d['cold'].get(s,[])):.1f}")
