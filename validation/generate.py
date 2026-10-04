"""Rebuild evidence-backed figures from this repository's regression fixtures.

Run with: python validation/generate.py
All CFD field values in Figures 2 and 3 are deliberately synthetic. The wall
geometry and area weights come from tests/samples/of_good_3d.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SCRIPT = ROOT / "scripts" / "mesh_check.py"
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))
from run_tests import CASES  # noqa: E402
from adapters import nearwall, polymesh  # noqa: E402

COLORS = {"ok": "#0072B2", "moderate": "#E69F00", "high": "#D55E00",
          "critical": "#6C4E9B", "unavailable": "#B8BEC5"}
ZH = {"ok": "正常", "moderate": "中等", "high": "高风险", "critical": "致命", "unavailable": "未运行"}
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
                     "axes.unicode_minus": False, "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.fonttype": "none"})


def run_case(case: Path, out: Path, *args: str) -> tuple[dict | None, str]:
    p = subprocess.run([sys.executable, str(SCRIPT), str(case), "-o", str(out), *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    report = out / "mesh_report.json"
    if not report.exists():
        return None, p.stderr
    return json.loads(report.read_text(encoding="utf-8")), p.stderr


def collect_regression(tmp: Path) -> list[dict]:
    rows = []
    for rel, source, expected, flagged in CASES:
        data, stderr = run_case(ROOT / "tests" / rel, tmp / rel.replace("/", "_"))
        if data is None:
            if "No module named 'meshio'" not in stderr and "No module named 'pyvista'" not in stderr:
                raise RuntimeError(f"{rel} produced no report: {stderr[-800:]}")
            rows.append({"case": rel, "source": source, "expected": expected,
                         "observed": None, "status": "unavailable", "reason": "meshio/pyvista 未安装"})
            continue
        observed = data["overall"]
        got = {f["metric"] for f in data["findings"] if f["severity"] != "ok"}
        match = data["detection"]["source"] == source and observed == expected and set(flagged) <= got
        rows.append({"case": rel, "source": source, "expected": expected,
                     "observed": observed, "status": "match" if match else "mismatch",
                     "required_findings": flagged, "observed_findings": sorted(got)})
    return rows


def field(path: Path, name: str, values: np.ndarray) -> None:
    text = (f"FoamFile {{ format ascii; class volScalarField; object {name}; }}\n"
            "internalField uniform 0;\n"
            f"boundaryField {{ walls {{ type fixedValue; value nonuniform List<scalar> {len(values)}\n(\n"
            + "\n".join(map(str, values)) + "\n); } }\n")
    path.write_text(text, encoding="ascii")


def one_finding(data: dict, metric: str) -> dict:
    items = [x for x in data["findings"] if x["metric"] == metric]
    if len(items) != 1:
        raise AssertionError(f"expected one {metric} finding, found {len(items)}")
    return items[0]


def collect_cfd(tmp: Path) -> tuple[dict, np.ndarray, np.ndarray]:
    case = ROOT / "tests" / "samples" / "of_good_3d"
    wall = nearwall.inspect(polymesh.analyse(str(case / "constant" / "polyMesh")))["walls"]
    centres = np.asarray(wall["face_centres"], dtype=float)
    area = np.asarray(wall["face_area"], dtype=float)
    n = len(area)
    if n != 432:
        raise AssertionError(f"demo fixture changed: {n} wall faces")
    context = {"flow": {"nu": 1e-6, "turbulence_model": "kOmegaSST"},
               "wall_defaults": {"treatment": "wall_resolved", "wall_conditions_verified": True,
                                 "target_yplus": [0, 2], "target_layers": 12,
                                 "min_layer_coverage": .9}}
    context_path = tmp / "context.json"
    context_path.write_text(json.dumps(context), encoding="utf-8")

    y_bad = np.r_[np.full(100, 100), np.ones(n - 100)]
    y_good = np.ones(n)
    zero_layers = np.r_[np.zeros(60, dtype=int), np.full(n - 60, 12)]
    shallow_layers = np.r_[np.full(60, 6), np.full(n - 60, 12)]
    y_bad_path, y_good_path = tmp / "yPlus_bad", tmp / "yPlus_good"
    zero_path, shallow_path = tmp / "nSurfaceLayers_zero", tmp / "nSurfaceLayers_shallow"
    field(y_bad_path, "yPlus", y_bad)
    field(y_good_path, "yPlus", y_good)
    field(zero_path, "nSurfaceLayers", zero_layers)
    field(shallow_path, "nSurfaceLayers", shallow_layers)

    y_report, err = run_case(case, tmp / "y_bad", "--context", str(context_path),
                             "--yplus-field", str(y_bad_path))
    if y_report is None:
        raise RuntimeError(err)
    zero_report, err = run_case(case, tmp / "layer_zero", "--context", str(context_path),
                                "--yplus-field", str(y_good_path), "--layer-field", str(zero_path))
    if zero_report is None:
        raise RuntimeError(err)
    shallow_report, err = run_case(case, tmp / "layer_shallow", "--context", str(context_path),
                                   "--yplus-field", str(y_good_path), "--layer-field", str(shallow_path))
    if shallow_report is None:
        raise RuntimeError(err)

    y = one_finding(y_report, "yplus")
    z = zero_report["cfd"]["wall_checks"]["walls"]["layer_distribution"]
    s = shallow_report["cfd"]["wall_checks"]["walls"]["layer_distribution"]
    if y["n_bad"] != 100 or y["severity"] != "high":
        raise AssertionError("synthetic y+ trigger was not detected")
    if one_finding(zero_report, "layer_coverage")["severity"] != "high" or z["n_covered"] != 372:
        raise AssertionError("zero-layer coverage trigger was not detected")
    if one_finding(shallow_report, "boundary_layers")["severity"] != "high" or s["n_under_target"] != 60:
        raise AssertionError("insufficient-layer trigger was not detected")
    metrics = {"fixture": "tests/samples/of_good_3d", "wall_patch": "walls", "n_wall_faces": n,
               "synthetic_yplus": {"values": {"first_100_faces": 100, "remaining_faces": 1},
                                   "finding": y, "outside_area_fraction": y_report["cfd"]["wall_checks"]["walls"]["yplus"]["outside_area_fraction"]},
               "synthetic_layers": {"zero_layer": z, "shallow_layer": s,
                                    "coverage_target": .9, "layer_target": 12}}
    return metrics, centres, area


def save(fig: plt.Figure, stem: str) -> None:
    qa_dir = os.environ.get("SCIPILOT_SKILL_DIR")
    if qa_dir:
        sys.path.insert(0, str(Path(qa_dir) / "scripts"))
        from visual_qa import audit_layout  # type: ignore[import-not-found]
        issues = audit_layout(fig)
        for severity, message in issues:
            print(f"{stem} {severity}: {message}")
        if any(severity == "FAIL" for severity, _ in issues):
            raise RuntimeError(f"{stem}: visual audit failed")
    fig.savefig(HERE / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(HERE / f"{stem}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_regression(rows: list[dict]) -> None:
    available = [r for r in rows if r["status"] != "unavailable"]
    matches = sum(r["status"] == "match" for r in available)
    labels = [Path(r["case"]).name for r in rows]
    labels = [x.replace("of_", "").replace(".log", " 日志").replace(".trn", " 日志") for x in labels]
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    fig.patch.set_facecolor("white")
    for i, row in enumerate(rows):
        for x, key in enumerate(("expected", "observed")):
            sev = row[key] or "unavailable"
            ax.add_patch(Rectangle((x - .36, i - .39), .72, .78, facecolor=COLORS[sev], edgecolor="white"))
            ax.text(x, i, ZH[sev], color="white" if sev != "unavailable" else "#263238",
                    ha="center", va="center", weight="bold", fontsize=9)
    ax.set_xlim(-.5, 1.5)
    ax.set_ylim(len(rows) - .5, -.5)
    ax.set_xticks([0, 1], ["预期分级", "实际分级"])
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(rows)), labels)
    ax.tick_params(length=0, pad=6)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(f"回归样例：可运行场景 {matches}/{len(available)} 与预期一致",
                 loc="left", pad=32, fontsize=15, weight="bold")
    fig.text(.11, .025, "共 10 个预设样例；灰色 3 项因 meshio / pyvista 未安装而未运行。此图不是工程算例检出率。",
             fontsize=9, color="#4E5964")
    fig.subplots_adjust(left=.31, right=.86, top=.83, bottom=.11)
    save(fig, "01_regression")


def plot_yplus(metrics: dict, centres: np.ndarray) -> None:
    y = metrics["synthetic_yplus"]
    bad = np.arange(len(centres)) < 100
    p = y["outside_area_fraction"] * 100
    fig = plt.figure(figsize=(10, 5.4))
    ax3d = fig.add_subplot(121, projection="3d")
    ax3d.scatter(*centres[~bad].T, s=9, c="#B5BEC7", alpha=.23, depthshade=False)
    ax3d.scatter(*centres[bad].T, s=22, c=COLORS["high"], alpha=.9, depthshade=False)
    ax3d.view_init(elev=24, azim=-66)
    ax3d.set_box_aspect((2, 1, 1))
    ax3d.set_xlabel("x", labelpad=1)
    ax3d.set_ylabel("y", labelpad=1)
    ax3d.set_zlabel("z", labelpad=1)
    ax3d.set(xlim=(0, 2), ylim=(0, 1), zlim=(0, 1))
    ax3d.set_xticks([0, 1, 2])
    ax3d.set_yticks([0, .5, 1])
    ax3d.set_zticks([0, .5, 1])
    ax3d.tick_params(labelsize=8, pad=0)
    ax3d.set_title("壁面面中心：局部异常位置", fontsize=11, pad=15)
    ax3d.legend(handles=[Patch(color=COLORS["high"], label="y+ = 100（超标）"),
                         Patch(color="#B5BEC7", label="y+ = 1（目标内）")],
                loc="upper left", bbox_to_anchor=(.0, .92), fontsize=8, frameon=False)
    ax = fig.add_subplot(122)
    ax.barh(0, 100 - p, color=COLORS["ok"], label="目标内")
    ax.barh(0, p, left=100 - p, color=COLORS["high"], label="目标外")
    ax.set_xlim(0, 100)
    ax.set_ylim(-.7, .7)
    ax.set_yticks([])
    ax.set_xlabel("壁面面积占比 / %")
    ax.set_title("面积加权判定", fontsize=11, pad=15)
    ax.text((100 - p) / 2, 0, f"{100-p:.1f}%\n目标内", color="white", ha="center", va="center", weight="bold")
    ax.text(100 - p / 2, 0, f"{p:.1f}%\n超标", color="white", ha="center", va="center", weight="bold")
    ax.text(0, -.55, "目标区间：0–2；识别出 100 / 432 个超标面",
            fontsize=9, color="#34404A", va="center")
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#CBD2D8")
    fig.suptitle("合成 y+ 场：能检出并定位局部超标", x=.08, y=.98, ha="left", fontsize=15, weight="bold")
    fig.text(.08, .025, "示例网格的面中心与面积是真实读取值；y+ = 1 / 100 是人为赋值，不代表求解器试算结果。",
             fontsize=9, color="#4E5964")
    fig.subplots_adjust(left=.04, right=.97, top=.81, bottom=.14, wspace=.12)
    save(fig, "02_yplus_localization")


def plot_layers(metrics: dict) -> None:
    z = metrics["synthetic_layers"]["zero_layer"]
    s = metrics["synthetic_layers"]["shallow_layer"]
    vals = np.array([[1 - z["coverage_area_fraction"], 0, z["coverage_area_fraction"]],
                     [0, s["under_target_area_fraction"], 1 - s["under_target_area_fraction"]]]) * 100
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
    cat = [("0 层", COLORS["high"]), ("1–11 层", COLORS["moderate"]),
           ("达到 12 层", COLORS["ok"])]
    labels = ["60 面完全缺层", "60 面只有 6 层"]
    for i in range(2):
        left = 0
        for j, (name, color) in enumerate(cat):
            value = vals[i, j]
            if value:
                ax.barh(i, value, left=left, color=color, height=.45)
                if value > 9:
                    ax.text(left + value / 2, i, f"{value:.1f}%", color="white", ha="center", va="center", weight="bold")
            left += value
    ax.set_xlim(0, 100)
    ax.set_yticks([0, 1], labels)
    ax.invert_yaxis()
    ax.set_xlabel("壁面面积占比 / %")
    ax.set_title("按实际层数分解壁面面积", fontsize=11)
    ax.legend(handles=[Patch(color=c, label=n) for n, c in cat], ncol=3,
              loc="upper center", bbox_to_anchor=(.5, -.18), frameon=False, fontsize=8)
    coverages = [z["coverage_area_fraction"] * 100, s["coverage_area_fraction"] * 100]
    for i, cov in enumerate(coverages):
        ax2.plot([0, cov], [i, i], color="#CBD2D8", lw=3)
        ax2.plot(cov, i, marker="o", markersize=11,
                 color=COLORS["high"] if cov < 90 else COLORS["ok"])
        ax2.text(cov - 3, i - .16, f"{cov:.1f}%", fontsize=10, weight="bold", ha="right")
    ax2.axvline(90, color="#34404A", linestyle="--", linewidth=1.5, label="覆盖率目标 90%")
    ax2.set_xlim(0, 108)
    ax2.set_ylim(1.5, -.5)
    ax2.set_yticks([])
    ax2.set_xlabel("有层覆盖面积 / %")
    ax2.set_title("覆盖率和目标", fontsize=11)
    ax2.legend(loc="lower right", frameon=False, fontsize=8)
    fig.suptitle("合成层字段：区分“缺层”与“层数不足”", x=.06, y=.98, ha="left", fontsize=15, weight="bold")
    fig.text(.06, .025, "两组均人为指定 60 / 432 个壁面面的层数；面积来自样例网格。覆盖率目标 90%，层数目标 12。",
             fontsize=9, color="#4E5964")
    fig.subplots_adjust(left=.18, right=.98, top=.76, bottom=.22, wspace=.22)
    save(fig, "03_layer_coverage")


def main() -> None:
    HERE.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        tmp = Path(folder)
        rows = collect_regression(tmp)
        metrics, centres, _ = collect_cfd(tmp)
    evidence = {"regression": rows, "cfd_demo": metrics,
                "interpretation": "Regression fixtures and synthetic CFD fields; no real OpenFOAM solver case was run."}
    (HERE / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    plot_regression(rows)
    plot_yplus(metrics, centres)
    plot_layers(metrics)
    available = [r for r in rows if r["status"] != "unavailable"]
    matched = sum(r["status"] == "match" for r in available)
    assert matched == len(available), "regression mismatch: figures would mislead"
    summary = f"""# Skill 验证图说明

