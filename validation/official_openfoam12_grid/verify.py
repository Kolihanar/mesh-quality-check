"""Independently compare saved native OpenFOAM evidence with the Skill report."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
METRIC = "kinematic_pressure_difference_m2_s2"


def rows(path: Path) -> list[tuple[int, float]]:
    return [
        (int(float(time)), float(value))
        for line in path.read_text().splitlines()
        if line and not line.startswith("#")
        for time, value in [line.split()]
    ]


def close(a: float, b: float) -> None:
    assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-11), (a, b)


def main() -> None:
    evidence = json.loads((ROOT / "evidence.json").read_text())
    context = json.loads((ROOT / "context.json").read_text())
    report = json.loads((ROOT / "report/mesh_report.json").read_text())
    checks = report["cfd"]["solution_checks"]
    assert report["overall"] == "high"
    assert report["extra"]["checkmesh_verdict"] == "Mesh OK"
    assert checks["grid_sensitivity"][METRIC]["interpretation"] == "provisional_target_unstable"
    assert len(checks["grid_sensitivity"][METRIC]["unstable_monitor_histories"]) == 3
    for index, grade in enumerate(("coarse", "medium", "fine")):
        native_mesh = (ROOT / f"{grade}.log.checkMesh").read_text()
        native_solver = (ROOT / f"{grade}.log.foamRun").read_text()
        assert "Mesh OK." in native_mesh
        native_cells = int(re.search(r"^\s*cells:\s*(\d+)", native_mesh, re.M).group(1))
        native_iterations = int(re.search(r"SIMPLE solution converged in (\d+) iterations", native_solver).group(1))
        assert native_cells == evidence["grids"][grade]["n_cells"]
        assert native_iterations == evidence["grids"][grade]["simple_converged_iterations"]
        assert native_cells == context["results"]["grid_study"][index]["n_cells"]
        assert native_cells == checks["grid_sensitivity"][METRIC]["n_cells"][index]
        pressure_in = rows(ROOT / f"{grade}.inletPressure.dat")
        pressure_out = rows(ROOT / f"{grade}.outletPressure.dat")
        flow_in = rows(ROOT / f"{grade}.inletFlow.dat")
        flow_out = rows(ROOT / f"{grade}.outletFlow.dat")
        assert all(len(data) == native_iterations + 1 for data in (pressure_in, pressure_out, flow_in, flow_out))
        history = [a - b for (_, a), (_, b) in zip(pressure_in, pressure_out)]
        key = f"{METRIC}_{grade}"
        assert history == context["results"]["monitor_history"][key]
        close(history[-1], context["results"]["grid_study"][index][METRIC])
        close(history[-1], checks["grid_sensitivity"][METRIC][grade])
        window = max(2, len(history) // 5)
        early = sum(history[-2*window:-window]) / window
        late = sum(history[-window:]) / window
        drift = abs(late - early) / max(abs(late), abs(early), 1e-12)
        close(drift, checks["monitor_drift"][key]["relative_change"])
        assert next(f for f in report["findings"] if f["name_zh"] == f"监测量 {key} 的末段漂移")["severity"] == "high"
        if grade == "fine":
            close(flow_in[-1][1], context["results"]["volumetric_flux_m3_s"]["inlet"])
            close(flow_out[-1][1], context["results"]["volumetric_flux_m3_s"]["outlet"])
            imbalance = abs(flow_in[-1][1] + flow_out[-1][1]) / max(-flow_in[-1][1], flow_out[-1][1])
            close(imbalance, checks["mass_balance"]["relative_imbalance"])
            assert report["mesh_info"]["n_cells"] == native_cells
    medium, fine = (evidence["grids"][grade][METRIC] for grade in ("medium", "fine"))
    change = abs(fine - medium) / max(abs(fine), abs(medium))
    close(change, checks["grid_sensitivity"][METRIC]["fine_medium_relative_change"])
    markdown = (ROOT / "report/mesh_report.md").read_text()
    assert "当前网格差异只是初步比较" in markdown
    assert "先使各套网格上的目标量监测序列稳定" in markdown

    extended = json.loads((ROOT / "extended_evidence.json").read_text())
    extended_context = json.loads((ROOT / "extended_context.json").read_text())
    extended_report = json.loads((ROOT / "extended_report/mesh_report.json").read_text())
    extended_checks = extended_report["cfd"]["solution_checks"]
    assert extended_report["overall"] == "high"
    assert extended_report["extra"]["checkmesh_verdict"] == "Mesh OK"
    assert extended_checks["grid_sensitivity"][METRIC]["interpretation"] == "provisional_target_unstable"
    assert extended_checks["grid_sensitivity"][METRIC]["unstable_monitor_histories"] == [f"{METRIC}_fine"]
    for index, grade in enumerate(("coarse", "medium", "fine")):
        start = extended["grids"][grade]["start_iteration"]
        native_solver = (ROOT / f"{grade}.log.foamRun.extended").read_text()
        assert "Time = 1000s" in native_solver and "SIMPLE solution converged" not in native_solver
        pressure = {}
        for patch in ("inlet", "outlet"):
            old = rows(ROOT / f"{grade}.{patch}Pressure.0.dat")
            new = rows(ROOT / f"{grade}.{patch}Pressure.{start}.dat")
            pressure[patch] = old + new[1:]
        history = [a - b for (_, a), (_, b) in zip(pressure["inlet"], pressure["outlet"])]
        assert len(history) == 1001
        key = f"{METRIC}_{grade}"
        assert history == extended_context["results"]["monitor_history"][key]
        close(history[-1], extended_context["results"]["grid_study"][index][METRIC])
        window = len(history) // 5
        old_mean = sum(history[-2*window:-window]) / window
        new_values = history[-window:]
        new_mean = sum(new_values) / window
        drift = abs(new_mean - old_mean) / max(abs(old_mean), abs(new_mean), 1e-12)
        span = (np.percentile(new_values, 95) - np.percentile(new_values, 5)) / max(abs(new_mean), 1e-12)
        close(drift, extended_checks["monitor_drift"][key]["relative_change"])
        close(span, extended_checks["monitor_spread"][key]["relative_span"])
        close(span, extended["grids"][grade]["last_20_percent_window_relative_p05_p95_span"])
        if grade == "fine":
            assert span > extended_checks["monitor_spread"][key]["tolerance"]
            assert drift < extended_checks["monitor_drift"][key]["tolerance"]
            for patch in ("inlet", "outlet"):
                flux = rows(ROOT / f"fine.{patch}Flow.{start}.dat")[-1][1]
                close(flux, extended_context["results"]["volumetric_flux_m3_s"][patch])
            assert extended_report["cfd"]["wall_checks"]["upperWall"]["provenance"] == "solver_result"
    extended_markdown = (ROOT / "extended_report/mesh_report.md").read_text()
    assert "P05–P95 波动" in extended_markdown and "当前网格差异只是初步比较" in extended_markdown
    print("OpenFOAM 12 three-grid native/Skill comparison: passed (initial and strict-stop trials, pressure, flux, drift, spread, provisional grid sensitivity)")


if __name__ == "__main__":
    main()
