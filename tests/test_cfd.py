"""Integration checks for the OpenFOAM CFD suitability path."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "scripts", "mesh_check.py")
CASE = os.path.join(HERE, "samples", "of_good_3d")


def run(path, out, *args):
    proc = subprocess.run([sys.executable, SCRIPT, path, "-o", out, *args],
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    with open(os.path.join(out, "mesh_report.json"), encoding="utf-8") as stream:
        report = json.load(stream)
    return proc, report


def main():
    with tempfile.TemporaryDirectory() as tmp:
        proc, data = run(os.path.join(tmp, "missing"), os.path.join(tmp, "unknown"))
        assert proc.returncode == 3
        assert data["overall"] == "unknown"
        assert "证据不足" in data["readiness"]

        context = {"flow": {"nu": 1e-6}, "wall_defaults": {
            "treatment": "wall_resolved", "friction_velocity": 0.1,
            "target_layers": 12, "measured_layers": 6}}
        path = os.path.join(tmp, "context.json")
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(context, stream)
        proc, data = run(CASE, os.path.join(tmp, "preflight"), "--context", path)
        assert proc.returncode == 2, proc.stderr
        assert data["cfd"]["wall_checks"]["walls"]["provenance"] == "preflight_estimate"
        assert {f["metric"] for f in data["findings"] if f["severity"] != "ok"} >= {"yplus", "boundary_layers"}
        assert any(x["metric"] == "yplus" and "第一层" in x["mesh_action"] for x in data["recommendations"])

        modern_case = os.path.join(tmp, "openfoam12_case")
        shutil.copytree(CASE, modern_case)
        with open(os.path.join(modern_case, "constant", "physicalProperties"), "w", encoding="ascii") as stream:
            stream.write("nu 1e-05;\n")
        modern_context = os.path.join(tmp, "openfoam12_context.json")
        with open(modern_context, "w", encoding="utf-8") as stream:
            json.dump({"wall_defaults": {"treatment": "wall_resolved", "friction_velocity": 0.1}}, stream)
        proc, modern = run(modern_case, os.path.join(tmp, "openfoam12_preflight"),
                           "--context", modern_context)
        assert modern["cfd"]["case_setup"]["nu"] == 1e-5
        assert modern["cfd"]["wall_checks"]["walls"]["provenance"] == "preflight_estimate"

        grouped_case = os.path.join(tmp, "openfoam_grouped_walls")
        shutil.copytree(CASE, grouped_case)
        boundary_path = os.path.join(grouped_case, "constant", "polyMesh", "boundary")
        with open(boundary_path, encoding="ascii") as stream:
            boundary_text = stream.read()
        assert boundary_text.count("type wall;") == 1
        with open(boundary_path, "w", encoding="ascii") as stream:
            stream.write(boundary_text.replace("type wall;", "type wall;\n        inGroups List<word> 1(wall);"))
        os.makedirs(os.path.join(grouped_case, "0"), exist_ok=True)
        with open(os.path.join(grouped_case, "0", "nut"), "w", encoding="ascii") as stream:
            stream.write("boundaryField { wall { type nutkWallFunction; } "
                         "walls { type nutUSpaldingWallFunction; } }\n")
        with open(os.path.join(grouped_case, "0", "epsilon"), "w", encoding="ascii") as stream:
            stream.write("boundaryField { wall { type epsilonWallFunction; } }\n")
        with open(os.path.join(grouped_case, "0", "alphat"), "w", encoding="ascii") as stream:
            stream.write("boundaryField { wall { type compressible::alphatJayatillekeWallFunction; } }\n")
        proc, grouped = run(grouped_case, os.path.join(tmp, "grouped_walls"))
        wall_types = grouped["cfd"]["wall_checks"]["walls"]["wall_field_types"]
        assert wall_types == {"nut": "nutUSpaldingWallFunction", "epsilon": "epsilonWallFunction",
                              "alphat": "compressible::alphatJayatillekeWallFunction"}, wall_types
        assert grouped["cfd"]["wall_checks"]["walls"]["wall_field_source"] == "patch_or_patch_over_group"
        assert not any("缺少 0/nut" in item for item in grouped["cfd"]["missing"])

        field = os.path.join(tmp, "yPlus")
        with open(field, "w", encoding="ascii") as stream:
            stream.write("FoamFile { format ascii; class volScalarField; object yPlus; }\n"
                         "internalField uniform 0;\n"
                         "boundaryField { walls { type calculated; value uniform 1; } }\n")
        proc, data = run(CASE, os.path.join(tmp, "postflight"), "--context", path, "--yplus-field", field)
        assert proc.returncode == 2, proc.stderr  # insufficient measured layers still fail
        assert data["cfd"]["wall_checks"]["walls"]["provenance"] == "solver_result"
        assert next(f for f in data["findings"] if f["metric"] == "yplus")["severity"] == "ok"
        assert data["cfd"]["wall_checks"]["walls"]["yplus"]["median"] == 1
        info = data["mesh_info"]
        native_log = os.path.join(tmp, "log.checkMesh")
        with open(native_log, "w", encoding="ascii") as stream:
            stream.write("Application : checkMesh\nMesh stats\n"
                         f"    points: {info['n_points']}\n    faces: {info['n_faces']}\n"
                         f"    internal faces: {info['n_internal_faces']}\n    cells: {info['n_cells']}\n"
                         f"Mesh has {info['n_dims']} geometric (non-empty/wedge) directions\nMesh OK.\n")
        complete = {"flow": {"nu": 1e-6, "turbulence_model": "kOmegaSST"}, "wall_defaults": {
            "treatment": "wall_resolved", "wall_conditions_verified": True,
            "target_layers": 12, "measured_layers": 12,
            "min_layer_coverage": .9, "measured_layer_coverage": .98,
            "max_growth_p95": 1.25, "measured_growth_p95": 1.15},
            "results": {"mass_flux_kg_s": {"inlet": -1, "outlet": 1.001},
                        "monitor_history": {"pressure_drop_Pa_coarse": [103] * 12,
                                            "pressure_drop_Pa_medium": [101] * 12,
                                            "pressure_drop_Pa_fine": [100] * 12},
                        "grid_study": [{"n_cells": 1000, "pressure_drop_Pa": 103},
                                       {"n_cells": 2000, "pressure_drop_Pa": 101},
                                       {"n_cells": 4000, "pressure_drop_Pa": 100}]}}
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(complete, stream)
        proc, data = run(CASE, os.path.join(tmp, "validated"), "--context", path,
                         "--yplus-field", field, "--checkmesh-log", native_log)
        assert proc.returncode == 0, proc.stderr
        assert data["overall"] == "ok"
        assert not data["cfd"]["missing"]
        assert data["cfd"]["solution_checks"]["mass_balance"]["relative_imbalance"] < .01
        with open(os.path.join(tmp, "validated", "mesh_report.md"), encoding="utf-8") as stream:
            report = stream.read()
        assert "按优先级排列的网格优化建议" in report
        assert "质量通量不平衡" in report
        partial_context = json.loads(json.dumps(complete))
        partial_context["results"]["monitor_history"] = {"pressure_drop_Pa_fine": [100] * 12}
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(partial_context, stream)
        proc, partial_report = run(CASE, os.path.join(tmp, "missing_grid_histories"),
                                   "--context", path, "--yplus-field", field,
                                   "--checkmesh-log", native_log)
        assert partial_report["cfd"]["solution_checks"]["grid_sensitivity"]["pressure_drop_Pa"]["interpretation"] == "provisional_missing_grid_histories"
        assert len(partial_report["cfd"]["solution_checks"]["grid_sensitivity"]["pressure_drop_Pa"]["missing_monitor_histories"]) == 2
        assert "证据不足" in partial_report["readiness"] or "证据" in partial_report["readiness"]
        unstable_context = json.loads(json.dumps(complete))
        unstable_context["results"]["monitor_history"] = {
            "pressure_drop_Pa_fine": [100] * 8 + [100, 102, 106, 110]}
        unstable_context["results"]["grid_study"][-1]["pressure_drop_Pa"] = 110
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(unstable_context, stream)
        proc, unstable_report = run(CASE, os.path.join(tmp, "unstable_target"),
                                    "--context", path, "--yplus-field", field,
                                    "--checkmesh-log", native_log)
        assert proc.returncode == 2, proc.stderr
        solution_checks = unstable_report["cfd"]["solution_checks"]
        assert solution_checks["grid_sensitivity"]["pressure_drop_Pa"]["interpretation"] == "provisional_target_unstable"
        assert solution_checks["grid_sensitivity"]["pressure_drop_Pa"]["unstable_monitor_histories"] == ["pressure_drop_Pa_fine"]
        assert next(f for f in unstable_report["findings"] if f["metric"] == "monitor_drift")["severity"] == "high"
        assert "先使各套网格" in next(x for x in unstable_report["recommendations"]
                                  if x["metric"] == "grid_sensitivity")["mesh_action"]
        oscillating_context = json.loads(json.dumps(complete))
        oscillating_context["results"]["monitor_history"]["pressure_drop_Pa_fine"] = [100] * 8 + [90, 110, 90, 110]
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(oscillating_context, stream)
        proc, oscillating_report = run(CASE, os.path.join(tmp, "oscillating_target"),
                                       "--context", path, "--yplus-field", field,
                                       "--checkmesh-log", native_log)
        assert proc.returncode == 2, proc.stderr
        oscillating_checks = oscillating_report["cfd"]["solution_checks"]
        assert oscillating_checks["monitor_drift"]["pressure_drop_Pa_fine"]["relative_change"] == 0
        assert oscillating_checks["monitor_spread"]["pressure_drop_Pa_fine"]["relative_span"] > .1
        assert oscillating_checks["grid_sensitivity"]["pressure_drop_Pa"]["interpretation"] == "provisional_target_unstable"
        volume_context = json.loads(json.dumps(complete))
        volume_context["flow"]["constant_density"] = True
        del volume_context["results"]["mass_flux_kg_s"]
        volume_context["results"]["volumetric_flux_m3_s"] = {"inlet": -1, "outlet": 1.001}
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(volume_context, stream)
        proc, volume_report = run(CASE, os.path.join(tmp, "volume_balance"), "--context", path,
                                  "--yplus-field", field, "--checkmesh-log", native_log)
        assert proc.returncode == 0, proc.stderr
        assert volume_report["cfd"]["solution_checks"]["mass_balance"]["basis"] == "volumetric_flux_m3_s"
        with open(os.path.join(tmp, "volume_balance", "mesh_report.md"), encoding="utf-8") as stream:
            assert "恒密度流体积通量相对不平衡" in stream.read()
        del volume_context["flow"]["constant_density"]
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(volume_context, stream)
        proc, unverified_density = run(CASE, os.path.join(tmp, "volume_unverified_density"),
                                       "--context", path, "--yplus-field", field,
                                       "--checkmesh-log", native_log)
        assert "mass_balance" not in unverified_density["cfd"]["solution_checks"]
        assert any("flow.constant_density" in x for x in unverified_density["cfd"]["missing"])
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(complete, stream)
        field2 = os.path.join(tmp, "yPlus_spatial")
        values = [100] * 100 + [1] * 332
        with open(field2, "w", encoding="ascii") as stream:
            stream.write("FoamFile { format ascii; class volScalarField; object yPlus; }\n"
                         "boundaryField { walls { type calculated; value nonuniform List<scalar> 432\n(\n"
                         + "\n".join(map(str, values)) + "\n); } }\n")
        proc, data = run(CASE, os.path.join(tmp, "spatial"), "--context", path,
                         "--yplus-field", field2, "--checkmesh-log", native_log)
        assert proc.returncode == 2, proc.stderr
        yplus = next(f for f in data["findings"] if f["metric"] == "yplus")
        assert yplus["severity"] == "high"
        assert yplus["location"]["bbox_min"]
        assert yplus["n_bad"] == 100

        layer_field = os.path.join(tmp, "nSurfaceLayers")
        layer_values = [0] * 60 + [12] * 372
        with open(layer_field, "w", encoding="ascii") as stream:
            stream.write("FoamFile { format ascii; class volScalarField; object nSurfaceLayers; }\n"
                         "internalField uniform 0;\n"
                         "boundaryField { walls { type fixedValue; value nonuniform List<scalar> 432\n(\n"
                         + "\n".join(map(str, layer_values)) + "\n); } }\n")
        proc, data = run(CASE, os.path.join(tmp, "layer_field"), "--context", path,
                         "--yplus-field", field, "--layer-field", layer_field,
                         "--checkmesh-log", native_log)
        assert proc.returncode == 2, proc.stderr
        lc = data["cfd"]["wall_checks"]["walls"]
        assert lc["layer_source"] == "mesh_generation_field"
        assert lc["layer_distribution"]["n_covered"] == 372
        assert lc["layer_distribution"]["coverage_area_fraction"] < .9
        layer_coverage = next(f for f in data["findings"] if f["metric"] == "layer_coverage")
        assert layer_coverage["severity"] == "high"
        assert layer_coverage["n_bad"] == 60
        assert layer_coverage["location"]["bbox_min"]
        assert any(x["metric"] == "layer_coverage" for x in data["recommendations"])
        with open(os.path.join(tmp, "layer_field", "mesh_report.md"), encoding="utf-8") as stream:
            assert "nSurfaceLayers" in stream.read()

        # Real snappyHexMesh surface patches may contain ':' and '%'.
        named_case = os.path.join(tmp, "named_wall_case")
        shutil.copytree(CASE, named_case)
        unusual_name = "motorBike_frt-fairing:001%1"
        boundary_path = os.path.join(named_case, "constant", "polyMesh", "boundary")
        with open(boundary_path, encoding="ascii") as stream:
            boundary_text = stream.read()
        assert "\n    walls\n" in boundary_text
        with open(boundary_path, "w", encoding="ascii") as stream:
            stream.write(boundary_text.replace("\n    walls\n", f"\n    {unusual_name}\n"))
        named_layer = os.path.join(tmp, "named_nSurfaceLayers")
        with open(layer_field, encoding="ascii") as stream:
            field_text = stream.read()
        with open(named_layer, "w", encoding="ascii") as stream:
            stream.write(field_text.replace("walls {", unusual_name + " {"))
        named_yplus = os.path.join(tmp, "named_yPlus")
        with open(field, encoding="ascii") as stream:
            yplus_text = stream.read()
        with open(named_yplus, "w", encoding="ascii") as stream:
            stream.write(yplus_text.replace("walls {", unusual_name + " {"))
        proc, named = run(named_case, os.path.join(tmp, "named_layer"), "--context", path,
                          "--yplus-field", named_yplus, "--layer-field", named_layer,
                          "--checkmesh-log", native_log)
        assert proc.returncode == 2, proc.stderr
        assert unusual_name in {p["name"] for p in named["mesh_info"]["patches"]}
        named_wall = named["cfd"]["wall_checks"][unusual_name]
        assert named_wall["layer_distribution"]["n_covered"] == 372
        assert named_wall["provenance"] == "solver_result"
        assert "1" not in named["cfd"]["wall_checks"]

        auto_case = os.path.join(tmp, "auto_case")
        shutil.copytree(CASE, auto_case)
        os.makedirs(os.path.join(auto_case, "1"))
        shutil.copyfile(layer_field, os.path.join(auto_case, "1", "nSurfaceLayers"))
        proc, data = run(auto_case, os.path.join(tmp, "auto_layer"), "--context", path,
                         "--yplus-field", field, "--checkmesh-log", native_log)
        assert proc.returncode == 2, proc.stderr
        assert data["cfd"]["wall_checks"]["walls"]["layer_source"] == "mesh_generation_field"

        shallow_field = os.path.join(tmp, "shallow_nSurfaceLayers")
        with open(shallow_field, "w", encoding="ascii") as stream:
            stream.write("FoamFile { format ascii; class volScalarField; object nSurfaceLayers; }\n"
                         "internalField uniform 0;\n"
                         "boundaryField { walls { type fixedValue; value nonuniform List<scalar> 432\n(\n"
                         + "\n".join(map(str, [6] * 60 + [12] * 372)) + "\n); } }\n")
        proc, data = run(CASE, os.path.join(tmp, "shallow_layer"), "--context", path,
                         "--yplus-field", field, "--layer-field", shallow_field,
                         "--checkmesh-log", native_log)
        assert proc.returncode == 2, proc.stderr
        shallow = data["cfd"]["wall_checks"]["walls"]["layer_distribution"]
        assert shallow["coverage_area_fraction"] == 1
        assert shallow["n_under_target"] == 60
        assert next(f for f in data["findings"] if f["metric"] == "boundary_layers")["severity"] == "high"
        assert next(f for f in data["findings"] if f["metric"] == "layer_coverage")["severity"] == "ok"

        wrong_field = os.path.join(tmp, "wrong_nSurfaceLayers")
        with open(wrong_field, "w", encoding="ascii") as stream:
            stream.write("FoamFile { format ascii; class volScalarField; object nSurfaceLayers; }\n"
                         "internalField uniform 0;\n"
                         "boundaryField { walls { type fixedValue; value nonuniform List<scalar> 1 (12); } }\n")
        proc, data = run(CASE, os.path.join(tmp, "bad_layer_field"), "--context", path,
                         "--yplus-field", field, "--layer-field", wrong_field,
                         "--checkmesh-log", native_log)
        assert proc.returncode == 0, proc.stderr
        assert any("层字段读取失败" in x for x in data["cfd"]["missing"])
        assert data["cfd"]["wall_checks"]["walls"]["layer_source"] == "external_input"
        mismatch = os.path.join(tmp, "wrong_log.checkMesh")
        with open(mismatch, "w", encoding="ascii") as stream:
            stream.write(f"Application : checkMesh\nMesh stats\n    cells: {info['n_cells'] + 1}\nMesh OK.\n")
        proc, data = run(CASE, os.path.join(tmp, "mismatch"), "--context", path,
                         "--yplus-field", field, "--checkmesh-log", mismatch)
        assert proc.returncode == 0, proc.stderr
        assert data["extra"]["consistency_errors"]
        assert "关键 CFD 证据不足" in data["readiness"]
    print("CFD integration: unknown input, preflight, yPlus, layerFields, balances, grid study and log consistency passed")


if __name__ == "__main__":
    main()
