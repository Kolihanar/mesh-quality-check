"""Plot an independently checked native-output versus Skill comparison."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
WALLS = ("upperWall", "lowerWall")


def native_yplus(log: str, wall: str) -> tuple[float, float]:
    match = re.search(
        rf"patch {re.escape(wall)} y\+ : min = ([\d.eE+-]+), max = ([\d.eE+-]+)",
        log,
    )
    assert match is not None, wall
    return float(match.group(1)), float(match.group(2))


def native_field_values(field: str, wall: str) -> np.ndarray:
    match = re.search(
        rf"\b{re.escape(wall)}\s*\{{[^{{}}]*?value\s+nonuniform\s+"
        rf"List<scalar>\s+(\d+)\s*\(([^)]*)\)",
        field,
        re.DOTALL,
    )
    assert match is not None, wall
    values = np.fromstring(match.group(2), sep=" ")
    assert len(values) == int(match.group(1)), wall
    return values


def main() -> None:
    report = json.loads((ROOT / "postflight/mesh_report.json").read_text(encoding="utf-8"))
    context = json.loads((ROOT / "postflight_context.json").read_text(encoding="utf-8"))
    target = tuple(context["wall_defaults"]["target_yplus"])
    flow = json.loads((ROOT / "flow_evidence.json").read_text(encoding="utf-8-sig"))
    log = (ROOT / "log.yPlus.solver").read_text(encoding="utf-8")
    field = (ROOT / "yPlus.286").read_text(encoding="utf-8")
    assert flow["source"] == "phi.286"
    assert report["cfd"]["solution_checks"]["mass_balance"]["basis"] == "volumetric_flux_m3_s"

    labels, native_extrema, skill_extrema = [], [], []
    outside = {}
    for wall in WALLS:
        low, high = native_yplus(log, wall)
        check = report["cfd"]["wall_checks"][wall]["yplus"]
        values = native_field_values(field, wall)
        count = int(np.count_nonzero((values < target[0]) | (values > target[1])))
        assert count == check["n_outside"] and len(values) == check["n_valid"]
        assert report["cfd"]["wall_checks"][wall]["target_source"] == "explicit"
        for name, native, skill in (("min", low, check["min"]), ("max", high, check["max"])):
            assert math.isclose(native, skill, rel_tol=1e-6, abs_tol=1e-8)
            labels.append(f"{wall}\n{name}")
            native_extrema.append(native)
            skill_extrema.append(skill)
        outside[wall] = (count, len(values))

    native_balance = 100 * flow["relative_imbalance"]
    skill_balance = 100 * report["cfd"]["solution_checks"]["mass_balance"]["relative_imbalance"]
    assert math.isclose(native_balance, skill_balance, rel_tol=1e-9)

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), width_ratios=(1.75, 1, 1))
    fig.suptitle("OpenFOAM 12 pitzDailySteady: native output vs Skill", fontsize=15, weight="bold")

    x = np.arange(len(labels))
    width = 0.37
    axes[0].bar(x - width / 2, native_extrema, width, color="#0072B2", label="OpenFOAM native")
    axes[0].bar(x + width / 2, skill_extrema, width, color="#D55E00", label="Skill report")
    axes[0].set_xticks(x, labels)
    axes[0].set_ylim(0, 31)
    axes[0].set_ylabel("Actual wall y+")
    axes[0].set_title("y+ extrema match")
    axes[0].legend(loc="upper left", frameon=False, fontsize=9)
    axes[0].grid(axis="y", alpha=0.2)

    y = np.arange(len(WALLS))
    axes[1].barh(y, [100 * outside[w][0] / outside[w][1] for w in WALLS], color="#009E73")
    axes[1].set_yticks(y, WALLS)
    axes[1].invert_yaxis()
    axes[1].set_xlim(0, 125)
    axes[1].set_xlabel("Wall faces outside target [%]")
    axes[1].set_title(f"Explicit target: {target[0]}-{target[1]}")
    for i, wall in enumerate(WALLS):
        bad, total = outside[wall]
        axes[1].text(102, i, f"{bad}/{total}", va="center", fontsize=10)
    axes[1].grid(axis="x", alpha=0.2)

    axes[2].bar(["Native phi", "Skill"], [native_balance, skill_balance], color=["#0072B2", "#D55E00"])
    axes[2].set_ylim(0, 0.0038)
    axes[2].set_ylabel("Relative volume imbalance [%]")
    axes[2].set_title("Flow balance matches")
    for i, value in enumerate((native_balance, skill_balance)):
        axes[2].text(i, value + 0.00007, f"{value:.7f}%", ha="center", fontsize=9)
    axes[2].grid(axis="y", alpha=0.2)

    fig.text(
        0.5, 0.01,
        "Saved solver fields and native flow tables; the y+ interval is a user-specified screening target, not a universal solver limit.",
        ha="center", fontsize=9, color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.94), w_pad=2.5)
    for ext in ("png", "svg"):
        fig.savefig(ROOT / f"native_vs_skill.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("Native/Skill comparison plot: passed (yPlus extrema, target counts, volume balance)")


if __name__ == "__main__":
    main()
