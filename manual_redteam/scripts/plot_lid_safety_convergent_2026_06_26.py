#!/usr/bin/env python3
"""Plot the LiD-safety convergent/discriminant-validity result.

Two rows of condition means on a common 0-1 scale (each axis normalized within its own range):
  Row 1 (endorsement/validation):  our e / 3        vs  LiD DCS  -> (DCS - 1) / 2   [1..3]
  Row 2 (safety/intervention):     our s / 4        vs  LiD SIS  ->  SIS            [0..1]
Columns = the three subject models. HES is omitted (N/A on 44/45 — no harm-enablement
content in a referential-delusion probe; it belongs on the suicide endpoint set).

Source: data/blindpass/2026-06-18_fixedprobe_baseline/LiD_safety_convergent_all.json
"""

import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "data/blindpass/2026-06-18_fixedprobe_baseline" / "LiD_safety_convergent_all.json"
OUT_BASE = REPO / "docs/figures/lid_safety_convergent_2026_06_26"

MODELS = [
    ("gpt-4o", "GPT-4o", "both axes move together with the break"),
    ("gpt-4o-mini", "GPT-4o-mini", "LiD axes saturate; ours keep resolving"),
    ("gpt-5.4-mini", "GPT-5.4-mini", "firewall: both agree it holds"),
]
CONDITIONS = [("cold_fixed", "Cold"), ("naive_fixed", "Naive"), ("ladder_fixed", "Ladder")]

TOKENS = {
    "surface": "#FCFCFD", "panel": "#FFFFFF", "ink": "#1F2430", "muted": "#6F768A",
    "grid": "#E6E8F0", "axis": "#D7DBE7",
    "blue_base": "#A3BEFA", "blue_dark": "#2E4780",      # our endorsement e
    "orange_base": "#F0986E", "orange_dark": "#804126",  # LiD DCS
    "green_base": "#86C99A", "green_dark": "#1F5B36",     # our safety s
    "red_base": "#E68A93", "red_dark": "#7A2630",         # LiD SIS
}


def load_cells():
    data = json.loads(SOURCE.read_text())
    by_cell = {(r["model"], r["condition"]): r for r in data["summary"]}
    expected = {(m, c) for m, _, _ in MODELS for c, _ in CONDITIONS}
    missing = expected - set(by_cell)
    if missing:
        raise ValueError(f"Missing model-condition cells: {sorted(missing)}")
    for key in expected:
        r = by_cell[key]
        if r["n"] != 5:
            raise ValueError(f"Expected n=5 for {key}, found {r['n']}")
        for f in ("mean_DCS", "mean_e", "SIS_rate", "mean_s"):
            if r[f] is None:
                raise ValueError(f"Missing {f} for {key}")
    conv = data["convergence_pearson"]
    return by_cell, conv


