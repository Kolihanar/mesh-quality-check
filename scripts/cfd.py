"""OpenFOAM single-phase RANS internal-flow suitability assessment.

The physical profile is explicit: mesh geometry alone cannot determine y+ or
whether a wall treatment matches the resulting flow.
"""
from __future__ import annotations

import gzip
import os
import re

import numpy as np

from common import finding
from adapters import nearwall


def _file_text(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="latin-1", errors="replace") as stream:
        return stream.read()


def _blocks(text):
    """Yield name/body pairs for flat patch dictionaries inside boundaryField."""
    mark = re.search(r"\bboundaryField\s*\{", text)
    if not mark:
        return
    pos = mark.end()
    while pos < len(text):
        match = re.search(r'(?:("[^"]+")|([^\s{}();]+))\s*\{', text[pos:])
        if not match:
            return
        name = (match.group(1) or match.group(2)).strip('"')
        start = pos + match.end()
        depth, end = 1, start
        while depth and end < len(text):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
            end += 1
        if depth:
            return
        yield name, text[start:end - 1]
        pos = end
        if text[pos:].lstrip().startswith("}"):
            return


def read_yplus(path, wall_faces):
    """Read per-face values from an ASCII OpenFOAM yPlus volScalarField."""
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", _file_text(path), flags=re.S)
    header = re.search(r"FoamFile\s*\{(.*?)\}", text, re.S)
    if header and re.search(r"\bformat\s+binary\s*;", header.group(1)):
        raise ValueError("yPlus 场为二进制格式；请导出 ASCII 场")
    data = {}
    for patch, body in _blocks(text):
        if patch not in wall_faces:
            continue
        arr = re.search(r"\bvalue\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)\s*;", body, re.S)
        if arr:
            count = int(arr.group(1))
            values = np.fromstring(arr.group(2), sep=" ")
            if len(values) != count:
                raise ValueError(f"{patch}: yPlus 声明 {count} 个值，实际读取 {len(values)} 个")
        else:
            one = re.search(r"\bvalue\s+uniform\s+([-+\d.eE]+)\s*;", body)
            if not one:
                continue
            values = np.full(wall_faces[patch], float(one.group(1)))
        if len(values) != wall_faces[patch]:
            raise ValueError(f"{patch}: yPlus 有 {len(values)} 个值，网格边界有 {wall_faces[patch]} 个面")
        data[patch] = values
    return data


def latest_yplus(case):
    found = []
    for name in os.listdir(case):
        try:
            time = float(name)
        except ValueError:
            continue
        for suffix in ("yPlus", "yPlus.gz"):
            path = os.path.join(case, name, suffix)
            if os.path.isfile(path):
                found.append((time, path))
    return max(found, default=(None, None))[1]


def latest_layer_field(case):
    """Find the newest snappyHexMesh layer field, including constant output."""
    found = []
    for name in os.listdir(case):
        if name != "constant":
            try:
                time = float(name)
            except ValueError:
                continue
        else:
            time = -1.0
        for suffix in ("nSurfaceLayers", "nSurfaceLayers.gz"):
            path = os.path.join(case, name, suffix)
            if os.path.isfile(path):
                found.append((time, path))
    return max(found, default=(None, None))[1]


