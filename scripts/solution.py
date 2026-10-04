"""Evidence checks for an existing steady internal-flow trial calculation.

All surface fluxes in the input use the outward-normal sign convention.
"""
from __future__ import annotations

import numpy as np

from common import finding


def _ratio(values):
    arr = np.asarray(list(values.values()), dtype=float)
    if not len(arr) or not np.isfinite(arr).all():
        raise ValueError("通量数据为空或含非有限值")
    scale = max(float(np.abs(arr[arr < 0]).sum()), float(arr[arr > 0].sum()), 1e-300)
    return float(abs(arr.sum()) / scale)


def assess(res, context):
    if "cfd" not in res:
        return res
    data = context.get("results", {})
    checked = {}
    res["cfd"]["solution_checks"] = checked
    flux_key = "mass_flux_kg_s" if "mass_flux_kg_s" in data else (
        "volumetric_flux_m3_s" if "volumetric_flux_m3_s" in data
        and context.get("flow", {}).get("constant_density") is True else None)
    if flux_key:
        ratio = _ratio(data[flux_key])
        tol = float(data.get("mass_balance_tolerance", .01))
        checked["mass_balance"] = {"relative_imbalance": ratio, "tolerance": tol, "basis": flux_key}
        definition = ("各边界质量通量按外法向有符号求和，除以较大的流入/流出总量" if flux_key == "mass_flux_kg_s"
                      else "恒密度不可压缩流：各边界体积通量按外法向有符号求和，除以较大的流入/流出总量")
        res["findings"].append(finding("mass_balance", "稳态质量守恒", value=ratio, stat="relative", unit="",
                                       severity="high" if ratio > tol else "ok",
                                       definition=definition,
                                       advice=[]))
    else:
        if "volumetric_flux_m3_s" in data:
            res["cfd"]["missing"].append("已有体积通量，但需在 flow.constant_density 明确设为 true 后才能据此核对质量守恒")
        else:
            res["cfd"]["missing"].append("缺少试算后各入口/出口的有符号质量通量（或恒密度流的体积通量），无法核对质量守恒")

    if "advective_enthalpy_W" in data and "wall_heat_flow_W" in data:
        energy = {**data["advective_enthalpy_W"]}
        energy.update({f"wall:{k}": v for k, v in data["wall_heat_flow_W"].items()})
        ratio = _ratio(energy)
        tol = float(data.get("energy_balance_tolerance", .02))
        checked["energy_balance"] = {"relative_imbalance": ratio, "tolerance": tol}
        res["findings"].append(finding("energy_balance", "稳态能量守恒", value=ratio, stat="relative",
                                       severity="high" if ratio > tol else "ok",
                                       definition="边界焓流与壁面热流均以向外为正；适用于无未列出的体热源/功项的稳态算例",
                                       advice=[]))
    elif context.get("flow", {}).get("heat_transfer"):
        res["cfd"]["missing"].append("换热算例缺少有符号焓流与壁面热流，无法核对能量守恒")

    histories = data.get("monitor_history", {})
    if histories:
        for name, values in histories.items():
            arr = np.asarray(values, dtype=float)
            if len(arr) < 10 or not np.isfinite(arr).all():
                res["cfd"]["missing"].append(f"监测量 {name} 需要至少 10 个有限值")
                continue
            n = max(2, len(arr) // 5)
            early, late = float(arr[-2*n:-n].mean()), float(arr[-n:].mean())
            drift = abs(late - early) / max(abs(late), abs(early), 1e-12)
            tol = float(data.get("monitor_drift_tolerance", .005))
            checked.setdefault("monitor_drift", {})[name] = {"relative_change": drift, "tolerance": tol}
            res["findings"].append(finding("monitor_drift", f"监测量 {name} 的末段漂移", value=drift,
                                           severity="high" if drift > max(4 * tol, .02) else "moderate" if drift > tol else "ok",
                                           definition="比较末尾两个等长窗口的均值；监测量稳定不单独证明网格无关",
                                           advice=[]))
            recent = arr[-n:]
            spread = float((np.percentile(recent, 95) - np.percentile(recent, 5)) /
                           max(abs(late), 1e-12))
            spread_tol = float(data.get("monitor_spread_tolerance", .01))
            checked.setdefault("monitor_spread", {})[name] = {"relative_span": spread, "tolerance": spread_tol}
            res["findings"].append(finding("monitor_spread", f"监测量 {name} 的末段波动", value=spread,
                                           severity="high" if spread > max(4 * spread_tol, .04) else "moderate" if spread > spread_tol else "ok",
                                           definition="末尾 20% 样本的 P95–P05 跨度相对末段均值；防止往复波动被窗口均值抵消",
                                           advice=[]))
    else:
        res["cfd"]["missing"].append("缺少压降、流量或换热量的监测序列，无法复核结果稳定性")

    study = data.get("grid_study", [])
    if len(study) >= 3:
        study = sorted(study, key=lambda x: int(x["n_cells"]))
        if len({int(s["n_cells"]) for s in study}) < 3:
            res["cfd"]["missing"].append("网格敏感性输入的单元数必须对应至少三套不同网格")
            return res
        metrics = set(study[0]).intersection(*(set(s) for s in study[1:])) - {"n_cells"}
        if not metrics:
            res["cfd"]["missing"].append("三套网格没有共同的目标量，无法比较网格敏感性")
        for name in sorted(metrics):
            coarse, medium, fine = (float(s[name]) for s in study[-3:])
            change = abs(fine - medium) / max(abs(fine), abs(medium), 1e-12)
            tol = float(data.get("grid_change_tolerance", .02))
            monitor_checks = checked.get("monitor_drift", {})
            spread_checks = checked.get("monitor_spread", {})
            related = {key: value for key, value in monitor_checks.items()
                       if key == name or key.startswith(f"{name}_")}
            unstable = [key for key, value in related.items()
                        if value["relative_change"] > value["tolerance"]
                        or (key in spread_checks and
                            spread_checks[key]["relative_span"] > spread_checks[key]["tolerance"])]
            required_histories = {f"{name}_{grade}" for grade in ("coarse", "medium", "fine")}
            missing_histories = sorted(required_histories - related.keys())
            if missing_histories:
                res["cfd"]["missing"].append(
                    f"网格敏感性目标量 {name} 缺少粗/中/细各自的有效监测序列：" + "、".join(missing_histories))
            interpretation = ("provisional_target_unstable" if unstable else
                              "provisional_missing_grid_histories" if missing_histories else "target_histories_stable")
            checked.setdefault("grid_sensitivity", {})[name] = {
                "coarse": coarse, "medium": medium, "fine": fine,
                "fine_medium_relative_change": change, "tolerance": tol,
                "n_cells": [int(s["n_cells"]) for s in study[-3:]],
                "unstable_monitor_histories": unstable,
                "missing_monitor_histories": missing_histories,
                "interpretation": interpretation}
            definition = "细/中网格目标量相对变化；需要同一物理模型和边界条件，未据此推断严格误差界"
            if unstable:
                definition += "；相关监测量末段仍在漂移或波动，网格敏感性比较暂为初步结果，需先使各网格目标量稳定"
            elif missing_histories:
                definition += "；缺少三套网格各自的目标量监测序列，网格敏感性比较暂为初步结果"
            res["findings"].append(finding("grid_sensitivity", f"目标量 {name} 的网格敏感性", value=change,
                                           severity="high" if change > tol else "ok",
                                           definition=definition,
                                           advice=[]))
    else:
        res["cfd"]["missing"].append("缺少至少三套网格的同一目标量结果，无法检查网格敏感性")
    return res
