"""Plot area-weighted observed layers on the official enclosed-flow walls."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from verify import ROOT, TARGETS, boundary, face_area, field_values, poly_list


def main() -> None:
    report = json.loads((ROOT / "report/mesh_report.json").read_text())
    points = np.asarray(poly_list(ROOT / "points", "points"), dtype=float)
    faces = poly_list(ROOT / "faces", "faces")
    patches = boundary()
    names = list(TARGETS)
    labels = ["igloo\ntarget 1", "seal\ntarget 3", "herring\ntarget 3"]
    fractions = []
    for name in names:
        first, count = patches[name]
        values = field_values(name, count)
        areas = np.asarray([face_area(points, face) for face in faces[first:first + count]])
        fractions.append([100 * areas[values == n].sum() / areas.sum() for n in range(4)])
    frac = np.asarray(fractions)
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.9), layout="constrained")
    colors = ["#D55E00", "#E69F00", "#56B4E9", "#009E73"]
    bottom = np.zeros(len(names))
    for n in range(4):
        axes[0].bar(labels, frac[:, n], bottom=bottom, color=colors[n], label=f"{n} layers")
        bottom += frac[:, n]
    axes[0].set_title("Observed layers by wall area")
    axes[0].set_ylabel("Wall area [%]")
    axes[0].set_ylim(0, 100)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="lower center", bbox_to_anchor=(.5, -.1),
               frameon=False, ncol=4, fontsize=9)

    below = [100 * report["cfd"]["wall_checks"][name]["layer_distribution"]["under_target_area_fraction"]
             for name in names]
    bars = axes[1].bar(labels, below, color="#D55E00", width=.55)
    axes[1].bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)
    axes[1].set_ylim(0, 70)
    axes[1].set_title("Area below each wall's target")
    axes[1].set_ylabel("Wall area [%]")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.2)
    fig.savefig(ROOT / "actual_layers.png", dpi=180, bbox_inches="tight")
    fig.savefig(ROOT / "actual_layers.svg", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