def read_layer_field(path, wall_faces, n_cells=None):
    """Read *boundary* actual layer counts from an ASCII layerFields output.

    snappyHexMesh writes the layer count on selected wall patch values. Its
    internalField is a cell diagnostic and must not substitute for wall data.
    """
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", _file_text(path), flags=re.S)
    header = re.search(r"FoamFile\s*\{(.*?)\}", text, re.S)
    if not header or not re.search(r"\bclass\s+volScalarField\s*;", header.group(1)):
        raise ValueError("层文件缺少 volScalarField 文件头")
    if re.search(r"\bformat\s+binary\s*;", header.group(1)):
        raise ValueError("层文件为二进制格式；请导出 ASCII 场")
    if not re.search(r"\bobject\s+nSurfaceLayers\s*;", header.group(1)):
        raise ValueError("层文件的 object 不是 nSurfaceLayers")
    internal = re.search(r"\binternalField\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)\s*;", text, re.S)
    if internal:
        count = int(internal.group(1))
        values = np.fromstring(internal.group(2), sep=" ")
        if len(values) != count or (n_cells is not None and count != n_cells):
            raise ValueError(f"层字段内部单元数 {count} 与当前网格 {n_cells} 不符")
    data = {}
    for patch, body in _blocks(text):
        if patch not in wall_faces:
            continue
        arr = re.search(r"\bvalue\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)\s*;", body, re.S)
        if arr:
            count = int(arr.group(1))
            values = np.fromstring(arr.group(2), sep=" ")
            if len(values) != count:
                raise ValueError(f"{patch}: 层数声明 {count} 个值，实际读取 {len(values)} 个")
        else:
            one = re.search(r"\bvalue\s+uniform\s+([-+\d.eE]+)\s*;", body)
            if not one:
                continue
            values = np.full(wall_faces[patch], float(one.group(1)))
        if len(values) != wall_faces[patch]:
            raise ValueError(f"{patch}: 层字段有 {len(values)} 个面，当前网格有 {wall_faces[patch]} 个")
        if not np.isfinite(values).all() or (values < 0).any() or not np.allclose(values, np.rint(values), atol=1e-6, rtol=0):
            raise ValueError(f"{patch}: 实际层数必须是非负整数")
        data[patch] = values.astype(int)
    return data


def _layer_summary(values, area, target):
    """Area-weighted layer distribution on wall faces."""
    values = np.asarray(values, dtype=int)
    area = np.asarray(area, dtype=float)
    if len(values) != len(area) or not len(values) or not np.isfinite(area).all() or (area <= 0).any():
        raise ValueError("层数与有效壁面面积不匹配")
    total = area.sum()
    covered = values > 0
    result = {"min": int(values.min()), "max": int(values.max()),
              "coverage_area_fraction": float(area[covered].sum() / total),
              "n_covered": int(covered.sum()), "n_faces": int(len(values)),
              "mean": float(np.average(values, weights=area))}
    if target is not None:
        under = values < int(target)
        result["under_target_area_fraction"] = float(area[under].sum() / total)
        result["n_under_target"] = int(under.sum())
    return result


def inspect_setup(case):
    """Read only simple, unambiguous OpenFOAM dictionary values."""
    setup = {"wall_field_types": {}}
    files = {"control": os.path.join(case, "system", "controlDict"),
             "turbulence": os.path.join(case, "constant", "turbulenceProperties"),
             "momentum": os.path.join(case, "constant", "momentumTransport"),
             "transport": os.path.join(case, "constant", "transportProperties"),
             "physical": os.path.join(case, "constant", "physicalProperties")}
    for kind, path in files.items():
        if not os.path.isfile(path):
            continue
        text = re.sub(r"//[^\n]*|/\*.*?\*/", "", _file_text(path), flags=re.S)
        if kind == "control":
            match = re.search(r"\bapplication\s+(\w+)\s*;", text)
            if match:
                setup["application"] = match.group(1)
        elif kind in ("turbulence", "momentum"):
            match = re.search(r"\bsimulationType\s+(\w+)\s*;", text)
            if match:
                setup["simulation_type"] = match.group(1)
            match = re.search(r"\b(?:RASModel|model)\s+(\w+)\s*;", text)
            if match:
                setup["turbulence_model"] = match.group(1)
        elif kind in ("transport", "physical"):
            match = re.search(r"\bnu\s+(?:\[[^\]]+\]\s*)?([-+\d.eE]+)\s*;", text)
            if match:
                setup["nu"] = float(match.group(1))
    for field in ("nut", "omega", "epsilon", "alphat"):
        path = os.path.join(case, "0", field)
        if not os.path.isfile(path):
            continue
        text = re.sub(r"//[^\n]*|/\*.*?\*/", "", _file_text(path), flags=re.S)
        for patch, body in _blocks(text):
            match = re.search(r"\btype\s+([^\s;]+)\s*;", body)
            if match:
                setup["wall_field_types"].setdefault(patch, {})[field] = match.group(1)
    return setup