图 1 基于 `tests/run_tests.py` 定义的 10 个预设样例。当前环境成功执行 {len(available)} 项，{matched} 项来源识别、总体分级及指定异常与预期一致；另 {len(rows)-len(available)} 项因缺少 `meshio` / `pyvista` 未运行。预设样例的匹配率不能用作真实工程算例的检出率。

图 2 和图 3 使用 `tests/samples/of_good_3d` 的 432 个壁面面几何与面面积，但逐面 y⁺ 与 `nSurfaceLayers` 是为了测试检测路径而人为赋值。图 2 应检出 100 个 y⁺ 超标面，超标面积占 {metrics['synthetic_yplus']['outside_area_fraction']:.1%}。图 3 的完全缺层场有 {metrics['synthetic_layers']['zero_layer']['coverage_area_fraction']:.1%} 面积覆盖率；另一场虽然覆盖率为 100%，但 {metrics['synthetic_layers']['shallow_layer']['under_target_area_fraction']:.1%} 的面积低于 12 层目标。

三幅图展示了当前代码的回归表现和指标区分能力。真实 OpenFOAM 网格的端到端有效性仍需按 `reference/official_validation.md` 运行官方算例验证，尤其是 snappyHexMesh 生成后的层字段。

复现：在 Skill 根目录运行 `python validation/generate.py`。原始结果保存于 `validation/evidence.json`；PNG 用于预览，SVG 可用于文档。
"""
    (HERE / "summary.md").write_text(summary, encoding="utf-8")
    print(f"Generated 3 figures; {matched}/{len(available)} executable regression cases matched.")


if __name__ == "__main__":
    main()
