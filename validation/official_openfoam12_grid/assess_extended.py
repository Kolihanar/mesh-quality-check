"""Summarize three isolated strict-stop continuations from native monitor tables."""
from __future__ import annotations

import json
import hashlib
import os
import shutil
import statistics
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RUN = Path.home() / "OpenFOAM" / f"{os.environ['USER']}-12" / "run"


def table(path: Path) -> list[tuple[int, float]]:
    return [
        (int(float(t)), float(v))
        for line in path.read_text().splitlines()
        if line and not line.startswith("#")
        for t, v in [line.split()]
    ]


def main() -> None:
    original = json.loads((HERE / "evidence.json").read_text())
    summary = {"grids": {}}
    histories = {}
    study = []
    settings = []
    fine_flux = None
    for grade in ("coarse", "medium", "fine"):
        case = RUN / f"pitzDailySteady-grid-{grade}-extended-20261004"
        start = original["grids"][grade]["simple_converged_iterations"]
        pressure = {}
        for patch in ("inlet", "outlet"):
            combined = []
            for time in (0, start):
                source = case / f"postProcessing/{patch}Pressure/{time}/surfaceFieldValue.dat"
                shutil.copyfile(source, HERE / f"{grade}.{patch}Pressure.{time}.dat")
                rows = table(source)
                combined.extend(rows if time == 0 else rows[1:])
            assert [t for t, _ in combined] == list(range(1001)), (grade, patch)
            pressure[patch] = combined
        history = [p_in - p_out for (_, p_in), (_, p_out) in zip(pressure["inlet"], pressure["outlet"])]
        metric = "kinematic_pressure_difference_m2_s2"
        histories[f"{metric}_{grade}"] = history
        study.append({"n_cells": original["grids"][grade]["n_cells"], metric: history[-1]})
        settings.append({name: hashlib.sha256((case / f"system/{name}").read_bytes()).hexdigest()
                         for name in ("controlDict", "fvSolution", "fvSchemes", "functions")})
        window = len(history) // 5
        older = statistics.mean(history[-2*window:-window])
        recent = history[-window:]
        newer = statistics.mean(recent)
        scale = max(abs(older), abs(newer), 1e-12)
        native_solver = (case / "log.foamRun.extended").read_text()
        assert "Time = 1000s" in native_solver and "SIMPLE solution converged" not in native_solver
        shutil.copyfile(case / "log.foamRun.extended", HERE / f"{grade}.log.foamRun.extended")
        if grade == "fine":
            fine_flux = {}
            for patch in ("inlet", "outlet"):
                source = case / f"postProcessing/{patch}Flow/{start}/surfaceFieldValue.dat"
                fine_flux[patch] = table(source)[-1][1]
                shutil.copyfile(source, HERE / f"fine.{patch}Flow.{start}.dat")
            shutil.copyfile(case / "log.yPlus.extended", HERE / "fine.log.yPlus.extended")
            shutil.copyfile(case / "1000/yPlus", HERE / "fine.yPlus.1000")
        summary["grids"][grade] = {
            "start_iteration": start,
            "end_iteration": 1000,
            "stopped_at_end_time_without_simple_convergence": True,
            "target_at_start_m2_s2": history[start],
            "target_at_end_m2_s2": history[-1],
            "last_window_mean_m2_s2": newer,
            "last_two_20_percent_window_relative_drift": abs(newer - older) / scale,
            "last_20_percent_window_relative_range": (max(recent) - min(recent)) / max(abs(newer), 1e-12),
            "last_20_percent_window_relative_p05_p95_span": (float(np.percentile(recent, 95)) - float(np.percentile(recent, 5))) / max(abs(newer), 1e-12),
            "last_20_percent_window_relative_std": statistics.pstdev(recent) / max(abs(newer), 1e-12),
        }
    assert settings[0] == settings[1] == settings[2]
    summary["matching_solver_setup_sha256"] = settings[0]
    context = {
        "flow": {"turbulence_model": "kEpsilon", "constant_density": True},
        "wall_defaults": {"treatment": "standard_wall_function", "target_yplus": [30, 300]},
        "results": {"volumetric_flux_m3_s": fine_flux,
                    "monitor_history": histories, "grid_study": study},
    }
    (HERE / "extended_evidence.json").write_text(json.dumps(summary, indent=2) + "\n")
    (HERE / "extended_context.json").write_text(json.dumps(context, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