def _weighted_summary(values, weights, low, high):
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    good = np.isfinite(values) & (values >= 0) & np.isfinite(weights) & (weights > 0)
    if not good.any():
        raise ValueError("没有有效的壁面数值和面积")
    v, w = values[good], weights[good]
    order = np.argsort(v)
    cdf = np.cumsum(w[order]) / w.sum()
    def pct(p):
        return float(v[order][min(np.searchsorted(cdf, p), len(v) - 1)])
    outside = (v < low) | (v > high)
    return {"min": float(v.min()), "p05": pct(.05), "median": pct(.5), "p95": pct(.95),
            "max": float(v.max()), "mean": float(np.average(v, weights=w)),
            "outside_area_fraction": float(w[outside].sum() / w.sum()),
            "n_outside": int(outside.sum()), "n_valid": int(len(v))}


def _target(profile):
    if "target_yplus" in profile:
        bounds = profile["target_yplus"]
        if len(bounds) != 2 or float(bounds[0]) < 0 or float(bounds[1]) <= float(bounds[0]):
            raise ValueError("target_yplus 必须是 [下限, 上限]，且上限大于下限")
        return float(bounds[0]), float(bounds[1])
    treatment = profile.get("treatment")
    if treatment == "wall_resolved":
        return 0.0, 2.0
    if treatment == "standard_wall_function":
        return 30.0, 300.0
    return None


def _severity(fraction):
    return "high" if fraction > .1 else "moderate" if fraction > .01 else "ok"


