"""Compare the saved Skill reports with independent OpenFOAM output."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_report(stage: str) -> dict:
    return json.loads((ROOT / stage / "mesh_report.json").read_text(encoding="utf-8"))


def required_number(text: str, pattern: str) -> float:
    match = re.search(pattern, text, re.MULTILINE)
    assert match is not None, pattern
    return float(match.group(1))


def close(actual: float, expected: float, label: str, abs_tol: float = 1e-7) -> None:
    assert math.isclose(actual, expected, rel_tol=2e-5, abs_tol=abs_tol), (label, actual, expected)


def main() -> None:
    native_mesh = (ROOT / "log.checkMesh").read_text(encoding="utf-8")
    native_yplus = (ROOT / "log.yPlus.solver").read_text(encoding="utf-8")
    field = (ROOT / "yPlus.286").read_text(encoding="utf-8")
    solver = (ROOT / "log.foamRun").read_text(encoding="utf-8")
    pre = read_report("preflight")
    post = read_report("postflight")
    flow = json.loads((ROOT / "flow_evidence.json").read_text(encoding="utf-8-sig"))
    post_context = json.loads((ROOT / "postflight_context.json").read_text(encoding="utf-8"))
    post_markdown = (ROOT / "postflight" / "mesh_report.md").read_text(encoding="utf-8")

    assert "Mesh OK." in native_mesh
    assert "SIMPLE solution converged in 286 iterations" in solver
    assert pre["overall"] == "ok" and post["overall"] == "high"
    assert "证据不足" in pre["readiness"] and "证据不足" in post["readiness"]
    assert post["extra"]["checkmesh_verdict"] == "Mesh OK"
    assert not post["extra"].get("consistency_errors")
    assert post["cfd"]["case_setup"]["nu"] == 1e-5
    mass_balance = post["cfd"]["solution_checks"]["mass_balance"]
    assert mass_balance["basis"] == "volumetric_flux_m3_s"
    assert post_context["flow"]["constant_density"] is True
    assert post_context["results"]["volumetric_flux_m3_s"] == flow["volumetric_flux_m3_s"]
    close(mass_balance["relative_imbalance"], flow["relative_imbalance"], "volume balance")
    for patch in ("inlet", "outlet"):
        native_table = (ROOT / f"{patch}Flow.dat").read_text(encoding="utf-8")
        native_count = required_number(native_table, r"^# Faces\s*:\s*(\d+)")
        native_flux = required_number(native_table, r"^286\s+([-\d.eE+]+)")
        assert native_count == flow["n_faces"][patch]
        close(flow["volumetric_flux_m3_s"][patch], native_flux, f"{patch} phi", abs_tol=5e-11)
    assert "nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支" in post_markdown
    assert "计算很可能不稳定" not in post_markdown
    for label, key in (("points", "n_points"), ("faces", "n_faces"), ("internal faces", "n_internal_faces"), ("cells", "n_cells")):
        native = required_number(native_mesh, rf"^\s*{re.escape(label)}:\s*(\d+)")
        assert pre["mesh_info"][key] == post["mesh_info"][key] == native, label
    for label, key in (("Max aspect ratio", "aspect_ratio"), ("Max skewness", "skewness")):
        native = required_number(native_mesh, rf"{re.escape(label)}\s*=\s*([\d.eE+-]+)")
        metric = next(f for f in post["findings"] if f["metric"] == key)
        close(metric["value"], native, label, abs_tol=5e-4)  # Report rounds displayed metrics.

    for wall, count in (("upperWall", 223), ("lowerWall", 250)):
        match = re.search(rf"\b{wall}\s*\{{[^{{}}]*?value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\(([^)]*)\)", field, re.DOTALL)
        assert match is not None, wall
        values = [float(x) for x in match.group(2).split()]
        assert len(values) == int(match.group(1)) == count
        log_match = re.search(rf"patch {wall} y\+ : min = ([\d.eE+-]+), max = ([\d.eE+-]+)", native_yplus)
        assert log_match is not None, wall
        result = post["cfd"]["wall_checks"][wall]
        assert result["provenance"] == "solver_result"
        assert result["low_y_wall_function"] is True
        assert result["target_source"] == "explicit"
        assert result["yplus"]["n_valid"] == result["yplus"]["n_outside"] == count
        for name, value, logged in (("min", min(values), float(log_match.group(1))),
                                    ("max", max(values), float(log_match.group(2)))):
            close(result["yplus"][name], value, f"{wall} {name} field")
            close(result["yplus"][name], logged, f"{wall} {name} log")
        assert pre["cfd"]["wall_checks"][wall]["status"] == "unknown"

    print("OpenFOAM 12 native/Skill comparison: passed (mesh, solver, wall yPlus, volume balance)")


if __name__ == "__main__":
    main()
