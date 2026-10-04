"""Save native OpenFOAM three-grid evidence and prepare a Skill context.

Run after prepare_cases.py, blockMesh, checkMesh, foamRun, and fine-grid yPlus.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUN = Path.home() / "OpenFOAM" / f"{os.environ['USER']}-12" / "run"
GRADES = ("coarse", "medium", "fine")
OBJECTS = ("inletPressure", "outletPressure", "inletFlow", "outletFlow")


def table(path: Path) -> list[tuple[int, float]]:
    rows = []
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        cells = line.split()
        assert len(cells) == 2, (path, line)
        rows.append((int(float(cells[0])), float(cells[1])))
    assert rows and [time for time, _ in rows] == list(range(rows[-1][0] + 1)), path
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setup_hashes(case: Path) -> dict[str, str]:
    paths = [*case.glob("0/*"), *case.glob("constant/*"), *case.glob("system/*")]
    return {
        str(path.relative_to(case)): sha256(path)
        for path in paths
        if path.is_file() and path.name != "blockMeshDict"
    }


def main() -> None:
    evidence = {"case": "OpenFOAM Foundation 12 pitzDailySteady", "grids": {}}
    setups = []
    study = []
    histories = {}
    fine_history = None
    fine_flux = None
    for grade in GRADES:
        case = RUN / f"pitzDailySteady-grid-{grade}-monitored-20261004"
        assert case.is_dir(), case
        native_mesh = (case / "log.checkMesh").read_text()
        native_solver = (case / "log.foamRun").read_text()
        assert "Mesh OK." in native_mesh and "Failed" not in native_mesh
        cells_match = re.search(r"^\s*cells:\s*(\d+)", native_mesh, re.M)
        assert cells_match
        n_cells = int(cells_match.group(1))
        convergence_match = re.search(r"SIMPLE solution converged in (\d+) iterations", native_solver)
        assert convergence_match
        n_iterations = int(convergence_match.group(1))

        raw = {}
        for name in OBJECTS:
            source = case / "postProcessing" / name / "0/surfaceFieldValue.dat"
            raw[name] = table(source)
            shutil.copyfile(source, HERE / f"{grade}.{name}.dat")
        times = [time for time, _ in raw["inletPressure"]]
        assert all([time for time, _ in rows] == times for rows in raw.values())
        assert len(times) == n_iterations + 1
        pressure_history = [p_in - p_out for (_, p_in), (_, p_out) in zip(
            raw["inletPressure"], raw["outletPressure"]
        )]
        histories[f"kinematic_pressure_difference_m2_s2_{grade}"] = pressure_history
        inlet_flux, outlet_flux = raw["inletFlow"][-1][1], raw["outletFlow"][-1][1]
        assert inlet_flux < 0 < outlet_flux
        imbalance = abs(inlet_flux + outlet_flux) / max(-inlet_flux, outlet_flux)
        study.append({"n_cells": n_cells, "kinematic_pressure_difference_m2_s2": pressure_history[-1]})
        evidence["grids"][grade] = {
            "n_cells": n_cells,
            "simple_converged_iterations": n_iterations,
            "kinematic_pressure_difference_m2_s2": pressure_history[-1],
            "inlet_volume_flux_m3_s": inlet_flux,
            "outlet_volume_flux_m3_s": outlet_flux,
            "relative_volume_flux_imbalance": imbalance,
            "number_of_monitor_samples": len(times),
        }
        setups.append(setup_hashes(case))
        for name in ("log.blockMesh", "log.checkMesh", "log.foamRun", "system/blockMeshDict"):
            shutil.copyfile(case / name, HERE / f"{grade}.{Path(name).name}")
        if grade == "fine":
            fine_history = pressure_history
            fine_flux = {"inlet": inlet_flux, "outlet": outlet_flux}
            shutil.copyfile(case / "log.yPlus", HERE / "fine.log.yPlus")
            shutil.copyfile(case / f"{n_iterations}/yPlus", HERE / f"fine.yPlus.{n_iterations}")

    assert setups[0] == setups[1] == setups[2], "Non-mesh case settings differ across grids"
    evidence["matching_setup_sha256"] = setups[0]
    evidence["coarse_medium_relative_change"] = abs(study[1]["kinematic_pressure_difference_m2_s2"] - study[0]["kinematic_pressure_difference_m2_s2"]) / max(abs(study[0]["kinematic_pressure_difference_m2_s2"]), abs(study[1]["kinematic_pressure_difference_m2_s2"]))
    evidence["fine_medium_relative_change"] = abs(study[2]["kinematic_pressure_difference_m2_s2"] - study[1]["kinematic_pressure_difference_m2_s2"]) / max(abs(study[1]["kinematic_pressure_difference_m2_s2"]), abs(study[2]["kinematic_pressure_difference_m2_s2"]))
    n = max(2, len(fine_history) // 5)
    early, late = sum(fine_history[-2*n:-n]) / n, sum(fine_history[-n:]) / n
    evidence["fine_monitor_last_two_window_relative_drift"] = abs(late - early) / max(abs(late), abs(early), 1e-12)
    evidence["monitor_last_two_window_relative_drift"] = {}
    for name, history in histories.items():
        window = max(2, len(history) // 5)
        prior = sum(history[-2*window:-window]) / window
        recent = sum(history[-window:]) / window
        evidence["monitor_last_two_window_relative_drift"][name] = abs(recent - prior) / max(abs(recent), abs(prior), 1e-12)
    context = {
        "flow": {"turbulence_model": "kEpsilon", "constant_density": True},
        "wall_defaults": {"treatment": "standard_wall_function", "target_yplus": [30, 300]},
        "results": {
            "volumetric_flux_m3_s": fine_flux,
            "monitor_history": histories,
            "grid_study": study,
        },
    }
    (HERE / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    (HERE / "context.json").write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"grids": evidence["grids"], "coarse_medium_relative_change": evidence["coarse_medium_relative_change"], "fine_medium_relative_change": evidence["fine_medium_relative_change"], "fine_monitor_last_two_window_relative_drift": evidence["fine_monitor_last_two_window_relative_drift"]}, indent=2))


if __name__ == "__main__":
    main()