def assess(res, det, context, yplus_path=None, layer_path=None):
    """Augment an OpenFOAM result with application-specific wall evidence."""
    if res.get("source") != "openfoam" or det.get("kind") != "case":
        return res
    raw = res.pop("near_wall_raw", {})
    walls = nearwall.compact(raw)
    out = {"profile": "OpenFOAM 单相 RANS 内流", "wall_geometry": walls,
           "wall_checks": {}, "evidence": [], "missing": []}
    res["cfd"] = out
    native = res.get("extra", {}).get("checkmesh_verdict")
    if native != "Mesh OK":
        out["missing"].append("缺少与当前网格匹配且结论为 Mesh OK 的完整 checkMesh 检查")
    if res.get("extra", {}).get("consistency_errors"):
        out["missing"].append("checkMesh 日志的网格规模与当前 polyMesh 不一致，需重新运行")
    setup = inspect_setup(det["path"])
    out["case_setup"] = setup
    if setup.get("simulation_type") not in (None, "RAS"):
        out["missing"].append(f"检测到 simulationType={setup['simulation_type']}；当前适用性规则针对单相 RANS 内流")
    elif not setup.get("turbulence_model") and not context.get("flow", {}).get("turbulence_model"):
        out["missing"].append("缺少湍流模型信息；提供 turbulenceProperties/momentumTransport 或在工况 JSON 中指定")
    elif setup.get("turbulence_model") and context.get("flow", {}).get("turbulence_model") \
            and setup["turbulence_model"] != context["flow"]["turbulence_model"]:
        out["missing"].append("工况 JSON 的湍流模型与算例字典不一致，需核对")
    if not raw:
        out["missing"].append("没有可分析的 wall 边界；确认边界类型及 ASCII 网格是否可读取")
        return res
    profiles = context.get("walls", {})
    default = context.get("wall_defaults", {})
    face_counts = {p: v["n_faces"] for p, v in raw.items()}
    layer_actual = {}
    layer_file = layer_path or context.get("results", {}).get("layer_field") or latest_layer_field(det["path"])
    if layer_file:
        try:
            layer_actual = read_layer_field(layer_file, face_counts, res.get("mesh_info", {}).get("n_cells"))
            out["evidence"].append({"kind": "mesh_generation_field", "path": os.path.abspath(layer_file),
                                    "metric": "nSurfaceLayers"})
        except (OSError, ValueError) as exc:
            out["missing"].append(f"nSurfaceLayers 层字段读取失败：{exc}")
    actual = {}
    path = yplus_path or context.get("results", {}).get("yplus_file") or latest_yplus(det["path"])
    if path:
        try:
            actual = read_yplus(path, face_counts)
            out["evidence"].append({"kind": "solver_result", "path": os.path.abspath(path), "metric": "yPlus"})
            for wall in set(face_counts) - set(actual):
                out["missing"].append(f"yPlus 场缺少壁面 {wall} 的逐面值")
        except (OSError, ValueError) as exc:
            out["missing"].append(f"yPlus 场读取失败：{exc}")
    patch_groups = {patch["name"]: patch.get("groups", [])
                    for patch in res.get("mesh_info", {}).get("patches", [])}
    for name, geom in raw.items():
        profile = {**default, **profiles.get(name, {})}
        check = {"treatment": profile.get("treatment"), "status": "unknown", "geometry": walls[name],
                 "wall_conditions_verified": bool(profile.get("wall_conditions_verified"))}
        out["wall_checks"][name] = check
        field_types = setup.get("wall_field_types", {})
        inherited = {}
        for group in patch_groups.get(name, []):
            if group in field_types:
                inherited.update(field_types[group])
                check["wall_field_source"] = f"patch_group:{group}"
        inherited.update(field_types.get(name, {}))
        if name in field_types:
            check["wall_field_source"] = "patch_or_patch_over_group"
        check["wall_field_types"] = inherited
        wall_types = check["wall_field_types"]
        model = setup.get("turbulence_model") or context.get("flow", {}).get("turbulence_model")
        check["low_y_wall_function"] = (str(res.get("mesh_info", {}).get("version")) == "12"
                                        and model == "kEpsilon"
                                        and wall_types.get("nut") == "nutkWallFunction"
                                        and wall_types.get("epsilon") == "epsilonWallFunction")
        if not check["wall_field_types"] and not profile.get("wall_conditions_verified"):
            out["missing"].append(f"壁面 {name} 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified")
        elif profile.get("treatment") == "standard_wall_function" and check["wall_field_types"] \
                and not any("WallFunction" in v for v in check["wall_field_types"].values()):
            out["missing"].append(f"壁面 {name} 声称使用标准壁面函数，但已读取的壁面场类型不含 WallFunction，需核对")
        target_layers = profile.get("target_layers")
        layer = profile.get("measured_layers")
        coverage = profile.get("measured_layer_coverage")
        if name in layer_actual and geom.get("status") != "invalid_faces":
            values = layer_actual[name][geom["local_face_indices"]]
            try:
                summary = _layer_summary(values, geom["face_area"], target_layers)
            except ValueError as exc:
                out["missing"].append(f"壁面 {name} 的层字段无效：{exc}")
            else:
                check["layer_distribution"] = summary
                check["layer_source"] = "mesh_generation_field"
                check["measured_layers"] = summary["min"]
                check["measured_layer_coverage"] = summary["coverage_area_fraction"]
                layer, coverage = None, None
                if target_layers is not None:
                    bad = np.where(values < int(target_layers))[0]
                    loc = None
                    if len(bad):
                        xyz = np.asarray(geom["face_centres"])[bad]
                        loc = {"near_patches": [{"patch": name, "count": int(len(bad))}],
                               "bbox_min": xyz.min(0).tolist(), "bbox_max": xyz.max(0).tolist()}
                    fraction = summary["under_target_area_fraction"]
                    res["findings"].append(finding("boundary_layers", f"壁面 {name} 实际边界层层数",
                                                   value=summary["min"], stat="min", severity=_severity(fraction),
                                                   n_bad=summary["n_under_target"], n_total=summary["n_faces"],
                                                   total_kind="壁面面", location=loc,
                                                   definition=f"目标至少 {target_layers} 层；按面积计算不足比例 {fraction:.1%}；来自 nSurfaceLayers 边界场",
                                                   advice=[]))
        elif layer_file and name not in layer_actual:
            out["missing"].append(f"nSurfaceLayers 层字段缺少壁面 {name} 的逐面值")
        if "layer_distribution" not in check:
            if layer is not None:
                check["measured_layers"] = int(layer)
                check["layer_source"] = "external_input"
                if target_layers is not None:
                    sev = "high" if int(layer) < int(target_layers) else "ok"
                    res["findings"].append(finding("boundary_layers", f"壁面 {name} 实际边界层层数", value=int(layer),
                                                   stat="min", severity=sev, definition=f"目标至少 {target_layers} 层；实测层数来自外部输入",
                                                   advice=[]))
            elif target_layers is not None:
                out["missing"].append(f"壁面 {name} 缺少实际层数；配置层数不能代替已生成层数")
            elif profile.get("treatment") == "wall_resolved":
                out["missing"].append(f"壁面 {name} 为壁面解析方案，缺少实际近壁层数")
        min_coverage = profile.get("min_layer_coverage")
        if "layer_distribution" in check:
            observed = check["measured_layer_coverage"]
            if min_coverage is not None:
                bad = np.where(values == 0)[0]
                loc = None
                if len(bad):
                    xyz = np.asarray(geom["face_centres"])[bad]
                    loc = {"near_patches": [{"patch": name, "count": int(len(bad))}],
                           "bbox_min": xyz.min(0).tolist(), "bbox_max": xyz.max(0).tolist()}
                sev = "high" if observed < float(min_coverage) else "ok"
                res["findings"].append(finding("layer_coverage", f"壁面 {name} 边界层覆盖率",
                                               value=round(observed, 6), stat="area_fraction", severity=sev,
                                               n_bad=summary["n_faces"] - summary["n_covered"],
                                               n_total=summary["n_faces"], total_kind="壁面面", location=loc,
                                               definition=f"目标不低于 {min_coverage}；按壁面面积加权；来自 nSurfaceLayers 边界场",
                                               advice=[]))
        elif coverage is not None:
            check["measured_layer_coverage"] = float(coverage)
            check["layer_source"] = "external_input"
            if min_coverage is not None:
                sev = "high" if float(coverage) < float(min_coverage) else "ok"
                res["findings"].append(finding("layer_coverage", f"壁面 {name} 边界层覆盖率", value=float(coverage),
                                               stat="min", severity=sev, definition=f"目标不低于 {min_coverage}；实测覆盖率来自外部输入",
                                               advice=[]))
        elif min_coverage is not None:
            out["missing"].append(f"壁面 {name} 缺少实际边界层覆盖率")
        elif profile.get("treatment") == "wall_resolved" and coverage is None:
            out["missing"].append(f"壁面 {name} 为壁面解析方案，缺少实际边界层覆盖率")
        growth = profile.get("measured_growth_p95")
        max_growth = profile.get("max_growth_p95")
        if growth is not None:
            check["measured_growth_p95"] = float(growth)
            if max_growth is not None:
                sev = "high" if float(growth) > float(max_growth) else "ok"
                res["findings"].append(finding("layer_growth", f"壁面 {name} 层增长率 P95", value=float(growth),
                                               stat="p95", severity=sev, definition=f"目标不高于 {max_growth}；实测增长率来自外部输入",
                                               advice=[]))
        elif max_growth is not None:
            out["missing"].append(f"壁面 {name} 缺少实际层增长率")
        elif profile.get("treatment") == "wall_resolved" and growth is None:
            out["missing"].append(f"壁面 {name} 为壁面解析方案，缺少实际层增长率")
        if geom.get("status") == "invalid_faces":
            out["missing"].append(f"壁面 {name} 含零面积面，无法计算首层距离")
            continue
        near_faces = geom["near_wall_internal_faces"]
        if near_faces:
            for metric, label, maximum, bad_high, bad_moderate, moderate, high in (
                ("near_wall_nonortho", "近壁内部面非正交角", geom["near_wall_nonortho_max"],
                 geom["near_wall_nonortho_over70"], geom["near_wall_nonortho_over65"], 65, 70),
                ("near_wall_skew", "近壁内部面歪斜度", geom["near_wall_skew_max"],
                 geom["near_wall_skew_over4"], geom["near_wall_skew_over2_5"], 2.5, 4),
            ):
                sev = "high" if maximum > high else "moderate" if maximum > moderate else "ok"
                bad = bad_high if sev == "high" else bad_moderate if sev == "moderate" else 0
                res["findings"].append(finding(metric, f"壁面 {name} 的{label}", value=round(maximum, 4),
                                               stat="max", unit="°" if metric == "near_wall_nonortho" else "",
                                               severity=sev, n_bad=bad, n_total=near_faces, total_kind="内部面",
                                               location={"near_patches": [{"patch": name, "count": bad}]} if sev != "ok" else None,
                                               definition="壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标",
                                               advice=[]))
        area = np.asarray(geom["face_area"])
        target = _target(profile)
        if not target:
            out["missing"].append(f"壁面 {name} 缺少 treatment 或 target_yplus，无法判断近壁模型匹配")
            continue
        check["target_yplus"] = list(target)
        check["target_source"] = "explicit" if "target_yplus" in profile else "treatment_default"
        if name in actual:
            values, provenance = actual[name][geom["local_face_indices"]], "solver_result"
        else:
            u_tau = profile.get("friction_velocity")
            tau = profile.get("wall_shear_stress")
            flow = context.get("flow", {})
            nu = flow.get("nu", setup.get("nu"))
            rho = flow.get("rho")
            if u_tau is None and tau is not None and rho is not None and float(rho) > 0:
                u_tau = (abs(float(tau)) / float(rho)) ** .5
            if u_tau is None or nu is None or float(nu) <= 0 or float(u_tau) <= 0:
                absent = []
                if nu is None or float(nu) <= 0:
                    absent.append("正的 nu")
                if u_tau is None or float(u_tau) <= 0:
                    absent.append("正的 friction_velocity（或 wall_shear_stress、rho）")
                out["missing"].append(f"壁面 {name} 缺少实际 yPlus；计算前估算还缺少" + "与".join(absent))
                continue
            values = np.asarray(geom["wall_distance"]) * float(u_tau) / float(nu)
            provenance = "preflight_estimate"
        try:
            summary = _weighted_summary(values, area, *target)
        except ValueError as exc:
            out["missing"].append(f"壁面 {name} 的 yPlus 数据无效：{exc}")
            continue
        check.update(status="evaluated", provenance=provenance, yplus=summary)
        out["evidence"].append({"kind": provenance, "metric": "yPlus", "wall": name})
        sev = _severity(summary["outside_area_fraction"])
        bad = np.where((np.asarray(values) < target[0]) | (np.asarray(values) > target[1]))[0]
        location = None
        if len(bad):
            xyz = np.asarray(geom["face_centres"])[bad]
            location = {"near_patches": [{"patch": name, "count": int(len(bad))}],
                        "bbox_min": xyz.min(0).tolist(), "bbox_max": xyz.max(0).tolist()}
        target_source_zh = "工况显式指定" if check["target_source"] == "explicit" else "壁面处理默认值"
        res["findings"].append(finding("yplus", f"壁面 {name} 的 y⁺ 区间偏离", value=round(summary["p95"], 3),
                                       stat="p95", severity=sev, n_bad=summary["n_outside"],
                                       n_total=summary["n_valid"], total_kind="壁面面",
                                       location=location,
                                       definition=f"筛查目标区间 {target[0]}–{target[1]}（{target_source_zh}）；按面积计算区间外比例 {summary['outside_area_fraction']:.1%}；证据 {provenance}；单凭偏离不能判定求解失败",
                                       advice=[]))
    return res
