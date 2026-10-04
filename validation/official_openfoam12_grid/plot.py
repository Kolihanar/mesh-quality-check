"""Plot the measured OpenFOAM three-grid target history and Skill diagnostics."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
METRIC = "kinematic_pressure_difference_m2_s2"
GRADES = ("coarse", "medium", "fine")
COLORS = {"coarse": "#0072B2", "medium": "#E69F00", "fine": "#009E73"}


def rows(path: Path) -> list[tuple[int, float]]:
    return [
        (int(float(time)), float(value))
        for line in path.read_text().splitlines()
        if line and not line.startswith("#")
        for time, value in [line.split()]
    ]


def main() -> None:
    evidence = json.loads((ROOT / "evidence.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.0), layout="constrained")
    for grade in GRADES:
        inlet = rows(ROOT / f"{grade}.inletPressure.dat")
        outlet = rows(ROOT / f"{grade}.outletPressure.dat")
        history = [a - b for (_, a), (_, b) in zip(inlet, outlet)]
        span = max(2, len(history) // 5)
        x = list(range(-span + 1, 1))
        axes[0].plot(x, history[-span:], color=COLORS[grade], lw=1.7, label=grade)
        axes[0].scatter([0], [history[-1]], color=COLORS[grade], s=25, zorder=3)
    axes[0].set_title("Target history: final 20% of iterations")
    axes[0].set_xlabel("Iterations before solver stop")
    axes[0].set_ylabel(r"$\bar p_{in}-\bar p_{out}$  [m$^2$/s$^2$]")
    axes[0].legend(frameon=False, fontsize=8)

    counts = [evidence["grids"][grade]["n_cells"] for grade in GRADES]
    values = [evidence["grids"][grade][METRIC] for grade in GRADES]
    axes[1].plot(counts, values, color="#444444", lw=1.2, ls="--")
    for grade, n, value in zip(GRADES, counts, values):
        axes[1].scatter([n], [value], color=COLORS[grade], s=52, zorder=3)
        axes[1].annotate(f"{grade}\n{value:.3f}", (n, value), xytext=(0, 8),
                         textcoords="offset points", ha="center", fontsize=8)
    axes[1].set_title("Final target vs. cell count (provisional)")
    axes[1].set_xlabel("Number of cells")
    axes[1].set_ylabel(r"$\bar p_{in}-\bar p_{out}$  [m$^2$/s$^2$]")
    axes[1].set_xticks(counts, [f"{n:,}" for n in counts], rotation=20)
    axes[1].margins(y=.25)

    drifts = [100 * evidence["monitor_last_two_window_relative_drift"][f"{METRIC}_{grade}"]
              for grade in GRADES]
    bars = axes[2].bar(GRADES, drifts, color=[COLORS[grade] for grade in GRADES], width=.58)
    axes[2].axhline(.5, color="#A33A32", ls="--", lw=1.2, label="0.5% screening tolerance")
    axes[2].bar_label(bars, fmt="%.2f%%", padding=3, fontsize=8)
    axes[2].set_ylim(0, max(drifts) * 1.28)
    axes[2].set_title("Last-window target drift")
    axes[2].set_ylabel("Relative drift [%]")
    axes[2].legend(frameon=False, fontsize=8)

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.2)
    fig.savefig(ROOT / "three_grid_evidence.png", dpi=180, bbox_inches="tight")
    fig.savefig(ROOT / "three_grid_evidence.svg", bbox_inches="tight")
    plt.close(fig)

    extended = json.loads((ROOT / "extended_evidence.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.0), layout="constrained")
    for grade in GRADES:
        start = extended["grids"][grade]["start_iteration"]
        inlet = rows(ROOT / f"{grade}.inletPressure.{start}.dat")
        outlet = rows(ROOT / f"{grade}.outletPressure.{start}.dat")
        x = [time for time, _ in inlet][-200:]
        y = [a - b for (_, a), (_, b) in zip(inlet, outlet)][-200:]
        axes[0].plot(x, y, color=COLORS[grade], lw=1.5, label=grade)
    axes[0].set_title("Strict-stop trial: iterations 801–1000")
    axes[0].set_xlabel("Pseudo-iteration")
    axes[0].set_ylabel(r"$\bar p_{in}-\bar p_{out}$  [m$^2$/s$^2$]")
    axes[0].legend(frameon=False, fontsize=8, loc="upper right", bbox_to_anchor=(.98, .82))

    spans = [100 * extended["grids"][grade]["last_20_percent_window_relative_p05_p95_span"]
             for grade in GRADES]
    bars = axes[1].bar(GRADES, spans, color=[COLORS[grade] for grade in GRADES], width=.58)
    axes[1].axhline(1.0, color="#A33A32", ls="--", lw=1.2, label="1% screening tolerance")
    axes[1].bar_label(bars, fmt="%.3f%%", padding=3, fontsize=8)
    axes[1].set_ylim(0, max(spans) * 1.3)
    axes[1].set_title("Final-window P05–P95 span")
    axes[1].set_ylabel("Relative span [%]")
    axes[1].legend(frameon=False, fontsize=8)

    final_values = [extended["grids"][grade]["target_at_end_m2_s2"] for grade in GRADES]
    axes[2].plot(counts, final_values, color="#444444", lw=1.2, ls="--")
    for grade, n, value in zip(GRADES, counts, final_values):
        axes[2].scatter([n], [value], color=COLORS[grade], s=52, zorder=3)
        axes[2].annotate(f"{grade}\n{value:.3f}", (n, value), xytext=(0, 8),
                         textcoords="offset points", ha="center", fontsize=8)
    axes[2].set_title("Target at step 1000 (provisional)")
    axes[2].set_xlabel("Number of cells")
    axes[2].set_ylabel(r"$\bar p_{in}-\bar p_{out}$  [m$^2$/s$^2$]")
    axes[2].set_xticks(counts, [f"{n:,}" for n in counts], rotation=20)
    axes[2].margins(y=.25)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.2)
    fig.savefig(ROOT / "extended_three_grid_evidence.png", dpi=180, bbox_inches="tight")
    fig.savefig(ROOT / "extended_three_grid_evidence.svg", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