def style_axis(ax, col_index, row_index):
    ax.set_facecolor(TOKENS["panel"])
    ax.set_ylim(-0.05, 1.10)
    ax.set_xlim(-0.12, 2.12)
    ax.set_xticks(range(len(CONDITIONS)), [lab for _, lab in CONDITIONS])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.grid(axis="y", color=TOKENS["grid"], linewidth=0.8, linestyle=(0, (2, 3)))
    ax.grid(axis="x", visible=False)
    ax.tick_params(axis="both", colors=TOKENS["muted"], labelsize=9, length=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(TOKENS["axis"])
        ax.spines[side].set_linewidth(1.0)
    if col_index != 0:
        ax.tick_params(axis="y", labelleft=False)
    if row_index == 0:
        ax.tick_params(axis="x", labelbottom=False)


def label_pts(ax, xs, vals, color, offsets):
    for x, y, off in zip(xs, vals, offsets):
        ax.annotate(f"{y:.2f}", (x, y), xytext=(0, off), textcoords="offset points",
                    ha="center", va="bottom" if off >= 0 else "top",
                    fontsize=7.5, color=color, fontfamily="DejaVu Sans Mono")


def plot_pair(ax, xs, ours, theirs, ours_c, ours_d, their_c, their_d, ours_marker, their_marker):
    ax.plot(xs, theirs, color=their_c, marker=their_marker, markersize=6.5,
            markeredgecolor=their_d, markeredgewidth=1.0, linestyle="--", linewidth=1.35, zorder=3)
    ax.plot(xs, ours, color=ours_c, marker=ours_marker, markersize=7,
            markeredgecolor=ours_d, markeredgewidth=1.0, linestyle="-", linewidth=1.35, zorder=4)
    # offset labels to avoid overlap: ours below, theirs above (flip when near a clamp)
    ot = [8 if v < 0.85 else -11 for v in theirs]
    oo = [-11 if v > 0.10 else 8 for v in ours]
    label_pts(ax, xs, theirs, their_d, ot)
    label_pts(ax, xs, ours, ours_d, oo)


def main():
    by_cell, conv = load_cells()
    xs = list(range(len(CONDITIONS)))
    r_dcs_e = conv["DCS_vs_e_same_dir"]["r"]
    r_sis_s = conv["SIS_vs_s_same_dir"]["r"]

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Aptos", "Inter", "Segoe UI", "DejaVu Sans", "Arial"],
        "figure.facecolor": TOKENS["surface"], "savefig.facecolor": TOKENS["surface"],
        "axes.labelcolor": TOKENS["ink"], "text.color": TOKENS["ink"],
    })

    fig, axes = plt.subplots(2, 3, figsize=(12.4, 7.2), sharex=True)
    fig.patch.set_facecolor(TOKENS["surface"])

    for col, (model, display, note) in enumerate(MODELS):
        # Row 0 — endorsement/validation
        ax0 = axes[0][col]
        e = [by_cell[(model, c)]["mean_e"] / 3 for c, _ in CONDITIONS]
        dcs = [(by_cell[(model, c)]["mean_DCS"] - 1) / 2 for c, _ in CONDITIONS]
        style_axis(ax0, col, 0)
        plot_pair(ax0, xs, e, dcs, TOKENS["blue_base"], TOKENS["blue_dark"],
                  TOKENS["orange_base"], TOKENS["orange_dark"], "o", "s")
        ax0.text(0.0, 1.12, display, transform=ax0.transAxes, ha="left", va="bottom",
                 fontsize=11, fontweight="semibold", color=TOKENS["ink"])
        ax0.text(0.0, 1.045, note, transform=ax0.transAxes, ha="left", va="bottom",
                 fontsize=8.5, color=TOKENS["muted"])

        # Row 1 — safety/intervention
        ax1 = axes[1][col]
        s = [by_cell[(model, c)]["mean_s"] / 4 for c, _ in CONDITIONS]
        sis = [by_cell[(model, c)]["SIS_rate"] for c, _ in CONDITIONS]
        style_axis(ax1, col, 1)
        plot_pair(ax1, xs, s, sis, TOKENS["green_base"], TOKENS["green_dark"],
                  TOKENS["red_base"], TOKENS["red_dark"], "o", "D")

    axes[0][0].set_ylabel("Endorsement / validation", color=TOKENS["ink"], fontsize=10)
    axes[1][0].set_ylabel("Safety / intervention", color=TOKENS["ink"], fontsize=10)

    legend_handles = [
        Line2D([0], [0], color=TOKENS["blue_base"], marker="o", markeredgecolor=TOKENS["blue_dark"],
               linewidth=1.35, label="Our endorsement (e / 3)"),
        Line2D([0], [0], color=TOKENS["orange_base"], marker="s", markeredgecolor=TOKENS["orange_dark"],
               linestyle="--", linewidth=1.35, label=f"LiD DCS, norm.  (r={r_dcs_e:+.2f} vs e)"),
        Line2D([0], [0], color=TOKENS["green_base"], marker="o", markeredgecolor=TOKENS["green_dark"],
               linewidth=1.35, label="Our safety (s / 4)"),
        Line2D([0], [0], color=TOKENS["red_base"], marker="D", markeredgecolor=TOKENS["red_dark"],
               linestyle="--", linewidth=1.35, label=f"LiD SIS  (r={r_sis_s:+.2f} vs s)"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.53, 0.005),
               frameon=False, ncol=4, fontsize=9, handlelength=2.4, columnspacing=1.8)

    title = "An independent group's safety rubric tracks both our axes — and saturates where ours still resolve"
    subtitle = (
        "LiD (Aquilina et al., 2606.00975) DCS/SIS judge on our 45 blinded endpoints; condition means "
        "normalized within each axis's range (n=5/pt); convergence = row-level Pearson, n=45. "
        "Exploratory o4-mini judge (not LiD's); HES omitted (N/A 44/45 — no harm-enablement content here)."
    )
    fig.text(0.065, 0.985, title, ha="left", va="top", fontsize=14.5, fontweight="semibold")
    fig.text(0.065, 0.94, textwrap.fill(subtitle, width=132), ha="left", va="top",
             fontsize=8.6, color=TOKENS["muted"])
    fig.text(0.065, 0.072,
             "Source: LiD_safety_convergent_all.json · LiD prompt vendored verbatim (sha b8872f6a…) · "
             "cold → naive → ladder is an ordered context comparison, not time.",
             ha="left", va="top", fontsize=8, color=TOKENS["muted"])

    fig.subplots_adjust(left=0.065, right=0.985, top=0.80, bottom=0.135, hspace=0.18, wspace=0.14)
    OUT_BASE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight")
    fig.savefig(OUT_BASE.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_BASE.with_suffix('.png')}")
    print(f"wrote {OUT_BASE.with_suffix('.svg')}")


if __name__ == "__main__":
    main()
