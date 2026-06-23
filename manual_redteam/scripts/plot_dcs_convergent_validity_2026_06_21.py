#!/usr/bin/env python3
"""Plot the exploratory DCS-vs-endorsement convergent-validity smoke result.

The figure compares condition means on a common 0-1 scale:
  - PsychosisBench-style DCS: mean_DCS / 2
  - our endorsement axis: mean_e / 3

Source: data/blindpass/2026-06-18_fixedprobe_baseline/
        DCS_convergent_smoke_all.json
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
SOURCE = (
    REPO
    / "data/blindpass/2026-06-18_fixedprobe_baseline"
    / "DCS_convergent_smoke_all.json"
)
OUT_BASE = REPO / "docs/figures/dcs_convergent_validity_2026_06_21"

MODELS = [
    ("gpt-4o", "GPT-4o", "headroom: both detect the ladder break"),
    ("gpt-4o-mini", "GPT-4o-mini", "DCS ceiling; endorsement retains gradient"),
    ("gpt-5.4-mini", "GPT-5.4-mini", "firewall: no DCS=2 and endorsement stays zero"),
]
CONDITIONS = [
    ("cold_fixed", "Cold"),
    ("naive_fixed", "Naive"),
    ("ladder_fixed", "Ladder"),
]

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
    "blue_base": "#A3BEFA",
    "blue_dark": "#2E4780",
    "orange_base": "#F0986E",
    "orange_dark": "#804126",
}


def load_rows():
    data = json.loads(SOURCE.read_text())
    by_cell = {(row["model"], row["condition"]): row for row in data["summary"]}
    expected = {(m, c) for m, _, _ in MODELS for c, _ in CONDITIONS}
    missing = expected - set(by_cell)
    if missing:
        raise ValueError(f"Missing model-condition cells: {sorted(missing)}")
    for key in expected:
        row = by_cell[key]
        if row["n"] != 5:
            raise ValueError(f"Expected n=5 for {key}, found {row['n']}")
        if row["mean_DCS"] is None or row["mean_e"] is None:
            raise ValueError(f"Missing score for {key}")
    return by_cell


def style_axis(ax, panel_index):
    ax.set_facecolor(TOKENS["panel"])
    ax.set_ylim(-0.035, 1.08)
    ax.set_xlim(-0.12, 2.12)
    ax.set_xticks(range(len(CONDITIONS)), [label for _, label in CONDITIONS])
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
    if panel_index == 0:
        ax.set_ylabel("Normalized score", color=TOKENS["ink"], fontsize=10)
    else:
        ax.tick_params(axis="y", labelleft=False)


def add_value_labels(ax, xs, values, color, offsets):
    for x, y, offset in zip(xs, values, offsets):
        ax.annotate(
            f"{y:.2f}",
            (x, y),
            xytext=(0, offset),
            textcoords="offset points",
            ha="center",
            va="bottom" if offset >= 0 else "top",
            fontsize=8,
            color=color,
            fontfamily="DejaVu Sans Mono",
        )


def main():
    by_cell = load_rows()
    xs = list(range(len(CONDITIONS)))

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Aptos", "Inter", "Segoe UI", "DejaVu Sans", "Arial"],
            "figure.facecolor": TOKENS["surface"],
            "savefig.facecolor": TOKENS["surface"],
            "axes.labelcolor": TOKENS["ink"],
            "text.color": TOKENS["ink"],
        }
    )

    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.7), sharey=True)
    fig.patch.set_facecolor(TOKENS["surface"])

    for panel_index, (ax, (model, display, panel_note)) in enumerate(zip(axes, MODELS)):
        dcs = [by_cell[(model, condition)]["mean_DCS"] / 2 for condition, _ in CONDITIONS]
        endorsement = [by_cell[(model, condition)]["mean_e"] / 3 for condition, _ in CONDITIONS]

        style_axis(ax, panel_index)
        ax.plot(
            xs,
            dcs,
            color=TOKENS["orange_base"],
            marker="s",
            markersize=6.5,
            markeredgecolor=TOKENS["orange_dark"],
            markeredgewidth=1.0,
            linestyle="--",
            linewidth=1.35,
            zorder=3,
        )
        ax.plot(
            xs,
            endorsement,
            color=TOKENS["blue_base"],
            marker="o",
            markersize=7,
            markeredgecolor=TOKENS["blue_dark"],
            markeredgewidth=1.0,
            linestyle="-",
            linewidth=1.35,
            zorder=4,
        )

        # Keep labels readable where the two measures overlap.
        dcs_offsets = [8, 8, 8]
        e_offsets = [-10, -10, -10]
        e_offsets = [8 if value == 0 else offset for value, offset in zip(endorsement, e_offsets)]
        if model == "gpt-4o-mini":
            e_offsets[-1] = -12
        add_value_labels(ax, xs, dcs, TOKENS["orange_dark"], dcs_offsets)
        add_value_labels(ax, xs, endorsement, TOKENS["blue_dark"], e_offsets)

        ax.text(
            0.0,
            1.105,
            display,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=11,
            fontweight="semibold",
            color=TOKENS["ink"],
        )
        ax.text(
            0.0,
            1.045,
            panel_note,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8.5,
            color=TOKENS["muted"],
        )

    legend_handles = [
        Line2D(
            [0],
            [0],
            color=TOKENS["blue_base"],
            marker="o",
            markeredgecolor=TOKENS["blue_dark"],
            linewidth=1.35,
            label="Our endorsement axis (e / 3)",
        ),
        Line2D(
            [0],
            [0],
            color=TOKENS["orange_base"],
            marker="s",
            markeredgecolor=TOKENS["orange_dark"],
            linestyle="--",
            linewidth=1.35,
            label="PsychosisBench-style DCS (DCS / 2)",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(0.07, 0.845),
        frameon=False,
        ncol=2,
        fontsize=9,
        handlelength=2.5,
        columnspacing=2.2,
    )

    title = "DCS confirms the break/firewall contrast but saturates on the most susceptible model"
    subtitle = (
        "Condition means on a common 0–1 scale; n=5 blinded endpoints per point. "
        "Exploratory smoke: o4-mini DCS judge; e is the mean of two fresh-Claude judges."
    )
    fig.text(0.07, 0.965, title, ha="left", va="top", fontsize=15, fontweight="semibold")
    fig.text(
        0.07,
        0.915,
        textwrap.fill(subtitle, width=145),
        ha="left",
        va="top",
        fontsize=9,
        color=TOKENS["muted"],
    )
    fig.text(
        0.07,
        0.02,
        "Source: DCS_convergent_smoke_all.json · cold → naive → ladder is an ordered context comparison, not time.",
        ha="left",
        va="bottom",
        fontsize=8,
        color=TOKENS["muted"],
    )

    fig.subplots_adjust(left=0.07, right=0.985, top=0.68, bottom=0.15, wspace=0.16)
    OUT_BASE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight")
    fig.savefig(OUT_BASE.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_BASE.with_suffix('.png')}")
    print(f"wrote {OUT_BASE.with_suffix('.svg')}")


if __name__ == "__main__":
    main()
